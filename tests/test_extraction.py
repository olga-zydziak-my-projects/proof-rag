"""Source extraction tests with real, offline synthetic Git corpus snapshots."""
from contextlib import ExitStack
import copy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from repo_proof import corpus
from repo_proof.extraction import (ExpectedInputs, SourceBindingError,
                                   canonical_import_path, extract_corpus,
                                   load_snapshot, valid_import_location)


class SyntheticCorpus:
    """A temporary Git tree, never a source checkout or network operation."""

    def __init__(self, files=None, *, references=(), specials=None, root="r.mojom"):
        self.files = files or {
            "r.mojom": b"module target;\n",
            "a.mojom": b'import "r.mojom";\nstruct A {};\n',
            "b.mojom": b'import "a.mojom";\nstruct B {};\n',
            "x.mojom": b"module isolated;\n",
        }
        self.references, self.specials, self.query_root = references, specials or {}, root

    def __enter__(self):
        self.stack = ExitStack()
        folder = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.root = Path(folder) / "corpus"
        self.store = self.root / "git"
        self.store.mkdir(parents=True)
        self.call("init", "--bare", str(self.store), bare=False)
        paths = {}
        self.oids = {}
        for path, data in self.files.items():
            oid = self.call("hash-object", "-w", "--stdin", data=data).decode().strip()
            self.oids[path] = oid
            paths[path] = ("100644", "blob", oid)
        for path, (mode, payload) in self.specials.items():
            if mode == "160000":
                paths[path] = (mode, "commit", payload)
            else:
                oid = self.call("hash-object", "-w", "--stdin", data=payload).decode().strip()
                paths[path] = (mode, "blob", oid)
        root_tree = self.make_tree(paths)
        self.commit = self.call("commit-tree", root_tree, data=b"synthetic source fixture\n").decode().strip()
        self.stack.enter_context(patch.object(corpus, "COMMIT", self.commit))
        self.stack.enter_context(patch.object(corpus, "REFERENCES", tuple(self.references)))
        corpus.run(self.root)
        self.manifest_bytes = (self.root / "manifest.json").read_bytes()
        self.expected = ExpectedInputs(self.commit, hashlib.sha256(self.manifest_bytes).hexdigest(),
                                       self.query_root)
        return self

    def __exit__(self, *args):
        self.stack.__exit__(*args)

    def call(self, *args, data=None, bare=True):
        command = ["git"] + (["--git-dir=" + str(self.store)] if bare else []) + list(args)
        env = dict(os.environ, GIT_AUTHOR_NAME="Synthetic fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Synthetic fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                   GIT_AUTHOR_DATE="2000-01-01T00:00:00Z", GIT_COMMITTER_DATE="2000-01-01T00:00:00Z",
                   GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
        return subprocess.run(command, input=data, capture_output=True, env=env, check=True).stdout

    def make_tree(self, paths):
        direct, children = {}, {}
        for path, metadata in paths.items():
            head, separator, tail = path.partition("/")
            if separator:
                children.setdefault(head, {})[tail] = metadata
            else:
                direct[head] = metadata
        for name, descendants in children.items():
            direct[name] = ("040000", "tree", self.make_tree(descendants))
        raw = b"".join(f"{mode} {kind} {oid}\t".encode() + name.encode("utf-8") + b"\0"
                       for name, (mode, kind, oid) in direct.items())
        return self.call("mktree", "--missing", "-z", data=raw).decode().strip()

    def blob_path(self, path):
        return corpus.blob_path(self.root, self.oids[path])

    def extract(self):
        return extract_corpus(self.root, self.expected)[0]


class ExtractionTests(unittest.TestCase):
    def test_comments_strings_conditions_duplicates_and_source_byte_locations(self):
        source = ('// żółć 🌍 import "fake.mojom";\r\n'
                  '/* import "fake2.mojom"; */\r\n'
                  '[EnableIf="✓"] import "r.mojom";\r\n'
                  'import "r.mojom";\r\n'
                  'const string Text = "import \\\"fake3.mojom\\\";";\r\n').encode("utf-8")
        with SyntheticCorpus({"r.mojom": b"module root;\n", "a.mojom": source}) as fixture:
            extraction = fixture.extract()
            self.assertEqual("complete", extraction["extraction_status"])
            self.assertEqual([["a.mojom", "r.mojom"]], extraction["graph"]["edges"])
            self.assertEqual(2, extraction["coverage"]["declarations"])
            self.assertEqual(1, extraction["coverage"]["duplicate_internal_declarations"])
            record = next(item for item in extraction["files"] if item["path"] == "a.mojom")
            self.assertEqual("[EnableIf=\"✓\"]", record["imports"][0]["attributes_literal"])
            self.assertEqual(2, len(record["imports"]))
            for declaration in record["imports"]:
                self.assertEqual(fixture.oids["a.mojom"], declaration["importer_blob_object_id"])
                self.assertEqual("a.mojom", declaration["importer"])
                self.assertTrue(valid_import_location(source, declaration))
                span = declaration["literal_span"]
                self.assertEqual(declaration["original_literal"].encode(), source[span["byte_start"]:span["byte_end"]])
            self.assertNotEqual(record["imports"][0]["literal_span"], record["imports"][1]["literal_span"])
            self.assertEqual(3, record["imports"][0]["literal_span"]["line"])

    def test_external_wrong_case_symlink_gitlink_and_regular_boundaries_are_resolved(self):
        source = (b'import "R.mojom"; import "absent.mojom"; import "link.mojom"; '
                  b'import "deps/remote.mojom"; import "notes.txt"; import "r.mojom";')
        with SyntheticCorpus({"r.mojom": b"module root;", "a.mojom": source, "notes.txt": b"notes"},
                             specials={"link.mojom": ("120000", b"r.mojom"),
                                       "deps": ("160000", "a" * 40)}) as fixture:
            extraction = fixture.extract()
            self.assertEqual("complete", extraction["extraction_status"])
            self.assertEqual(["a.mojom", "r.mojom"], extraction["graph"]["nodes"])
            imports = next(r for r in extraction["files"] if r["path"] == "a.mojom")["imports"]
            self.assertEqual(["outside_scope"] * 5 + ["internal"], [i["status"] for i in imports])
            self.assertEqual("R.mojom", imports[0]["resolved_path"])
            self.assertIn("gitlink", imports[3]["reason"])
            self.assertEqual([["a.mojom", "r.mojom"]], extraction["graph"]["edges"])

    def test_noncanonical_imports_are_unresolved_without_normalization(self):
        literals = ['"./r.mojom"', '"foo/../r.mojom"', '"/r.mojom"',
                    '"C:/r.mojom"', '"foo//r.mojom"', '"foo\\\\r.mojom"',
                    '"\\x72.mojom"']
        source = ("\n".join("import " + literal + ";" for literal in literals)).encode()
        with SyntheticCorpus({"r.mojom": b"module root;", "a.mojom": source}) as fixture:
            extraction = fixture.extract()
            record = next(r for r in extraction["files"] if r["path"] == "a.mojom")
            self.assertEqual("parsed", record["parse_status"])
            self.assertEqual("unresolved", record["status"])
            self.assertEqual("unresolved", extraction["extraction_status"])
            self.assertEqual(len(literals), extraction["coverage"]["declaration_statuses"]["unresolved"])
            self.assertEqual([], extraction["graph"]["edges"])
            self.assertTrue(all(i["resolved_path"] is None for i in record["imports"]))

    def test_invalid_suffix_and_lexical_failures_keep_terminal_status_for_every_file(self):
        sources = {
            "r.mojom": b"module target;",
            "good.mojom": b'import "r.mojom"; struct Good {};',
            "bad.mojom": b'import "r.mojom"; struct Bad { uint8 missing_semicolon };',
            "comment.mojom": b'import "r.mojom"; /* unfinished',
            "literal.mojom": b'import "r.mojom"; const string Bad = "unfinished',
            "semicolon.mojom": b'import "r.mojom"',
        }
        with SyntheticCorpus(sources) as fixture:
            extraction = fixture.extract()
            self.assertEqual(len(sources), len(extraction["files"]))
            self.assertEqual({"resolved": 2, "unresolved": 4}, extraction["coverage"]["file_statuses"])
            self.assertTrue(extraction["coverage"]["all_S_have_terminal_status"])
            self.assertFalse(extraction["coverage"]["source_complete"])
            self.assertEqual([["good.mojom", "r.mojom"]], extraction["graph"]["edges"])
            bad = next(r for r in extraction["files"] if r["path"] == "bad.mojom")
            self.assertTrue(bad["diagnostics"])
            self.assertEqual("unresolved", bad["imports"][0]["status"])
            self.assertEqual("enclosing_source_not_fully_validated", bad["imports"][0]["reason"])

    def test_missing_and_corrupt_unrelated_source_both_block_global_completeness(self):
        with SyntheticCorpus() as fixture:
            fixture.blob_path("a.mojom").unlink()
            fixture.blob_path("x.mojom").write_bytes(b"corrupt isolated file")
            extraction = fixture.extract()
            self.assertEqual(4, len(extraction["files"]))
            self.assertEqual("unresolved", extraction["corpus_status"])
            self.assertFalse(extraction["coverage"]["source_complete"])
            by_path = {r["path"]: r for r in extraction["files"]}
            for path in ("a.mojom", "x.mojom"):
                self.assertEqual("not_parsed", by_path[path]["parse_status"])
                self.assertEqual("unresolved", by_path[path]["status"])
                self.assertTrue(by_path[path]["diagnostics"])
            self.assertEqual({"a.mojom", "x.mojom"}, {d["path"] for d in extraction["corpus_diagnostics"]})

    def test_missing_materialized_parser_reference_is_not_silently_ignored(self):
        with SyntheticCorpus({"r.mojom": b"module target;", "reference.py": b"# reference\n"},
                             references=("reference.py",)) as fixture:
            fixture.blob_path("reference.py").unlink()
            extraction = fixture.extract()
            self.assertEqual(1, extraction["coverage"]["source_files"])
            self.assertEqual(1, extraction["coverage"]["fully_parsed_files"])
            self.assertEqual("unresolved", extraction["extraction_status"])
            self.assertEqual("reference.py", extraction["corpus_diagnostics"][0]["path"])

    def test_independent_pin_manifest_contract_and_tree_expectations(self):
        with SyntheticCorpus() as fixture:
            for expected in (replace(fixture.expected, commit="0" * 40),
                             replace(fixture.expected, manifest_sha256="0" * 64),
                             replace(fixture.expected, contract_version="different")):
                with self.subTest(expected=expected):
                    with self.assertRaises(SourceBindingError):
                        load_snapshot(fixture.root, expected)
            manifest = json.loads(fixture.manifest_bytes)
            manifest["entries"].pop()
            encoded = corpus.encoded(manifest)
            (fixture.root / "manifest.json").write_bytes(encoded)
            with self.assertRaisesRegex(SourceBindingError, "independently expected"):
                load_snapshot(fixture.root, fixture.expected)
            forged_expectation = replace(fixture.expected, manifest_sha256=hashlib.sha256(encoded).hexdigest())
            with self.assertRaisesRegex(SourceBindingError, "omits/adds"):
                load_snapshot(fixture.root, forged_expectation)

    def test_repeated_offline_extraction_is_byte_deterministic(self):
        with SyntheticCorpus() as fixture:
            first = fixture.extract()
            second = fixture.extract()
            self.assertEqual(corpus.encoded(first), corpus.encoded(second))
            self.assertEqual(4, first["coverage"]["source_files"])
            self.assertEqual([["a.mojom", "r.mojom"], ["b.mojom", "a.mojom"]], first["graph"]["edges"])

    def test_byte_coordinate_validation_rejects_character_offsets_and_bool_coordinates(self):
        source = '// żółć\r\nimport "r.mojom";'.encode()
        literal_start = source.index(b'"r.mojom"')
        declaration_start = source.index(b"import")
        item = {"original_literal": '"r.mojom"',
                "declaration_span": {"byte_start": declaration_start, "byte_end": len(source),
                                     "line": 2, "byte_column": 1},
                "keyword_span": {"byte_start": declaration_start, "byte_end": declaration_start + 6,
                                 "line": 2, "byte_column": 1},
                "literal_span": {"byte_start": literal_start, "byte_end": len(source) - 1,
                                 "line": 2, "byte_column": 8},
                "attributes_literal": None}
        self.assertTrue(valid_import_location(source, item))
        item["literal_span"]["byte_start"] -= 4  # Unicode char index mistaken for byte offset.
        self.assertFalse(valid_import_location(source, item))
        item["literal_span"]["byte_start"] = literal_start
        item["declaration_span"]["byte_column"] = True
        self.assertFalse(valid_import_location(source, item))

    def test_keyword_and_attribute_locations_are_verified_against_original_unicode_bytes(self):
        source = '// żółć 🌍\r\n[EnableIf="✓"]\r\nimport "r.mojom";\r\n'.encode("utf-8")
        declaration_start = source.index(b"[EnableIf")
        keyword_start = source.index(b"import")
        literal_start = source.index(b'"r.mojom"')
        declaration_end = source.index(b";") + 1
        item = {"original_literal": '"r.mojom"',
                "attributes_literal": '[EnableIf="✓"]',
                "declaration_span": {"byte_start": declaration_start, "byte_end": declaration_end,
                                     "line": 2, "byte_column": 1},
                "keyword_span": {"byte_start": keyword_start, "byte_end": keyword_start + 6,
                                 "line": 3, "byte_column": 1},
                "literal_span": {"byte_start": literal_start, "byte_end": declaration_end - 1,
                                 "line": 3, "byte_column": 8}}
        self.assertTrue(valid_import_location(source, item))
        shifted_keyword = copy.deepcopy(item)
        shifted_keyword["keyword_span"].update(byte_start=keyword_start + 1,
                                                byte_end=keyword_start + 7, byte_column=2)
        wrong_attributes = copy.deepcopy(item)
        wrong_attributes["attributes_literal"] = '[EnableIf="x"]'
        missing_attributes = copy.deepcopy(item)
        missing_attributes["attributes_literal"] = None
        for altered in (shifted_keyword, wrong_attributes, missing_attributes):
            with self.subTest(altered=altered):
                self.assertFalse(valid_import_location(source, altered))


if __name__ == "__main__":
    unittest.main()
