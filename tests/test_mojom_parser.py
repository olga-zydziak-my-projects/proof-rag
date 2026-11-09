"""Adversarial wrapper tests, independent expected bytes and header counts."""
import unittest
from unittest.mock import patch
import sys
import types
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile

from repo_proof import mojom_parser
from repo_proof.mojom_parser import parse_source, parser_identity


class MojomParserTests(unittest.TestCase):
    def parse(self, data):
        return parse_source(data, "fixture.mojom")

    def test_official_runtime_identity_is_pinned_and_checked(self):
        identity = parser_identity()
        self.assertEqual("27cec857a08a0ee0e1b41f5eb18c07467a0ce093", identity["upstream_commit"])
        self.assertEqual("3.11", identity["ply_version"])
        self.assertEqual(14, identity["upstream_files"])

    def test_comments_and_other_string_literals_do_not_form_imports(self):
        data = (b'// import "fake.mojom";\n/* import "also_fake.mojom"; */\n'
                b'import "real.mojom";\nconst string Text = "import \\\"string_fake.mojom\\\";";\n')
        result = self.parse(data)
        self.assertEqual("parsed", result["status"], result["diagnostics"])
        self.assertEqual(["real.mojom"], [i["decoded_path"] for i in result["imports"]])

    def test_attributes_and_duplicate_imports_keep_every_source_location(self):
        data = (b'[EnableIf=feature_flag] import "a.mojom";\n'
                b'import "a.mojom";\nstruct Holder { array<array<uint8>> value; };\n')
        result = self.parse(data)
        self.assertEqual("parsed", result["status"], result["diagnostics"])
        self.assertEqual(2, len(result["imports"]))
        first, second = result["imports"]
        self.assertEqual("[EnableIf=feature_flag]", first["attributes_literal"])
        self.assertIsNone(second["attributes_literal"])
        self.assertEqual(0, first["declaration_span"]["byte_start"])
        self.assertNotEqual(first["literal_span"], second["literal_span"])

    def test_crlf_unicode_coordinates_are_original_utf8_byte_offsets(self):
        data = ('// żółć 🌍\r\n[EnableIf="✓"]\r\nimport "żółć.mojom";\r\n'
                'const string Greeting = "cześć";\r\n').encode("utf-8")
        result = self.parse(data)
        self.assertEqual("parsed", result["status"], result["diagnostics"])
        item = result["imports"][0]
        literal = item["literal_span"]
        self.assertEqual(data.index('"żółć.mojom"'.encode()), literal["byte_start"])
        self.assertEqual('"żółć.mojom"'.encode(), data[literal["byte_start"]:literal["byte_end"]])
        self.assertEqual(3, literal["line"])
        self.assertEqual(8, literal["byte_column"])
        self.assertEqual(data.index(b"[EnableIf"), item["declaration_span"]["byte_start"])

    def test_noncanonical_paths_are_preserved_without_windows_normalization(self):
        data = b'import "a/../b.mojom";\nimport "foo\\\\bar.mojom";\n'
        result = self.parse(data)
        self.assertEqual("parsed", result["status"], result["diagnostics"])
        self.assertEqual("a/../b.mojom", result["imports"][0]["decoded_path"])
        self.assertEqual("foo\\bar.mojom", result["imports"][1]["decoded_path"])
        self.assertEqual('"foo\\\\bar.mojom"', result["imports"][1]["original_literal"])

    def test_full_file_guard_and_state_reset_after_each_error(self):
        valid = b'import "real.mojom";\nstruct Good { uint8 field; };\n'
        expected = self.parse(valid)
        self.assertEqual("parsed", expected["status"])
        cases = [
            b'import "real.mojom";\nthis is invalid;',
            b'import "real.mojom";\nstruct Bad { uint8 field } ;',
            b'import "real.mojom";\n/* unfinished',
            b'import "real.mojom";\nconst string Bad = "unfinished',
            b'import "real.mojom"\n',
            b'struct First {};\nimport "real.mojom";\n',
            b'interface I { Method() => result<uint8, >; };',
        ]
        for data in cases:
            with self.subTest(data=data):
                failed = self.parse(data)
                self.assertEqual("unresolved", failed["status"])
                self.assertTrue(failed["diagnostics"])
                self.assertTrue(all(i["source_status"] == "unresolved" for i in failed["imports"]))
                self.assertEqual(expected, self.parse(valid))

    def test_prefix_imports_on_invalid_suffix_are_explicitly_partial(self):
        result = self.parse(b'import "a.mojom";\nstruct Invalid { !!! };')
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(1, len(result["imports"]))
        self.assertEqual("lexical_prefix_only", result["imports"][0]["declaration_validation"])

    def test_utf8_and_bom_errors_fail_closed(self):
        for data in (b'\xff', b'\xef\xbb\xbfimport "a.mojom";'):
            result = self.parse(data)
            self.assertEqual("unresolved", result["status"])
            self.assertEqual([], result["imports"])
            self.assertTrue(result["diagnostics"])

    def test_empty_attribute_section_and_unicode_before_import_keep_spans(self):
        data = '/* żółć */ [] import "a.mojom";'.encode("utf-8")
        result = self.parse(data)
        self.assertEqual("parsed", result["status"], result["diagnostics"])
        item = result["imports"][0]
        self.assertEqual("[]", item["attributes_literal"])
        self.assertEqual(data.index(b"[]"), item["declaration_span"]["byte_start"])
        self.assertEqual(data.index(b"import"), item["keyword_span"]["byte_start"])
        self.assertEqual(data.index(b'"a.mojom"') + 1, item["literal_span"]["byte_column"])

    def test_foreign_preloaded_module_fails_closed(self):
        with patch.dict(sys.modules, {"ply.foreign": types.ModuleType("ply.foreign")}):
            result = self.parse(b'import "a.mojom";')
            self.assertEqual("unresolved", result["status"])
            self.assertIn("foreign module", result["diagnostics"][0]["message"])
        self.assertEqual("parsed", self.parse(b'import "a.mojom";')["status"])

    def test_changed_vendor_lock_identity_is_rejected(self):
        with patch.object(mojom_parser, "LOCK_SHA256", "0" * 64):
            with self.assertRaisesRegex(mojom_parser.ParserRuntimeError, "lock identity mismatch"):
                parser_identity()

    def test_vendor_tool_rejects_rewritten_lock_before_check_or_download(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "vendor_mojom_parser.py"
        spec = importlib.util.spec_from_file_location("vendor_tool_for_test", script)
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        self.assertEqual(mojom_parser.LOCK_SHA256, tool.LOCK_SHA256)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "forged-lock.json"
            forged = json.loads(tool.LOCK.read_bytes())
            forged["entries"][0]["sha256"] = "0" * 64
            path.write_bytes(tool.encoded(forged))
            with patch.object(tool, "LOCK", path), patch.object(tool.urllib.request, "urlopen") as download:
                for option in ("--check", "--download"):
                    error = io.StringIO()
                    with contextlib.redirect_stderr(error):
                        self.assertEqual(2, tool.main([option]))
                    self.assertIn("lock identity mismatch", error.getvalue())
                download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
