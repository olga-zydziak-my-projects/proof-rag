from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_r2_checked import CheckedR2Fixture, PROJECT, SCRIPTS


QUESTION = "Klient złożył wniosek 12 maja. Czy według reguły daty można go zatwierdzić również 12 maja?"
LIMIT_QUESTION = "Jaki jest limit rozmiaru pliku?"
RULE = "approvedOnDate != null && "
BEFORE = "DateUtils.isBefore(approvedOnDate, loan.getSubmittedOnDate())"
AFTER = "!DateUtils.isAfter(approvedOnDate, loan.getSubmittedOnDate())"
CALL = "loanApplicationValidator.validateApproval(command, loanId);"
OTHER_RULE = "loan.isClosed()"
RULE_PATH = "src/LoanApplicationValidator.java"
SERVICE_PATH = "src/ApprovalService.java"


class Block:
    def __init__(self, number, name, **arguments):
        self.data = {"type": "tool_use", "id": f"toolu_{number}", "name": name, "input": arguments}

    def model_dump(self, **kwargs):
        return self.data


class ScriptedModel:
    """Chooses later reads and the verdict from the preceding real tool results."""

    def __init__(self, mode):
        self.mode = mode
        self.turn = 0
        self.messages = self

    def create(self, *, model, messages, tools, tool_choice, **kwargs):
        assert tool_choice == {"type": "auto"}
        assert all(tool["strict"] is True for tool in tools)
        question = LIMIT_QUESTION if self.mode.startswith("file-limit") else QUESTION
        assert messages[0]["content"].split("\n\n", 1)[0] == question
        self.turn += 1
        stop_reason = "tool_use"
        if (self.mode == "never-submit" or (self.mode == "file-limit-nudge" and self.turn == 1)
                or (self.mode == "nudge-synthesis" and self.turn == 6)):
            block = SimpleNamespace(model_dump=lambda **_: {"type": "text", "text": "Unverified text."})
            stop_reason = "end_turn"
        elif self.mode.startswith("file-limit"):
            if self.turn == 1 or (self.mode == "file-limit-nudge" and self.turn == 2):
                if self.mode == "file-limit-nudge":
                    assert messages[-2]["content"] == [{"type": "text", "text": "Unverified text."}]
                    assert "submit" in messages[-1]["content"][0]["text"]
                block = Block(self.turn, "search", literal="upload.max-file-size")
            else:
                [tool] = messages[-1]["content"]
                [hit] = json.loads(tool["content"])["shown"]
                citation = {"repository": hit["repository"], "path": hit["path"], "start": hit["line"],
                            "end": hit["line"], "quote": "upload.max-file-size=5MB"}
                block = Block(self.turn, "submit", answer_pl="5 MB.", verdict="yes", citations=[citation])
        elif self.turn == 1:
            block = Block(self.turn, "search", literal=RULE, path_terms="LoanApplicationValidator")
        elif self.turn >= 6:
            context = json.loads(messages[0]["content"].split("\n\n", 1)[1])
            assert " validateApproval(" in context["method_declaration"]
            assert context["rule"]["commit"] == context["callers"][0]["commit"]
            if self.mode == "nudge-synthesis":
                assert "submit" in context["correction"]
            citations = [self.rule, self.caller]
            if self.mode == "caller-only" or (self.mode == "recover-rule" and self.turn == 6):
                citations = [self.caller]
            elif self.mode == "condition-only":
                citations = [{**self.rule, "end": self.rule["start"]}, self.caller]
            elif self.mode in ("other-rule", "other-rule-wide"):
                decoy = self.other_rule
                if self.mode == "other-rule-wide":
                    decoy = {**decoy, "start": self.rule["start"]}
                citations = [decoy, self.caller]
            elif self.mode == "rule-only":
                citations = [self.rule]
            elif self.mode == "tamper-final":
                citations = [{**self.rule, "quote": "fakeDateConditionNeverInGit()"}, self.caller]
            if self.mode == "draft-condition-only":
                assert context["rule"]["suggested_citation"] == {
                    "start": self.rule["start"], "end": self.rule["end"],
                }
            block = self.submit(citations)
        else:
            [tool] = messages[-1]["content"]
            assert not tool["is_error"], tool
            result = json.loads(tool["content"])
            if self.turn == 2:
                if self.mode == "pause":
                    print("first-search-completed", file=sys.stderr, flush=True)
                    if sys.stdin.readline() != "continue\n":
                        raise ValueError("Test did not release the model")
                [hit] = [item for item in result["shown"] if item["path"].endswith("/LoanApplicationValidator.java")]
                block = Block(self.turn, "read", repository=hit["repository"], path=hit["path"], needle=RULE)
            elif self.turn == 3:
                effect = {"draft-condition-only": "message);", "draft-no-effect": "}"}.get(self.mode, "throw ")
                self.rule = self.citation(result, RULE, effect)
                if self.mode in ("other-rule", "other-rule-wide"):
                    self.other_rule = self.citation(result, OTHER_RULE, "throw ")
                self.verdict = "no" if AFTER in self.rule["quote"] else "yes"
                assert AFTER in self.rule["quote"] or BEFORE in self.rule["quote"]
                block = Block(self.turn, "search", literal=CALL)
            elif self.turn == 4:
                [hit] = result["shown"]
                block = Block(self.turn, "read", repository=hit["repository"], path=hit["path"], needle=CALL)
            else:
                self.caller = self.citation(result, CALL, "loanScheduleAssembler.assembleLoanApproval(")
                if self.mode == "tamper":
                    self.rule["quote"] = "fakeDateConditionNeverInGit()"
                draft = self.rule
                if self.mode in ("draft-condition-only", "draft-no-effect"):
                    draft = {**draft, "end": draft["start"]}
                block = self.submit([draft, self.caller])
        return SimpleNamespace(model=model, id=f"controlled-{self.turn}", stop_reason=stop_reason, content=[block],
                               usage=SimpleNamespace(model_dump=lambda **kwargs: {}))

    def submit(self, citations):
        text = ("Reguła dopuszcza tę datę." if self.verdict == "yes" else "Reguła wyklucza tę datę.")
        return Block(self.turn, "submit", answer_pl=text,
                     verdict=self.verdict, citations=citations)

    @staticmethod
    def citation(result, marker, consequence):
        lines = [(int(number), line) for row in result["lines"] for number, _, line in [row.partition(": ")]]
        start, quote = next((n, line) for n, line in lines if marker in line)
        end = next(n for n, line in lines if n > start and consequence in line)
        return {"repository": result["repository"], "path": result["path"], "start": start, "end": end,
                "quote": quote.strip()}


