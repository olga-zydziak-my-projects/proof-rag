"""Build shard indexes and atomically publish one Git-verified corpus answer."""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
from time import perf_counter, time_ns
from uuid import uuid4

from fineract_r2 import (
    METHOD, SNAPSHOT_FIELDS, STATUS, StatusParser, new_path, run_supervisor, sha256_file, strict_json, write_json,
)
from repo_proof import git_search
from repo_proof.checked_index import checked_receipt, find_verified
from repo_proof.corpus import encoded
from repo_proof.fineract_delta import update_hits
from repo_proof.fineract_oracle import ResultMismatch, SourceUnavailable, compare_section, scan_git


FORMAT = "git-literal-corpus-v1"
RECEIPT_FORMAT = "git-literal-corpus-verification-v1"
GIB = 1024 ** 3


def read_manifest(path):
    return parse_manifest(path.read_bytes())


def parse_manifest(data):
    manifest = strict_json(data)
    if manifest["format"] != "git-literal-corpus-manifest-v1":
        raise ValueError("invalid corpus manifest format")
    repos = manifest["repositories"]
    if (not repos or len({repo["id"] for repo in repos}) != len(repos)
            or len({repo["snapshot"]["repository"] for repo in repos}) != len(repos)):
        raise ValueError("manifest must list unique repositories")
    for repo in repos:
        pin, directories = repo["snapshot"], repo["directories"]
        if (not re.fullmatch(r"[a-z0-9-]+", repo["id"]) or set(pin) != SNAPSHOT_FIELDS
                or pin["object_format"] != "sha1"
                or any(not re.fullmatch(r"[0-9a-f]{40}", pin[key]) for key in ("commit", "root_tree"))
                or type(directories) is not list or len(set(directories)) != len(directories)
                or any(not re.fullmatch(r"[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*", directory)
                       or set(directory.split("/")) & {".", ".."} for directory in directories)):
            raise ValueError("invalid repository pin or directories in corpus manifest")
    return repos


def counts(repos, sections):
    return [{"repository": repo["snapshot"]["repository"], "count": section["count"]}
            for repo, section in zip(repos, sections, strict=True)]


def header(repos, literal, manifest_hash):
    return {"type": "corpus-result", "format": FORMAT, "manifest_sha256": manifest_hash,
            "literal": literal, "repositories": [repo["snapshot"]["repository"] for repo in repos]}


def trailer(repos, sections):
    return {"type": "corpus-complete", "count": sum(section["count"] for section in sections),
            "repositories": counts(repos, sections)}


def candidate(repos, index, literal, manifest_hash, answer):
    searches = []
    with answer.open("xb") as stream:
        stream.write(encoded(header(repos, literal, manifest_hash)))
        for repo in repos:
            name = repo["id"]
            section_file = answer.parent.parent / f"section-{name}.jsonl"
            try:
                searches.append(git_search.query(index / f"{name}.sqlite", repo["snapshot"], literal,
                                                 section_file, 0, directories=repo["directories"]))
                with section_file.open("rb") as section:
                    shutil.copyfileobj(section, stream)
            finally:
                section_file.unlink(missing_ok=True)
        stream.write(encoded(trailer(repos, searches)))
        stream.flush()
        os.fsync(stream.fileno())
    return searches


def compare_corpus(answer, repos, literal, manifest_hash, expected, *, strict_order=False):
    with answer.open("rb") as stream:
        return compare_corpus_stream(stream, repos, literal, manifest_hash, expected, strict_order=strict_order)


def compare_corpus_stream(stream, repos, literal, manifest_hash, expected, *, strict_order=False):
    if stream.readline() != encoded(header(repos, literal, manifest_hash)):
        raise ResultMismatch("corpus result header differs from the manifest")
    sections = []
    for repo, hits in zip(repos, expected, strict=True):
        try:
            sections.append(compare_section(stream, repo["snapshot"], literal, hits, strict_order=strict_order))
        except ResultMismatch as exc:
            raise ResultMismatch(f"{repo['snapshot']['repository']}: {exc}") from exc
    complete = trailer(repos, sections)
    if stream.readline() != encoded(complete) or stream.read(1):
        raise ResultMismatch("corpus completion record differs from verified sections")
    return complete["count"], complete["repositories"]


