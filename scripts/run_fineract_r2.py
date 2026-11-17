"""Run the frozen Fineract R2 inputs sequentially and record exact evidence."""

import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sqlite3
import statistics
import subprocess
import sys
from time import perf_counter

import psutil


PROJECT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT / "docs/fineract-r2-contract.json"
PYTHON = [sys.executable, "-B"]
CLI = [*PYTHON, str(PROJECT / "scripts/fineract_r2.py")]
SOURCE = (
    "scripts/fineract_r2.py", "scripts/run_fineract_r2.py", "scripts/stage8_supervise.py",
    "src/repo_proof/__init__.py", "src/repo_proof/checker.py", "src/repo_proof/corpus.py",
    "src/repo_proof/cli.py", "src/repo_proof/fineract_oracle.py", "src/repo_proof/generator.py",
    "src/repo_proof/git_search.py", "src/repo_proof/graph.py",
    "tests/test_cli.py", "tests/test_corpus.py", "tests/test_fineract_r2.py",
)
TEST_GROUPS = {"cli": ("test_cli.py", 2), "corpus": ("test_corpus.py", 13),
               "r2": ("test_fineract_r2.py", 17)}
FROZEN_MEASUREMENT = {
    "parallel_heavy_jobs": 1, "priority": "Normal", "build_timeout_seconds": 300,
    "query_timeout_seconds": 60, "sample_seconds": 0.02, "tree_memory_bytes": 2147483648,
    "artifact_bytes": 4294967296, "filesystem_cache": "Not cleared",
}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    value = sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(data)
    return value.hexdigest()


def save(path, data):
    path.write_bytes((json.dumps(data, ensure_ascii=True, indent=2) + "\n").encode("ascii"))


def read(path):
    return json.loads(path.read_bytes())


def input_sets(contract):
    if contract["measurement"] != FROZEN_MEASUREMENT:
        raise ValueError("measurement configuration differs from the frozen limits")
    seen = set()
    groups = {}
    for group, count, repetitions in (("historical", 8, 3), ("development", 20, 1), ("final", 20, 1)):
        declaration = contract["query_sets"][group]
        source = PROJECT / declaration["file"]
        if digest(source) != declaration["sha256"]:
            raise ValueError(f"frozen list digest differs for {group}")
        raw = read(source)
        literals = raw["queries"] if group == "historical" else raw
        if (len(literals) != count or declaration["literals"] != count
                or declaration["runs_per_literal"] != repetitions
                or any(not re.fullmatch(r"[ -~]+", literal) for literal in literals)
                or len(set(literals)) != count or seen.intersection(literals)):
            raise ValueError(f"invalid frozen list: {group}")
        seen.update(literals)
        groups[group] = (literals, repetitions)
    return groups


def identities():
    dependencies = Path(psutil.__file__).resolve().parent
    psutil_files = {str(path): digest(path) for path in sorted(dependencies.rglob("*"))
                    if path.suffix in (".py", ".pyd", ".dll") and path.is_file()}
    binaries = {Path(sys.executable), Path(shutil.which("git"))}
    binaries.update(Path(sys.base_prefix).glob("python*.dll"))
    binaries.update((Path(sys.base_prefix) / "DLLs").glob("*sqlite*"))
    return {"source_and_tests": {name: digest(PROJECT / name) for name in SOURCE},
            "local_dependency_files": psutil_files,
            "executables": {str(path): digest(path) for path in sorted(binaries)},
            "versions": {"python": platform.python_version(), "git": subprocess.check_output(
                ["git", "--version"], text=True, cwd=PROJECT).strip(), "sqlite": sqlite3.sqlite_version,
                "psutil": psutil.__version__}}


def historical_anchors(contract):
    directory = PROJECT / "verification/fineract-r1"
    summary = read(directory / "summary.json")
    anchors = {}
    for row in summary["queries"]:
        archive = directory / row["result_file"]
        decoded = sha256(gzip.decompress(archive.read_bytes())).hexdigest()
        if decoded != row["first"]["result_sha256"] or digest(archive) != row["gzip_sha256"]:
            raise ValueError(f"historical result changed: {archive.name}")
        anchors[row["literal"]] = {"file": row["result_file"], "answer_sha256": decoded,
                                   "archive_sha256": row["gzip_sha256"], "count": row["first"]["count"]}
    if summary["contract_sha256"] != contract["query_sets"]["historical"]["sha256"]:
        raise ValueError("historical results reference a different contract")
    return anchors


def baseline_files(baseline):
    raw = subprocess.check_output(["git", "diff-tree", "--no-commit-id", "--name-only", "-r",
                                   "-z", baseline], cwd=PROJECT)
    inventory = {}
    for name in raw.decode("utf-8").split("\0")[:-1]:
        expected = subprocess.check_output(["git", "show", f"{baseline}:{name}"], cwd=PROJECT)
        actual = (PROJECT / name).read_bytes()
        if expected != actual:
            raise ValueError(f"historical R1 bytes changed: {name}")
        inventory[name] = sha256(actual).hexdigest()
    if len(inventory) != 16:
        raise ValueError("unexpected R1 baseline inventory")
    return inventory


