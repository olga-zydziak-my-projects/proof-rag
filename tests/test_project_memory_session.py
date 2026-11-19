"""Run session commands and questions against a single public CLI process."""

from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Timer
import unittest

from test_project_memory import CLI, QUESTION, write_bundle


FAKE_ANTHROPIC = '''
import os
from pathlib import Path
from types import SimpleNamespace

def record(event):
    with Path(os.environ["SESSION_TEST_TRACE"]).open("a", encoding="utf-8") as trace:
        print(event, file=trace)

class Anthropic:
    def __init__(self, *, api_key, base_url, max_retries, timeout):
        assert api_key == "test-only" and max_retries == 0
        record("client opened")
        self.messages = self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        record("client closed")

    def count_tokens(self, **payload):
        record("count " + payload["messages"][0]["content"])
        return SimpleNamespace(input_tokens=400)

    def create(self, **payload):
        question = payload["messages"][0]["content"]
        record("generate " + question)
        if question == "test timeoutu":
            raise TimeoutError()
        return SimpleNamespace(model=payload["model"], stop_reason="end_turn",
                               content=[SimpleNamespace(type="text", text="show_test_paths")],
                               model_dump=lambda **_: {})
'''


class SessionTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.database = self.root / "memory.sqlite3"
        self.environment = dict(os.environ)
        self.environment.pop("ANTHROPIC_API_KEY", None)
        self.a_paths = ["src/test/Z.java", "modul/src/test/A.java"]
        self.b_paths = ["modul/src/test/Y.java", "src/test/B.java"]
        self.open_result("A", "LoanTransaction", self.a_paths)
        self.open_result("B", "BigDecimal", self.b_paths)

    def cli(self, *args):
        return [sys.executable, "-B", "-X", "utf8", CLI, "--db", self.database, *args]

    def open_result(self, conversation, literal, paths):
        folder = self.root / literal
        write_bundle(folder, "apache/fineract", "2" * 40, [paths[0], "src/main/Main.java", *paths[1:]],
                     literal=literal)
        result = subprocess.run(self.cli("otwórz-wynik", "--rozmowa", conversation, folder),
                                env=self.environment, capture_output=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        return folder

    def expected(self, literal, paths):
        return ["Repozytorium: apache/fineract", f"Commit: {'2' * 40}", f"Literał: {literal}",
                f"Pliki pod src/test/ ({len(paths)} z {len(paths) + 1})", *(f"  {path}" for path in paths)]

    @contextmanager
    def session(self, *args):
        with subprocess.Popen(self.cli("sesja", "--rozmowa", "A", *args), env=self.environment,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding="utf-8") as process:
            deadline = Timer(20, process.kill)
            deadline.daemon = True
            deadline.start()
            try:
                yield process
            finally:
                deadline.cancel()
                if process.poll() is None:
                    process.kill()

    def send(self, process, line):
        process.stdin.write(line + "\n")
        process.stdin.flush()

    def assert_answer(self, process, literal, paths):
        expected = self.expected(literal, paths)
        actual = [process.stdout.readline().removesuffix("\n") for _ in expected]
        self.assertEqual(actual, expected)

    def test_switch_a_b_a_in_one_process_and_exit(self):
        with self.session() as process:
            self.send(process, f"a {QUESTION}")
            self.assert_answer(process, "LoanTransaction", self.a_paths)
            self.send(process, "/rozmowa B")
            self.send(process, f"a {QUESTION}")
            self.assert_answer(process, "BigDecimal", self.b_paths)
            self.send(process, "/rozmowa A")
            self.send(process, f"a {QUESTION}")
            self.assert_answer(process, "LoanTransaction", self.a_paths)
            self.send(process, "/koniec")
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(process.stdout.read(), "")

    def test_reloads_external_update_and_can_switch_after_tampering(self):
        with self.session() as process:
            self.send(process, QUESTION)
            self.assert_answer(process, "LoanTransaction", self.a_paths)

            paths = ["extra/src/test/New.java"]
            replacement = self.open_result("A", "Updated", paths)
            self.send(process, QUESTION)
            self.assert_answer(process, "Updated", paths)

            receipt = replacement / "verification.json"
            receipt.write_bytes(receipt.read_bytes() + b"\n")
            self.send(process, QUESTION)
            error = process.stdout.readline()
            self.assertTrue(error.startswith("Błąd:"), error)
            self.assertIn("SHA-256 pliku verification.json", error)
            self.send(process, "/rozmowa B")
            self.send(process, QUESTION)
            self.assert_answer(process, "BigDecimal", self.b_paths)
            process.stdin.close()
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(process.stdout.read(), "")

    def test_claude_is_lazy_reuses_one_client_and_recovers_after_timeout(self):
        (self.root / "anthropic.py").write_text(FAKE_ANTHROPIC, encoding="utf-8")
        trace = self.root / "trace.txt"
        self.environment.update(PYTHONPATH=str(self.root), SESSION_TEST_TRACE=str(trace),
                                ANTHROPIC_API_KEY="test-only")
        with self.session("--interpreter", "claude") as process:
            self.send(process, f"a {QUESTION}")
            self.assert_answer(process, "LoanTransaction", self.a_paths)
            self.send(process, QUESTION)
            self.assert_answer(process, "LoanTransaction", self.a_paths)
            self.assertFalse(trace.exists())

            self.send(process, "test timeoutu")
            self.assertIn("limit czasu Anthropic API", process.stdout.readline())
            self.send(process, "/rozmowa B")
            self.send(process, "proszę tylko o testowe")
            self.assert_answer(process, "BigDecimal", self.b_paths)
            self.send(process, "/koniec")
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(process.stdout.read(), "")

        self.assertEqual(trace.read_text(encoding="utf-8").splitlines(), [
            "client opened", "count test timeoutu", "generate test timeoutu",
            "count proszę tylko o testowe", "generate proszę tylko o testowe", "client closed",
        ])
