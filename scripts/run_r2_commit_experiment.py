"""Create and benchmark a local Electron commit over the frozen R2 corpus."""

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
from shutil import copytree
from statistics import median
import subprocess
import sys
from time import perf_counter

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_corpus import read_manifest, read_verified_base


LITERAL = "chrome://"
ADDED_HIT = "docs/README.md"
REMOVED_HIT = "docs/api/content-tracing.md"
OLD_NAME = "docs/tutorial/debugging-main-process.md"
NEW_NAME = "docs/tutorial/debugging-main-process-r2-experiment.md"
CLI = PROJECT / "scripts/fineract_r2_corpus.py"
OFFLINE = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="", GIT_TERMINAL_PROMPT="0")


def git(store, *args, data=None, env=OFFLINE):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(store), *args],
                                   input=data, env=env, timeout=45)


def base_paths(args):
    baseline = read_manifest(args.base_manifest)
    hits, digest = read_verified_base(args.base_answer, baseline, LITERAL, sha256_file(args.base_manifest))
    if sum(map(len, hits)) != 5866:
        raise ValueError("the frozen baseline must contain 5866 matches")
    return baseline, hits, digest


def make_commit(args):
    baseline, _, digest = base_paths(args)
    args.work_dir.mkdir(parents=True)
    sources = args.work_dir / "sources"
    sources.mkdir()
    for repo in baseline:
        name = repo["id"] + ".git"
        local = sources / name
        copytree(args.sources / name, local)
        git(local, "update-ref", "refs/heads/base", repo["snapshot"]["commit"])

    store = sources / "electron.git"
    old = next(repo["snapshot"] for repo in baseline if repo["id"] == "electron")
    commit_a = old["commit"]
    needle = LITERAL.encode("ascii")

    def entry(path):
        metadata, name = git(store, "ls-tree", "-z", commit_a, "--", path).split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        if kind != "blob" or mode not in ("100644", "100755") or name != path.encode("ascii") + b"\0":
            raise ValueError(f"expected a tracked regular path at {path}")
        return mode, oid, git(store, "cat-file", "blob", oid)

    mode_add, _, add_bytes = entry(ADDED_HIT)
    mode_remove, _, remove_bytes = entry(REMOVED_HIT)
    mode_rename, rename_oid, rename_bytes = entry(OLD_NAME)
    if needle in add_bytes or needle not in remove_bytes or needle not in rename_bytes:
        raise ValueError("the frozen paths do not have the expected matches")
    git_env = dict(OFFLINE, GIT_INDEX_FILE=str(args.work_dir / "commit.index"),
                   GIT_AUTHOR_NAME="R2 experiment", GIT_AUTHOR_EMAIL="r2@example.invalid",
                   GIT_COMMITTER_NAME="R2 experiment", GIT_COMMITTER_EMAIL="r2@example.invalid",
                   GIT_AUTHOR_DATE="2026-11-18T12:00:00Z", GIT_COMMITTER_DATE="2026-11-18T12:00:00Z")
    git(store, "read-tree", commit_a, env=git_env)
    deletion = f"0 {'0' * 40}\t{OLD_NAME}\0".encode("ascii")
    git(store, "update-index", "-z", "--index-info", data=deletion, env=git_env)
    changed = [(mode_add, ADDED_HIT, add_bytes + b"\n<!-- Local R2 experiment: chrome:// -->\n"),
               (mode_remove, REMOVED_HIT, remove_bytes.replace(needle, b"https://"))]
    for mode, path, raw in changed:
        oid = git(store, "hash-object", "-w", "--stdin", data=raw).strip().decode("ascii")
        git(store, "update-index", "--add", "--cacheinfo", f"{mode},{oid},{path}", env=git_env)
    git(store, "update-index", "--add", "--cacheinfo", f"{mode_rename},{rename_oid},{NEW_NAME}", env=git_env)
    tree_b = git(store, "write-tree", env=git_env).strip().decode("ascii")
    commit_b = git(store, "commit-tree", tree_b, "--no-gpg-sign", "-p", commit_a,
                   "-m", "Local R2 experiment: change two hits and rename a third", env=git_env).strip().decode("ascii")
    git(store, "update-ref", "refs/heads/r2-experiment", commit_b)
    changes = [line.split("\t") for line in git(store, "diff-tree", "--no-commit-id", "-r", "-M100%",
                                               "--name-status", commit_a, commit_b).decode("ascii").splitlines()]
    expected = [["M", ADDED_HIT], ["M", REMOVED_HIT], ["R100", OLD_NAME, NEW_NAME]]
    if sorted(changes) != sorted(expected):
        raise ValueError(f"the experiment must make exactly the three specified changes: {changes}")
    result = {"repository": old["repository"], "id": "electron", "commit_a": commit_a,
              "tree_a": old["root_tree"], "commit_b": commit_b, "tree_b": tree_b,
              "changes": changes, "rename_blob": rename_oid, "base_result_sha256": digest,
              "base_manifest_sha256": sha256_file(args.base_manifest)}
    write_json(args.work_dir / "scenario.json", result)
    print(f"Local Electron commit B {commit_b}, tree {tree_b}", flush=True)