class ConclusionModel(ScriptedModel):
    incorrect_extra = "Reguła przepuszcza także zamkniętą pożyczkę."
    objection = "Warunek loan.isClosed() prowadzi do wyjątku."
    primary = "Reguła dopuszcza tę datę."
    policy_path = "src/ClosedLoanPolicy.java"
    policy_line = "boolean approveClosedLoan() { return false; }"

    def create(self, *, model, messages, tools, **kwargs):
        if self.mode == "review-drop-evidence":
            self.objection = "Odrębna reguła approveClosedLoan zwraca false."
        if self.turn < 6:
            if self.turn == 1:
                hits = json.loads(messages[-1]["content"][0]["content"])["shown"]
                self.commit = hits[0]["commit"]
            response = super().create(model=model, messages=messages, tools=tools, **kwargs)
            if self.turn == 6 and self.mode != "review-pass":
                proposal = response.content[0].data["input"]
                proposal["answer_pl"] += " " + self.incorrect_extra
                if self.mode == "review-drop-evidence":
                    proposal["citations"].append({"repository": self.rule["repository"], "path": self.policy_path,
                                                  "start": 3, "end": 3, "quote": self.policy_line})
            return response

        self.turn += 1
        [tool] = tools
        assert kwargs["tool_choice"] == {"type": "auto"} and tool["strict"]
        request = json.loads(messages[0]["content"])
        assert request["question"] == QUESTION
        rule, caller, *others = request["sources"]
        assert (rule["source"], rule["path"], rule["commit"]) == (1, RULE_PATH, self.commit)
        assert (caller["source"], caller["path"], caller["commit"]) == (2, SERVICE_PATH, self.commit)
        assert rule["manifest_sha256"] == caller["manifest_sha256"]
        assert OTHER_RULE in "\n".join(rule["lines"]) and CALL in "\n".join(caller["lines"])
        if self.mode == "review-drop-evidence":
            [policy] = others
            assert (policy["source"], policy["path"], policy["commit"]) == (3, self.policy_path, self.commit)
            assert self.policy_line in "\n".join(policy["lines"])
            if self.turn == 7:
                self.original_windows = request["sources"]
            else:
                assert request["sources"] == self.original_windows
            if self.turn == 9:
                assert self.policy_path not in [c["path"] for c in request["proposal"]["citations"]]
        answer = request["proposal"]["answer_pl"]
        if tool["name"] == "review_conclusion":
            assert self.primary in answer
            asked_units = [self.primary]
            if self.incorrect_extra in answer:
                asked_units.append(self.incorrect_extra)
            assert request["units"] == [{"unit": n, "text": claim} for n, claim in enumerate(asked_units, 1)]
            if self.mode == "review-racing-push" and self.turn == 7:
                print("first-search-completed", file=sys.stderr, flush=True)
                if sys.stdin.readline() != "continue\n":
                    raise ValueError("Test did not release the conclusion review")
            ref = {"source": 1, "start": self.rule["start"], "end": self.rule["end"]}
            findings = [{"unit": 1, "claim": self.primary, "assessment": "supported", "reason": "Warunek używa isBefore.",
                         "evidence": [ref]}]
            if self.incorrect_extra in answer:
                # The second if and its throw appear immediately after the first guarded block.
                other = {**ref, "start": self.rule["end"] + 2, "end": self.rule["end"] + 3}
                if self.mode == "review-drop-evidence":
                    other = {"source": 3, "start": 3, "end": 3}
                findings.append({"unit": 2, "claim": self.incorrect_extra, "assessment": "contradicted",
                                 "reason": self.objection, "evidence": [other]})
            if self.mode == "review-pass":
                findings[0]["reason"] = ""
            elif self.mode == "review-empty-objection":
                findings[-1]["reason"] = ""
            elif self.mode == "review-no-findings":
                findings = []
            elif self.mode == "review-overlooked-extra":
                findings = findings[:1]
            elif self.mode == "review-unknown-source":
                findings[0]["evidence"] = [{**ref, "source": 99}]
            elif self.mode == "review-outside-source":
                findings[0]["evidence"] = [{**ref, "start": 1000, "end": 1001}]
            block = Block(self.turn, "review_conclusion", findings=findings)
        else:
            assert tool["name"] == "submit" and self.turn == 8
            assert self.incorrect_extra in answer
            assert any(f["claim"] == self.incorrect_extra and f["reason"] == self.objection
                       for f in request["findings"])
            assert request["required_citations"]
            answer = self.primary
            citations = [self.rule, self.caller]
            if self.mode == "review-repeat":
                answer += " " + self.incorrect_extra
            elif self.mode == "review-empty-citations":
                citations = []
            elif self.mode == "review-lost-caller":
                citations = [self.rule]
            elif self.mode == "review-false-quote":
                citations = [{**self.rule, "quote": "notInGit()"}, self.caller]
            block = Block(self.turn, "submit", answer_pl=answer, verdict=self.verdict, citations=citations)
        return SimpleNamespace(model=model, id=f"controlled-{self.turn}", stop_reason="tool_use", content=[block],
                               usage=SimpleNamespace(model_dump=lambda **kwargs: {}))


