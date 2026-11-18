"""Run the fixed 32-attempt Claude/DSPy benchmark through the public memory CLI."""

import argparse
from collections import Counter
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
from statistics import median
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from repo_proof.memory_intent import (
    MAX_INPUT_RESERVATION, MAX_OUTPUT, MODEL, InterpretationError, anthropic_client, api_error,
)


CLI = PROJECT / "scripts/project_memory.py"
QUESTIONS = PROJECT / "verification/project-memory-intent-questions.json"
HISTORICAL = PROJECT / "local/fineract-r2/run-02/historical"
VARIANTS = ("claude", "dspy")
# USD billionths per token from the public standard Anthropic API prices.
PRICING = {
    "source": "https://platform.claude.com/docs/en/about-claude/pricing",
    "checked": "2026-11-18", "model": "claude-haiku-5-5",
    "long_input_threshold": 100_000, "regular": [100, 500], "long": [500, 2500],
}
BUDGET = 1_000_000_000
ATTEMPTS = 32
RESERVATION = MAX_INPUT_RESERVATION * PRICING["long"][0] + MAX_OUTPUT * PRICING["long"][1]


def usd(nanos):
    whole, fraction = divmod(nanos, 1_000_000_000)
    return f"{whole}.{fraction:09d}"


class Budget:
    def __init__(self, planned):
        self.reservations = 0
        self.committed = 0
        if PRICING["model"] != MODEL or planned > ATTEMPTS or planned * RESERVATION > BUDGET:
            raise ValueError("Plan wywołań przekracza budżet lub model nie ma potwierdzonej ceny.")

    def reserve(self):
        if self.reservations >= ATTEMPTS or self.committed + RESERVATION > BUDGET:
            raise ValueError("Wyczerpano budżet wywołań.")
        self.reservations += 1
        self.committed += RESERVATION

    def settle(self, evidence):
        response = evidence.get("response")
        if not response:
            return None
        if response.get("model") != MODEL:
            raise ValueError("Brak potwierdzonej ceny dla modelu w odpowiedzi.")
        usage = response.get("usage") or {}
        input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
        if any(type(value) is not int or value < 0 for value in (input_tokens, output_tokens)):
            raise ValueError("Brak wiarygodnego rozliczenia tokenów odpowiedzi.")
        if usage.get("cache_creation_input_tokens") or usage.get("cache_read_input_tokens"):
            raise ValueError("Dostawca zgłosił cache w próbie wykonywanej bez cache.")
        tier = "long" if input_tokens > PRICING["long_input_threshold"] else "regular"
        input_price, output_price = PRICING[tier]
        cost = input_price * input_tokens + output_price * output_tokens
        self.committed += cost - RESERVATION
        if input_tokens > MAX_INPUT_RESERVATION or output_tokens > MAX_OUTPUT:
            raise ValueError("Zgłoszone użycie przekracza granice przyjęte w budżecie.")
        return cost


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def expected_output(folder, literal, count, total):
    answer = folder / "answer.jsonl"
    header, *hits, trailer = map(json.loads, answer.read_bytes().splitlines())
    paths = [hit["path"] for hit in hits if re.search(r"(?:^|/)src/test/.+", hit["path"])]
    if header["literal"] != literal or len(paths) != count or len(hits) != total or trailer["count"] != total:
        raise ValueError(f"Nieoczekiwany wynik R2 dla {literal}.")
    return [f"Repozytorium: {header['repository']}", f"Commit: {header['commit']}", f"Literał: {literal}",
            f"Pliki pod src/test/ ({count} z {total})", *(f"  {path}" for path in paths)]


def invoke(db, *args):
    return subprocess.run([sys.executable, "-B", "-X", "utf8", CLI, "--db", db, *args],
                          cwd=PROJECT, capture_output=True, encoding="utf-8", timeout=90)


def measure(db, args, variant, measurement, expected):
    started = perf_counter()
    try:
        proc = invoke(db, "zapytaj", "--rozmowa", args["conversation"], "--interpreter", variant,
                      "--measurement", measurement, args["question"])
    except subprocess.TimeoutExpired:
        return {}, {"status": "process_timeout", "seconds": perf_counter() - started}
    elapsed = perf_counter() - started
    evidence = (json.loads(measurement.read_text(encoding="utf-8"))
                if measurement.exists() and measurement.stat().st_size else {})
    lines = proc.stdout.splitlines()
    issued = any(line.startswith("Pliki pod src/test/ (") for line in lines)
    return evidence, {
        "status": evidence.get("application", "process_error"), "return_code": proc.returncode,
        "seconds": elapsed, "issued_list": issued, "false_release": issued and args["expected"] != "show_test_paths",
        "full_list_matched": lines == expected if issued else None,
        "stdout_sha256": sha256(proc.stdout.encode("utf-8")).hexdigest(),
        "stderr": proc.stderr if evidence else None,
    }


def distribution(values):
    return {"n": len(values), "median": median(values), "min": min(values), "max": max(values)} if values else None