def checked_call(script, *args):
    command = [sys.executable, "-B", "-X", "utf8", str(script), *map(str, args)]
    start = perf_counter()
    run = subprocess.run(command, cwd=PROJECT, env=OFFLINE, capture_output=True, encoding="utf-8", timeout=930)
    elapsed = perf_counter() - start
    if run.returncode:
        raise RuntimeError(f"{command!r} failed with {run.returncode}: {run.stdout} {run.stderr}")
    return {"seconds": elapsed, "argv": command, "stdout": run.stdout, "stderr": run.stderr}


def trial(args, scenario, baseline, variant, repeat):
    # Each trial starts at delivery of the B commit ID, with only A's outputs prepared.
    start = perf_counter()
    folder = args.run_dir / f"{repeat:02d}-{variant}"
    folder.mkdir()
    sources = args.work_dir / "sources"
    name, commit_b = scenario["id"], scenario["commit_b"]
    repos = deepcopy(baseline)
    changed = next(repo for repo in repos if repo["id"] == name)
    changed["snapshot"]["commit"] = commit_b
    changed["snapshot"]["root_tree"] = git(sources / f"{name}.git", "rev-parse", commit_b + "^{tree}").strip().decode("ascii")
    scope = folder / "scope.json"
    write_json(scope, {"scope_version": 1, "repositories": [
        {"id": repo["id"], "directories": repo["directories"], **{key: repo["snapshot"][key]
         for key in ("repository", "url", "commit", "root_tree")}} for repo in repos
    ]})
    manifest = folder / "manifest.json"
    manifest_call = checked_call(PROJECT / "scripts/prepare_r2_corpus.py", "--scope", scope, "--sources", sources,
                                 "--manifest", manifest)
    manifest_seconds = perf_counter() - start
    index_seconds, build = 0.0, None
    if variant == "full":
        index_start = perf_counter()
        target = strict_json(manifest.read_bytes())
        shard_manifest = folder / "electron-manifest.json"
        shard = next(repo for repo in target["repositories"] if repo["id"] == name)
        write_json(shard_manifest, {**target, "repositories": [shard], "totals": {
            "regular_paths": shard["snapshot"]["regular_paths"], **{key: shard[key] for key in
            ("regular_path_bytes", "distinct_regular_blobs", "distinct_regular_blob_bytes")},
        }})
        index = folder / "index"
        build = checked_call(CLI, "build", "--sources", sources, "--manifest", shard_manifest, "--index", index,
                             "--log-dir", folder / "build-log")
        for repo in repos:
            if repo["id"] != name:
                shard = f"{repo['id']}.sqlite"
                os.link(args.base_index / shard, index / shard)
        index_seconds = perf_counter() - index_start
        command = ("query-verified", "--index", index)
    else:
        command = ("update-verified", "--base-manifest", args.base_manifest, "--base-answer", args.base_answer)
    output = folder / "answer"
    query = checked_call(CLI, *command, "--sources", sources, "--manifest", manifest, f"--literal={LITERAL}",
                         "--output-dir", output, "--log-dir", folder / "query-log")
    wall = perf_counter() - start
    report = strict_json(query["stdout"].encode())
    receipt = strict_json((output / "verification.json").read_bytes())
    if (report["status"] != "VERIFIED" or receipt["status"] != "VERIFIED"
            or receipt["manifest_sha256"] != sha256_file(manifest) or receipt["literal"] != LITERAL
            or receipt["result_sha256"] != report["result_sha256"]
            or receipt["result_sha256"] != sha256_file(output / "answer.jsonl")):
        raise ValueError("trial did not publish the verified B answer")
    print(f"{repeat:02d} {variant}: total={wall:.3f} s, manifest={manifest_seconds:.3f} s, "
          f"index={index_seconds:.3f} s, query={query['seconds']:.3f} s, count={report['count']}", flush=True)
    return {"repeat": repeat, "variant": variant, "directory": str(folder), "commit_to_answer_seconds": wall,
            "manifest_seconds": manifest_seconds, "index_preparation_seconds": index_seconds,
            "query_seconds": query["seconds"], "manifest_subprocess": manifest_call, "index_subprocess": build,
            "query_subprocess": query, "response": report}


