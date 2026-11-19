"""Handle a local pull_request event and publish a refreshed checked PR index."""

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from time import perf_counter, time_ns
from uuid import uuid4

from fineract_r2 import STATUS, StatusParser, strict_json, write_json
from fineract_r2_current import (
    DEFAULT_CONFIG, FreshnessError, R2Error, collect_repositories, corpus_entry, git, index_for,
    latest_transaction, manifest_for, matching_checked_manifest, publish_pr, read_latest, registered_pr, selected_heads,
    settings, validate_pr_number,
)
from prepare_checked_r2_index import prepare, trusted_bundle
from repo_proof.fineract_oracle import SourceUnavailable


def register(path, entry, corpus, event):
    repository = event.get("repository")
    if repository is None:
        raise ValueError("Zdarzenie opened wymaga pola repository")
    _, repositories, _, _ = settings(path, entry, corpus)
    repo = next((item for item in repositories if item["id"] == repository), None)
    if repo is None:
        raise ValueError(f"Repozytorium {repository!r} nie należy do korpusu {corpus!r}")
    if repo["branch"] != event["base"] or event["base"] == event["head"]:
        raise ValueError("PR event must identify a configured base and a different head branch")
    git(None, "check-ref-format", "refs/heads/" + event["head"])
    view = {"number": event["number"], "corpus": corpus,
            **{key: event[key] for key in ("repository", "base", "head")}}
    base_head, pr_head = selected_heads([repo, {**repo, "branch": event["head"]}])
    room, view = publish_pr(path, entry, view)
    return (room, view), {"status": "REGISTERED", "view": view, "view_directory": str(room),
                          "base_head": base_head, "pr_head": pr_head}


def refresh(path, entry, corpus, selected_pr):
    started = perf_counter()
    _, repositories, seed, previous = settings(path, entry, corpus, selected_pr=selected_pr)
    if previous is None:
        raise ValueError("PR refresh requires a configured checked baseline")
    room, _ = selected_pr
    ready_path = room / "ready.json"
    existing = read_latest(ready_path)
    if existing:
        previous_release = room / "r" / existing["release"]
        previous = previous_release / "checked", existing["receipt_sha256"]
        seed = previous_release / "index"
    heads = selected_heads(repositories)
    if matching_checked_manifest(previous, repositories, heads) is not None:
        return {"status": "READY", "already_ready": True, "selection": heads, "receipt_sha256": previous[1]}

    pinned, _ = trusted_bundle(*previous)
    release = room / "r" / uuid4().hex
    release.mkdir(parents=True)
    sources = room / "worker" / "sources"
    manifest = release / "manifest.json"
    stage = perf_counter()
    new, downloads = collect_repositories(sources, repositories, heads, {row["id"]: row for row in pinned})
    write_json(manifest, manifest_for(new))
    preparation_seconds = perf_counter() - stage
    stage = perf_counter()
    index = index_for(release, sources, new, seed)
    index_seconds = perf_counter() - stage
    verified = prepare(sources, manifest, index, release / "checked", reuse=previous)
    reused_candidates, rebuilt_candidates = [], []
    for repo in new:
        shard = repo["id"] + ".sqlite"
        if (index / shard).samefile(seed / shard):
            reused_candidates.append(repo["id"])
        else:
            rebuilt_candidates.append(repo["id"])
    candidate_bytes = sum((index / f"{name}.sqlite").stat().st_size for name in rebuilt_candidates)
    checked_bytes = sum((release / "checked" / f"{name}.{suffix}").stat().st_size
                        for name in verified["reconciled_repositories"] for suffix in ("sqlite", "grams", "objects"))
    ready = {"release": release.name, "receipt_sha256": verified["receipt_sha256"],
             "manifest_sha256": verified["manifest_sha256"]}
    temporary = room / f"{release.name}.tmp"
    try:
        write_json(temporary, ready)
        with latest_transaction(ready_path):
            confirmed = selected_heads(repositories)
            if [row["commit"] for row in confirmed] != [row["commit"] for row in heads]:
                raise FreshnessError("PR advanced during preparation; its earlier index was not activated")
            os.replace(temporary, ready_path)
            published = time_ns()
    finally:
        temporary.unlink(missing_ok=True)
    return {"status": "READY", **ready, "selection": heads, "ready_unix_ns": published,
            "seconds": perf_counter() - started, "manifest_and_fetch_seconds": preparation_seconds,
            "candidate_index_seconds": index_seconds, "downloads": downloads, "verification": verified,
            "candidate_directory": str(index), "candidate_reused": reused_candidates,
            "candidate_rebuilt": rebuilt_candidates, "candidate_rebuilt_bytes": candidate_bytes,
            "verifier_rebuilt_bytes": checked_bytes}


def receive(config, corpus, event):
    action = event["action"]
    if action not in ("opened", "synchronize"):
        raise ValueError("Expected pull_request action opened or synchronize")
    path, entry = corpus_entry(config, corpus)
    number = event["number"]
    if action == "synchronize":
        selected_pr = registered_pr(path, entry, corpus, number, event.get("repository"))
        room, _ = selected_pr
        with latest_transaction(room / "events.json"):
            return refresh(path, entry, corpus, selected_pr)

    validate_pr_number(number)
    selected_pr, registration = register(path, entry, corpus, event)
    if "checked_index" in entry:
        room, _ = selected_pr
        with latest_transaction(room / "events.json"):
            registration["refresh"] = refresh(path, entry, corpus, selected_pr)
    return registration


def main():
    parser = StatusParser(description=__doc__)
    parser.add_argument("operation", choices=["event"])
    parser.add_argument("--corpus", default="default")
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("REPO_PROOF_CURRENT_CONFIG", DEFAULT_CONFIG)))
    try:
        args = parser.parse_args()
        result = receive(args.config, args.corpus, strict_json(sys.stdin.buffer.read()))
    except R2Error as exc:
        result = exc.result
    except (FreshnessError, SourceUnavailable) as exc:
        result = {"status": "BLOCKED", "reason": str(exc)}
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        result = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return 0 if result["status"] in ("REGISTERED", "READY") else STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
