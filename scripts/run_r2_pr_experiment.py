"""Push one local PR commit and measure first visibility and checked-index readiness."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter_ns, sleep, time_ns
from uuid import uuid4

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_current import R2, git, local_commit, pr_room
from prepare_checked_r2_index import trusted_bundle
from run_r2_freshness_experiment import CURRENT, bare, call, read, require


EVENT = PROJECT / "scripts/fineract_r2_pr.py"
PR_BRANCH = "r2-pr-1"
BASE_BRANCH = "main"
UNCHANGED = "'engflow_reclient_configs_version':"
NEW_PATH = "docs/r2-pr-refresh-experiment.txt"


def event_process():
    return [sys.executable, "-B", "-X", "utf8", str(EVENT), "event"]


def record(command, process, stdout, stderr, started, ended):
    return {"argv": command, "exit_code": process.returncode, "start_unix_ns": started,
            "ended_unix_ns": ended, "wall_seconds": (ended - started) / 1e9,
            "stdout": strict_json(stdout), "stderr": stderr.decode("utf-8", "replace")}


def setup(root, scale):
    prepared = read(PROJECT / "verification/r2-checked-preparation.json")
    original = (scale / "checked-01", prepared["receipt_sha256"])
    entries, _ = trusted_bundle(*original)
    require(sum(repo["snapshot"]["regular_paths"] for repo in entries) == 133565, "unexpected corpus size")
    config = root / "config.json"
    stores = root / "server"
    room = pr_room(config, {"pr_directory": "pr"}, "default", "electron", 1)
    repositories = []
    for entry in entries:
        name, pin = entry["id"], entry["snapshot"]
        original_store = scale / "sources" / f"{name}.git"
        server = stores / f"{name}.git"
        branch = BASE_BRANCH if name == "electron" else name + "-pin"
        if name == "electron":
            bare(server)
            git(server, "fetch", "--quiet", "--depth=1", "--no-tags", original_store.as_uri(),
                f"{pin['commit']}:refs/heads/{branch}")
            git(server, "update-ref", f"refs/heads/{PR_BRANCH}", pin["commit"])
            git(server, "config", "receive.denyNonFastForwards", "true")
        else:
            bare(server, original_store / "objects")
            git(server, "update-ref", "refs/heads/" + branch, pin["commit"])
        for role in ("agent", "worker"):
            local = room / role / "sources" / f"{name}.git"
            if name == "electron":
                bare(local)
                git(local, "fetch", "--quiet", "--depth=1", "--no-tags", server.as_uri(),
                    f"refs/heads/{branch}:refs/pins/baseline")
            else:
                bare(local, original_store / "objects")
        repositories.append({"id": name, "repository": pin["repository"], "url": pin["url"],
                             "directories": entry["directories"], "branch": branch, "remote": server.as_uri()})
    write_json(config, {"corpora": {"default": {"repositories": repositories, "workspace": "base",
        "pr_directory": "pr", "seed_index": str(scale / "index-01"),
        "checked_index": {"directory": str(original[0]), "receipt_sha256": original[1]}}}})
    os.environ["REPO_PROOF_CURRENT_CONFIG"] = str(config)
    return repositories, entries, original, room


def check_answer(call_result, expected, paths):
    response = call_result["stdout"]
    require(response["status"] == "VERIFIED", "query failed to verify")
    require({row["id"]: (row["branch"], row["commit"]) for row in response["selection"]["repositories"]}
            == expected, "query selected an unexpected branch or commit")
    require(sorted((row["repository"], row["path"]) for row in response["answer"] if row["type"] == "hit")
            == paths, "query produced unexpected paths")
    artifact = Path(response["output_directory"]) / "answer.jsonl"
    receipt = read(artifact.with_name("verification.json"))
    require(receipt["status"] == "VERIFIED" and receipt["result_sha256"] == response["result_sha256"]
            == sha256_file(artifact), "wrong published receipt")
    require([strict_json(line) for line in artifact.read_bytes().splitlines()] == response["answer"],
            "complete CLI JSON differs from the published answer")
    return artifact


def measure(root, scale):
    repos, entries, original, room = setup(root, scale)
    baseline = {repo["id"]: (repo["branch"], entry["snapshot"]["commit"])
                for repo, entry in zip(repos, entries, strict=True)}
    a = baseline["electron"][1]
    server = root / "server/electron.git"
    author = root / "author"
    git(None, "init", "--quiet", "--object-format=sha1", str(author))
    git(author, "fetch", "--quiet", "--depth=1", "--no-tags", server.as_uri(), f"refs/heads/{PR_BRANCH}")
    git(author, "checkout", "--quiet", "-b", PR_BRANCH, "FETCH_HEAD")
    for key, value in (("user.name", "Repo Proof Lab"), ("user.email", "lab@example.invalid"),
                       ("commit.gpgsign", "false"), ("core.autocrlf", "false")):
        git(author, "config", key, value)
    opened = {"action": "opened", "number": 1, "repository": "electron", "base": BASE_BRANCH, "head": PR_BRANCH}
    event_open = root / "opened.json"
    write_json(event_open, opened)
    require(not (room / "view.json").exists(), "PR was pre-registered")
    at = time_ns()
    proc = subprocess.run(event_process(), input=event_open.read_bytes(), capture_output=True, timeout=120)
    registered = record(event_process(), proc, proc.stdout, proc.stderr, at, time_ns())
    require(registered["exit_code"] == 0 and registered["stdout"]["status"] == "REGISTERED"
            and registered["stdout"]["base_head"]["commit"] == registered["stdout"]["pr_head"]["commit"] == a,
            "branches were not registered at A")

    literal = "R2_PR1_" + uuid4().hex.upper()
    (author / NEW_PATH).write_bytes((literal + "\n").encode("ascii"))
    git(author, "add", "--", NEW_PATH)
    git(author, "commit", "--quiet", "-m", "Add one file for the local PR refresh experiment")
    b = git(author, "rev-parse", "HEAD").strip().decode("ascii")
    change = git(author, "diff-tree", "--no-commit-id", "--name-status", "-r", a, b).decode("ascii").strip()
    require(change == f"A\t{NEW_PATH}", "the PR must add exactly one file")
    require(git(author, "rev-parse", b + "^").decode("ascii").strip() == a
            and not local_commit(server, b) and all(not local_commit(room / role / "sources/electron.git", b)
                                                   for role in ("agent", "worker")), "unexpected parent or existing B")

    event_update = root / "synchronize.json"
    write_json(event_update, {"action": "synchronize", "number": 1})
    push_args = ("push", "--porcelain", server.as_uri(), f"refs/heads/{PR_BRANCH}:refs/heads/{PR_BRANCH}")
    push_start = time_ns()
    push_output = git(author, *push_args).decode("utf-8", "replace")
    pushed = time_ns()
    push = {"argv": ["git", "-C", str(author), *push_args], "stdout": push_output,
            "start_unix_ns": push_start, "ended_unix_ns": pushed}
    deadline = perf_counter_ns() + 1_000_000_000
    dispatched = time_ns()
    with event_update.open("rb") as payload, subprocess.Popen(
            event_process(), stdin=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as event:
        delay = deadline - perf_counter_ns()
        if delay > 0:
            sleep(delay / 1e9)
        command = [sys.executable, "-B", "-X", "utf8", str(CURRENT), "query", "--pr", "1", literal]
        at = time_ns()
        query = subprocess.run(command, capture_output=True, timeout=300)
        first = record(command, query, query.stdout, query.stderr, at, time_ns())
        stdout, stderr = event.communicate(timeout=300)
        updated = record(event_process(), event, stdout, stderr, dispatched, time_ns())
    write_json(root / "push-attempt.json", {"push": push, "first_pr": first, "refresh": updated})
    ready = updated["stdout"]
    require(first["exit_code"] == 0 and updated["exit_code"] == 0, f"push attempt failed: {first}, {updated}")
    require(ready["status"] == "READY" and ready["candidate_reused"] == ["chromium", "brave-core"]
            and ready["candidate_rebuilt"] == ["electron"]
            and ready["verification"]["reused_repositories"] == ["chromium", "brave-core"]
            and ready["verification"]["reconciled_repositories"] == ["electron"], "event did not refresh only Electron")
    require(git(server, "rev-parse", "refs/heads/" + BASE_BRANCH).strip().decode("ascii") == a
            and git(server, "rev-parse", "refs/heads/" + PR_BRANCH).strip().decode("ascii") == b,
            "push did not affect only the PR head")
    expected = {**baseline, "electron": (PR_BRANCH, b)}
    new_paths = [("electron/electron", NEW_PATH)]
    first_answer = check_answer(first, expected, new_paths)
    fast = call(CURRENT, "query", "--pr", 1, literal)
    fast_answer = check_answer(fast, expected, new_paths)
    require(fast["stdout"]["operation"] == "query-checked"
            and fast["stdout"]["checked_index_sha256"] == ready["receipt_sha256"]
            and fast["stdout"]["full_git_scans"] == 0, "next query did not use the refreshed checked B index")
    base = call(CURRENT, "query", literal)
    base_answer = check_answer(base, baseline, [])
    unchanged = call(CURRENT, "query", "--pr", 1, UNCHANGED)
    unchanged_answer = check_answer(unchanged, expected, [("electron/electron", "DEPS")])
    require(unchanged["stdout"]["operation"] == "query-checked", "unchanged PR file did not use checked B")

    source = room / "worker/sources"
    candidate = Path(ready["candidate_directory"])
    checked = Path(ready["verification"]["directory"])
    for name in ("chromium", "brave-core"):
        for suffix in ("sqlite", "grams", "objects"):
            require((checked / f"{name}.{suffix}").samefile(original[0] / f"{name}.{suffix}"),
                    "unchanged verifier shard was not reused")
    regular = sum(repo["snapshot"]["regular_paths"] for repo in read(checked / "manifest.json")["repositories"])
    require(regular == 133566, "wrong regular path count after push")

    controls = {}
    checks = (("pr-new", literal, checked / "manifest.json", candidate, [first_answer, fast_answer]),
              ("base-new", literal, original[0] / "manifest.json", scale / "index-01", [base_answer]),
              ("pr-old", UNCHANGED, checked / "manifest.json", candidate, [unchanged_answer]))
    for label, needle, manifest, index, answers in checks:
        target = root / "control" / label
        control = call(R2, "query-verified", "--sources", source, "--manifest", manifest, "--index", index,
                       "--output-dir", target, "--log-dir", target.with_name(label + "-log"), f"--literal={needle}")
        raw = (target / "answer.jsonl").read_bytes()
        require(control["stdout"]["status"] == "VERIFIED" and control["stdout"]["full_git_scans"] == 1
                and all(path.read_bytes() == raw for path in answers), f"{label}: independent full scan differs")
        controls[label] = control

    first_ended = first["ended_unix_ns"]
    active = ready["ready_unix_ns"]
    return {"literal": literal, "unchanged_literal": UNCHANGED, "new_path": NEW_PATH, "commit_a": a, "commit_b": b,
            "single_git_change": change, "tree_a": git(author, "rev-parse", a + "^{tree}").decode("ascii").strip(),
            "tree_b": git(author, "rev-parse", b + "^{tree}").decode("ascii").strip(),
            "regular_paths_a": 133565, "regular_paths_b": regular, "registered": registered,
            "push": push,
            "event_dispatch_unix_ns": dispatched, "refresh": updated, "first_pr": first,
            "fast_pr": fast, "base": base, "unchanged_pr": unchanged, "controls": controls,
            "all_answers_byte_equal_to_git": True, "stale_pr_answers": 0, "b_present_before_push": False,
            "push_to_first_start_seconds": (first["start_unix_ns"] - pushed) / 1e9,
            "push_to_first_response_seconds": (first_ended - pushed) / 1e9,
            "push_to_ready_seconds": (active - pushed) / 1e9,
            "fast_response_seconds": fast["wall_seconds"], "ready_before_first_response": active < first_ended}


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
    result = measure(root, scale)
    write_json(args.measurements, result)
    print(json.dumps({name: result[name] for name in ("push_to_first_response_seconds", "push_to_ready_seconds",
                                                    "fast_response_seconds", "ready_before_first_response")}))


if __name__ == "__main__":
    main()