class ToolHistoryModel(ScriptedModel):
    no_run = "Nie uruchamiałem kodu, wniosek wynika z samej lektury."
    did_run = "Uruchomiłem kod."
    second_rule = "Zamknięta pożyczka jest odrzucana."
    mixed = "Nie uruchamiałem kodu, lecz reguła przepuszcza zamkniętą pożyczkę."

    def create(self, *, model, messages, tools, **kwargs):
        primary = ConclusionModel.primary
        drafts = {
            "review-history-pass": f"{primary} {self.no_run} {self.second_rule}",
            "review-history-false": f"{primary} {self.did_run}",
            "review-history-mixed": f"{primary} {self.mixed}",
            "review-history-only": self.no_run,
        }
        if self.turn < 6:
            if self.mode == "review-history-pass" and self.turn == 2:
                actual_read, empty_read = messages[-1]["content"]
                assert not empty_read["is_error"] and json.loads(empty_read["content"])["lines"] == []
                messages = [*messages[:-1], {**messages[-1], "content": [actual_read]}]
            response = super().create(model=model, messages=messages, tools=tools, **kwargs)
            if self.mode == "review-history-pass" and self.turn == 2:
                arguments = response.content[0].data["input"]
                response.content.append(Block("missing-needle", "read", **{**arguments, "needle": "absent_needle_91"}))
            if self.turn == 6:
                response.content[0].data["input"]["answer_pl"] = drafts[self.mode]
            return response

        self.turn += 1
        request = json.loads(messages[0]["content"])
        [tool] = tools
        if tool["name"] == "submit":
            # Deliberately leave the false or unsupported claim in place.
            block = Block(self.turn, "submit", **request["proposal"])
        else:
            assert tool["name"] == "review_conclusion" and request["question"] == QUESTION
            git_units = [(r["unit"], r["text"]) for r in request["units"]]
            assert self.mode != "review-history-only", "A method note cannot answer this code question on its own."
            ref = {"source": 1, "start": self.rule["start"], "end": self.rule["end"]}
            findings = [{"unit": 1, "claim": primary, "assessment": "supported",
                         "reason": "Warunek używa isBefore.", "evidence": [ref]}]
            if self.mode == "review-history-mixed":
                assert git_units == [(1, primary), (2, self.mixed)]
                assert not request["tool_history_findings"]
                # Even a reviewer which blesses the whole mixed sentence must supply Git evidence.
                findings.append({"unit": 2, "claim": self.mixed, "assessment": "supported",
                                 "reason": "", "evidence": []})
            else:
                positive = self.mode == "review-history-pass"
                [host] = request["tool_history_findings"]
                assert host["unit"] == 2
                assert host["fact"] == "project_code_executed"
                assert host["assessment"] == ("supported" if positive else "contradicted")
                if positive:
                    assert git_units == [(1, primary), (3, self.second_rule)]
                    other = {**ref, "start": self.rule["end"] + 2, "end": self.rule["end"] + 3}
                    findings.append({"unit": 3, "claim": self.second_rule, "assessment": "supported",
                                     "reason": "loan.isClosed() prowadzi do wyjątku.", "evidence": [other]})
                else:
                    assert git_units == [(1, primary)]
            block = Block(self.turn, "review_conclusion", findings=findings)
        return SimpleNamespace(model=model, id=f"controlled-{self.turn}", stop_reason="tool_use", content=[block],
                               usage=SimpleNamespace(model_dump=lambda **_: {}))


