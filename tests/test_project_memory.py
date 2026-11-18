"""Exercise project memory across independent invocations of the public CLI."""

from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


CLI = Path(__file__).resolve().parents[1] / "scripts/project_memory.py"
QUESTION = "które z tych plików są testami?"


def write_bundle(folder, project, commit, paths, *, literal="Needle", output_directory=None):
    identity = {"repository": project, "commit": commit}
    snapshot = {**identity, "root_tree": "0" * 40}
    header = {"type": "result", "format": "git-literal-search-v1", **snapshot, "literal": literal}
    hits = [{"type": "hit", **identity, "path": path, "blob_id": "1" * 40,
             "byte_offset": 0, "line": 1} for path in paths]
    rows = [header, *hits, {"type": "complete", "count": len(paths)}]
    answer = "".join(json.dumps(row) + "\n" for row in rows).encode("ascii")
    receipt = {"format": "fineract-r2-verification-v1", "status": "VERIFIED", "snapshot": snapshot,
               "output_directory": str(folder.resolve() if output_directory is None else output_directory),
               "literal": literal, "result_sha256": sha256(answer).hexdigest(), "count": len(paths)}
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


class ConversationMemoryTests(unittest.TestCase):
    repository = "apache/fineract"
    commit = "2" * 40

    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / "memory" / "conversations.sqlite3"

    def run_cli(self, *args, code=0, cwd=None):
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", CLI, "--db", self.database, *args],
            cwd=cwd or self.root, capture_output=True, encoding="utf-8", timeout=10,
        )
        self.assertEqual(result.returncode, code, (result.stdout, result.stderr))
        self.assertFalse(result.stdout if code else result.stderr)
        return (result.stderr if code else result.stdout).splitlines()

    def bundle(self, name, literal, paths, *, output_directory=None):
        folder = self.root / name
        write_bundle(folder, self.repository, self.commit, paths, literal=literal,
                     output_directory=output_directory)
        return folder

    def assert_tests(self, conversation, literal, paths, total, *, question=QUESTION, cwd=None):
        self.assertEqual(self.run_cli("zapytaj", "--rozmowa", conversation, question, cwd=cwd), [
            f"Repozytorium: {self.repository}", f"Commit: {self.commit}", f"Literał: {literal}",
            f"Pliki pod src/test/ ({len(paths)} z {total})", *(f"  {path}" for path in paths),
        ])

    def test_conversations_survive_restart_and_stay_isolated(self):
        tests_a = ["modul/src/test/java/A.java", "src/test/Zażółć.java"]
        tests_b = ["modul/src/test/java/B.java", "another/src/test/java/B2.java"]
        tests_later = ["src/test/C.java", "modul/src/test/java/C2.java"]
        other = ["modul/src/testing/No.java", "modul/notsrc/test/No.java", "modul/src/test"]
        a = self.bundle("a", "LoanTransaction", [tests_a[0], *other, tests_a[1]])
        b = self.bundle("b", "BigDecimal", [*other, *tests_b])
        later = self.bundle("later", "Money", [*tests_later, *other])
        preference = "pokazuj pliki testowe osobno"
        project = ("--project", self.repository)
        self.run_cli("zapamiętaj", *project, preference)
        self.assertIn("nie ma aktywnego wyniku", self.run_cli("zapytaj", "--rozmowa", "A", QUESTION, code=1)[0])

        self.assertEqual(self.run_cli("otwórz-wynik", "--rozmowa", "A", a.name), [
            "Otwarto wynik apache/fineract — literał 'LoanTransaction' — pliki (5)",
        ])
        self.run_cli("otwórz-wynik", "--rozmowa", "B", b.name)
        self.assertEqual(self.run_cli("pokaż, co pamiętasz", *project), [f"{self.repository} — {preference}"])
        self.run_cli("zapomnij", *project)
        self.assert_tests("A", "LoanTransaction", tests_a, 5, cwd=b)
        self.assert_tests("B", "BigDecimal", tests_b, 5, question=f"a {QUESTION}")

        self.run_cli("otwórz-wynik", "--rozmowa", "A", later)
        self.assert_tests("A", "Money", tests_later, 5)
        self.assert_tests("B", "BigDecimal", tests_b, 5)

    def test_missing_conversation_unknown_question_and_zero_matches(self):
        unknown = self.run_cli("zapytaj", "--rozmowa", "N", QUESTION, code=1)[0]
        self.assertIn("Rozmowa 'N' nie ma aktywnego wyniku", unknown)
        self.assertIn("otwórz-wynik", unknown)
        self.assertFalse(self.database.exists())

        non_tests = self.bundle("non-tests", "OnlyMain", ["src/main/Main.java"])
        self.run_cli("otwórz-wynik", "--rozmowa", "A", non_tests)
        unknown = self.run_cli("zapytaj", "--rozmowa", "N", QUESTION, code=1)[0]
        self.assertIn("Rozmowa 'N' nie ma aktywnego wyniku", unknown)
        self.assertIn("otwórz-wynik", unknown)
        self.assertEqual(self.run_cli("zapytaj", "--rozmowa", "A", "co dalej?", code=1), [
            f"Błąd: Obsługiwane pytanie: {QUESTION}",
        ])
        self.assert_tests("A", "OnlyMain", [], 1)

        empty = self.bundle("empty", "Absent", [])
        self.run_cli("otwórz-wynik", "--rozmowa", "A", empty)
        self.assert_tests("A", "Absent", [], 0)

    def test_stale_artifacts_require_reopening(self):
        original = self.bundle("original", "Needle", ["src/test/Original.java"])
        replacement = self.bundle("replacement", "Other", ["src/test/Replacement.java"],
                                  output_directory=original.resolve())
        self.run_cli("otwórz-wynik", "--rozmowa", "A", original)

        renamed = self.root / "renamed"
        original.rename(renamed)
        missing = self.run_cli("zapytaj", "--rozmowa", "A", QUESTION, code=1)[0]
        self.assertIn("Brakuje zapamiętanego pliku R2", missing)
        self.assertIn("verification.json", missing)
        self.assertIn("otwórz-wynik", missing)
        renamed.rename(original)

        for filename in ("answer.jsonl", "verification.json"):
            with self.subTest(filename=filename):
                artifact = original / filename
                raw = artifact.read_bytes()
                artifact.write_bytes(raw + b"\n")
                changed = self.run_cli("zapytaj", "--rozmowa", "A", QUESTION, code=1)[0]
                self.assertIn(f"SHA-256 pliku {filename} różni się od zapamiętanego", changed)
                self.assertIn("otwórz-wynik", changed)
                artifact.write_bytes(raw)

        for filename in ("answer.jsonl", "verification.json"):
            (original / filename).write_bytes((replacement / filename).read_bytes())
        changed = self.run_cli("zapytaj", "--rozmowa", "A", QUESTION, code=1)[0]
        self.assertIn("SHA-256 pliku verification.json różni się od zapamiętanego", changed)
        self.assertIn("otwórz-wynik", changed)
        self.run_cli("otwórz-wynik", "--rozmowa", "A", original)
        self.assert_tests("A", "Other", ["src/test/Replacement.java"], 1)

    def test_open_requires_publication_by_rename(self):
        loan_paths = ["modul/src/test/Loan.java", "src/test/LoanDetails.java"]
        decimal_paths = ["src/test/Decimal.java", "modul/src/test/Rounding.java"]
        loan = self.bundle("loan", "LoanTransaction", [*loan_paths, "src/main/Loan.java"])
        self.run_cli("otwórz-wynik", "--rozmowa", "A", loan.name)

        target = self.root / "decimal"
        (self.root / "work").mkdir()
        staged = self.bundle("work/bundle", "BigDecimal", [*decimal_paths, "src/main/Decimal.java"],
                             output_directory=target.resolve())
        artifacts = ("answer.jsonl", "verification.json")
        staged_bytes = [(staged / name).read_bytes() for name in artifacts]
        self.assertFalse(target.exists())
        rejected = self.run_cli("otwórz-wynik", "--rozmowa", "A", staged, code=1)[0]
        self.assertIn("nie jest opublikowanym katalogiem R2", rejected)
        self.assertIn("output_directory", rejected)
        self.assert_tests("A", "LoanTransaction", loan_paths, 3)

        staged.rename(target)
        self.assertEqual([(target / name).read_bytes() for name in artifacts], staged_bytes)
        self.run_cli("otwórz-wynik", "--rozmowa", "A", target.name)
        self.assert_tests("A", "BigDecimal", decimal_paths, 3)

    def test_publication_directory_must_be_an_absolute_path(self):
        paths = ["src/test/A.java"]
        folder = self.bundle("result", "Needle", paths)
        receipt_file = folder / "verification.json"
        receipt = json.loads(receipt_file.read_bytes())
        del receipt["output_directory"]
        invalid_fields = [
            {}, {"output_directory": None}, {"output_directory": 42},
            {"output_directory": ""}, {"output_directory": folder.name},
        ]
        if sys.platform == "win32":
            invalid_fields.extend([{"output_directory": f"{folder.drive}{folder.name}"},
                                   {"output_directory": str(folder)[len(folder.drive):]}])
        for field in invalid_fields:
            with self.subTest(field=field):
                receipt_file.write_text(json.dumps(receipt | field), encoding="ascii")
                rejected = self.run_cli("otwórz-wynik", "--rozmowa", "A", folder, code=1)[0]
                self.assertIn("output_directory", rejected)
                self.assertIn("bezwzględną ścieżkę", rejected)
        self.assertFalse(self.database.exists())

        target = folder.resolve()
        if sys.platform == "win32":
            target = target.with_name(target.name.upper())
        receipt_file.write_text(json.dumps(receipt | {"output_directory": target.as_posix() + "/"}),
                                encoding="ascii")
        self.run_cli("otwórz-wynik", "--rozmowa", "A", folder.name)
        self.assert_tests("A", "Needle", paths, 1)

    def test_resume_rejects_working_directory_remembered_by_older_cli(self):
        target = self.bundle("target", "Needle", ["src/test/Old.java"])
        self.run_cli("otwórz-wynik", "--rozmowa", "A", target)
        staged = self.root / "work"
        target.rename(staged)
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("UPDATE active_results SET folder = ? WHERE conversation = 'A'", (str(staged.resolve()),))

        rejected = self.run_cli("zapytaj", "--rozmowa", "A", QUESTION, code=1)[0]
        self.assertIn("nie jest opublikowanym katalogiem R2", rejected)
        self.assertIn("output_directory", rejected)
        self.assertIn("otwórz-wynik", rejected)

    def test_open_validates_before_replacing_active_result(self):
        paths = ["src/test/Retained.java"]
        valid = self.bundle("valid", "Needle", paths)
        invalid = self.bundle("invalid", "Other", ["src/test/Other.java"])
        self.run_cli("otwórz-wynik", "--rozmowa", "A", valid)
        self.run_cli("otwórz-wynik", "--rozmowa", "A", self.root / "missing", code=1)
        self.assert_tests("A", "Needle", paths, 1)

        receipt_file = invalid / "verification.json"
        answer_file = invalid / "answer.jsonl"
        receipt = json.loads(receipt_file.read_bytes())
        for change, message in [({"status": "MISMATCH"}, "VERIFIED"),
                                ({"literal": "Different"}, "nagłówek"),
                                ({"count": 9}, "liczba")]:
            with self.subTest(change=change):
                receipt_file.write_text(json.dumps(receipt | change), encoding="ascii")
                error = self.run_cli("otwórz-wynik", "--rozmowa", "A", invalid, code=1)[0]
                self.assertIn(message, error)

        rows = answer_file.read_bytes().splitlines(keepends=True)
        partial_answer = b"".join(rows[:-1])
        answer_file.write_bytes(partial_answer)
        receipt_file.write_text(json.dumps(receipt | {"result_sha256": sha256(partial_answer).hexdigest()}),
                                encoding="ascii")
        error = self.run_cli("otwórz-wynik", "--rozmowa", "A", invalid, code=1)[0]
        self.assertIn("liczba", error)
        self.assert_tests("A", "Needle", paths, 1)