def summarize(rows, variant):
    trials = [row for row in rows if row["variant"] == variant and "model_evidence" in row]
    usage = [row["model_evidence"]["response"]["usage"] for row in trials if row.get("cost_usd") is not None]
    errors = [row["id"] for row in trials if row["expected"] != row["model_evidence"].get("decision")]
    return {
        "attempted": sum(row["model_evidence"].get("paid_attempt", False) for row in trials),
        "correct_decisions": len(trials) - len(errors), "incorrect_or_missing": errors,
        "false_releases": sum(row["application"].get("false_release", False) for row in trials),
        "complete_lists_matched": sum(row["application"].get("full_list_matched") is True for row in trials),
        "billed_usage_rows": len(usage),
        "reported_input_tokens": sum(item["input_tokens"] for item in usage),
        "reported_output_tokens": sum(item["output_tokens"] for item in usage),
        "reported_cost_usd": usd(sum(row.get("cost_nanos") or 0 for row in trials)),
        "full_seconds": distribution([row["application"]["seconds"] for row in trials]),
        **{key: distribution([row["model_evidence"][key] for row in trials if key in row["model_evidence"]])
           for key in ("api_seconds", "count_seconds", "local_seconds")},
    }


def save(path, report):
    staged = path.with_suffix(".tmp")
    staged.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    staged.replace(path)


def evaluate(args):
    questions = json.loads(QUESTIONS.read_bytes())
    if (Counter(row["expected"] for row in questions) != {"show_test_paths": 8, "clarify": 4, "unsupported": 4}
            or len({row["id"] for row in questions}) != 16):
        raise ValueError("Niepoprawny zamrożony zestaw pytań.")
    budget = Budget(len(questions) * len(VARIANTS))
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True)
    report_path = run_dir / "report.json"
    rows = []
    report = {
        "status": "preflight", "model": MODEL, "pricing": PRICING, "rows": rows,
        "planned_attempts": ATTEMPTS, "limit_usd": usd(BUDGET), "planned_upper_bound_usd": usd(ATTEMPTS * RESERVATION),
        "per_attempt_reservation_usd": usd(RESERVATION), "max_output_tokens": MAX_OUTPUT,
        "input_token_reserve": MAX_INPUT_RESERVATION,
        "source_sha256": {str(path.relative_to(PROJECT).as_posix()): file_hash(path) for path in (
            CLI, QUESTIONS, Path(__file__).resolve(), PROJECT / "src/repo_proof/memory_intent.py",
            PROJECT / "requirements-project-memory-intent.txt")},
    }
    save(report_path, report)
    try:
        with anthropic_client() as api:
            try:
                model = api.models.retrieve(MODEL)
            except Exception as exc:
                raise api_error(exc) from None
        report["model_confirmed"] = model.id
        if model.id != MODEL:
            raise ValueError("Anthropic API zwróciło inny model niż zatwierdzony w cenniku.")
        report["versions"] = {"python": sys.version.split()[0], **{pkg: version(pkg) for pkg in (
            "anthropic", "dspy", "litellm")}}
        os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
        import dspy  # preflight before any generation, including when optional dependencies are broken
        if not all(hasattr(dspy, name) for name in ("Predict", "ChatAdapter", "BaseLM")):
            raise ValueError("Brakuje komponentów DSPy wymaganych w porównaniu.")

        expected = {}
        report["r2_artifact_sha256"] = {}
        with TemporaryDirectory() as directory:
            db = Path(directory) / "evaluation.sqlite3"
            for conv, folder, literal, count, total in (
                ("A", args.loan_result.resolve(), "LoanTransaction", 294, 718),
                ("B", args.decimal_result.resolve(), "BigDecimal", 570, 1362),
            ):
                expected[conv] = expected_output(folder, literal, count, total)
                report["r2_artifact_sha256"][conv] = {name: file_hash(folder / name) for name in (
                    "answer.jsonl", "verification.json")}
                if invoke(db, "otwórz-wynik", "--rozmowa", conv, folder).returncode:
                    raise ValueError(f"Nie udało się otworzyć opublikowanego wyniku dla rozmowy {conv}.")

            report["status"] = "running"
            for index, item in enumerate(questions):
                for variant in VARIANTS if index % 2 == 0 else VARIANTS[::-1]:
                    budget.reserve()
                    row = {**item, "variant": variant, "state": "reserved"}
                    rows.append(row)
                    save(report_path, report)
                    measurement = run_dir / f"{item['id']}-{variant}.json"
                    evidence, application = measure(db, item, variant, measurement, expected[item["conversation"]])
                    row.update(state="finished", model_evidence=evidence, application=application)
                    cost = budget.settle(evidence)
                    row.update(cost_nanos=cost, cost_usd=usd(cost) if cost is not None else None)
                    save(report_path, report)
                    if (application["status"] in ("configuration_error", "budget_error", "process_timeout", "process_error")
                            or not evidence.get("paid_attempt") or (cost is not None and cost > RESERVATION)):
                        raise ValueError(f"Przerwano serię po {item['id']} ({variant}, {application['status']}).")
        report["status"] = "complete"
    except (OSError, ValueError, ImportError, subprocess.SubprocessError) as exc:
        report.update(status="partial" if rows else "blocked", reason=str(exc))
    finally:
        report.update(reservations=budget.reservations, charged_or_reserved_usd=usd(budget.committed),
                      summaries={variant: summarize(rows, variant) for variant in VARIANTS})
        save(report_path, report)
    print(report_path)
    return 0 if report["status"] == "complete" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True, help="nowy katalog na pierwszy pomiar")
    parser.add_argument("--loan-result", type=Path, default=HISTORICAL / "01-03/answer")
    parser.add_argument("--decimal-result", type=Path, default=HISTORICAL / "01-04/answer")
    args = parser.parse_args()
    try:
        return evaluate(args)
    except (OSError, ValueError) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