def scripted_command(config, mode="plain", *, repo=None):
    view = ("--repo", repo) if repo else ()
    question = LIMIT_QUESTION if mode.startswith("file-limit") else QUESTION
    review = ("--review-conclusion",) if mode.startswith("review-") else ()
    return [sys.executable, "-B", "-X", "utf8", str(Path(__file__)), "--scripted", mode,
            "ask", "--config", str(config), *view, "--pr", "1", *review, question]


def recorded(proc, started, stdout, stderr):
    return {"exit_code": proc.returncode, "wall_seconds": perf_counter() - started,
            "stdout_json": json.loads(stdout), "stderr": stderr.decode("utf-8", "replace")}


def run_scripted(config, env, mode="plain", *, repo=None):
    started = perf_counter()
    proc = subprocess.run(scripted_command(config, mode, repo=repo), env=env, cwd=PROJECT,
                          capture_output=True, timeout=180)
    return recorded(proc, started, proc.stdout, proc.stderr)


def overlap_push(config, env, advance, *, mode="pause"):
    def wait_for_search(stderr):
        return any(line.rstrip() == b"first-search-completed" for line in stderr)

    started = perf_counter()
    with (
        subprocess.Popen(scripted_command(config, mode), env=env, cwd=PROJECT, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc,
        ThreadPoolExecutor(max_workers=1) as pool,
    ):
        try:
            if not pool.submit(wait_for_search, proc.stderr).result(timeout=120):
                raise AssertionError(f"CLI exited before the first search gate: {proc.stdout.read()!r}")
            advance()
            stdout, stderr = proc.communicate(b"continue\n", timeout=180)
        finally:
            if proc.poll() is None:
                proc.kill()
    return recorded(proc, started, stdout, stderr)


def check_version(row, commit, verdict):
    result = row["stdout_json"]
    assert (row["exit_code"], result["status"], result["verdict"]) == (0, "VERIFIED", verdict), row
    [repo] = result["view"]["repositories"]
    assert repo["commit"] == commit, result["view"]
    manifest = Path(result["run_directory"]) / "manifest.json"
    digest = sha256(manifest.read_bytes()).hexdigest()
    assert digest == result["manifest_sha256"]
    assert len(result["searches"]) == 3 and len(result["reads"]) >= 4 and len(result["citations"]) == 2
    assert result["model_calls"] == 6
    for search in result["searches"]:
        assert search["manifest_sha256"] == digest and search["status"] == "VERIFIED"
        rows = (Path(search["output_directory"]) / "answer.jsonl").read_bytes().splitlines()
        assert all(record["commit"] == commit for line in rows
                   if (record := json.loads(line))["type"] in ("result", "hit"))
    for item in result["reads"] + result["citations"]:
        assert (item["commit"], item["manifest_sha256"]) == (commit, digest)
    return result


@unittest.skipUnless(sys.platform == "win32", "requires the Windows R2 supervisor")
class FineractAskTests(CheckedR2Fixture):
    def setUp(self):
        super().setUp()
        checked = self.root / "checked"
        self.configure(checked, self.prepare(self.index, checked), self.index)
        config = json.loads(self.config.read_bytes())
        config["corpora"]["default"]["pr_directory"] = "pr"
        self.config.write_text(json.dumps(config), encoding="ascii")
        self.git(self.author, "checkout", "--quiet", "-b", "feature")
        (self.author / SERVICE_PATH).write_bytes(
            (CALL + "\nloanScheduleAssembler.assembleLoanApproval(command);\n").encode("ascii"))
        self.a = self.push_rule(BEFORE)
        opened = {"action": "opened", "number": 1, "repository": "demo", "base": "main", "head": "feature"}
        result = self.cli("fineract_r2_pr.py", "event", data=json.dumps(opened).encode("ascii"))
        self.assertEqual(result["refresh"]["status"], "READY")

    def push_rule(self, comparison, heading="", *, effect="            throw new IllegalArgumentException();\n"):
        rule = ("class LoanApplicationValidator {\n    public void validateApproval() {\n" + heading
                + f"        if ({RULE}{comparison}) {{\n{effect}"
                f"        }}\n        if ({OTHER_RULE}) {{\n            throw new IllegalStateException();\n"
                "        }\n    }\n}\n")
        (self.author / RULE_PATH).write_bytes(
            rule.encode("ascii"))
        self.git(self.author, "add", ".")
        self.git(self.author, "commit", "--quiet", "-m", "Set date rule")
        commit = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", self.server.as_uri(), "feature:feature")
        return commit

    def test_push_during_question_keeps_searches_reads_and_citations_on_a(self):
        commits = {}

        def advance():
            commits["b"] = self.push_rule(AFTER, "// Shift the rule down.\n\n")

        previous = check_version(overlap_push(self.config, self.env, advance), self.a, "yes")
        fresh = check_version(run_scripted(self.config, self.env), commits["b"], "no")
        for answer in (previous, fresh):
            self.assertEqual(answer["model"], "claude-sonnet-5-5")
            self.assertEqual({call["model"] for call in answer["api_calls"]}, {answer["model"]})
        self.assertEqual(previous["answer_pl"], "Reguła dopuszcza tę datę.")
        self.assertEqual(fresh["answer_pl"], "Reguła wyklucza tę datę.")
        self.assertNotEqual(previous["manifest_sha256"], fresh["manifest_sha256"])
        self.assertEqual(previous["citations"][0]["start"] + 2, fresh["citations"][0]["start"])
        self.assertEqual({search["operation"] for search in previous["searches"]}, {"query-checked"})
        self.assertEqual({search["operation"] for search in fresh["searches"]}, {"query-verified"})

    def test_direct_answer_preserves_value_without_a_verdict_prefix(self):
        path = "src/upload.properties"
        (self.author / path).write_bytes(b"upload.max-file-size=5MB\n")
        commit = self.push_rule(BEFORE)
        for mode, calls in (("file-limit", 2), ("file-limit-nudge", 3)):
            with self.subTest(mode=mode):
                result = run_scripted(self.config, self.env, mode)
                response = result["stdout_json"]
                self.assertEqual((result["exit_code"], response["status"]), (0, "VERIFIED"))
                self.assertEqual((response["answer_pl"], response["verdict"], response["model_calls"]),
                                 ("5 MB.", "yes", calls))
                [citation] = response["citations"]
                self.assertEqual((citation["path"], citation["commit"], citation["excerpt"]),
                                 (path, commit, "upload.max-file-size=5MB"))

    def test_text_only_replies_do_not_publish_an_unverified_answer(self):
        result = run_scripted(self.config, self.env, "never-submit")
        response = result["stdout_json"]
        self.assertEqual((result["exit_code"], response["status"], response["model_calls"]), (3, "BLOCKED", 10))
        self.assertNotIn("answer_pl", response)
        self.assertNotIn("verdict", response)

        result = run_scripted(self.config, self.env, "nudge-synthesis")
        response = result["stdout_json"]
        self.assertEqual((result["exit_code"], response["status"], response["model_calls"]), (0, "VERIFIED", 7))
        self.assertEqual(response["answer_pl"], "Reguła dopuszcza tę datę.")
        self.assertEqual({c["path"] for c in response["citations"]}, {RULE_PATH, SERVICE_PATH})

    def test_unreachable_source_blocks_even_with_a_prepared_index(self):
        offline = self.server.with_name("offline.git")
        self.server.rename(offline)
        try:
            result = run_scripted(self.config, self.env)
        finally:
            offline.rename(self.server)
        self.assertEqual(result["exit_code"], 3, result)
        response = result["stdout_json"]
        self.assertEqual((response["status"], response["model_calls"]), ("BLOCKED", 0))
        self.assertNotIn("answer_pl", response)

    def test_rejects_a_tampered_citation_and_does_not_publish_the_answer(self):
        for mode in ("tamper", "tamper-final"):
            with self.subTest(mode=mode):
                result = run_scripted(self.config, self.env, mode)
                response = result["stdout_json"]
                self.assertEqual((result["exit_code"], response["status"], response["checks"]["citations"]),
                                 (2, "MISMATCH", "REJECTED"))
                self.assertIn("Cytat nie występuje w Git", response["reason"])
                self.assertNotIn("answer_pl", response)
                self.assertNotIn("verdict", response)

    def test_incomplete_final_rule_blocks_the_answer(self):
        for mode in ("caller-only", "condition-only", "other-rule", "other-rule-wide", "rule-only"):
            with self.subTest(mode=mode):
                result = run_scripted(self.config, self.env, mode)
                response = result["stdout_json"]
                self.assertEqual((result["exit_code"], response["status"]), (3, "BLOCKED"))
                self.assertEqual(response["model_calls"], 7)
                self.assertEqual(response["checks"], {"citations": "INCOMPLETE", "business_conclusion": "NOT_CHECKED"})
                expected = "dowodu wywołania" if mode == "rule-only" else "dowodu reguły"
                self.assertIn(expected, response["reason"])
                self.assertIn(expected, response["api_calls"][5]["retry_reason"])
                self.assertNotIn("answer_pl", response)
                self.assertNotIn("verdict", response)

    def test_retry_can_restore_the_complete_rule(self):
        result = run_scripted(self.config, self.env, "recover-rule")
        response = result["stdout_json"]
        self.assertEqual((result["exit_code"], response["status"], response["verdict"]), (0, "VERIFIED", "yes"))
        self.assertEqual(response["model_calls"], 7)
        self.assertIn("dowodu reguły", response["api_calls"][5]["retry_reason"])
        self.assertEqual({c["path"] for c in response["citations"]}, {RULE_PATH, SERVICE_PATH})
        rule = next(c for c in response["citations"] if c["path"] == RULE_PATH)
        self.assertIn(BEFORE, rule["excerpt"])
        self.assertIn("throw new IllegalArgumentException()", rule["excerpt"])

    def test_conclusion_review_accepts_supported_answer_without_repair(self):
        row = run_scripted(self.config, self.env, "review-pass")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (0, "VERIFIED"), response)
        self.assertEqual(response["answer_pl"], ConclusionModel.primary)
        self.assertEqual(response["checks"], {"citations": "VERIFIED", "business_conclusion": "MODEL_REVIEWED"})
        review = response["conclusion_review"]
        self.assertEqual((review["disposition"], review["repair_attempted"], len(review["reviews"])),
                         ("accepted", False, 1))
        self.assertEqual([call["provider_id"] for call in response["api_calls"]],
                         [f"controlled-{n}" for n in range(1, 8)])

    def test_no_execution_note_uses_dispatched_tools_between_two_git_claims(self):
        row = run_scripted(self.config, self.env, "review-history-pass")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (0, "VERIFIED"), response)
        self.assertEqual(response["answer_pl"], " ".join((ConclusionModel.primary, ToolHistoryModel.no_run,
                                                         ToolHistoryModel.second_rule)))
        self.assertTrue(response["tool_history"]["complete"])
        events = response["tool_history"]["events"]
        self.assertEqual([(e["tool"], e["outcome"]) for e in events],
                         [("search", "ok"), ("read", "ok"), ("read", "empty"), ("search", "ok"), ("read", "ok")])
        review = response["conclusion_review"]
        self.assertFalse(review["repair_attempted"])
        [assessment] = review["reviews"]
        by_unit = {r["unit"]: r for r in assessment["findings"]}
        self.assertTrue(by_unit[1]["evidence"] and by_unit[3]["evidence"])
        note = by_unit[2]
        self.assertEqual((note["basis"], note["assessment"], note["evidence"]),
                         ("tool_history", "supported", []))
        self.assertIs(note["claimed_value"], False)
        self.assertIs(note["observed_value"], False)

    def test_false_execution_claim_still_blocks_after_one_repair(self):
        row = run_scripted(self.config, self.env, "review-history-false")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (3, "BLOCKED"), response)
        review = response["conclusion_review"]
        self.assertTrue(review["repair_attempted"])
        self.assertEqual(len(review["reviews"]), 2)
        for assessment in review["reviews"]:
            [note] = [r for r in assessment["findings"] if r.get("basis") == "tool_history"]
            self.assertEqual(note["assessment"], "contradicted")
            self.assertIs(note["claimed_value"], True)
            self.assertIs(note["observed_value"], False)
        self.assertNotIn("answer_pl", response)
        self.assertNotIn("verdict", response)

    def test_method_note_cannot_replace_evidence_of_business_behavior(self):
        for mode in ("review-history-mixed", "review-history-only"):
            with self.subTest(mode=mode):
                row = run_scripted(self.config, self.env, mode)
                response = row["stdout_json"]
                self.assertEqual((row["exit_code"], response["status"]), (3, "BLOCKED"), response)
                self.assertNotIn("answer_pl", response)
                self.assertNotIn("verdict", response)

    def test_conclusion_repair_removes_false_extra_and_stays_on_original_commit(self):
        def advance():
            self.push_rule(AFTER, "// A newer commit now rejects the same date.\n")

        row = overlap_push(self.config, self.env, advance, mode="review-racing-push")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (0, "VERIFIED"), response)
        self.assertEqual(response["answer_pl"], ConclusionModel.primary)
        self.assertEqual(response["verdict"], "yes")
        self.assertEqual(response["model_calls"], 9)
        review = response["conclusion_review"]
        self.assertEqual((review["disposition"], review["repair_attempted"], len(review["reviews"])),
                         ("accepted_after_repair", True, 2))
        self.assertEqual(response["checks"]["business_conclusion"], "MODEL_REVIEWED")
        for cite in response["citations"]:
            self.assertEqual((cite["commit"], cite["manifest_sha256"]), (self.a, response["manifest_sha256"]))

    def test_conclusion_review_blocks_repeated_unsupported_claim_after_one_repair(self):
        row = run_scripted(self.config, self.env, "review-repeat")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (3, "BLOCKED"), response)
        self.assertEqual(response["model_calls"], 9)
        review = response["conclusion_review"]
        self.assertEqual((review["disposition"], review["repair_attempted"], len(review["reviews"])),
                         ("blocked", True, 2))
        self.assertNotIn("answer_pl", response)
        self.assertNotIn("verdict", response)
        self.assertNotIn(ConclusionModel.incorrect_extra, json.dumps(response, ensure_ascii=False))

    def test_conclusion_recheck_retains_contrary_source_after_dropping_its_citation(self):
        policy = self.author / ConclusionModel.policy_path
        content = f"class ClosedLoanPolicy {{\n// {RULE}...\n{ConclusionModel.policy_line}\n}}\n"
        policy.write_bytes(content.encode("ascii"))
        commit = self.push_rule(BEFORE)
        row = run_scripted(self.config, self.env, "review-drop-evidence")
        response = row["stdout_json"]
        self.assertEqual((row["exit_code"], response["status"]), (0, "VERIFIED"), response)
        self.assertEqual((response["model_calls"], response["answer_pl"]), (9, ConclusionModel.primary))
        self.assertEqual(response["conclusion_review"]["disposition"], "accepted_after_repair")
        self.assertEqual({(c["path"], c["commit"]) for c in response["citations"]},
                         {(RULE_PATH, commit), (SERVICE_PATH, commit)})

    def test_conclusion_repair_preserves_original_git_and_java_evidence_gates(self):
        for mode, status, code in (("review-empty-citations", "BLOCKED", 3),
                                   ("review-lost-caller", "BLOCKED", 3),
                                   ("review-false-quote", "MISMATCH", 2)):
            with self.subTest(mode=mode):
                row = run_scripted(self.config, self.env, mode)
                response = row["stdout_json"]
                self.assertEqual((row["exit_code"], response["status"]), (code, status), response)
                self.assertEqual(response["model_calls"], 8)
                self.assertTrue(response["conclusion_review"]["repair_attempted"])
                self.assertEqual(len(response["conclusion_review"]["reviews"]), 1)
                if status == "MISMATCH":
                    self.assertEqual(response["checks"]["citations"], "REJECTED")
                self.assertNotIn("answer_pl", response)
                self.assertNotIn("verdict", response)

    def test_invalid_conclusion_review_cannot_approve_an_answer(self):
        for mode in ("review-no-findings", "review-overlooked-extra", "review-unknown-source",
                     "review-outside-source", "review-empty-objection"):
            with self.subTest(mode=mode):
                row = run_scripted(self.config, self.env, mode)
                response = row["stdout_json"]
                self.assertEqual((row["exit_code"], response["status"]), (3, "BLOCKED"), response)
                self.assertEqual(response["model_calls"], 7)
                self.assertFalse(response["conclusion_review"]["repair_attempted"])
                self.assertNotIn("answer_pl", response)
                self.assertNotIn("verdict", response)

    def test_discovers_the_missing_effect_in_pinned_git(self):
        self.push_rule(BEFORE, effect=(
            '            String message = "an example containing } ) and ;";\n'
            "            throw new IllegalArgumentException(\n"
            "                    message);\n"
        ))
        result = run_scripted(self.config, self.env, "draft-condition-only")
        response = result["stdout_json"]
        self.assertEqual((result["exit_code"], response["status"]), (0, "VERIFIED"), response.get("reason"))
        rule = next(cite for cite in response["citations"] if cite["path"] == RULE_PATH)
        self.assertTrue(rule["excerpt"].endswith("message);"))

    def test_draft_condition_with_an_empty_branch_blocks_before_synthesis(self):
        self.push_rule(BEFORE, effect="            /* No effect; braces } in a comment */\n")
        result = run_scripted(self.config, self.env, "draft-no-effect")
        response = result["stdout_json"]
        self.assertEqual((result["exit_code"], response["status"], response["model_calls"]), (3, "BLOCKED", 5))
        self.assertIn("warunku i skutku wybranej reguły", response["reason"])
        self.assertNotIn("answer_pl", response)
        self.assertNotIn("verdict", response)

    def test_ambiguous_pr_is_rejected_before_any_model_call(self):
        spec = json.loads(self.config.read_bytes())
        entry = spec["corpora"]["default"]
        mirror = self.sources / "mirror.git"
        self.git(self.root, "init", "--quiet", "--bare", "--object-format=sha1", mirror)
        self.git(self.author, "push", mirror.as_uri(), "main:main", "feature:feature")
        entry["repositories"].append(self.repository("mirror", mirror))
        del entry["checked_index"]
        self.config.write_text(json.dumps(spec), encoding="ascii")
        opened = {"action": "opened", "number": 1, "repository": "mirror", "base": "main", "head": "feature"}
        self.cli("fineract_r2_pr.py", "event", data=json.dumps(opened).encode("ascii"))
        result = run_scripted(self.config, self.env)
        self.assertEqual(result["exit_code"], 4, result)
        response = result["stdout_json"]
        self.assertEqual(response["model_calls"], 0)
        self.assertIn("demo, mirror", response["reason"])
        self.assertIn("--repo demo --pr 1", response["reason"])
        self.assertNotIn("run_directory", response)


