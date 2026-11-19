"""Profile the R2 verifier against complete, already-published corpus answers."""

import argparse
import cProfile
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter


def direct_calls(entries, function):
    return {call.code: call for call in entries[function.__code__].calls or ()}


def profile_scan(oracle, sources, repo, literal, scratch):
    profiler = cProfile.Profile()
    started = perf_counter()
    with profiler:
        hits, inventory = oracle.scan_git(
            sources / f"{repo['id']}.git", repo["snapshot"], repo["distinct_regular_blobs"], literal,
            scratch, directories=repo["directories"], include_sizes=True,
        )
    elapsed = perf_counter() - started
    entries = {entry.code: entry for entry in profiler.getstats()}
    batch = direct_calls(entries, oracle.batch_objects)
    scan = direct_calls(entries, oracle.scan_git)
    reads = [batch[f"<method '{name}' of '_io.BufferedReader' objects>"] for name in ("read", "readline")]
    search = scan["<method 'search' of 're.Pattern' objects>"]
    hashes = entries[oracle.check_object.__code__]
    pipe = sum(call.totaltime for call in reads)
    if search.callcount != repo["distinct_regular_blobs"] or any(
        inventory[key] != repo[key] for key in ("distinct_regular_blob_bytes", "regular_path_bytes")
    ):
        raise ValueError("profile must scan the complete pinned scope")
    return hits, {
        "repository": repo["snapshot"]["repository"], "seconds": elapsed, "batch_pipe_seconds": pipe,
        "sha1_check_seconds": hashes.totaltime, "literal_search_seconds": search.totaltime,
        "remaining_seconds": elapsed - pipe - hashes.totaltime - search.totaltime,
        "batch_pipe_calls": sum(call.callcount for call in reads), "hash_calls": hashes.callcount,
        "literal_search_calls": search.callcount, "hits": len(hits),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, default=Path(__file__).resolve().parents[1])
    for name in ("sources", "manifest", "queries", "answers", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    code_root = args.code_root.resolve()
    sys.path.insert(0, str(code_root / "scripts"))
    from fineract_r2 import sha256_file, strict_json, write_json
    from fineract_r2_corpus import compare_corpus, read_manifest
    from repo_proof import fineract_oracle

    repos = read_manifest(args.manifest)
    manifest_hash = sha256_file(args.manifest)
    cases = strict_json(args.queries.read_bytes())["queries"]
    rows = []
    with TemporaryDirectory(dir=args.report.resolve().parent) as scratch:
        for case in cases:
            literal = case["literal"]
            expected, profiles = zip(*(profile_scan(fineract_oracle, args.sources.resolve(), repo, literal, scratch)
                                       for repo in repos), strict=True)
            answer = args.answers / f"{case['id']}-01" / "answer.jsonl"
            started = perf_counter()
            count, per_repo = compare_corpus(answer, repos, literal, manifest_hash, expected)
            comparison = perf_counter() - started
            if [entry["count"] for entry in per_repo] != case["counts"]:
                raise ValueError("profile disagrees with the frozen counts")
            row = {"id": case["id"], "literal": literal, "hit_count": count, "repositories": profiles,
                   "comparison_seconds": comparison, "answer_sha256": sha256_file(answer)}
            row["totals"] = {name: sum(detail[name] for detail in profiles) for name in (
                "seconds", "batch_pipe_seconds", "sha1_check_seconds", "literal_search_seconds", "remaining_seconds")}
            rows.append(row)
            print(f"{case['id']}: {row['totals']}, comparison={comparison:.3f}s", flush=True)
    write_json(args.report, {
        "method": "Separate serial cProfile scans; batch pipe includes Git producer, I/O, decompression and waiting."
                  " Comparison timed separately without cProfile.",
        "manifest_sha256": manifest_hash, "queries_sha256": sha256_file(args.queries),
        "oracle_sha256": sha256_file(Path(fineract_oracle.__file__)), "cases": rows,
    })


if __name__ == "__main__":
    main()
