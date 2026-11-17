"""Run the frozen pilot through the public CLI and retain its measurements."""

import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
from time import perf_counter


PROJECT = Path(__file__).resolve().parents[1]
CONTRACT = PROJECT / "docs/fineract-r1-contract.json"
CLI = [sys.executable, "-m", "repo_proof.git_search"]
ORACLE = [sys.executable, str(PROJECT / "scripts/verify_fineract_r1.py")]


def write_json(path, value):
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("ascii"))


def invoke(command, log):
    start = perf_counter()
    run = subprocess.run([str(arg) for arg in command], capture_output=True, cwd=PROJECT,
                         env=dict(os.environ, PYTHONPATH=str(PROJECT / "src")))
    elapsed = perf_counter() - start
    if run.stderr:
        log.with_suffix(".stderr.log").write_bytes(run.stderr)
    log.write_bytes(run.stdout)
    return run.returncode, json.loads(run.stdout) if run.stdout else {}, elapsed


def build_attempt(store, spec, index, log):
    return invoke([*CLI, "build", "--git-dir", store, "--contract", spec, "--index", index], log)


def query_attempt(spec, index, literal, output, log, preview=1):
    return invoke([*CLI, "query", "--contract", spec, "--index", index,
                   f"--literal={literal}", "--output", output, "--preview", preview], log)


def verify_attempt(store, spec, results, log):
    return invoke([*ORACLE, "--git-dir", store, "--contract", spec, "--result-dir", results], log)


def controls(folder):
    folder.mkdir()
    store, index = folder / "fixture.git", folder / "fixture.sqlite"
    subprocess.run(["git", "init", "--bare", "--object-format=sha1", str(store)],
                   check=True, capture_output=True)
    git_env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                   GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_EMAIL="fixture@example.invalid",
                   GIT_AUTHOR_DATE="2000-01-01T00:00:00Z",
                   GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")

    def git(*args, data=None):
        return subprocess.run(["git", "-C", str(store), *args], input=data, capture_output=True,
                              env=git_env, check=True).stdout.strip()

    blob = git("hash-object", "-w", "--stdin", data=b"header\r\n\x00Needle and Needle.\n")
    final = git("hash-object", "-w", "--stdin", data=b"x\nNeedle")
    link = git("hash-object", "-w", "--stdin", data=b"Needle")
    tree = git("mktree", "-z", data=b"".join([
        b"100644 blob " + blob + b"\tbinary.bin\0",
        b"100755 blob " + blob + b"\tcopy.bin\0",
        b"100644 blob " + final + b"\tfinal.txt\0",
        b"120000 blob " + link + b"\tsymlink\0",
    ]))
    commit = git("commit-tree", tree.decode("ascii"), "-m", "literal search fixture")
    pin = {"repository": "local/literal-search-fixture", "url": store.as_uri(),
           "object_format": "sha1", "commit": commit.decode("ascii"),
           "root_tree": tree.decode("ascii"), "blob_paths": 4, "regular_paths": 3,
           "symlinks": 1, "gitlinks": 0}
    literals = ["Needle", ".", "NEEDLE"]
    spec = folder / "contract.json"
    write_json(spec, {"snapshot": pin, "queries": literals})
    correct = folder / "correct"
    correct.mkdir()
    code, build, _ = build_attempt(store, spec, index, folder / "build.json")
    if code:
        return {"passed": False, "build_exit": code}
    for number, literal in enumerate(literals, 1):
        code, _, _ = query_attempt(spec, index, literal, correct / f"{number:02d}.jsonl",
                                   folder / f"query-{number:02d}.json")
        if code:
            return {"passed": False, "query_exit": code, "literal": literal}

    result = correct / "01.jsonl"
    rows = [json.loads(row) for row in result.read_bytes().splitlines()]
    by_path = {row["path"]: (row["blob_id"], row["byte_offset"], row["line"])
               for row in rows[1:-1]}
    expected = {"binary.bin": (blob.decode("ascii"), 9, 2),
                "copy.bin": (blob.decode("ascii"), 9, 2),
                "final.txt": (final.decode("ascii"), 2, 2)}
    code, original, _ = verify_attempt(store, spec, correct, folder / "verify-correct.json")
    shifted = [rows[0], {**rows[1], "byte_offset": 20}, *rows[2:]]
    omitted = [rows[0], *rows[2:-1], {"type": "complete", "count": 2}]
    rejections = {}
    for name, changed in (("shifted-offset", shifted), ("omitted-path", omitted)):
        altered = folder / name
        shutil.copytree(correct, altered)
        with (altered / "01.jsonl").open("w", encoding="ascii", newline="\n") as stream:
            for row in changed:
                stream.write(json.dumps(row) + "\n")
        bad_code, report, _ = verify_attempt(store, spec, altered, folder / f"verify-{name}.json")
        first = report.get("queries", [{}])[0]
        rejections[name] = {"rejected": bad_code == 1 and first.get("agrees") is False,
                            "comparison": first}
    checks = {"known_witnesses": by_path == expected, "deduplicated_blobs":
              build["distinct_regular_blobs"] == 2, "correct_result_accepted": code == 0,
              "shifted_offset_rejected": rejections["shifted-offset"]["rejected"],
              "omitted_path_rejected": rejections["omitted-path"]["rejected"]}
    return {"passed": all(checks.values()), "checks": checks, "fixture_snapshot": pin,
            "known_witnesses": by_path, "verification": original, "tampering": rejections}