class ToolHistoryTests(unittest.TestCase):
    def test_missing_partial_or_unknown_history_cannot_confirm_non_execution(self):
        with patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
            from fineract_r2_ask import execution_observation, history_finding

        read = {"tool": "read", "outcome": "ok", "id": "read-1"}
        for history in (None, {}, {"complete": False, "events": [read]},
                        {"complete": True, "events": []},
                        {"complete": True, "events": [read, read]},
                        {"complete": True, "events": [read, {"tool": "run_project", "outcome": "ok", "id": "r"}]},
                        {"complete": True, "events": [{"tool": "unregistered", "outcome": "rejected", "id": "u"}]}):
            with self.subTest(history=history):
                self.assertIsNone(execution_observation(history))
                self.assertEqual(history_finding({"unit": 2, "text": ToolHistoryModel.no_run}, history)["assessment"],
                                 "insufficient")
        note = {"unit": 2, "text": ToolHistoryModel.no_run}
        for outcome in ("empty", "error"):
            with self.subTest(read_outcome=outcome):
                no_source_read = {"complete": True, "events": [{**read, "outcome": outcome}]}
                self.assertIs(execution_observation(no_source_read), False)
                self.assertEqual(history_finding(note, no_source_read)["assessment"], "insufficient")
                plain = history_finding({**note, "text": "Nie uruchamiałem kodu."}, no_source_read)
                self.assertEqual(plain["assessment"], "supported")


