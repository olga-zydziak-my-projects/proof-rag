"""Exercise project memory across independent invocations of the public CLI."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


CLI = Path(__file__).resolve().parents[1] / "scripts/project_memory.py"


def write_bundle(folder, project, commit, paths):
    identity = {"repository": project, "commit": commit}
    snapshot = {**identity, "root_tree": "0" * 40}
    header = {"type": "result", "format": "git-literal-search-v1", **snapshot, "literal": "Needle"}
    hits = [{"type": "hit", **identity, "path": path, "blob_id": "1" * 40,
             "byte_offset": 0, "line": 1} for path in paths]
    rows = [header, *hits, {"type": "complete", "count": len(paths)}]
    answer = "".join(json.dumps(row) + "\n" for row in rows).encode("ascii")
    receipt = {"format": "fineract-r2-verification-v1", "status": "VERIFIED", "snapshot": snapshot,
               "literal": "Needle", "result_sha256": sha256(answer).hexdigest(), "count": len(paths)}
    folder.mkdir()
    (folder / "answer.jsonl").write_bytes(answer)
    (folder / "verification.json").write_text(json.dumps(receipt), encoding="ascii")


class ProjectMemoryTests(unittest.TestCase):
    def test_preference_survives_restart_and_stays_with_its_project(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "memory" / "preferences.sqlite3"

            def run(*args, code=0):
                result = subprocess.run(
                    [sys.executable, "-B", "-X", "utf8", CLI, "--db", database, *args],
                    cwd=root, capture_output=True, encoding="utf-8", timeout=10,
                )
                self.assertEqual(result.returncode, code, (result.stdout, result.stderr))
                return (result.stderr if code else result.stdout).splitlines()

            project_a, project_b = "apache/fineract", "apache/other"
            commit_1, commit_2 = "2" * 40, "3" * 40
            paths = ["modul/src/test/java/A.java", "modul/src/testing/A.java",
                     "src/test/B.java", "modul/src/test", "modul/notsrc/test/C.java",
                     "modul/src/main/Ścieżka.java"]
            bundle_a, later_a, bundle_b = root / "a", root / "later-a", root / "b"
            write_bundle(bundle_a, project_a, commit_1, paths)
            write_bundle(later_a, project_a, commit_2, paths)
            write_bundle(bundle_b, project_b, commit_1, paths)
            published_files = [bundle / filename for bundle in (bundle_a, later_a, bundle_b)
                               for filename in ("answer.jsonl", "verification.json")]
            original_bytes = [path.read_bytes() for path in published_files]
            show_a = ("pokaż, co pamiętasz", "--project", project_a)
            remember_a = ("zapamiętaj", "--project", project_a)
            forget_a = ("zapomnij", "--project", project_a)
            empty = ["Brak zapisanych preferencji"]
            flat = ["Wszystkie pliki (6)", *(f"  {path}" for path in paths)]
            preference = "pokazuj pliki testowe osobno"

            self.assertEqual(run(*show_a), empty)
            self.assertEqual(run("pokaż-wynik", bundle_a), flat)
            self.assertFalse(database.exists())

            run(*remember_a, preference)
            run(*remember_a, preference)
            self.assertEqual(run(*show_a), [f"{project_a} — {preference}"])
            saved_bytes = database.read_bytes()
            for invalid in [("nieznane",), (*remember_a, "inna preferencja")]:
                with self.subTest(invalid=invalid):
                    self.assertTrue(run(*invalid, code=2)[0].startswith("usage:"))
                    self.assertEqual(database.read_bytes(), saved_bytes)

            grouped = ["Pliki pod src/test/ (2)", f"  {paths[0]}", f"  {paths[2]}",
                       "Pozostałe pliki (4)", *(f"  {paths[i]}" for i in (1, 3, 4, 5))]
            self.assertEqual(run("pokaż-wynik", bundle_a), grouped)
            self.assertEqual(run("pokaż-wynik", later_a), grouped)
            self.assertEqual([path.read_bytes() for path in published_files], original_bytes)

            self.assertEqual(run("pokaż, co pamiętasz", "--project", project_b), empty)
            self.assertEqual(run("pokaż-wynik", bundle_b), flat)

            run(*forget_a)
            self.assertEqual(run(*show_a), empty)
            self.assertEqual(run("pokaż-wynik", bundle_a), flat)
            run(*forget_a)
            self.assertEqual(run(*show_a), empty)
            self.assertEqual([path.read_bytes() for path in published_files], original_bytes)

            invalid_bundle = root / "invalid"
            write_bundle(invalid_bundle, project_a, commit_1, paths)
            invalid_answer = invalid_bundle / "answer.jsonl"
            invalid_answer.write_bytes(invalid_answer.read_bytes() + b"\n")
            self.assertIn("SHA-256", run("pokaż-wynik", invalid_bundle, code=1)[0])
            invalid_receipt = invalid_bundle / "verification.json"
            receipt = json.loads(invalid_receipt.read_bytes())
            receipt.update(status="MISMATCH", result_sha256=sha256(invalid_answer.read_bytes()).hexdigest())
            invalid_receipt.write_text(json.dumps(receipt), encoding="ascii")
            self.assertIn("VERIFIED", run("pokaż-wynik", invalid_bundle, code=1)[0])