def resource_ok(resource, timeout):
    config = FROZEN_MEASUREMENT
    return (resource["status"] == "PROCESS_PASS" and resource["exit_code"] == 0
            and resource["remaining_job_processes"] == 0
            and resource["limits"] == {"timeout_seconds": timeout,
                                       "sample_seconds": config["sample_seconds"],
                                       "tree_memory_bytes": config["tree_memory_bytes"],
                                       "artifact_bytes": config["artifact_bytes"]}
            and resource["elapsed_seconds"] < timeout
            and 0 < resource["peak_tree_rss"] <= config["tree_memory_bytes"]
            and 0 < resource["peak_tree_private"] <= config["tree_memory_bytes"]
            and resource["peak_artifact_bytes"] <= config["artifact_bytes"]
            and resource["final_artifact_limit_exceeded"] is False)


def stats(samples):
    return {"median": statistics.median(samples), "min": min(samples), "max": max(samples)}


def invoke(command, directory, environment):
    directory.mkdir()
    started = perf_counter()
    with (directory / "stdout.log").open("wb") as out, (directory / "stderr.log").open("wb") as err:
        result = subprocess.run(command, cwd=PROJECT, env=environment, stdout=out, stderr=err,
                                creationflags=subprocess.NORMAL_PRIORITY_CLASS)
    return {"command": command, "returncode": result.returncode,
            "wall_seconds": perf_counter() - started, "log_directory": str(directory),
            "stdout_sha256": digest(directory / "stdout.log"),
            "stderr_sha256": digest(directory / "stderr.log")}


