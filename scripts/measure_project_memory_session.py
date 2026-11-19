"""Compare full public CLI responses in new processes and in one session, offline."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import runpy
from statistics import median
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Timer
from time import perf_counter

from evaluate_project_memory_intent import CLI, HISTORICAL, PROJECT, expected_output, file_hash


RECORDING = PROJECT / "verification/project-memory-intent-first.json"
KNOWN = "a które z tych plików są testami?"
TRIALS = 17


def replay_cli(fixture, args):
    from repo_proof import memory_intent

    def client():
        import anthropic
        import httpx2

        replies = json.loads(Path(fixture).read_bytes())

        def respond(request):
            assert request.method == "POST" and request.url.host == "api.anthropic.com"
            payload = json.loads(request.content)
            assert payload["model"] == memory_intent.MODEL
            reply = replies[payload["messages"][0]["content"]]
            if request.url.path == "/v1/messages/count_tokens":
                return httpx2.Response(200, json={"input_tokens": reply["estimated_input_tokens"]})
            assert request.url.path == "/v1/messages"
            return httpx2.Response(200, json=reply["response"])

        return anthropic.Anthropic(
            api_key="offline-replay", base_url="https://api.anthropic.com", max_retries=0,
            timeout=memory_intent.TIMEOUT,
            http_client=httpx2.Client(transport=httpx2.MockTransport(respond), trust_env=False),
        )

    memory_intent.anthropic_client = client
    sys.argv = [str(CLI), *args]
    runpy.run_path(str(CLI), run_name="__main__")


def command(database, *args, fixture=None):
    entry = [CLI] if fixture is None else [Path(__file__).resolve(), "--replay-child", fixture]
    return [sys.executable, "-B", "-X", "utf8", *entry, "--db", database, *args]


@contextmanager
def running_cli(argv, environment):
    with subprocess.Popen(argv, cwd=PROJECT, env=environment, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8") as process:
        deadline = Timer(60, process.kill)
        deadline.daemon = True
        deadline.start()
        try:
            yield process
        finally:
            deadline.cancel()
            if process.poll() is None:
                process.kill()


def send(process, line):
    process.stdin.write(line + "\n")
    process.stdin.flush()


def timed_answer(process, lines, started):
    actual = [process.stdout.readline().removesuffix("\n") for _ in lines]
    elapsed = (perf_counter() - started) * 1000
    if actual != lines:
        mismatch = next((pair for pair in zip(lines, actual) if pair[0] != pair[1]))
        raise ValueError(f"Odpowiedź różni się od wyniku R2: {mismatch!r}")
    return elapsed


def check_exit(process):
    trailing = process.stdout.read()
    if process.wait(timeout=5) or trailing:
        raise ValueError(f"Nieoczekiwane zakończenie CLI: {trailing!r}")


def measure(database, sequence, expected, environment, fixture=None):
    interpreter = ("--interpreter", "claude") if fixture else ()
    first_conversation, first_question = sequence[0]
    session_args = command(database, "sesja", "--rozmowa", first_conversation, *interpreter, fixture=fixture)
    started = perf_counter()
    with running_cli(session_args, environment) as session:
        send(session, first_question)
        ongoing = [timed_answer(session, expected[first_conversation], started)]
        fresh = []
        for i, (conversation, question) in enumerate(sequence):
            argv = command(database, "zapytaj", "--rozmowa", conversation, *interpreter, question, fixture=fixture)
            started = perf_counter()
            with running_cli(argv, environment) as process:
                fresh.append(timed_answer(process, expected[conversation], started))
                check_exit(process)
            if i + 1 < len(sequence):
                next_conversation, next_question = sequence[i + 1]
                send(session, f"/rozmowa {next_conversation}")
                started = perf_counter()
                send(session, next_question)
                ongoing.append(timed_answer(session, expected[next_conversation], started))
        send(session, "/koniec")
        check_exit(session)
    return {"zapytaj": summarize(fresh), "sesja": summarize(ongoing),
            "median_savings_ms": median(fresh[1:]) - median(ongoing[1:])}


def summarize(times):
    subsequent = times[1:]
    return {"first_ms": times[0], "next_ms": subsequent, "next_n": len(subsequent),
            "median_ms": median(subsequent), "min_ms": min(subsequent), "max_ms": max(subsequent)}


def evaluate(loan, decimal):
    cases = {"A": (loan, "LoanTransaction", 294, 718), "B": (decimal, "BigDecimal", 570, 1362)}
    expected = {conversation: expected_output(*case) for conversation, case in cases.items()}
    source_rows = json.loads(RECORDING.read_bytes())["rows"]
    rows = [row for row in source_rows if row["variant"] == "claude"
            and row["expected"] == row["model_evidence"].get("decision") == "show_test_paths"]
    replay_questions = [(row["conversation"], row["question"]) for row in rows]
    if len(rows) != 8 or [conversation for conversation, _ in replay_questions] != ["A", "B"] * 4:
        raise ValueError("Nieoczekiwana kolejność pytań w zapisie odpowiedzi Claude.")
    replay = [replay_questions[i % len(replay_questions)] for i in range(TRIALS)]
    local = [(conversation, KNOWN) for conversation, _ in replay]
    environment = dict(os.environ)
    environment.pop("ANTHROPIC_API_KEY", None)
    originals = [folder / name for folder, *_ in cases.values()
                 for name in ("answer.jsonl", "verification.json")]
    fingerprints = [file_hash(path) for path in originals]
    with TemporaryDirectory() as directory:
        database = Path(directory) / "evaluation.sqlite3"
        fixture = Path(directory) / "replay.json"
        fixture.write_text(json.dumps({row["question"]: row["model_evidence"] for row in rows}), encoding="utf-8")
        for conversation, (folder, _, _, _) in cases.items():
            subprocess.run(command(database, "otwórz-wynik", "--rozmowa", conversation, folder),
                           cwd=PROJECT, env=environment, capture_output=True, encoding="utf-8",
                           check=True, timeout=10)
        modes = {"local": measure(database, local, expected, environment),
                 "claude_offline_replay": measure(database, replay, expected, environment, fixture)}
    if [file_hash(path) for path in originals] != fingerprints:
        raise ValueError("Artefakty R2 zmieniły się podczas pomiaru.")
    return {"modes": modes, "all_complete_answers_matched": True, "paid_calls": 0,
            "recording_sha256": file_hash(RECORDING), "replayed_ids": [row["id"] for row in rows],
            "conversations": [conversation for conversation, _ in replay]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loan-result", type=Path, default=HISTORICAL / "01-03/answer")
    parser.add_argument("--decimal-result", type=Path, default=HISTORICAL / "01-04/answer")
    parser.add_argument("--report", type=Path, help="nowy plik JSON z indywidualnymi czasami prób")
    args = parser.parse_args()
    report = json.dumps(evaluate(args.loan_result.resolve(), args.decimal_result.resolve()), indent=2)
    if args.report:
        with args.report.open("x", encoding="utf-8") as stream:
            stream.write(report + "\n")
    print(report)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--replay-child"]:
        replay_cli(sys.argv[2], sys.argv[3:])
    else:
        main()
