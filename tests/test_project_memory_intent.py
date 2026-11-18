"""Offline tests for interpretation, budget and the public memory command."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from test_project_memory import CLI, write_bundle

sys.path.insert(0, str(CLI.parent))
import evaluate_project_memory_intent as benchmark
import project_memory
from repo_proof import memory_intent


def reply(text, *, stop="end_turn"):
    response = {"model": memory_intent.MODEL, "stop_reason": stop,
                "usage": {"input_tokens": 400, "output_tokens": 8},
                "content": [{"type": "text", "text": text}]}
    return SimpleNamespace(model=response["model"], stop_reason=stop,
                           content=[SimpleNamespace(**response["content"][0])],
                           model_dump=lambda **_: response)


class InterpretationTests(unittest.TestCase):
    def test_shared_transport_counts_before_one_paid_call(self):
        client = Mock()
        client.messages.count_tokens.return_value.input_tokens = 399
        client.messages.create.return_value = reply("show_test_paths")
        evidence = {}
        request = memory_intent.ClaudeRequest(client, evidence)
        self.assertEqual(request.complete("rules", "pytanie"), "show_test_paths")
        payload = dict(model=memory_intent.MODEL, system="rules", thinking={"type": "disabled"},
                       messages=[{"role": "user", "content": "pytanie"}])
        client.messages.count_tokens.assert_called_once_with(**payload)
        client.messages.create.assert_called_once_with(**payload, max_tokens=memory_intent.MAX_OUTPUT)
        with self.assertRaisesRegex(memory_intent.InterpretationError, "limit jednego"):
            request.complete("rules", "pytanie")
        self.assertTrue(evidence["paid_attempt"])
        self.assertEqual(evidence["response"]["usage"]["input_tokens"], 400)

    def test_large_prompt_stops_before_paid_call(self):
        client = Mock()
        client.messages.count_tokens.return_value.input_tokens = memory_intent.MAX_INPUT_RESERVATION
        evidence = {}
        with self.assertRaisesRegex(memory_intent.InterpretationError, "rezerwę"):
            memory_intent.ClaudeRequest(client, evidence).complete("rules", "pytanie")
        client.messages.create.assert_not_called()
        self.assertNotIn("paid_attempt", evidence)

    def test_budget_keeps_reserve_when_usage_is_unknown_and_caps_attempts(self):
        budget = benchmark.Budget(32)
        budget.reserve()
        self.assertIsNone(budget.settle({"paid_attempt": True}))
        self.assertEqual(budget.committed, benchmark.RESERVATION)
        budget.reserve()
        self.assertEqual(budget.settle({"response": reply("clarify").model_dump()}), 44_000)
        self.assertEqual(budget.committed, benchmark.RESERVATION + 44_000)
        for _ in range(30):
            budget.reserve()
        with self.assertRaisesRegex(ValueError, "Wyczerpano"):
            budget.reserve()
        with self.assertRaisesRegex(ValueError, "Plan"):
            benchmark.Budget(33)


class IntentCLITests(unittest.TestCase):
    question = "Daj same pliki testowe z ostatniego wyniku."

    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        self.db = root / "conversation.sqlite3"
        self.folder = root / "result"
        self.measurement = root / "measurement.json"
        write_bundle(self.folder, "apache/fineract", "2" * 40,
                     ["src/test/A.java", "src/main/A.java", "module/src/test/B.java"])
        code, _, err = self.cli("otwórz-wynik", "--rozmowa", "A", str(self.folder))
        self.assertEqual((code, err), (0, ""))

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = project_memory.main(["--db", str(self.db), *args])
        return code, out.getvalue(), err.getvalue()

    def ask(self, *, variant="claude", conversation="A", result=None, error=None):
        client = Mock()
        client.messages.count_tokens.return_value.input_tokens = 400
        client.messages.create.return_value = result
        client.messages.create.side_effect = error
        with patch.object(memory_intent, "anthropic_client") as factory:
            factory.return_value.__enter__.return_value = client
            status = self.cli("zapytaj", "--rozmowa", conversation, "--interpreter", variant,
                              "--measurement", str(self.measurement), self.question)
        return status, json.loads(self.measurement.read_bytes())

    def test_show_decision_releases_only_verified_local_paths(self):
        (code, out, err), evidence = self.ask(result=reply("show_test_paths"))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.splitlines()[-3:], ["Pliki pod src/test/ (2 z 3)",
                                                "  src/test/A.java", "  module/src/test/B.java"])
        self.assertEqual((evidence["decision"], evidence["application"]), ("show_test_paths", "showed_paths"))

    def test_clarify_and_unsupported_do_not_resume(self):
        for value, app, text in (("clarify", "asked_for_clarification", "Czy chodzi"),
                                 ("unsupported", "explained_scope", "Mogę pokazać")):
            with self.subTest(value=value), patch.object(project_memory, "resume_result") as resume:
                (code, out, err), evidence = self.ask(result=reply(value))
                self.assertEqual((code, err, evidence["application"]), (0, "", app))
                self.assertTrue(out.startswith(text))
                self.assertNotIn("src/test/A.java", out)
                resume.assert_not_called()
                self.measurement.unlink()

    def test_invalid_model_format_and_truncation_fail_closed(self):
        for response in (reply("show_test_paths\nunsupported"), reply("show_test_paths please"),
                         reply("show_test_paths", stop="max_tokens")):
            with self.subTest(response=response):
                (code, out, err), evidence = self.ask(result=response)
                self.assertEqual((code, out, evidence["application"]), (1, "", "invalid_response"))
                self.assertIn("Niepoprawna odpowiedź modelu", err)
                self.assertIn("response", evidence)
                self.measurement.unlink()

    def test_api_timeout_is_distinct_from_unsupported(self):
        (code, out, err), evidence = self.ask(error=TimeoutError("private exception text"))
        self.assertEqual((code, out, evidence["application"]), (1, "", "api_timeout"))
        self.assertIn("limit czasu Anthropic API", err)
        self.assertNotIn("private exception text", err)
        self.assertNotIn("decision", evidence)

    def test_unknown_conversation_does_not_release_paths(self):
        (code, out, err), evidence = self.ask(conversation="unknown", result=reply("show_test_paths"))
        self.assertEqual((code, out, evidence["application"]), (1, "", "active_result_error"))
        self.assertIn("nie ma aktywnego wyniku", err)

    def test_changed_artifacts_do_not_release_paths(self):
        answer = self.folder / "answer.jsonl"
        answer.write_bytes(answer.read_bytes() + b"\n")
        (code, out, err), evidence = self.ask(result=reply("show_test_paths"))
        self.assertEqual((code, out, evidence["application"]), (1, "", "active_result_error"))
        self.assertIn("SHA-256", err)

    def test_missing_key_does_not_import_sdk_or_release_paths(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            code, out, err = self.cli("zapytaj", "--rozmowa", "A", "--interpreter", "claude", self.question)
        self.assertEqual((code, out), (1, ""))
        self.assertIn("ANTHROPIC_API_KEY", err)
