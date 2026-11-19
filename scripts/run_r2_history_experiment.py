"""Benchmark two independent update chains on six official Electron commits."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from itertools import zip_longest
import os
from pathlib import Path
from shutil import copytree
import subprocess
from time import perf_counter

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_corpus import read_manifest
from prepare_r2_corpus import acquire, fetch_one, local_sizes
from repo_proof import git_search
from repo_proof.corpus import parse_tree
from repo_proof.fineract_oracle import check_object
from run_r2_commit_experiment import CLI, OFFLINE, checked_call, git, hits


def acquire_history(args):
    repos = read_manifest(args.base_manifest)
    electron = next(repo for repo in repos if repo["id"] == "electron")
    pin = electron["snapshot"]
    sources = args.work_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    for repo in repos:
        name = f"{repo['id']}.git"
        local = sources / name
        if not local.exists():
            copytree(args.sources / name, local)

    store = sources / "electron.git"
    if git(store, "config", "--local", "--get", "remote.origin.url").decode().strip() != pin["url"]:
        raise ValueError("Electron origin differs from the frozen public source")
    tip = pin["commit"]
    commits = git(store, "rev-list", "--first-parent", "--max-count=6", "--reverse", tip).decode().splitlines()
    if len(commits) < 6:
        acquire(store, ["fetch", "--deepen=5", "--no-tags", "--no-recurse-submodules", "--no-auto-maintenance",
                        "--filter=blob:none", "origin", f"{tip}:refs/r2-history/tip"])
        commits = git(store, "rev-list", "--first-parent", "--max-count=6", "--reverse", tip).decode().splitlines()
    if len(commits) != 6 or commits[-1] != tip:
        raise ValueError("six official first-parent commits not available")

    versions, oids = [], set()
    unchanged = sum(repo["snapshot"]["regular_paths"] for repo in repos if repo["id"] != "electron")
    for i, commit in enumerate(commits):
        raw = git(store, "cat-file", "commit", commit)
        check_object(commit, "commit", raw)
        headers, _, body = raw.partition(b"\n\n")
        lines = headers.splitlines()
        tree = lines[0].removeprefix(b"tree ").decode("ascii")
        parent = lines[1].removeprefix(b"parent ").decode("ascii")
        if i and parent != commits[i - 1]:
            raise ValueError("commits are not adjacent on the first-parent line")
        paths = parse_tree(git(store, "ls-tree", "-rz", "--full-tree", commit, "--", *electron["directories"]))
        regular = [row for row in paths if row["category"] == "regular"]
        oids.update(row["object_id"] for row in regular)
        version = {"id": f"A{i}", "commit": commit, "root_tree": tree, "first_parent": parent,
                   "electron_regular_paths": len(regular), "corpus_regular_paths": len(regular) + unchanged,
                   "subject": body.splitlines()[0].decode("utf-8", "replace")}
        versions.append(version)
        print(version, flush=True)
    _, missing = local_sizes(store, sorted(oids))
    for start in range(0, len(missing), 2000):
        fetch_one(missing[start:start + 2000], store)
    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _, unresolved = local_sizes(store, sorted(oids))
    if unresolved:
        raise ValueError("the six scoped trees still have missing blobs")
    write_json(args.work_dir / "acquisition.json", {"base_manifest_sha256": sha256_file(args.base_manifest),
               "electron_origin": pin["url"], "objects_available_utc": finished,
               "requested_missing_blobs": len(missing), "distinct_electron_blobs_in_six_versions": len(oids),
               "versions": versions})
    print(f"All objects present at {finished}, fetched {len(missing)} missing blobs", flush=True)


def electron_matches(store, commit, literal):
    result = subprocess.run(git_search.git_command(store, "grep", "-a", "-F", "-l", "-z", "-e", literal, commit, "--"),
                            env=OFFLINE, capture_output=True, timeout=60)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    prefix = commit.encode("ascii") + b":"
    paths = result.stdout.split(b"\0")
    if paths.pop() or any(not path.startswith(prefix) for path in paths):
        raise ValueError("unexpected Electron grep records")
    return sorted(path[len(prefix):].decode("utf-8", "surrogateescape") for path in paths)


def freeze(args):
    acquisition = strict_json((args.work_dir / "acquisition.json").read_bytes())
    versions = acquisition["versions"]
    store = args.work_dir / "sources/electron.git"
    recon = args.work_dir / "reconnaissance"
    recon.mkdir()
    repos = read_manifest(args.base_manifest)
    cases = []
    for name, literal in (("many", args.many), ("few", args.few)):
        if not literal or any(not 32 <= ord(char) <= 126 for char in literal):
            raise ValueError("R2 requires a nonempty printable ASCII literal")
        fixed = {}
        for repo in repos:
            shard = repo["id"]
            if shard != "electron":
                result = git_search.query(args.base_index / f"{shard}.sqlite", repo["snapshot"], literal,
                                          recon / f"{name}-{shard}.jsonl", 0, directories=repo["directories"])
                fixed[shard] = result["count"]
        matches = {v["id"]: electron_matches(store, v["commit"], literal) for v in versions}
        totals = {key: len(paths) + sum(fixed.values()) for key, paths in matches.items()}
        cases.append({"id": name, "literal": literal, "fixed_repository_counts": fixed,
                      "electron_paths": matches, "expected_totals": totals})
        print(name, literal, totals, flush=True)
    if args.many == args.few or min(cases[0]["expected_totals"].values()) <= max(cases[1]["expected_totals"].values()):
        raise ValueError("the chosen cases must have different hit volumes")
    if not any(len({tuple(paths) for paths in case["electron_paths"].values()}) > 1 for case in cases):
        raise ValueError("neither literal changes its matched path set")

    changes = {}
    for parent, child in zip(versions, versions[1:]):
        raw = git(store, "diff-tree", "--no-commit-id", "-r", "--no-renames", "--name-only", "-z",
                  parent["commit"], child["commit"])
        changes[child["id"]] = [path.decode("utf-8", "surrogateescape") for path in raw.split(b"\0")[:-1]]
    write_json(args.plan, {"acquisition": acquisition, "frozen_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           "literals": cases, "first_parent_changed_paths": changes})


def prepare_version(args, version, repos, folder):
    scope, manifest = folder / "scope.json", folder / "manifest.json"
    scoped = []
    for repo in repos:
        pin = deepcopy(repo["snapshot"])
        if repo["id"] == "electron":
            pin.update(commit=version["commit"], root_tree=version["root_tree"])
        scoped.append({"id": repo["id"], "directories": repo["directories"],
                       **{key: pin[key] for key in ("repository", "url", "commit", "root_tree")}})
    write_json(scope, {"scope_version": 1, "repositories": scoped})
    preparation = checked_call(PROJECT / "scripts/prepare_r2_corpus.py", "--scope", scope,
                               "--sources", args.work_dir / "sources", "--manifest", manifest)
    return manifest, preparation


def prepare_index(args, manifest, folder):
    data = strict_json(manifest.read_bytes())
    electron = next(repo for repo in data["repositories"] if repo["id"] == "electron")
    subset, index = folder / "electron-manifest.json", folder / "index"
    totals = {"regular_paths": electron["snapshot"]["regular_paths"], **{key: electron[key] for key in (
        "regular_path_bytes", "distinct_regular_blobs", "distinct_regular_blob_bytes")}}
    write_json(subset, {**data, "repositories": [electron], "totals": totals})
    build = checked_call(CLI, "build", "--sources", args.work_dir / "sources", "--manifest", subset,
                         "--index", index, "--log-dir", folder / "build-log")
    for repo in data["repositories"]:
        if repo["id"] != "electron":
            shard = f"{repo['id']}.sqlite"
            os.link(args.base_index / shard, index / shard)
    return index, build


def published(folder, manifest, case, call, chain_input):
    response = strict_json(call["stdout"].encode("ascii"))
    receipt = strict_json((folder / "verification.json").read_bytes())
    digest = sha256_file(folder / "answer.jsonl")
    if (response["status"] != "VERIFIED" or receipt["status"] != "VERIFIED"
            or not Path(receipt["output_directory"]).samefile(folder)
            or receipt["literal"] != case["literal"] or receipt["manifest_sha256"] != sha256_file(manifest)
            or receipt["result_sha256"] != digest or response["result_sha256"] != digest):
        raise ValueError(f"{folder}: response is not bound to the published answer")
    if chain_input and (receipt["base_result_sha256"] != chain_input["sha256"]
                        or receipt["base_manifest_sha256"] != chain_input["manifest_sha256"]):
        raise ValueError(f"{folder}: published result broke the update chain")
    return {"output": str(folder), "sha256": digest, "manifest_sha256": receipt["manifest_sha256"],
            "chain_input": chain_input, "response": response, "subprocess": call}


def variant(args, version, cases, repos, kind, previous=None):
    started = perf_counter()
    folder = args.run_dir / version["id"] / kind
    folder.mkdir(parents=True)
    manifest, preparation = prepare_version(args, version, repos, folder)
    manifest_seconds = perf_counter() - started
    index_seconds, build = 0.0, None
    if kind == "full":
        index_start = perf_counter()
        index, build = prepare_index(args, manifest, folder)
        index_seconds = perf_counter() - index_start
        operation = "query-verified"
    else:
        operation = "update-verified"

    calls = []
    for case in cases:
        output = folder / case["id"]
        chain_input = None
        if kind == "delta":
            base = previous["answers"][case["id"]]
            chain_input = {key: base[key] for key in ("output", "sha256", "manifest_sha256")}
            specific = ("--base-manifest", previous["manifest"], "--base-answer", base["output"])
        else:
            specific = ("--index", index)
        result = checked_call(CLI, operation, *specific, "--sources", args.work_dir / "sources", "--manifest", manifest,
                              "--output-dir", output, "--log-dir", folder / (case["id"] + "-log"),
                              f"--literal={case['literal']}")
        calls.append((output, case, result, chain_input, perf_counter() - started))
    both = calls[-1][-1]
    answers = {}
    for output, case, call, base, elapsed in calls:
        answer = published(output, manifest, case, call, base)
        answers[case["id"]] = {**answer, "commit_to_answer_seconds": elapsed, "query_seconds": call["seconds"]}
    if strict_json(manifest.read_bytes())["totals"]["regular_paths"] != version["corpus_regular_paths"]:
        raise ValueError("measured manifest has a different file count than the frozen version")
    print(f"{version['id']} {kind}: both {both:.3f} s, manifest {manifest_seconds:.3f} s, index {index_seconds:.3f} s",
          flush=True)
    return {"manifest": str(manifest), "manifest_seconds": manifest_seconds, "manifest_subprocess": preparation,
            "index_seconds": index_seconds, "index_subprocess": build, "both_answers_seconds": both, "answers": answers}


def answer_bytes(answer):
    return (Path(answer["output"]) / "answer.jsonl").read_bytes()


def first_difference(candidate, full):
    for line, (a, b) in enumerate(zip_longest(candidate.splitlines(keepends=True), full.splitlines(keepends=True)), 1):
        if a != b:
            return {"line": line, "delta": a.decode("utf-8", "backslashreplace") if a is not None else None,
                    "full": b.decode("utf-8", "backslashreplace") if b is not None else None}
    return None


def compare(version, case, previous, delta, full):
    a, b, reference = (answer_bytes(answer) for answer in (previous, delta, full))
    old, new = hits(a), hits(b)
    positions = ("byte_offset", "line")
    shifted = []
    for key in sorted(old.keys() & new.keys()):
        before = {field: old[key][field] for field in positions}
        after = {field: new[key][field] for field in positions}
        if before != after:
            shifted.append({"repository": key[0], "path": key[1], "before": before, "after": after})
    expected = case["electron_paths"][version["id"]]
    return {"literal": case["literal"], "identical_bytes": b == reference,
            "first_difference": first_difference(b, reference) if b != reference else None,
            "matches_reconnaissance": sorted(path for repo, path in new if repo == "electron/electron") == expected
            and len(new) == delta["response"]["count"] == case["expected_totals"][version["id"]],
            "added": [new[key] for key in sorted(new.keys() - old.keys())],
            "removed": [old[key] for key in sorted(old.keys() - new.keys())], "first_hit_changes": shifted}


def measure(args):
    plan = strict_json(args.plan.read_bytes())
    acquisition = strict_json((args.work_dir / "acquisition.json").read_bytes())
    versions, cases = acquisition["versions"], plan["literals"]
    if (acquisition["base_manifest_sha256"] != sha256_file(args.base_manifest)
            or versions != plan["acquisition"]["versions"]):
        raise ValueError("the local sources and frozen plan differ")
    args.run_dir.mkdir(parents=True)
    repos = read_manifest(args.base_manifest)
    baseline = variant(args, versions[0], cases, repos, "full")
    write_json(args.run_dir / "A0.json", baseline)
    chain = baseline
    steps = []
    for i, version in enumerate(versions[1:], 1):
        order = ("delta", "full") if i % 2 else ("full", "delta")
        row = {"version": version, "order": order, "git_changed_paths": plan["first_parent_changed_paths"][version["id"]]}
        for kind in order:
            row[kind] = variant(args, version, cases, repos, kind, previous=chain)
        row["comparisons"] = {case["id"]: compare(version, case, chain["answers"][case["id"]],
                                                  row["delta"]["answers"][case["id"]], row["full"]["answers"][case["id"]])
                              for case in cases}
        chain = row["delta"]
        steps.append(row)
        write_json(args.run_dir / f"{version['id']}.json", row)

    for case in cases:
        label = case["id"]
        expected = baseline["answers"][label]
        for step in steps:
            result = step["delta"]["answers"][label]
            if result["chain_input"] != {key: expected[key] for key in ("output", "sha256", "manifest_sha256")}:
                raise ValueError("measured steps do not form a continuous chain")
            expected = result
    equivalent = sum(result["identical_bytes"] for step in steps for result in step["comparisons"].values())
    write_json(args.run_dir / "measurements.json", {"plan_sha256": sha256_file(args.plan), "acquisition": acquisition,
               "filesystem_cache": "enabled, not cleared", "baseline": baseline, "steps": steps,
               "continuous_chains": True, "identical_pairs": equivalent})
    print(f"Continuous chains, {equivalent}/10 byte-identical pairs", flush=True)
    if equivalent != 10 or not all(result["matches_reconnaissance"] for step in steps for result in step["comparisons"].values()):
        raise ValueError("answers differ; see the preserved result files and comparison records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    setup = commands.add_parser("acquire")
    setup.add_argument("--sources", type=Path, required=True)
    lock = commands.add_parser("freeze")
    lock.add_argument("--many", required=True)
    lock.add_argument("--few", required=True)
    run = commands.add_parser("measure")
    run.add_argument("--run-dir", type=lambda value: Path(value).resolve(), required=True)
    for command in (lock, run):
        command.add_argument("--base-index", type=Path, required=True)
        command.add_argument("--plan", type=Path, required=True)
    for command in (setup, lock, run):
        command.add_argument("--base-manifest", type=Path, default=PROJECT / "verification/r2-scale-manifest.json")
        command.add_argument("--work-dir", type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    if args.operation == "acquire":
        acquire_history(args)
    else:
        args.base_index = args.base_index.resolve()
        if args.operation == "freeze":
            freeze(args)
        else:
            measure(args)


if __name__ == "__main__":
    main()
