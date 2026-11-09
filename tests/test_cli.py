import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from repo_proof.cli import main


class CLITests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.json"
            path.write_text('{"nodes":[],"nodes":["r"],"edges":[]}', encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["query", "--graph", str(path), "--root", "r"]), 2)

    def test_query_verify_and_both_tampering_cases(self):
        with tempfile.TemporaryDirectory() as folder:
            graph = Path(folder) / "graph.json"
            cert = Path(folder) / "cert.json"
            graph.write_text(json.dumps({"nodes": ["r", "a", "x"],
                                        "edges": [["a", "r"]]}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["query", "--graph", str(graph), "--root", "r",
                                       "--out", str(cert)]), 0)
                self.assertEqual(main(["verify", "--graph", str(graph), "--root", "r",
                                       "--certificate", str(cert)]), 0)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["demo", "--graph", str(graph), "--root", "r"]), 0)
            result = json.loads(output.getvalue())
            self.assertTrue(result["original_certificate_accepted"])
            self.assertTrue(all(case["rejected"] for case in result["tampering"]))


if __name__ == "__main__":
    unittest.main()
