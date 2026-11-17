"""Independently compare complete literal results with a direct Git blob scan."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha1
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from time import perf_counter


class SourceUnavailable(ValueError):
    pass


def scan_git(store, pin, literals):
    environment = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    git = ["git", "--no-replace-objects", "-C", str(store.resolve())]

    def read(*args):
        return subprocess.check_output(git + list(args), env=environment,
                                       stderr=subprocess.PIPE, timeout=120)

    commit = read("cat-file", "commit", pin["commit"])
    header = b"commit %d\0" % len(commit)
    if (sha1(header + commit).hexdigest() != pin["commit"]
            or commit.partition(b"\n")[0] != b"tree " + pin["root_tree"].encode("ascii")):
        raise SourceUnavailable("Git commit bytes do not bind the pinned root")
    raw_tree = read("ls-tree", "--full-tree", "-r", "-z", pin["root_tree"])
    entries = raw_tree.split(b"\0")
    if entries.pop():
        raise SourceUnavailable("unterminated tree listing")
    paths_by_blob = defaultdict(list)
    modes = Counter()
    seen = set()
    for entry in entries:
        metadata, path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        if (not path or path in seen or not re.fullmatch(rb"[0-9a-f]{40}", oid)
                or kind != (b"commit" if mode == b"160000" else b"blob")
                or mode not in (b"100644", b"100755", b"120000", b"160000")):
            raise SourceUnavailable(f"invalid tree entry: {entry!r}")
        seen.add(path)
        modes[mode] += 1
        if mode in (b"100644", b"100755"):
            paths_by_blob[oid].append(path.decode("utf-8", "surrogateescape"))
    regular = modes[b"100644"] + modes[b"100755"]
    counts = {"regular_paths": regular, "symlinks": modes[b"120000"],
              "gitlinks": modes[b"160000"], "blob_paths": regular + modes[b"120000"]}
    if any(pin[key] != value for key, value in counts.items()):
        raise SourceUnavailable(f"pinned tree counts disagree: {counts}")

    patterns = [re.compile(re.escape(literal.encode("ascii"))) for literal in literals]
    expected = [{} for _ in literals]
    with tempfile.TemporaryFile() as requests:
        for oid in paths_by_blob:
            requests.write(oid + b"\n")
        requests.seek(0)
        with subprocess.Popen(git + ["cat-file", "--batch"], env=environment,
                              stdin=requests, stdout=subprocess.PIPE) as process:
            try:
                for oid, paths in paths_by_blob.items():
                    fields = process.stdout.readline().split()
                    if len(fields) != 3 or fields[:2] != [oid, b"blob"]:
                        raise SourceUnavailable(f"invalid Git batch response: {fields!r}")
                    size = int(fields[2])
                    raw = process.stdout.read(size)
                    digest = sha1(b"blob %d\0" % size)
                    digest.update(raw)
                    if (len(raw) != size or process.stdout.read(1) != b"\n"
                            or digest.hexdigest().encode("ascii") != oid):
                        raise SourceUnavailable(f"Git blob integrity failed: {oid!r}")
                    for pattern, hits in zip(patterns, expected):
                        match = pattern.search(raw)
                        if match is not None:
                            offset = match.start()
                            witness = (oid.decode("ascii"), offset, raw.count(b"\n", 0, offset) + 1)
                            hits.update((path, witness) for path in paths)
                if process.stdout.read(1) or process.wait(timeout=30):
                    raise SourceUnavailable("Git batch did not end successfully")
            finally:
                if process.poll() is None:
                    process.kill()
    return expected, {**counts, "distinct_regular_blobs": len(paths_by_blob)}


def compare(file, pin, literal, expected):
    start = perf_counter()
    identity = {"repository": pin["repository"], "commit": pin["commit"]}
    header = {"type": "result", "format": "git-literal-search-v1", **identity,
              "root_tree": pin["root_tree"], "literal": literal}
    problems = []
    seen = set()
    problem_count = 0
    complete = False

    def reject(message):
        nonlocal problem_count
        problem_count += 1
        if len(problems) < 8:
            problems.append(message)

    try:
        open_result = gzip.open if file.suffix == ".gz" else Path.open
        with open_result(file, "rb") as stream:
            if json.loads(stream.readline()) != header:
                reject("result header or pinned provenance differs")
            for row in map(json.loads, stream):
                if row.get("type") == "complete":
                    if type(row.get("count")) is not int or row["count"] != len(seen):
                        reject("completion count differs from unique returned paths")
                    if stream.read(1):
                        reject("records follow the completion marker")
                    complete = True
                    break
                path = row.get("path")
                if not isinstance(path, str) or path in seen:
                    reject(f"invalid or duplicate path: {path!r}")
                    continue
                seen.add(path)
                if (row.get("type") != "hit"
                        or any(row.get(key) != value for key, value in identity.items())):
                    reject(f"witness provenance differs: {path!r}")
                actual = (row.get("blob_id"), row.get("byte_offset"), row.get("line"))
                if (type(actual[1]) is not int or type(actual[2]) is not int
                        or actual != expected.get(path)):
                    reject(f"unexpected witness for {path!r}: {actual!r}; "
                           f"expected {expected.get(path)!r}")
    except (OSError, ValueError, AttributeError, EOFError) as exc:
        reject(f"cannot read a complete result: {exc}")
    if not complete:
        reject("missing completion marker")
    missing = expected.keys() - seen
    if missing:
        reject(f"{len(missing)} missing path(s); first examples: {sorted(missing)[:3]!r}")
    return {"literal": literal, "agrees": not problem_count,
            "expected_count": len(expected), "returned_unique_paths": len(seen),
            "discrepancies": problem_count, "examples": problems,
            "comparison_seconds": perf_counter() - start}


def verify(store, contract, result_dir):
    start = perf_counter()
    pin, literals = contract["snapshot"], contract["queries"]
    try:
        expected, inventory = scan_git(store, pin, literals)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        detail = getattr(exc, "stderr", None)
        reason = detail.decode("utf-8", "replace").strip() if detail else str(exc)
        return {"status": "BLOCKED", "reason": reason}
    scan_seconds = perf_counter() - start
    comparisons = []
    for number, (literal, hits) in enumerate(zip(literals, expected), 1):
        result = result_dir / f"{number:02d}.jsonl"
        if not result.exists() and result.with_suffix(".jsonl.gz").exists():
            result = result.with_suffix(".jsonl.gz")
        comparisons.append(compare(result, pin, literal, hits))
    agreements = sum(row["agrees"] for row in comparisons)
    return {"status": "PASS" if agreements == len(literals) else "FAIL", "inventory": inventory,
            "agreements": agreements, "query_count": len(literals), "queries": comparisons,
            "git_scan_seconds": scan_seconds, "verification_seconds": perf_counter() - start}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-dir", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_bytes())
    result = verify(args.git_dir, contract, args.result_dir)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 3}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