def hits(raw):
    return {(row["repository"], row["path"]): row for row in map(strict_json, raw.splitlines()) if row["type"] == "hit"}


def compare_trials(args, scenario, delta, full):
    a = (args.base_answer / "answer.jsonl").read_bytes()
    b = (Path(delta["directory"]) / "answer/answer.jsonl").read_bytes()
    reference = (Path(full["directory"]) / "answer/answer.jsonl").read_bytes()
    old, new = hits(a), hits(b)
    repo, commit = scenario["repository"], scenario["commit_b"]
    expected = {key: ({**row, "commit": commit} if key[0] == repo else row) for key, row in old.items()}
    for path in (REMOVED_HIT, OLD_NAME):
        del expected[repo, path]
    for path in (ADDED_HIT, NEW_NAME):
        store = args.work_dir / "sources" / (scenario["id"] + ".git")
        oid = git(store, "rev-parse", f"{commit}:{path}").strip().decode("ascii")
        raw = git(store, "cat-file", "blob", oid)
        offset = raw.index(LITERAL.encode("ascii"))
        expected[repo, path] = {"type": "hit", "repository": repo, "commit": commit, "path": path, "blob_id": oid,
                                "byte_offset": offset, "line": 1 + raw.count(b"\n", 0, offset)}
    return {"repeat": delta["repeat"], "answers_byte_identical": b == reference,
            "answer_sha256": sha256_file(Path(delta["directory"]) / "answer/answer.jsonl"),
            "full_answer_sha256": sha256_file(Path(full["directory"]) / "answer/answer.jsonl"),
            "expected_full_hit_map": len(old) == len(new) == 5866 and new == expected
            and delta["response"]["count"] == full["response"]["count"] == len(new),
            "new_name_occurrences": sum(strict_json(line).get("path") == NEW_NAME for line in b.splitlines()),
            "removed_hits_absent": all((repo, path) not in new for path in (REMOVED_HIT, OLD_NAME)),
            "added_hits_present": all((repo, path) in new for path in (ADDED_HIT, NEW_NAME)),
            "retained_hits": len(old) - 2}


def measure(args):
    baseline, _, digest = base_paths(args)
    scenario = strict_json((args.work_dir / "scenario.json").read_bytes())
    if scenario["base_result_sha256"] != digest:
        raise ValueError("the base answer differs from the one selected for this scenario")
    args.run_dir.mkdir(parents=True)
    trials, pairs = [], []
    for repeat in range(1, 4):
        results = {}
        for variant in (("delta", "full") if repeat % 2 else ("full", "delta")):
            row = trial(args, scenario, baseline, variant, repeat)
            trials.append(row)
            results[variant] = row
            write_json(args.run_dir / f"{repeat:02d}-{variant}.json", row)
        pairs.append(compare_trials(args, scenario, **results))
    summary = {}
    for variant in ("delta", "full"):
        summary[variant] = {}
        for field in ("commit_to_answer_seconds", "manifest_seconds", "index_preparation_seconds", "query_seconds"):
            data = [row[field] for row in trials if row["variant"] == variant]
            summary[variant][field] = {"seconds": data, "median": median(data), "min": min(data), "max": max(data)}
    write_json(args.run_dir / "measurements.json", {"scenario": scenario, "filesystem_cache": "enabled, not cleared",
               "trials": trials, "checks": pairs, "summary": summary})
    if not all(row["answers_byte_identical"] and row["expected_full_hit_map"] and row["new_name_occurrences"] == 1
               and row["removed_hits_absent"] and row["added_hits_present"] for row in pairs):
        raise ValueError("update differs from the independently checked, expected full answer")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    setup = commands.add_parser("setup")
    setup.add_argument("--sources", required=True, type=lambda value: Path(value).resolve())
    run = commands.add_parser("measure")
    run.add_argument("--base-index", required=True, type=lambda value: Path(value).resolve())
    run.add_argument("--run-dir", required=True, type=lambda value: Path(value).resolve())
    for command in (setup, run):
        for name in ("work-dir", "base-manifest", "base-answer"):
            command.add_argument("--" + name, required=True, type=lambda value: Path(value).resolve())
    args = parser.parse_args()
    if args.operation == "setup":
        make_commit(args)
    else:
        measure(args)


if __name__ == "__main__":
    main()