def test_steps(folder, environment):
    results = {}
    for label, (pattern, count) in TEST_GROUPS.items():
        command = [*PYTHON, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"]
        result = invoke(command, folder / ("tests-" + label), environment)
        raw = (Path(result["log_directory"]) / "stderr.log").read_text(encoding="utf-8", errors="replace")
        entries = list(re.finditer(r"^test_\w+ \(([^)]+)\) \.\.\. ", raw, flags=re.MULTILINE))
        roster = []
        for position, entry in enumerate(entries):
            end = entries[position + 1].start() if position + 1 < len(entries) else len(raw)
            lines = raw[entry.end():end].splitlines()
            if "ok" in lines:
                roster.append(entry[1])
        results[label] = {**result, "passed_tests": roster,
                          "passed": result["returncode"] == 0 and len(set(roster)) == len(entries) == count}
    return results


def supervision(log, timeout):
    path = log / "resource-report.json"
    if not path.exists():
        return {"passed": False}
    raw = read(path)
    return {"passed": resource_ok(raw, timeout), "report": str(path), "sha256": digest(path),
            "worker_command": raw["command"], "worker_returncode": raw["exit_code"],
            "status": raw["status"], "wall_seconds": raw["elapsed_seconds"],
            "peak_tree_rss": raw["peak_tree_rss"], "peak_tree_private": raw["peak_tree_private"],
            "peak_artifact_bytes": raw["peak_artifact_bytes"],
            "descendants_after_cleanup": raw.get("remaining_job_processes"),
            "worker_stdout_sha256": digest(log / "stdout.log"),
            "worker_stderr_sha256": digest(log / "stderr.log")}


def run(store, folder, output):
    if psutil.Process().nice() != psutil.NORMAL_PRIORITY_CLASS:
        raise ValueError("the benchmark controller must be at Normal priority")
    contract = read(CONTRACT)
    groups = input_sets(contract)
    history = historical_anchors(contract)
    if list(history) != groups["historical"][0]:
        raise ValueError("historical answer order differs from the pinned R1 query set")
    folder.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    fixture = folder / "fixture"
    environment = dict(os.environ, PYTHONPATH=os.pathsep.join(
        [str(PROJECT / "src"), str(Path(psutil.__file__).resolve().parent.parent)]),
        FINERACT_R2_TEST_ROOT=str(fixture), PYTHONPYCACHEPREFIX=str(folder / "empty-bytecode"))
    git_source = str(store)
    summary = {"experiment": contract["experiment"], "started_utc": timestamp(),
               "r1_baseline": contract["r1_baseline"], "snapshot": contract["snapshot"],
               "contract_sha256": digest(CONTRACT), "query_sets": contract["query_sets"],
               "measurement": contract["measurement"], "work_dir": str(folder),
               "git_store": git_source, "runtime_environment_paths":
               {key: environment[key] for key in ("PYTHONPATH", "PYTHONPYCACHEPREFIX", "FINERACT_R2_TEST_ROOT")},
               "historical_answers": [{"literal": literal, **anchor} for literal, anchor in history.items()],
               "historical_bytes": baseline_files(contract["r1_baseline"]),
               "identity": identities(), "query_runs": [], "progress": []}
    save(folder / "frozen-inputs.json", {key: summary[key] for key in
         ("started_utc", "r1_baseline", "snapshot", "contract_sha256", "query_sets", "measurement", "identity")})

    def finish(phase):
        summary.update(stopped_after=phase, finished_utc=timestamp(),
                       input_bytes_unchanged=(summary["identity"] == identities()
                                              and summary["contract_sha256"] == digest(CONTRACT)
                                              and groups == input_sets(read(CONTRACT))
                                              and summary["historical_bytes"] == baseline_files(contract["r1_baseline"])))
        summary["local_artifact_bytes"] = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file())
        assert not output.exists()
        save(output, summary)
        print(json.dumps({"stopped_after": phase, "query_runs": len(summary["query_runs"]),
                          "report": str(output)}), flush=True)
        return 0 if phase == "complete" and summary["input_bytes_unchanged"] else 1

    summary["tests"] = test_steps(folder, environment)
    if not all(record["passed"] for record in summary["tests"].values()):
        return finish("tests")
    summary["fixture"] = read(fixture / "deleted-posting-evidence.json")
    index = folder / "index.sqlite"
    log = folder / "build-monitor"
    common = ["--git-dir", git_source, "--contract", str(CONTRACT), "--index", str(index)]
    build = invoke([*CLI, "build", *common, "--log-dir", str(log)], folder / "build-cli", environment)
    build_result = read(Path(build["log_directory"]) / "stdout.log")
    build_resources = supervision(log, 300)
    summary["build"] = {**build, "result": build_result, "supervisor": build_resources}
    if (build["returncode"] != 0 or not build_resources["passed"] or build_result["status"] != "BUILT"
            or build_result["build"]["snapshot"] != contract["snapshot"]
            or build_result["build"]["distinct_regular_blobs"] != contract["distinct_regular_blobs"]
            or build_result["index_sha256"] != digest(index)):
        return finish("build")
    print("Fineract R2: tests and supervised build passed", flush=True)
    for label, (literals, repetitions) in groups.items():
        summary["progress"].append({"group": label, "started_utc": timestamp()})
        recorded = []
        for repetition in range(1, repetitions + 1):
            for number, literal in enumerate(literals, 1):
                case = folder / label / f"{repetition:02}-{number:02}"
                case.mkdir(parents=True)
                answer, log = case / "answer", case / "monitor"
                result = invoke([*CLI, "query-verified", *common, f"--literal={literal}",
                                 "--output-dir", str(answer), "--log-dir", str(log)],
                                case / "cli", environment)
                cli = read(case / "cli/stdout.log")
                monitor = supervision(log, 60)
                passed = result["returncode"] == 0 and cli["status"] == "VERIFIED" and monitor["passed"]
                proof_hash = None
                if passed:
                    proof = read(answer / "verification.json")
                    proof_hash = digest(answer / "verification.json")
                    passed = (proof["status"] == "VERIFIED" and proof["literal"] == literal
                              and proof["snapshot"] == contract["snapshot"]
                              and proof["inventory"]["regular_paths"] == contract["snapshot"]["regular_paths"]
                              and proof["inventory"]["distinct_regular_blobs"] == contract["distinct_regular_blobs"]
                              and proof["result_sha256"] == cli["result_sha256"] == digest(answer / "answer.jsonl")
                              and proof["count"] == cli["count"]
                              and proof["contract_sha256"] == summary["contract_sha256"]
                              and result["wall_seconds"] < 60)
                    if label == "historical":
                        passed = passed and (cli["result_sha256"], cli["count"]) == (
                            history[literal]["answer_sha256"], history[literal]["count"])
                record = {"group": label, "repeat": repetition, "position": number, "literal": literal,
                          "passed": passed, "answer_directory": str(answer), "receipt_sha256": proof_hash,
                          **result, "result": cli, "supervisor": monitor}
                summary["query_runs"].append(record)
                recorded.append(record)
        if not all(row["passed"] for row in recorded):
            return finish(label)
        print(f"Fineract R2: {label} verified {len(recorded)} executions", flush=True)
    summary["historical_aggregates"] = []
    for literal in groups["historical"][0]:
        runs = [row for row in summary["query_runs"] if row["group"] == "historical" and row["literal"] == literal]
        phases = {key: stats([row["result"]["seconds"][key] for row in runs])
                  for key in ("search", "matching", "candidate_serialization", "git_scan", "comparison")}
        phases.update(publication=stats([row["result"]["publication_seconds"] for row in runs]),
                      full_cli=stats([row["wall_seconds"] for row in runs]))
        summary["historical_aggregates"].append({"literal": literal, "count": history[literal]["count"],
            "samples": len(runs), "seconds": phases,
            "peak_tree_rss_bytes": stats([row["supervisor"]["peak_tree_rss"] for row in runs])})
    return finish("complete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-dir", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.run_dir.exists() or args.report.exists():
        parser.error("run directory and report must be new")
    return run(args.git_dir.resolve(), args.run_dir.resolve(), args.report.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
