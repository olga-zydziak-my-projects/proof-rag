"""Materialize the Git blobs in a frozen scope and write its measured manifest."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
from time import perf_counter

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from repo_proof import git_search
from repo_proof.corpus import parse_tree


def acquire(store, args, data=None):
    subprocess.run(git_search.git_command(store, *args), input=data, check=True, timeout=600,
                   env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never"))


def fetch_one(oid_batch, store):
    args = ["-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-tags", "--no-recurse-submodules",
            "--no-auto-maintenance", "--no-write-fetch-head", "--filter=blob:none", "--stdin", "origin"]
    try:
        acquire(store, args, ("\n".join(oid_batch) + "\n").encode("ascii"))
    except subprocess.CalledProcessError:
        if len(oid_batch) <= 250:
            raise
        middle = len(oid_batch) // 2
        fetch_one(oid_batch[:middle], store)
        fetch_one(oid_batch[middle:], store)


def local_sizes(store, object_ids):
    if not object_ids:
        return {}, []
    batch = ("\n".join(object_ids) + "\n").encode("ascii")
    result = subprocess.check_output(git_search.git_command(store, "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)"), input=batch, env=git_search.git_env(), timeout=180)
    sizes, missing = {}, []
    for oid, line in zip(object_ids, result.decode("ascii").splitlines(), strict=True):
        if line == oid + " missing":
            missing.append(oid)
        else:
            actual, kind, size = line.split()
            if (actual, kind) != (oid, "blob"):
                raise ValueError(f"unexpected Git object {line}")
            sizes[oid] = int(size)
    return sizes, missing


def prepare(source, root, fetch, *, fetch_missing=None):
    started = perf_counter()
    store = root / (source["id"] + ".git")
    commit, tree, directories = (source[key] for key in ("commit", "root_tree", "directories"))
    if not store.exists() and fetch:
        subprocess.run(["git", "init", "--bare", "--object-format=sha1", store], check=True)
        acquire(store, ["remote", "add", "origin", source["url"]])
        acquire(store, ["fetch", "--depth=1", "--no-tags", "--filter=blob:none", "--no-recurse-submodules",
                        "origin", f"{commit}:refs/pins/corpus"])
    if git_search.git_read(store, "rev-parse", commit + "^{tree}").strip().decode() != tree:
        raise ValueError("commit tree differs from the frozen scope")
    for directory in directories:
        entry = git_search.git_read(store, "ls-tree", "-z", "--full-tree", commit, "--", directory)
        if not entry.startswith(b"040000 tree ") or entry.split(b"\t", 1)[1] != directory.encode() + b"\0":
            raise ValueError(f"scope is not a committed directory: {directory}")
    rows = parse_tree(git_search.git_read(store, "ls-tree", "-rz", "--full-tree", commit, "--", *directories))
    counts = Counter(row["category"] for row in rows)
    paths = Counter(row["object_id"] for row in rows if row["category"] == "regular")
    sizes, missing = local_sizes(store, list(paths))
    print(f"{source['id']}: {counts['regular']} regular paths, {len(paths)} distinct blobs, {len(missing)} to fetch",
          flush=True)
    if fetch_missing is None and fetch:
        fetch_missing = lambda batch: fetch_one(batch, store)
    if fetch_missing is not None:
        for start in range(0, len(missing), 6000):
            fetch_missing(missing[start:start + 6000])
            print(f"{source['id']}: fetched {min(start + 6000, len(missing))}/{len(missing)}", flush=True)
        if missing:
            sizes, missing = local_sizes(store, list(paths))
    if missing:
        raise ValueError(f"{source['id']}: {len(missing)} regular blobs are absent")
    pin = {key: source[key] for key in ("repository", "url", "commit", "root_tree")}
    pin.update(object_format="sha1", regular_paths=counts["regular"], blob_paths=counts["regular"] + counts["symlink"],
               symlinks=counts["symlink"], gitlinks=len(rows) - counts["regular"] - counts["symlink"])
    repo = {"id": source["id"], "directories": directories, "snapshot": pin,
            "distinct_regular_blobs": len(sizes), "distinct_regular_blob_bytes": sum(sizes.values()),
            "regular_path_bytes": sum(sizes[oid] * count for oid, count in paths.items())}
    print(f"{source['id']}: {repo['distinct_regular_blob_bytes']} unique blob bytes, {perf_counter()-started:.2f} s",
          flush=True)
    return repo, sizes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", type=Path, default=PROJECT / "verification/r2-scale-scope.json")
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--fetch", action="store_true", help="fetch missing pinned blobs from the declared origin")
    args = parser.parse_args()
    if args.manifest.exists():
        parser.error("the manifest output already exists")
    free = shutil.disk_usage(args.sources.resolve().anchor).free
    print(f"Free bytes before acquisition: {free}", flush=True)
    scope = strict_json(args.scope.read_bytes())
    args.sources.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as workers:
        results = list(workers.map(lambda source: prepare(source, args.sources, args.fetch), scope["repositories"]))
    unique = {}
    for _, sizes in results:
        unique.update(sizes)
    repos = [repo for repo, _ in results]
    totals = {"regular_paths": sum(repo["snapshot"]["regular_paths"] for repo in repos),
              "regular_path_bytes": sum(repo["regular_path_bytes"] for repo in repos),
              "distinct_regular_blobs": len(unique), "distinct_regular_blob_bytes": sum(unique.values())}
    write_json(args.manifest, {"format": "git-literal-corpus-manifest-v1", "scope_sha256": sha256_file(args.scope),
                               "repositories": repos, "totals": totals})


if __name__ == "__main__":
    main()