def read_verified_base(folder, repos, literal, manifest_hash):
    receipt = strict_json((folder / "verification.json").read_bytes())
    data = (folder / "answer.jsonl").read_bytes()
    published = Path(receipt["output_directory"])
    if (receipt["format"] != RECEIPT_FORMAT or receipt["status"] != "VERIFIED"
            or not published.is_absolute() or not published.samefile(folder) or receipt["literal"] != literal
            or receipt["manifest_sha256"] != manifest_hash or receipt["result_sha256"] != sha256(data).hexdigest()):
        raise ResultMismatch("base answer is not the published, verified result for this manifest and literal")
    by_repo = {repo["snapshot"]["repository"]: {} for repo in repos}
    for line in data.splitlines():
        row = strict_json(line)
        if row["type"] == "hit":
            by_repo[row["repository"]][row["path"]] = (row["blob_id"], row["byte_offset"], row["line"])
    hits = list(by_repo.values())
    count, per_repo = compare_corpus_stream(BytesIO(data), repos, literal, manifest_hash, hits)
    if count != receipt["count"] or per_repo != receipt["repositories"]:
        raise ResultMismatch("base receipt counts differ from the verified answer")
    return hits, receipt["result_sha256"]


def write_delta_answer(answer, repos, literal, manifest_hash, expected):
    with answer.open("xb") as stream:
        stream.write(encoded(header(repos, literal, manifest_hash)))
        sections = []
        for repo, hits in zip(repos, expected, strict=True):
            pin = repo["snapshot"]
            identity = {key: pin[key] for key in ("repository", "commit")}
            stream.write(encoded({"type": "result", "format": git_search.RESULT_FORMAT, **identity,
                                  "root_tree": pin["root_tree"], "literal": literal}))
            for path in sorted(hits, key=lambda value: value.encode("utf-8", "surrogateescape")):
                oid, offset, line = hits[path]
                stream.write(encoded({"type": "hit", **identity, "path": path, "blob_id": oid,
                                      "byte_offset": offset, "line": line}))
            sections.append({"count": len(hits)})
            stream.write(encoded({"type": "complete", **sections[-1]}))
        stream.write(encoded(trailer(repos, sections)))
        stream.flush()
        os.fsync(stream.fileno())


def stage_update(args, repos, manifest_hash, answer):
    started = perf_counter()
    previous = read_manifest(args.base_manifest)
    if len(previous) != len(repos) or any(
        (a["id"], a["directories"], a["snapshot"]["repository"], a["snapshot"]["url"])
        != (b["id"], b["directories"], b["snapshot"]["repository"], b["snapshot"]["url"])
        for a, b in zip(previous, repos)
    ):
        raise ValueError("update requires the same repositories, order and directory scope")
    base_hash = sha256_file(args.base_manifest)
    hits, base_result = read_verified_base(args.base_answer, previous, args.literal, base_hash)
    load_seconds = perf_counter() - started
    started = perf_counter()
    stats = []
    for a, b, by_path in zip(previous, repos, hits, strict=True):
        _, stock = update_hits(args.sources / f"{b['id']}.git", a["snapshot"], b["snapshot"],
                               b["directories"], args.literal, by_path, args.scratch)
        stats.append({"repository": b["snapshot"]["repository"], **stock})
    delta_seconds = perf_counter() - started
    started = perf_counter()
    write_delta_answer(answer, repos, args.literal, manifest_hash, hits)
    count, per_repo = compare_corpus(answer, repos, args.literal, manifest_hash, hits)
    return {"status": "STAGED", "manifest_sha256": manifest_hash, "literal": args.literal,
            "result_sha256": sha256_file(answer), "count": count, "repositories": per_repo,
            "method": "Verified base plus SHA-1 checked pinned Git tree delta and new regular blobs",
            "base_manifest_sha256": base_hash, "base_result_sha256": base_result, "delta": stats,
            "seconds": {"load_verified_base": load_seconds, "git_delta": delta_seconds,
                        "serialization_and_comparison": perf_counter() - started}}


