"""Exercise Electron #1 and Brave Core #1 against the same pinned local corpus."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Barrier
from time import perf_counter
from uuid import uuid4

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_current import R2, git, pr_room
from measure_r2_concurrency import max_overlap, request
from prepare_checked_r2_index import trusted_bundle
from run_r2_freshness_experiment import CURRENT, bare, call, read, require
from run_r2_pr_experiment import PR_BRANCH, check_answer, event_process


REPOS = ("electron", "brave-core")
FILES = {"electron": "electron-pr-only.txt", "brave-core": "brave-pr-only.txt"}
SECOND = "electron-pr-second.txt"
HIT_REPOS = {"electron": "electron/electron", "brave-core": "brave/brave-core"}


def git_text(store, *args, data=None):
    return git(store, *args, data=data).decode("utf-8").strip()


def push_file(server, author, parent, path, literal):
    ref = f"refs/heads/{PR_BRANCH}"
    git(author, "read-tree", parent)
    oid = git_text(author, "hash-object", "-w", "--stdin", data=(literal + "\n").encode("ascii"))
    git(author, "update-index", "--add", "--cacheinfo", f"100644,{oid},{path}")
    tree = git_text(author, "write-tree")
    commit = git_text(author, "commit-tree", tree, "-p", parent, "-m", f"Add {path}")
    git(author, "update-ref", ref, commit, parent)
    delta = git_text(author, "diff-tree", "--no-commit-id", "--name-status", "-r", parent, commit)
    require(delta == f"A\t{path}", f"unexpected Git change: {delta}")
    args = ["push", "--porcelain", server.as_uri(), f"{ref}:{ref}"]
    push = git_text(author, *args)
    require(git_text(server, "rev-parse", ref) == commit, "push did not update the requested branch")
    return {"parent": parent, "commit": commit, "tree": tree, "delta": delta, "push": push,
            "argv": ["git", "-C", str(author), *args]}


def event(root, label, payload, code=0):
    path = root / f"{label}.json"
    write_json(path, payload)
    command = event_process()
    started = perf_counter()
    proc = subprocess.run(command, input=path.read_bytes(), capture_output=True, timeout=1000)
    seconds = perf_counter() - started
    result = {"event": payload, "argv": command, "exit_code": proc.returncode, "seconds": seconds,
              "stdout": strict_json(proc.stdout), "stderr": proc.stderr.decode("utf-8", "replace")}
    write_json(root / f"{label}-reply.json", result)
    require(proc.returncode == code, f"{label}: expected exit {code}, got {result}")
    return result


def release(room):
    ready = read(room / "ready.json")
    folder = room / "r" / ready["release"]
    return {**ready, "manifest": folder / "checked/manifest.json", "index": folder / "index"}


def control(root, label, sources, manifest, index, literal):
    target = root / "control" / label
    result = call(R2, "query-verified", "--sources", sources, "--manifest", manifest, "--index", index,
                  "--output-dir", target, "--log-dir", target.with_name(label + "-log"), f"--literal={literal}")
    data = target / "answer.jsonl"
    stdout = result["stdout"]
    receipt = read(data.with_name("verification.json"))
    require(stdout["status"] == receipt["status"] == "VERIFIED" and stdout["full_git_scans"] == 1
            and sha256_file(manifest) == receipt["manifest_sha256"]
            and sha256_file(data) == stdout["result_sha256"] == receipt["result_sha256"], "invalid full Git control")
    return {**result, "answer": str(data)}


def concurrent_pair(literal):
    barrier = Barrier(3)
    commands = [[sys.executable, "-B", "-X", "utf8", str(CURRENT), "query", "--repo", name, "--pr", "1", literal]
                for name in REPOS]
    with ThreadPoolExecutor(max_workers=2) as pool:
        clients = [pool.submit(request, barrier, cmd, literal) for cmd in commands]
        barrier.wait(timeout=30)
        rows = {}
        for name, cmd, client in zip(REPOS, commands, clients, strict=True):
            info, stdout, stderr = client.result()
            require(info.get("returncode") == 0, f"{name}: {stdout!r} {stderr!r}")
            rows[name] = {**info, "argv": cmd, "stdout": strict_json(stdout), "stderr": stderr.decode("utf-8", "replace")}
    require(max_overlap(list(rows.values())) == 2, "the two CLI processes did not overlap")
    return rows


def fingerprint(rooms):
    return {name: {str(path.relative_to(room)): sha256_file(path)
                   for path in sorted(room.rglob("*.json"))
                   if path.name in ("view.json", "ready.json") or path.parent.name == "latest"}
            for name, room in rooms.items()}


def measure(root, scale):
    prior = read(PROJECT / "verification/r2-checked-preparation.json")
    checked = scale / "checked-01"
    entries, _ = trusted_bundle(checked, prior["receipt_sha256"])
    require(sum(repo["snapshot"]["regular_paths"] for repo in entries) == 133565, "unexpected corpus size")
    literal = "R2_PR_SCOPE_" + uuid4().hex.upper()
    sources, config = root / "server", root / "config.json"
    repos, base, servers, authors = [], {}, {}, {}
    for row in entries:
        name, pin = row["id"], row["snapshot"]
        commit = pin["commit"]
        objects = scale / "sources" / f"{name}.git" / "objects"
        servers[name] = server = sources / f"{name}.git"
        bare(server, objects)
        git(server, "update-ref", "refs/heads/main", commit)
        base[name] = ("main", commit)
        repos.append({"id": name, "repository": pin["repository"], "url": pin["url"], "directories": row["directories"],
                      "branch": "main", "remote": server.as_uri()})
        if name in REPOS:
            authors[name] = author = root / f"author-{name}.git"
            bare(author, objects)
            for store in (server, author):
                (store / "shallow").write_bytes((commit + "\n").encode("ascii"))
                git(store, "update-ref", f"refs/heads/{PR_BRANCH}", commit)
            git(server, "config", "receive.denyNonFastForwards", "true")
            for key, value in (("user.name", "Repo Proof Lab"), ("user.email", "lab@example.invalid"),
                               ("commit.gpgsign", "false")):
                git(author, "config", key, value)
    spec = {"repositories": repos, "workspace": "base", "pr_directory": "pr", "seed_index": str(scale / "index-01"),
            "checked_index": {"directory": str(checked), "receipt_sha256": prior["receipt_sha256"]}}
    write_json(config, {"corpora": {"default": spec}})
    os.environ["REPO_PROOF_CURRENT_CONFIG"] = str(config)
    rooms = {name: pr_room(config, spec, "default", name, 1) for name in REPOS}
    for room in rooms.values():
        for role in ("agent", "worker"):
            for name, server in servers.items():
                bare(room / role / "sources" / f"{name}.git", server / "objects")

    base_control = control(root, "base", sources, checked / "manifest.json", scale / "index-01", literal)
    require(base_control["stdout"]["count"] == 0, "the literal already occurs in the baseline")
    print("Baseline full Git scan: 0 matches", flush=True)
    initial_pushes = {name: push_file(servers[name], authors[name], base[name][1], FILES[name], literal) for name in REPOS}
    print("Both new files pushed before the opened events", flush=True)

    def open_one(name):
        result = event(root, f"open-{name}", {"action": "opened", "number": 1, "repository": name,
                                             "base": "main", "head": PR_BRANCH})
        response = result["stdout"]
        require(response["status"] == "REGISTERED" and response["pr_head"]["commit"] == initial_pushes[name]["commit"]
                and Path(response["view_directory"]).samefile(rooms[name])
                and response["refresh"]["status"] == "READY"
                and response["refresh"]["candidate_rebuilt"] == [name]
                and response["refresh"]["verification"]["reconciled_repositories"] == [name],
                f"{name} did not auto-publish its checked index on opened")
        print(f"{name} #1 opened and checked index ready", flush=True)
        return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        opened = dict(zip(REPOS, pool.map(open_one, REPOS), strict=True))

    releases = {name: release(rooms[name]) for name in REPOS}
    first = concurrent_pair(literal)
    answers = {}

    def verify_query(result, name, commit, paths, ready):
        expected = {**base, name: (PR_BRANCH, commit)}
        artifact = check_answer(result, expected, sorted((HIT_REPOS[name], path) for path in paths))
        stdout = result["stdout"]
        require(stdout["operation"] == "query-checked" and stdout["selection"]["pull_request_repository"] == name
                and stdout["checked_index_sha256"] == ready["receipt_sha256"], "CLI used an unexpected checked index")
        return artifact

    for name in REPOS:
        answers[name] = verify_query(first[name], name, initial_pushes[name]["commit"], [FILES[name]], releases[name])
    base_query = call(CURRENT, "query", literal)
    base_answer = check_answer(base_query, base, [])
    require(base_answer.read_bytes() == Path(base_control["answer"]).read_bytes(), "baseline bytes differ")
    print("First answers overlapped and each published its own single hit", flush=True)

    brave_before = fingerprint({"brave-core": rooms["brave-core"]})
    newer = push_file(servers["electron"], authors["electron"], initial_pushes["electron"]["commit"], SECOND, literal)
    sync = event(root, "sync-electron", {"action": "synchronize", "repository": "electron", "number": 1})
    updated = release(rooms["electron"])
    require(sync["stdout"]["status"] == "READY" and updated["receipt_sha256"] != releases["electron"]["receipt_sha256"]
            and sync["stdout"]["candidate_rebuilt"] == ["electron"], "Electron did not activate a new index")
    require(fingerprint({"brave-core": rooms["brave-core"]}) == brave_before, "Electron changed Brave state files")
    after = {name: call(CURRENT, "query", "--repo", name, "--pr", 1, literal) for name in REPOS}
    electron_answer = verify_query(after["electron"], "electron", newer["commit"], [FILES["electron"], SECOND], updated)
    brave_answer = verify_query(after["brave-core"], "brave-core", initial_pushes["brave-core"]["commit"],
                                [FILES["brave-core"]], releases["brave-core"])
    require(brave_answer.read_bytes() == answers["brave-core"].read_bytes()
            and release(rooms["brave-core"]) == releases["brave-core"], "Brave answer or index changed")

    before_ambiguous = fingerprint(rooms)
    ambiguous_query = call(CURRENT, "query", "--pr", 1, literal, code=4)
    ambiguous_sync = event(root, "sync-ambiguous", {"action": "synchronize", "number": 1}, code=4)
    for result in (ambiguous_query, ambiguous_sync):
        reason = result["stdout"]["reason"]
        require(result["stdout"]["status"] == "ERROR" and "niejednoznaczny" in reason
                and all(name in reason for name in REPOS) and "--repo" in reason, "ambiguity was not explained")
    require(fingerprint(rooms) == before_ambiguous, "ambiguous operation changed a view")
    recovery = {name: call(CURRENT, "query", "--repo", name, "--pr", 1, literal) for name in REPOS}
    e_final = verify_query(recovery["electron"], "electron", newer["commit"], [FILES["electron"], SECOND], updated)
    b_final = verify_query(recovery["brave-core"], "brave-core", initial_pushes["brave-core"]["commit"],
                           [FILES["brave-core"]], releases["brave-core"])
    print("Electron updated, Brave unchanged, and both ambiguous requests rejected", flush=True)

    comparisons = (("electron-first", releases["electron"], [answers["electron"]]),
                   ("brave", releases["brave-core"], [answers["brave-core"], brave_answer, b_final]),
                   ("electron-updated", updated, [electron_answer, e_final]))

    def verify_full(item):
        label, frozen, published = item
        result = control(root, label, sources, frozen["manifest"], frozen["index"], literal)
        expected = Path(result["answer"]).read_bytes()
        require(all(path.read_bytes() == expected for path in published), f"{label}: full Git result differs")
        print(f"{label}: all published answers match an independent full Git scan", flush=True)
        return label, result

    with ThreadPoolExecutor(max_workers=2) as pool:
        controls = dict(pool.map(verify_full, comparisons))
    return {"literal": literal, "baseline": base, "base_control": base_control, "base_query": base_query,
            "initial_pushes": initial_pushes, "opened": opened, "first_queries": first, "simultaneous_clients": 2,
            "electron_update_push": newer, "electron_sync": sync, "queries_after_update": after,
            "brave_commit_index_and_answer_unchanged": True, "ambiguous_query": ambiguous_query,
            "ambiguous_sync": ambiguous_sync, "ambiguous_operations_unchanged_fingerprint": before_ambiguous,
            "recovery_queries": recovery, "full_controls": controls, "published_byte_comparisons": 7}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    args = parser.parse_args()
    scale = (PROJECT / "local/r2-scale").resolve(strict=True)
    root = args.work_dir.resolve()
    require(root.is_relative_to(scale) and not args.measurements.exists(), "use a new ignored workspace and output")
    root.mkdir()
    os.environ["GIT_ALLOW_PROTOCOL"] = "file"
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    write_json(args.measurements, measure(root, scale))
    print(json.dumps({"status": "VERIFIED", "report": str(args.measurements)}))


if __name__ == "__main__":
    main()
