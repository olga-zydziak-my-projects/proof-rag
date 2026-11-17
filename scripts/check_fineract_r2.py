"""Recompute the Fineract R2 acceptance gates from a retained run and reviews."""

import argparse
from pathlib import Path
import sys

from run_fineract_r2 import (
    CONTRACT, FROZEN_MEASUREMENT, PROJECT, TEST_GROUPS, baseline_files, digest,
    historical_anchors, identities, input_sets, read, resource_ok, save,
)


def log_binding(run):
    root = Path(run["log_directory"])
    return all(digest(root / f"{stream}.log") == run[f"{stream}_sha256"]
               for stream in ("stdout", "stderr"))


def monitored(run, timeout):
    monitor = run["supervisor"]
    report = Path(monitor["report"])
    raw = read(report)
    return (run["returncode"] == 0 and run["wall_seconds"] < timeout
            and resource_ok(raw, timeout) and monitor["passed"]
            and digest(report) == monitor["sha256"]
            and raw["command"] == monitor["worker_command"]
            and raw["exit_code"] == monitor["worker_returncode"]
            and raw["status"] == monitor["status"]
            and raw["remaining_job_processes"] == monitor["descendants_after_cleanup"]
            and raw["peak_tree_rss"] == monitor["peak_tree_rss"]
            and raw["peak_tree_private"] == monitor["peak_tree_private"]
            and raw["peak_artifact_bytes"] == monitor["peak_artifact_bytes"]
            and raw["elapsed_seconds"] == monitor["wall_seconds"]
            and all(digest(report.parent / f"{stream}.log") == monitor[f"worker_{stream}_sha256"]
                    for stream in ("stdout", "stderr")))


def outcomes(runs, contract, contract_hash):
    pin = contract["snapshot"]
    for row in runs:
        folder = Path(row["answer_directory"])
        proof = read(folder / "verification.json")
        result = row["result"]
        inv = proof["inventory"]
        yield (row["passed"] and row["returncode"] == 0
               and result == read(Path(row["log_directory"]) / "stdout.log")
               and set(path.name for path in folder.iterdir()) == {"answer.jsonl", "verification.json"}
               and proof["status"] == result["status"] == "VERIFIED"
               and proof["literal"] == result["literal"] == row["literal"]
               and proof["snapshot"] == result["snapshot"] == pin
               and proof["inventory"] == result["inventory"]
               and proof["contract_sha256"] == result["contract_sha256"] == contract_hash
               and proof["output_directory"] == result["path"] == str(folder)
               and proof["result_sha256"] == result["result_sha256"] == digest(folder / "answer.jsonl")
               and digest(folder / "verification.json") == row["receipt_sha256"]
               and proof["method"] == result["method"] and proof["count"] == result["count"]
               and inv["distinct_regular_blobs"] == contract["distinct_regular_blobs"]
               and all(inv[key] == pin[key] for key in ("regular_paths", "blob_paths", "gitlinks", "symlinks"))
               and len(inv["excluded_symlinks"]) == pin["symlinks"]
               and f"--literal={row['literal']}" in row["command"]
               and f"--literal={row['literal']}" in row["supervisor"]["worker_command"])


def fixture_log(folder, name):
    return read(folder / "fixture" / name / "resource-report.json")