class SavedClaudeEvidenceTests(unittest.TestCase):
    def test_rechecks_three_saved_answers_against_pinned_git(self):
        with patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
            from fineract_r2_ask import PinnedSearch, check_final_evidence, checked_proposal
            from fineract_r2_corpus import parse_manifest

        archive = PROJECT / "verification/fineract-approval-current-04.json"
        if not archive.is_file():
            self.skipTest("the recorded Claude experiment is absent")
        rows = [row for row in json.loads(archive.read_bytes())["attempts"] if "grade" in row]
        self.assertEqual(len(rows), 3)
        for row in rows:
            recorded = row["stdout_json"]
            directory = Path(recorded["run_directory"])
            if not (directory / "sources/fineract.git/HEAD").is_file():
                self.skipTest(f"local Git and model artifacts are absent for {row['id']}")
        for row in rows:
            with self.subTest(view=row["id"]):
                recorded = row["stdout_json"]
                run = Path(recorded["run_directory"])
                manifest = (run / "manifest.json").read_bytes()
                digest = sha256(manifest).hexdigest()
                self.assertEqual(digest, recorded["manifest_sha256"])
                repos = parse_manifest(manifest)
                self.assertEqual({repo["id"]: repo["snapshot"]["commit"] for repo in repos},
                                 {repo["id"]: repo["commit"] for repo in recorded["view"]["repositories"]})
                store = object.__new__(PinnedSearch)
                store.sources, store.digest, store.trace = run / "sources", digest, {"reads": []}
                store.by_id = {repo["id"]: repo for repo in repos}
                repo_ids = {repo["snapshot"]["repository"]: repo["id"] for repo in repos}
                store.found, store.lines = {}, {}
                searches = {}
                for search in recorded["searches"]:
                    key = (search["literal"], search["path_terms"])
                    self.assertEqual((search["status"], search["manifest_sha256"]), ("VERIFIED", digest))
                    answer = (Path(search["output_directory"]) / "answer.jsonl").read_bytes()
                    self.assertEqual(sha256(answer).hexdigest(), search["result_sha256"])
                    hits = []
                    for line in answer.splitlines():
                        hit = json.loads(line)
                        if hit["type"] == "hit":
                            repo = repo_ids[hit["repository"]]
                            self.assertEqual(hit["commit"], store.by_id[repo]["snapshot"]["commit"])
                            store.found[repo, hit["path"]] = hit["blob_id"]
                            hits.append({**hit, "repository": repo})
                    self.assertEqual(len(hits), search["count"])
                    searches[key] = {"shown": hits}
                store.search = lambda literal, path_terms: searches[literal, path_terms]

                first, *_, final = [block["input"] for path in sorted(run.glob("model-*.json"))
                                    for block in json.loads(path.read_bytes()) if block.get("name") == "submit"]
                self.assertEqual(final["answer_pl"], recorded["answer_pl"])
                self.assertEqual(final["verdict"], recorded["verdict"])
                git_config = int(os.environ.get("GIT_CONFIG_COUNT", 0))
                with patch.dict(os.environ, {"GIT_CONFIG_COUNT": str(git_config + 1),
                                             f"GIT_CONFIG_KEY_{git_config}": "safe.directory",
                                             f"GIT_CONFIG_VALUE_{git_config}": (store.sources / "fineract.git").as_posix()}):
                    context = store.method_context(checked_proposal(store, first))
                    self.assertTrue(context["callers"])
                    citations, missing = check_final_evidence(store, final, context)
                self.assertEqual(missing, [])
                self.assertEqual(citations, recorded["citations"])
                span = context["rule"]["suggested_citation"]
                if row["id"] == "pr-after-push-before-synchronize":
                    self.assertEqual(first["citations"][0]["start"] - final["citations"][0]["start"], 2)
                    self.assertGreater(span["start"], final["citations"][0]["start"])
                print(f"{row['id']}: VERIFIED ({context['rule']['commit']}, rule {span['start']}-{span['end']})")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--scripted"]:
        sys.path.insert(0, str(SCRIPTS))
        from fineract_r2_ask import main

        mode = sys.argv[2]
        if mode.startswith("review-history-"):
            scripted = ToolHistoryModel(mode)
        elif mode.startswith("review-"):
            scripted = ConclusionModel(mode)
        else:
            scripted = ScriptedModel(mode)
        raise SystemExit(main(sys.argv[3:], get_client=lambda: nullcontext(scripted)))
    unittest.main()