def stage(args):
    repos = read_manifest(args.manifest)
    manifest_hash = sha256_file(args.manifest)
    if manifest_hash != args.manifest_hash:
        raise ValueError("manifest changed before the worker started")
    bundle = args.scratch / "bundle"
    bundle.mkdir()
    result = {"status": "STAGED", "manifest_sha256": manifest_hash}
    if args.task == "build":
        shards = {}
        for repo in repos:
            name = repo["id"]
            db = bundle / f"{name}.sqlite"
            data = git_search.build(args.sources / f"{name}.git", repo["snapshot"], db, directories=repo["directories"])
            if (data["distinct_regular_blobs"] != repo["distinct_regular_blobs"]
                    or data["raw_blob_bytes"] != repo["distinct_regular_blob_bytes"]):
                raise SourceUnavailable("index contents differ from the manifest")
            shards[name] = {**data, "sha256": sha256_file(db)}
        return {**result, "shards": shards}

    answer = bundle / "answer.jsonl"
    if args.task == "update-verified":
        return stage_update(args, repos, manifest_hash, answer)
    start = perf_counter()
    searches = candidate(repos, args.index, args.literal, manifest_hash, answer)
    search = perf_counter() - start
    reads = [{"repository": repo["snapshot"]["repository"], "objects": section["candidate_blobs"],
              "blob_bytes": section["candidate_blob_bytes"]} for repo, section in zip(repos, searches, strict=True)]

    def scan_repository(repo):
        start = perf_counter()
        hits, stock = scan_git(args.sources / f"{repo['id']}.git", repo["snapshot"], repo["distinct_regular_blobs"],
                               args.literal, args.scratch, directories=repo["directories"], include_sizes=True)
        scan_time = perf_counter() - start
        if any(stock[key] != repo[key] for key in ("distinct_regular_blob_bytes", "regular_path_bytes")):
            raise SourceUnavailable("read Git bytes differ from the manifest")
        return hits, {"repository": repo["snapshot"]["repository"], **stock}, scan_time

    start = perf_counter()
    checked = args.task == "query-checked"
    if checked:
        receipt = checked_receipt(args.checked_directory, args.checked_sha256)
        stocks = receipt["repositories"]
        if (receipt["manifest_sha256"] != manifest_hash
                or [stock["id"] for stock in stocks] != [repo["id"] for repo in repos]):
            raise SourceUnavailable("checked index is for a different corpus manifest")
        expected, authenticated = zip(*(find_verified(args.checked_directory, stock, args.literal)
                                        for stock in stocks), strict=True)
        proof = {"checked_index_sha256": args.checked_sha256, "full_git_scans": 0,
                 "verifier_reads": [{"repository": repo["snapshot"]["repository"], **read}
                                    for repo, read in zip(repos, authenticated, strict=True)],
                 "method": "Independently reconciled Git paths and postings; authenticated exact byte verification"}
        timings = {"checked_verification": perf_counter() - start}
    else:
        # Git producers can run concurrently. Consume their results in manifest order.
        with ThreadPoolExecutor(max_workers=min(3, len(repos))) as readers:
            expected, inventories, scan_times = zip(*readers.map(scan_repository, repos), strict=True)
        timings = {"git_scan": perf_counter() - start, "git_scan_per_repository": scan_times}
        proof = {"inventories": inventories, "method": METHOD, "full_git_scans": 1,
                 "git_repositories_scanned": len(repos)}
    proof["candidate_reads"] = reads
    start = perf_counter()
    answer_hash = sha256_file(answer)
    try:
        count, per_repo = compare_corpus(answer, repos, args.literal, manifest_hash, expected, strict_order=checked)
    except ResultMismatch as exc:
        return {"status": "MISMATCH", "reason": str(exc), "candidate_sha256": answer_hash,
                "candidate_counts": counts(repos, searches),
                "git_counts": counts(repos, [{"count": len(hits)} for hits in expected]), **proof}
    return {**result, "literal": args.literal, "result_sha256": answer_hash, "count": count,
            "repositories": per_repo, **proof,
            "seconds": {"search": search, **timings, "comparison": perf_counter() - start}}