def evaluate(report_path, review_path):
    summary, reviews, contract = read(report_path), read(review_path), read(CONTRACT)
    groups = input_sets(contract)
    runs = summary["query_runs"]
    by_group = {group: [row for row in runs if row["group"] == group] for group in groups}
    expected = [(group, repeat, position, literal)
                for group, (literals, repetitions) in groups.items()
                for repeat in range(1, repetitions + 1)
                for position, literal in enumerate(literals, 1)]
    actual = [(row["group"], row["repeat"], row["position"], row["literal"]) for row in runs]
    plan = summary["stopped_after"] == "complete" and expected == actual
    history = historical_anchors(contract)
    history_exact = all((row["result"]["result_sha256"], row["result"]["count"]) ==
                        (history[row["literal"]]["answer_sha256"], history[row["literal"]]["count"])
                        for row in by_group["historical"])
    contract_hash = digest(CONTRACT)
    folder = Path(summary["work_dir"])
    build = summary["build"]
    pin = contract["snapshot"]
    complete_map = plan and all(outcomes(runs, contract, contract_hash))
    tests = summary["tests"]
    tested = set(tests) == set(TEST_GROUPS) and all(
        run["passed"] and run["returncode"] == 0 and len(set(run["passed_tests"])) == TEST_GROUPS[group][1]
        and log_binding(run) for group, run in tests.items())
    r2_names = {name.rsplit(".", 1)[-1] for name in tests["r2"]["passed_tests"]}
    fixture = read(folder / "fixture/deleted-posting-evidence.json")
    timeout, interrupted = (fixture_log(folder, name) for name in ("timeout-log", "interrupt-log"))
    verifier = reviews["verifier_publication"]
    evidence = reviews["evidence"]
    expected_review_files = ("scripts/fineract_r2.py", "src/repo_proof/fineract_oracle.py",
                             "tests/test_fineract_r2.py")
    review_ok = (verifier["agent"] != evidence["agent"]
                 and verifier["blocking_findings"] == evidence["blocking_findings"] == []
                 and all(verifier["file_sha256"][name] == digest(PROJECT / name)
                         for name in expected_review_files)
                 and evidence["run_report_sha256"] == digest(report_path)
                 and evidence["gate_code_sha256"] == digest(Path(__file__))
                 and evidence["results_doc_sha256"] == digest(PROJECT / "docs/fineract-r2-results.md")
                 and evidence["usage_doc_sha256"] == digest(PROJECT / "docs/fineract-r2-usage.md"))
    gates = {
        "public_verified_command": complete_map and "test_known_witnesses_and_raw_names" in r2_names
                                   and "test_verified_empty" in r2_names,
        "pinned_scope_and_byte_semantics": complete_map and summary["snapshot"] == pin
            and build["result"]["build"]["snapshot"] == pin
            and build["result"]["build"]["distinct_regular_blobs"] == contract["distinct_regular_blobs"]
            and build["result"]["build"]["path_and_blob_sets_reconciled"] is True
            and "test_wrong_contract_pins" in r2_names,
        "historical_answers": complete_map and len(by_group["historical"]) == 24 and history_exact,
        "development_and_final": complete_map and len(by_group["development"]) == len(by_group["final"]) == 20,
        "controlled_mutations_rejected": fixture == summary["fixture"]
            and (fixture["removed_postings"], fixture["r1_exit_code"], fixture["r1_count"],
                 fixture["git_count"], fixture["r2_exit_code"], fixture["r2_status"],
                 fixture["r2_published"]) == (1, 0, 0, 3, 2, "MISMATCH", False)
            and {"test_deleted_trigram_reproduces_false_empty_then_rejects", "test_changed_blob_bytes",
                 "test_changed_path_mapping", "test_second_occurrence_and_wrong_line",
                 "test_omitted_and_additional_path", "test_wrong_result_provenance",
                 "test_duplicate_keys_paths_and_wrong_types", "test_incomplete_and_invalid_jsonl"} <= r2_names,
        "fail_closed": {"test_timeout_does_not_publish", "test_supervised_interrupt_does_not_publish",
                        "test_missing_git_blob", "test_existing_output", "test_invalid_literals",
                        "test_interrupt_mask_at_publication_commit"} <= r2_names
            and (timeout["status"], interrupted["status"]) == ("TIMEOUT", "INTERRUPTED")
            and timeout["remaining_job_processes"] == interrupted["remaining_job_processes"] == 0
            and all(not (folder / "fixture" / name).exists() for name in
                    ("timeout", "interrupt", "missing-blob", "deleted-posting-answer",
                     "wrong-blob-bytes", "wrong-path-mapping")),
        "required_tests": tested,
        "measurement_budget": plan and summary["measurement"] == FROZEN_MEASUREMENT
            and summary["local_artifact_bytes"] <= FROZEN_MEASUREMENT["artifact_bytes"]
            and monitored(build, 300) and all(monitored(row, 60) for row in runs),
        "bound_artifacts_and_code": complete_map and summary["input_bytes_unchanged"]
            and summary["contract_sha256"] == contract_hash
            and summary["query_sets"] == contract["query_sets"]
            and summary["identity"] == identities()
            and summary["historical_bytes"] == baseline_files(contract["r1_baseline"])
            and summary["r1_baseline"] == contract["r1_baseline"]
            and log_binding(build) and all(log_binding(row) for row in runs)
            and build["result"] == read(Path(build["log_directory"]) / "stdout.log")
            and digest(folder / "index.sqlite") == build["result"]["index_sha256"]
            and read(folder / "frozen-inputs.json") == {key: summary[key] for key in
                ("started_utc", "r1_baseline", "snapshot", "contract_sha256", "query_sets",
                 "measurement", "identity")},
        "independent_reviews": review_ok,
    }
    failing = [name for name, passed in gates.items() if not passed]
    return {"status": "FINERACT_R2_PASS" if not failing else "FINERACT_R2_FAIL",
            "gates": gates, "unmet_gates": failing, "r1_baseline": contract["r1_baseline"],
            "contract_sha256": contract_hash, "run_report_sha256": digest(report_path),
            "reviews_sha256": digest(review_path), "gate_code_sha256": digest(Path(__file__)),
            "query_runs": len(runs), "distinct_literals": len({row["literal"] for row in runs}),
            "tests_passed": sum(len(item["passed_tests"]) for item in tests.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output file must be new")
    try:
        result = evaluate(args.report, args.reviews)
    except (OSError, KeyError, ValueError, TypeError) as exc:
        result = {"status": "FINERACT_R2_BLOCKED", "reason": str(exc),
                  "unmet_gates": ["complete_reproducible_evidence"]}
    save(args.out, result)
    print(result["status"])
    return 0 if result["status"] == "FINERACT_R2_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
