"""Build an index or publish a Git-verified literal search answer on Windows."""

import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
from time import perf_counter
from uuid import uuid4


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from repo_proof import git_search
from repo_proof.fineract_oracle import (
    ResultMismatch, SourceUnavailable, compare, scan_git, strict_json,
)


STATUS = {"VERIFIED": 0, "BUILT": 0, "MISMATCH": 2, "BLOCKED": 3, "ERROR": 4}
METHOD = "SHA-1 checked Git commit, raw trees and all regular blobs; independent escaped-byte pattern; strict complete JSONL comparison"
SNAPSHOT_FIELDS = {"repository", "url", "object_format", "commit", "root_tree",
                   "blob_paths", "regular_paths", "symlinks", "gitlinks"}


def sha256_file(path):
    digest = sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def write_json(path, data):
    with path.open("xb") as stream:
        stream.write((json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode("ascii"))
        stream.flush()
        os.fsync(stream.fileno())


def read_contract(path):
    raw = path.read_bytes()
    contract = strict_json(raw)
    if type(contract) is not dict or type(contract.get("contract_version")) is not int \
            or contract["contract_version"] != 2:
        raise ValueError("expected a version 2 trusted literal search contract")
    pin = contract["snapshot"]
    if (type(pin) is not dict or set(pin) != SNAPSHOT_FIELDS or pin["object_format"] != "sha1"
            or any(type(pin[key]) is not str or not pin[key] for key in ("repository", "url"))
            or any(type(pin[key]) is not str or not re.fullmatch(r"[0-9a-f]{40}", pin[key])
                   for key in ("commit", "root_tree"))
            or any(type(pin[key]) is not int or pin[key] < 0 for key in
                   ("blob_paths", "regular_paths", "symlinks", "gitlinks"))
            or pin["blob_paths"] != pin["regular_paths"] + pin["symlinks"]):
        raise ValueError("invalid pinned Git snapshot")
    distinct = contract["distinct_regular_blobs"]
    if type(distinct) is not int or not 0 <= distinct <= pin["regular_paths"]:
        raise ValueError("invalid count of distinct regular Git blobs")
    return pin, distinct, sha256(raw).hexdigest()


def stage(args):
    pin, distinct, contract_hash = read_contract(args.contract)
    if contract_hash != args.contract_hash:
        raise ValueError("contract changed between controller and worker")
    if args.operation == "build":
        build = git_search.build(args.git_dir, pin, args.scratch / "index.sqlite")
        if build["distinct_regular_blobs"] != distinct:
            raise SourceUnavailable("built index differs from the contracted unique blob count")
        return {"status": "STAGED", "build": build, "contract_sha256": contract_hash,
                "index_sha256": sha256_file(args.scratch / "index.sqlite")}

    bundle = args.scratch / "bundle"
    bundle.mkdir()
    answer = bundle / "answer.jsonl"
    started = perf_counter()
    search = git_search.query(args.index, pin, args.literal, answer, preview_limit=0)
    search_seconds = perf_counter() - started
    started = perf_counter()
    expected, inventory = scan_git(args.git_dir, pin, distinct, args.literal, args.scratch)
    scan_seconds = perf_counter() - started
    started = perf_counter()
    comparison = compare(answer, pin, args.literal, expected)
    return {"status": "STAGED", **comparison, "contract_sha256": contract_hash,
            "snapshot": pin, "literal": args.literal, "inventory": inventory, "method": METHOD,
            "seconds": {"search": search_seconds, "matching": search["match_seconds"],
                        "candidate_serialization": search["output_seconds"],
                        "git_scan": scan_seconds, "comparison": perf_counter() - started},
            "search_method": search["method"], "candidate_blobs": search["candidate_blobs"]}


def new_path(path):
    target = path.absolute()
    target = target.parent.resolve() / target.name
    if os.path.lexists(target):
        raise ValueError(f"path already exists: {target}")
    return target


def run_supervisor(command, scratch, limits):
    import stage8_supervise

    config = scratch / "limits.json"
    log = scratch / "monitor"
    write_json(config, {"limits": limits})
    original = sys.argv
    try:
        sys.argv = [str(PROJECT / "scripts/stage8_supervise.py"), "--config", str(config),
                    "--run-dir", str(log), "--artifact-root", str(scratch), "--", *command]
        with redirect_stdout(io.StringIO()):
            code = stage8_supervise.main()
    finally:
        sys.argv = original
    return code, strict_json((log / "resource-report.json").read_bytes())


def controlled(args):
    if sys.platform != "win32":
        raise ValueError("the public R2 command requires Windows Job Objects")
    import psutil
    if psutil.Process().nice() != psutil.NORMAL_PRIORITY_CLASS:
        raise ValueError("run Fineract R2 at Normal priority")
    args.contract = args.contract.resolve(strict=True)
    pin, distinct, contract_hash = read_contract(args.contract)
    store = args.git_dir.resolve()
    if not store.is_dir():
        raise SourceUnavailable("Git store directory is unavailable")
    querying = args.operation == "query-verified"
    if querying and not re.fullmatch(r"[ -~]+", args.literal):
        raise ValueError("literal must be nonempty printable ASCII on one line")
    target = new_path(args.output_dir if querying else args.index)
    log = new_path(args.log_dir) if args.log_dir else None
    if log and (log.is_relative_to(target) or target.is_relative_to(log)):
        raise ValueError("log and output locations must be disjoint")
    max_seconds = 60 if querying else 300
    timeout = args.timeout if args.timeout is not None else max_seconds
    if not math.isfinite(timeout) or not 0 < timeout <= max_seconds:
        raise ValueError(f"timeout must be positive and at most {max_seconds} seconds")
    limits = {"timeout_seconds": timeout, "tree_memory_bytes": 2 * 1024 ** 3,
              "artifact_bytes": 4 * 1024 ** 3, "sample_seconds": 0.02}
    start = perf_counter()
    target.parent.mkdir(parents=True, exist_ok=True)
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
    scratch = target.parent / f".fineract-r2-stage-{uuid4().hex}"
    scratch.mkdir()
    try:
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "_stage",
                   args.operation, "--git-dir", str(store), "--contract", str(args.contract),
                   "--contract-hash", contract_hash, "--scratch", str(scratch)]
        if querying:
            command.extend(("--index", str(args.index.resolve()), f"--literal={args.literal}"))
        monitor_code, resources = run_supervisor(command, scratch, limits)
        monitor = scratch / "monitor"
        if log:
            os.rename(monitor, log)
            monitor = log
        stdout = (monitor / "stdout.log").read_bytes()
        worker = strict_json(stdout) if stdout and resources["status"] in ("PROCESS_PASS", "FAILED") else {}
        if (resources["status"] == "FAILED" and resources.get("remaining_job_processes") == 0
                and resources.get("exit_code") == STATUS.get(worker.get("status"))
                and worker.get("status") in ("MISMATCH", "BLOCKED", "ERROR")):
            return worker
        if (monitor_code or resources["status"] != "PROCESS_PASS"
                or resources["exit_code"] != 0 or resources.get("remaining_job_processes") != 0
                or worker.get("status") != "STAGED" or worker.get("contract_sha256") != contract_hash):
            return {"status": "ERROR", "reason": f"supervised worker did not complete: {resources['status']}"}

        publication = perf_counter()
        if querying:
            bundle = scratch / "bundle"
            if (worker["snapshot"] != pin or worker["literal"] != args.literal
                    or worker["inventory"]["distinct_regular_blobs"] != distinct
                    or sha256_file(bundle / "answer.jsonl") != worker["result_sha256"]):
                raise ResultMismatch("staged answer differs from the verified bytes or pinned scope")
            proof = {key: worker[key] for key in
                     ("snapshot", "literal", "inventory", "method", "contract_sha256",
                      "result_sha256", "count")}
            write_json(bundle / "verification.json", {"format": "fineract-r2-verification-v1",
                       "status": "VERIFIED", "output_directory": str(target), **proof})
            staged = bundle
        else:
            staged = scratch / "index.sqlite"
            if sha256_file(staged) != worker["index_sha256"]:
                raise ValueError("staged index hash differs from the build")
        from stage8_supervise import directory_bytes
        if directory_bytes(scratch) + (directory_bytes(log) if log else 0) > limits["artifact_bytes"]:
            raise ValueError("artifact limit exceeded before publication")
        if perf_counter() - start >= timeout:
            raise ValueError("timeout before publication")

        # Both paths are on the same volume. Windows rename refuses clobbering
        # an existing destination, including one created after validation.
        # The CLI restores the handler after reporting the committed outcome.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        os.rename(staged, target)
        worker.update(status="VERIFIED" if querying else "BUILT", path=str(target),
                      publication_seconds=perf_counter() - publication,
                      controller_seconds=perf_counter() - start)
        return worker
    finally:
        # This directory belongs to this invocation. After rename the published
        # bundle is outside it, including if metadata cleanup fails.
        try:
            shutil.rmtree(scratch)
        except OSError as exc:
            print(f"R2 temporary directory cleanup: {exc}", file=sys.stderr)


class StatusParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def dispatch(argv):
    parser = StatusParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    build = commands.add_parser("build")
    search = commands.add_parser("query-verified")
    search.add_argument("--literal", required=True)
    search.add_argument("--output-dir", type=Path, required=True)
    for command in (build, search):
        command.add_argument("--git-dir", type=Path, required=True)
        command.add_argument("--contract", type=Path, required=True)
        command.add_argument("--index", type=Path, required=True)
        command.add_argument("--log-dir", type=Path)
        command.add_argument("--timeout", type=float, help="lower the default wall-clock limit")
    worker = commands.add_parser("_stage")
    worker.add_argument("task", choices=("query-verified", "build"))
    worker.add_argument("--contract", type=Path, required=True)
    worker.add_argument("--git-dir", type=Path, required=True)
    worker.add_argument("--scratch", type=Path, required=True)
    worker.add_argument("--contract-hash", required=True)
    worker.add_argument("--index", type=Path)
    worker.add_argument("--literal")
    try:
        args = parser.parse_args(argv)
        if args.operation == "_stage":
            args.operation = args.task
            result = stage(args)
        else:
            result = controlled(args)
    except ResultMismatch as exc:
        result = {"status": "MISMATCH", "reason": str(exc)}
    except (SourceUnavailable, git_search.SnapshotError) as exc:
        result = {"status": "BLOCKED", "reason": str(exc)}
    except KeyboardInterrupt:
        result = {"status": "ERROR", "reason": "interrupted before completed publication"}
    except (OSError, ValueError, TypeError, KeyError, ImportError, sqlite3.Error,
            subprocess.SubprocessError) as exc:
        result = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return 0 if result["status"] == "STAGED" else STATUS[result["status"]]


def main(argv=None):
    previous = signal.getsignal(signal.SIGINT)
    try:
        return dispatch(argv)
    finally:
        signal.signal(signal.SIGINT, previous)


if __name__ == "__main__":
    raise SystemExit(main())
