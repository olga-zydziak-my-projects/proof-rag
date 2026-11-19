"""Replay the official Electron A2 to A3 update through local Git servers."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter, time_ns

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_current import R2, git, local_commit, manifest_for


CURRENT = PROJECT / "scripts/fineract_r2_current.py"
LITERAL = "140.0.7339.133"
BRANCHES = {"chromium": "chromium-pin", "electron": "38-x-y", "brave-core": "brave-pin"}
BEFORE = [("brave/brave-core", "package.json")]
AFTER = [*BEFORE, ("electron/electron", "DEPS")]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return strict_json(path.read_bytes())


def bare(path, objects=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    git(None, "init", "--quiet", "--bare", "--object-format=sha1", str(path))
    if objects is not None:
        (path / "objects/info/alternates").write_bytes((objects.as_posix() + "\n").encode("utf-8"))


def call(script, *args, code=0):
    command = [sys.executable, "-B", "-X", "utf8", str(script), *map(str, args)]
    started_ns = time_ns()
    started = perf_counter()
    proc = subprocess.run(command, capture_output=True)
    elapsed = perf_counter() - started
    require(proc.returncode == code,
            f"{command}: expected exit {code}, got {proc.returncode}\n{proc.stdout!r}\n{proc.stderr!r}")
    return {"argv": command, "exit_code": proc.returncode, "start_unix_ns": started_ns,
            "ended_unix_ns": time_ns(), "wall_seconds": elapsed, "stdout": strict_json(proc.stdout),
            "stderr": proc.stderr.decode("utf-8", "replace")}


def check_publication(result, expected_paths, expected_commits):
    response = result["stdout"]
    require(response["status"] == "VERIFIED", "current query not verified")
    require(response["count"] == len(expected_paths), "incorrect result count")
    selected = {repo["repository"]: (repo["branch"], repo["commit"])
                for repo in response["selection"]["repositories"]}
    require(selected == expected_commits, "unexpected branch snapshot")
    output = Path(response["output_directory"])
    receipt, artifact = read(output / "verification.json"), output / "answer.jsonl"
    manifest = Path(response["manifest"])
    require(sha256_file(artifact) == response["result_sha256"] == receipt["result_sha256"]
            and sha256_file(manifest) == response["manifest_sha256"] == receipt["manifest_sha256"]
            and receipt["status"] == "VERIFIED" and receipt["literal"] == LITERAL
            and Path(receipt["output_directory"]).samefile(output), "invalid publication receipt")
    rows = [strict_json(line) for line in artifact.read_bytes().splitlines()]
    hits = [row for row in rows if row["type"] == "hit"]
    expected_sections = {repo: commit for repo, (_, commit) in expected_commits.items()}
    require(rows == response["answer"]
            and sorted((row["repository"], row["path"]) for row in hits) == expected_paths
            and {row["repository"]: row["commit"] for row in rows if row["type"] == "result"} == expected_sections
            and all(row["commit"] == expected_sections[row["repository"]] for row in hits),
            "CLI answer differs from expected complete published result")
    require(read(output.parent / "selection.json") == response["selection"], "saved selection differs")
    return artifact


def measure(root, scale, history):
    os.environ["GIT_ALLOW_PROTOCOL"] = "file"
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    plan = read(PROJECT / "verification/r2-history-plan.json")
    positions = {row["id"]: row for row in plan["acquisition"]["versions"]}
    a2, a3 = positions["A2"]["commit"], positions["A3"]["commit"]
    require(positions["A3"]["first_parent"] == a2, "history plan needs a fast-forward")
    frozen = read(PROJECT / "verification/r2-scale-manifest.json")
    original = history / "sources"
    electron = original / "electron.git"
    require(git(electron, "cat-file", "commit", a3).splitlines()[1] == b"parent " + a2.encode("ascii"),
            "A3 does not have A2 as first parent")

    servers, author, agent = root / "server", root / "author.git", root / "agent"
    agent_sources = agent / "sources"
    repositories = []
    expected_before, expected_after = {}, {}
    for entry in frozen["repositories"]:
        name, snapshot = entry["id"], entry["snapshot"]
        repo, branch = snapshot["repository"], BRANCHES[name]
        ref = f"refs/heads/{branch}"
        server, client = servers / f"{name}.git", agent_sources / f"{name}.git"
        if name == "electron":
            # Isolated real fetches. The agent starts without an Electron object store.
            bare(server)
            bare(author)
            git(server, "fetch", "--quiet", "--depth=1", "--no-tags", electron.as_uri(), f"{a2}:{ref}")
            git(author, "fetch", "--quiet", "--depth=2", "--no-tags", electron.as_uri(), f"{a3}:{ref}")
            require(not local_commit(server, a3) and not client.exists(), "A3 present before push")
            before, after = a2, a3
        else:
            objects = (original / f"{name}.git/objects").resolve(strict=True)
            bare(server, objects)
            bare(client, objects)
            before = after = snapshot["commit"]
            git(server, "update-ref", ref, before)
        repositories.append({"id": name, "repository": repo, "url": snapshot["url"],
                             "directories": entry["directories"], "remote": server.as_uri(), "branch": branch})
        expected_before[repo] = (branch, before)
        expected_after[repo] = (branch, after)

    config = root / "config.json"
    write_json(config, {"corpora": {"default": {"workspace": "agent", "seed_index": str(scale / "index-01"),
                                              "repositories": repositories}}})
    os.environ["REPO_PROOF_CURRENT_CONFIG"] = str(config)
    first = call(CURRENT, "query", LITERAL)
    a2_answer = check_publication(first, BEFORE, expected_before)
    require(first["stdout"]["operation"] == "query-verified", "first query did not use the full verifier")

    server = servers / "electron.git"
    client = agent_sources / "electron.git"
    ref = "refs/heads/" + BRANCHES["electron"]
    push_args = ("push", "--porcelain", server.as_uri(), f"{ref}:{ref}")
    push_started_ns = time_ns()
    push_output = git(author, *push_args).decode("utf-8", "replace")
    push_ended_ns = time_ns()
    require(git(server, "rev-parse", ref).strip().decode("ascii") == a3
            and f"{a2[:7]}..{a3[:7]}" in push_output, "Git push did not advance the branch to A3")
    [latest] = (agent / "latest").glob("*.json")
    old_pointer = read(latest)
    require(old_pointer["run"] == a2_answer.parent.parent.name
            and old_pointer["result_sha256"] == sha256_file(a2_answer)
            and not local_commit(client, a3), "agent already advanced before the second question")

    second = call(CURRENT, "query", LITERAL)
    a3_answer = check_publication(second, AFTER, expected_after)
    updated = second["stdout"]
    receipt = read(a3_answer.parent / "verification.json")
    require(first["argv"] == second["argv"] and updated["operation"] == "update-verified"
            and receipt["base_result_sha256"] == sha256_file(a2_answer)
            and receipt["base_manifest_sha256"] == old_pointer["manifest_sha256"]
            and local_commit(client, a3), "incremental publication did not start at A2 and obtain A3")
    electron_download = next(repo for repo in updated["downloads"] if repo["repository"] == "electron/electron")
    require(not electron_download["commit_present_before_fetch"] and electron_download["fetches"] >= 1,
            "A3 was not acquired from the server by the agent")

    # Use the historical A3 manifest and index as pinned control inputs only after publication.
    historical = history / "measure-01/A3/full"
    control_repos = read(historical / "manifest.json")["repositories"]
    require({repo["snapshot"]["repository"]: repo["snapshot"]["commit"] for repo in control_repos}
            == {repo: commit for repo, (_, commit) in expected_after.items()}, "incorrect control commits")
    control_manifest, control = root / "control.json", root / "control"
    write_json(control_manifest, manifest_for(control_repos))
    require(control_manifest.read_bytes() == Path(updated["manifest"]).read_bytes(), "manifest differs from control")
    comparison = call(R2, "query-verified", "--sources", original, "--manifest", control_manifest,
                      "--index", historical / "index", f"--literal={LITERAL}", "--output-dir", control,
                      "--log-dir", root / "control-log")
    artifact = control / "answer.jsonl"
    control_receipt = read(control / "verification.json")
    require(comparison["stdout"]["status"] == control_receipt["status"] == "VERIFIED"
            and Path(control_receipt["output_directory"]).samefile(control)
            and sha256_file(control_manifest) == control_receipt["manifest_sha256"]
            and a3_answer.read_bytes() == artifact.read_bytes()
            and sha256_file(artifact) == control_receipt["result_sha256"] == updated["result_sha256"],
            "independent full result is different")

    latest_bytes, a3_hash = latest.read_bytes(), sha256_file(a3_answer)
    outcomes = sorted((agent / "runs").iterdir())
    disconnected = servers / "electron.offline"
    server.rename(disconnected)
    try:
        offline = call(CURRENT, "query", LITERAL, code=3)
        require(offline["argv"] == second["argv"] and offline["stdout"]["status"] == "BLOCKED"
                and "Nie można potwierdzić bieżącej wersji electron/electron" in offline["stdout"]["reason"]
                and "answer" not in offline["stdout"] and "output_directory" not in offline["stdout"]
                and latest.read_bytes() == latest_bytes and sorted((agent / "runs").iterdir()) == outcomes
                and sha256_file(a3_answer) == a3_hash, "offline query published or lost an earlier answer")
    finally:
        disconnected.rename(server)

    published_ns = updated["published_unix_ns"]
    question_ns = second["start_unix_ns"]
    require(push_ended_ns <= question_ns <= published_ns <= second["ended_unix_ns"],
            "push, question and publication timestamps out of order")
    return {"literal": LITERAL, "selected_before": expected_before, "selected_after": expected_after,
            "agent_had_a3_before_question": False, "server_had_a3_before_push": False,
            "push": {"argv": ["git", "-C", str(author), *push_args], "stdout": push_output,
                     "start_unix_ns": push_started_ns, "ended_unix_ns": push_ended_ns},
            "publication_unix_ns": published_ns,
            "question_to_publication_seconds": (published_ns - question_ns) / 1e9,
            "push_to_publication_seconds": (published_ns - push_ended_ns) / 1e9,
            "initial": first, "updated": second, "independent_full_scan": comparison,
            "byte_equal": True, "independent_sha256": sha256_file(artifact), "offline": offline,
            "old_pointer_after_push": old_pointer, "latest_pointer_after_offline": read(latest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    args = parser.parse_args()
    scale = (PROJECT / "local/r2-scale").resolve(strict=True)
    root = args.work_dir.resolve()
    require(root.is_relative_to(scale), "use a new ignored directory under local/r2-scale")
    require(not args.measurements.exists(), "measurement output already exists")
    root.mkdir()
    result = measure(root, scale, scale / "history-study-01")
    result["publication_utc"] = datetime.fromtimestamp(result["publication_unix_ns"] / 1e9, timezone.utc).isoformat()
    write_json(args.measurements, result)
    print(json.dumps({key: result[key] for key in ("question_to_publication_seconds", "push_to_publication_seconds",
                                                   "independent_sha256")}))


if __name__ == "__main__":
    main()