def hardware():
    cpu = platform.processor()
    memory = None
    if sys.platform == "win32":
        import ctypes
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
        kib = ctypes.c_ulonglong()
        if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(kib)):
            memory = kib.value * 1024
    elif hasattr(os, "sysconf"):
        memory = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    return {"cpu": cpu, "logical_cpus": os.cpu_count(), "physical_memory_bytes": memory,
            "platform": platform.platform(), "python": platform.python_version(),
            "git": subprocess.check_output(["git", "--version"], text=True).strip(),
            "sqlite": sqlite3.sqlite_version}


def preserve(source, target):
    with source.open("rb") as raw, target.open("wb") as packed:
        with gzip.GzipFile(filename="", fileobj=packed, mode="wb", mtime=0) as stream:
            shutil.copyfileobj(raw, stream)


def run(store, work, evidence, warm_passes, manifest_status):
    work.mkdir(parents=True)
    evidence.mkdir(parents=True)
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    summary = {
        "experiment": contract["experiment"],
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "contract_sha256": sha256(contract_bytes).hexdigest(),
        "hardware": hardware(),
        "optional_manifest_crosscheck": manifest_status,
        "measurement": {
            "build": "Inventory through atomic index publication; excludes network fetch.",
            "match_seconds": "From opening the read-only SQLite index through exact blob matching.",
            "output_seconds": "Path traversal, preview collection, JSONL serialization, fsync and atomic publication.",
            "cli_wall_seconds": "Fresh Python process including startup, queries, result serialization and stdout.",
            "peak_rss_bytes": "Per-process peak working set or RSS; excludes child Git processes.",
            "cache": "First query pass on the just-built index, OS file cache not cleared. Warm passes immediately follow in the same order, with fresh CLI processes.",
        },
        "queries": [],
    }

    def finish(verdict, reason=None):
        summary.update(verdict=verdict, finished_utc=datetime.now(timezone.utc).isoformat())
        if reason:
            summary["reason"] = reason
        write_json(evidence / "summary.json", summary)
        print(json.dumps({"verdict": verdict, "agreements": summary.get("agreements"),
                          "summary": str(evidence / "summary.json")}))
        return {"PASS": 0, "FAIL": 1, "BLOCKED": 3}[verdict]

    summary["controls"] = controls(work / "controls")
    index = work / "index.sqlite"
    code, build, elapsed = build_attempt(store, CONTRACT, index, work / "build.json")
    summary["build"] = {**build, "cli_wall_seconds": elapsed, "exit_code": code}
    if code:
        log = work / "build.stderr.log"
        reason = log.read_text(encoding="utf-8", errors="replace").strip() if log.exists() else ""
        return finish("BLOCKED" if code == 3 else "FAIL", reason or f"build exited {code}")

    literals = contract["queries"]
    summary["queries"] = [{"literal": literal, "first": None, "warm": []} for literal in literals]
    first_dir = work / "first"
    reliable_repeats = True
    for pass_number in range(warm_passes + 1):
        result_dir = first_dir if pass_number == 0 else work / f"warm-{pass_number:02d}"
        result_dir.mkdir()
        for number, row in enumerate(summary["queries"], 1):
            path = result_dir / f"{number:02d}.jsonl"
            code, receipt, wall = query_attempt(CONTRACT, index, row["literal"], path,
                                                result_dir / f"{number:02d}-query.json")
            record = {**receipt, "cli_wall_seconds": wall, "exit_code": code}
            if not code:
                record["result_sha256"] = sha256(path.read_bytes()).hexdigest()
            if pass_number == 0:
                row["first"] = record
                if not code:
                    artifact = evidence / f"{number:02d}.jsonl.gz"
                    preserve(path, artifact)
                    row["result_file"] = artifact.name
                    row["gzip_sha256"] = sha256(artifact.read_bytes()).hexdigest()
            else:
                record["matches_first_result"] = (not code and row["first"].get("result_sha256")
                                                  == record["result_sha256"])
                reliable_repeats &= record["matches_first_result"]
                row["warm"].append(record)

    code, verified, wall = verify_attempt(store, CONTRACT, evidence, evidence / "verification.json")
    summary["independent_verification"] = {**verified, "cli_wall_seconds": wall}
    summary["agreements"] = verified.get("agreements")
    if code == 3:
        return finish("BLOCKED", verified.get("reason"))
    counts = [row["first"].get("count") for row in summary["queries"]]
    coverage = verified.get("inventory", {})
    passed = (code == 0 and summary["agreements"] == 8
              and build["path_and_blob_sets_reconciled"] and build["regular_paths"] == 8635
              and coverage.get("regular_paths") == 8635
              and coverage.get("distinct_regular_blobs") == build["distinct_regular_blobs"]
              and 0 in counts and any(count for count in counts if count is not None)
              and summary["controls"]["passed"] and reliable_repeats)
    return finish("PASS" if passed else "FAIL")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--warm-passes", type=int, default=3)
    parser.add_argument("--manifest-status", default="not_found")
    args = parser.parse_args()
    if args.warm_passes < 1:
        parser.error("--warm-passes must be positive")
    if args.work_dir.exists() or args.evidence_dir.exists():
        parser.error("work and evidence directories must be new")
    return run(args.git_dir.resolve(), args.work_dir.resolve(), args.evidence_dir.resolve(),
               args.warm_passes, args.manifest_status)


if __name__ == "__main__":
    raise SystemExit(main())