def controlled(args):
    import psutil
    from stage8_supervise import directory_bytes

    if sys.platform != "win32" or psutil.Process().nice() != psutil.NORMAL_PRIORITY_CLASS:
        raise ValueError("requires Windows and Normal process priority")
    args.manifest = args.manifest.resolve(strict=True)
    repos = read_manifest(args.manifest)
    digest = sha256_file(args.manifest)
    querying = args.operation != "build"
    if querying and not re.fullmatch(r"[ -~]+", args.literal):
        raise ValueError("literal must be nonempty printable ASCII on one line")
    target = new_path(args.output_dir if querying else args.index)
    log = new_path(args.log_dir)
    if log.is_relative_to(target) or target.is_relative_to(log):
        raise ValueError("log and output locations must be disjoint")
    target.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    limits = {"timeout_seconds": 900 if not querying else 240, "tree_memory_bytes": 3 * GIB,
              "artifact_bytes": 16 * GIB, "sample_seconds": 0.02}
    scratch = target.parent / f".r2-corpus-stage-{uuid4().hex}"
    scratch.mkdir()
    started = perf_counter()
    try:
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "_stage", args.operation,
                   "--manifest", str(args.manifest), "--manifest-hash", digest,
                   "--sources", str(args.sources.resolve()), "--scratch", str(scratch)]
        if querying:
            command.append(f"--literal={args.literal}")
            if args.operation == "update-verified":
                command.extend(("--base-manifest", str(args.base_manifest.resolve()),
                                "--base-answer", str(args.base_answer.resolve())))
            else:
                command.extend(("--index", str(args.index.resolve())))
                if args.operation == "query-checked":
                    command.extend(("--checked-directory", str(args.checked_directory.resolve()),
                                    "--checked-sha256", args.checked_sha256))
        code, resources = run_supervisor(command, scratch, limits)
        os.rename(scratch / "monitor", log)
        payload = (log / "stdout.log").read_bytes()
        response = strict_json(payload) if payload else {}
        if (resources["status"] == "FAILED" and resources["remaining_job_processes"] == 0
                and resources["exit_code"] == STATUS.get(response.get("status"))
                and response.get("status") in ("MISMATCH", "BLOCKED", "ERROR")):
            return response
        if (code or resources["status"] != "PROCESS_PASS" or resources["exit_code"] != 0
                or resources["remaining_job_processes"] != 0 or response.get("status") != "STAGED"
                or response.get("manifest_sha256") != digest or sha256_file(args.manifest) != digest):
            raise ValueError(f"supervised corpus worker did not complete: {resources['status']}")
        published = perf_counter()
        bundle = scratch / "bundle"
        if querying:
            if (response["literal"] != args.literal
                    or sha256_file(bundle / "answer.jsonl") != response["result_sha256"]):
                raise ResultMismatch("staged corpus answer changed after verification")
            write_json(bundle / "verification.json", {**response, "format": RECEIPT_FORMAT, "status": "VERIFIED",
                       "output_directory": str(target)})
        else:
            for repo in repos:
                name = repo["id"]
                if sha256_file(bundle / f"{name}.sqlite") != response["shards"][name]["sha256"]:
                    raise ValueError("staged index changed")
        if directory_bytes(scratch) + directory_bytes(log) > limits["artifact_bytes"]:
            raise ValueError("artifact limit exceeded before publication")
        if perf_counter() - started >= limits["timeout_seconds"]:
            raise ValueError("time limit exceeded before publication")
        previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            os.rename(bundle, target)
            if querying:
                response["published_unix_ns"] = time_ns()
            response.update(status="VERIFIED" if querying else "BUILT", output_directory=str(target),
                            publication_seconds=perf_counter() - published)
        finally:
            signal.signal(signal.SIGINT, previous)
        return response
    finally:
        # Only remove this invocation's newly created work directory.
        if scratch.resolve().parent == target.parent and scratch.name.startswith(".r2-corpus-stage-"):
            try:
                shutil.rmtree(scratch)
            except OSError as exc:
                print(f"R2 corpus temporary directory cleanup ({scratch}): {exc}", file=sys.stderr)


def main(argv=None):
    parser = StatusParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    build = commands.add_parser("build")
    query = commands.add_parser("query-verified")
    checked = commands.add_parser("query-checked")
    update = commands.add_parser("update-verified")
    for command in (query, checked, update):
        command.add_argument("--literal", required=True)
        command.add_argument("--output-dir", required=True, type=Path)
    worker = commands.add_parser("_stage")
    worker.add_argument("task", choices=("build", "query-verified", "query-checked", "update-verified"))
    worker.add_argument("--scratch", required=True, type=Path)
    worker.add_argument("--manifest-hash", required=True)
    worker.add_argument("--literal")
    for command in (update, worker):
        command.add_argument("--base-manifest", required=command is update, type=Path)
        command.add_argument("--base-answer", required=command is update, type=Path)
    for command in (checked, worker):
        command.add_argument("--checked-directory", type=Path, required=command is checked)
        command.add_argument("--checked-sha256", required=command is checked)
    for command in (build, query, checked, update, worker):
        command.add_argument("--sources", required=True, type=Path)
        command.add_argument("--manifest", required=True, type=Path)
        if command is not update:
            command.add_argument("--index", type=Path, required=command is not worker)
        if command is not worker:
            command.add_argument("--log-dir", required=True, type=Path)
    try:
        args = parser.parse_args(argv)
        result = stage(args) if args.operation == "_stage" else controlled(args)
    except ResultMismatch as exc:
        result = {"status": "MISMATCH", "reason": str(exc)}
    except (SourceUnavailable, git_search.SnapshotError) as exc:
        result = {"status": "BLOCKED", "reason": str(exc)}
    except KeyboardInterrupt:
        result = {"status": "ERROR", "reason": "interrupted"}
    except (ImportError, OSError, ValueError, TypeError, KeyError, sqlite3.Error, subprocess.SubprocessError) as exc:
        result = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return 0 if result["status"] == "STAGED" else STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
