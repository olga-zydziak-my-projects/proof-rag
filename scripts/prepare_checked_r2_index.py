"""Publish a shared verifier after reconciling the complete search index with Git."""

from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event, Thread
from time import perf_counter

import psutil

from fineract_r2 import STATUS, StatusParser, new_path, sha256_file, write_json
from fineract_r2_corpus import parse_manifest
from repo_proof.checked_index import FORMAT, checked_receipt, immutable_bytes, reconcile_shard
from repo_proof.fineract_oracle import SourceUnavailable


def trusted_bundle(directory, anchor):
    receipt = checked_receipt(directory, anchor)
    raw = (directory / "manifest.json").read_bytes()
    if sha256(raw).hexdigest() != receipt["manifest_sha256"]:
        raise SourceUnavailable("checked index manifest SHA-256 differs from the receipt")
    repositories = parse_manifest(raw)
    if [row["id"] for row in repositories] != [row["id"] for row in receipt["repositories"]]:
        raise SourceUnavailable("checked index receipt has a different repository list")
    return repositories, receipt


def prepare(sources, manifest, index, output, *, reuse=None):
    started = perf_counter()
    output = new_path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_bytes = manifest.read_bytes()
    repos = parse_manifest(manifest_bytes)
    manifest_hash = sha256(manifest_bytes).hexdigest()
    previous = {}
    if reuse is not None:
        old_repos, receipt = trusted_bundle(*reuse)
        previous = {repo["id"]: (repo, stock)
                    for repo, stock in zip(old_repos, receipt["repositories"], strict=True)}
    stop = Event()
    peak_rss = 0

    def sample():
        nonlocal peak_rss
        parent = psutil.Process()
        while not stop.is_set():
            rss = 0
            for process in [parent, *parent.children(recursive=True)]:
                try:
                    rss += process.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            peak_rss = max(peak_rss, rss)
            stop.wait(0.05)

    monitor = Thread(target=sample)
    monitor.start()
    try:
        with TemporaryDirectory(prefix=".checked-", dir=output.parent) as scratch:
            bundle = Path(scratch) / "index"
            bundle.mkdir()
            stock, phases, reused, rebuilt = [], {}, [], []
            for repo in repos:
                name = repo["id"]
                begin = perf_counter()
                old, existing = previous.get(name, (None, None))
                if old == repo:
                    for suffix in ("grams", "objects", "sqlite"):
                        artifact = reuse[0] / f"{name}.{suffix}"
                        if suffix != "sqlite" and sha256_file(artifact) != existing[f"{suffix}_sha256"]:
                            raise SourceUnavailable(f"checked catalog changed: {artifact}")
                        os.link(artifact, bundle / artifact.name)
                    stock.append(existing)
                    reused.append(name)
                else:
                    stock.append(reconcile_shard(repo, sources / f"{name}.git", index / f"{name}.sqlite", bundle))
                    rebuilt.append(name)
                phases[name] = perf_counter() - begin
                action = "reused checked shard" if name in reused else "checked paths, objects and postings"
                print(f"{name}: {action} in {phases[name]:.3f} s", file=sys.stderr, flush=True)
            immutable_bytes(bundle / "manifest.json", manifest_bytes)
            write_json(bundle / "receipt.json", {"format": FORMAT, "manifest_sha256": manifest_hash,
                                                 "repositories": stock})
            identity = sha256_file(bundle / "receipt.json")
            size = sum(path.stat().st_size for path in bundle.iterdir())
            os.rename(bundle, output)
    finally:
        stop.set()
        monitor.join()
    return {"status": "VERIFIED", "directory": str(output), "receipt_sha256": identity, "manifest_sha256": manifest_hash,
            "seconds": perf_counter() - started, "repository_seconds": phases, "bytes": size,
            "peak_tree_rss_bytes": peak_rss, "sample_interval_seconds": 0.05, "repositories": stock,
            "reused_repositories": reused, "reconciled_repositories": rebuilt}


def main():
    parser = StatusParser(description=__doc__)
    for flag in ("sources", "manifest", "index", "output"):
        parser.add_argument("--" + flag, type=Path, required=True)
    try:
        args = parser.parse_args()
        result = prepare(args.sources, args.manifest, args.index, args.output)
    except SourceUnavailable as exc:
        result = {"status": "BLOCKED", "reason": str(exc)}
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        result = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
