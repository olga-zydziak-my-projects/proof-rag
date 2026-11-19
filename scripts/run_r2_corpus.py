"""Record R2 corpus reconnaissance, repeated public queries and a single-hit omission."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import shutil
import sqlite3
from statistics import median
import subprocess
import sys
from time import perf_counter

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_corpus import candidate, compare_corpus, read_manifest
from repo_proof import git_search


CLI = PROJECT / "scripts/fineract_r2_corpus.py"


def invoke(args, index, label, literal):
    folder, log = (args.run_dir / f"{label}{suffix}" for suffix in ("", "-log"))
    argv = [sys.executable, "-B", "-X", "utf8", str(CLI), "query-verified", "--sources", str(args.sources),
            "--manifest", str(args.manifest), "--index", str(index), "--log-dir", str(log),
            "--output-dir", str(folder), f"--literal={literal}"]
    start = perf_counter()
    proc = subprocess.run(argv, cwd=PROJECT, capture_output=True, encoding="utf-8", timeout=270)
    elapsed = perf_counter() - start
    row = {"label": label, "literal": literal, "argv": argv, "wall_seconds": elapsed,
           "returncode": proc.returncode, "response": strict_json(proc.stdout.encode()), "stderr": proc.stderr,
           "published": folder.exists(), "resources": strict_json((log / "resource-report.json").read_bytes())}
    write_json(args.run_dir / f"{label}.json", row)
    print(f"{label}: {row['response']['status']}, {elapsed:.3f} s, {row['response'].get('count', '-')}", flush=True)
    return row


def verified(args, label, row, manifest_hash, frozen):
    folder = args.run_dir / label
    receipt = strict_json((folder / "verification.json").read_bytes())
    response = row["response"]
    if (row["returncode"] or response["status"] != "VERIFIED" or receipt["status"] != "VERIFIED"
            or Path(receipt["output_directory"]) != folder or receipt["manifest_sha256"] != manifest_hash
            or receipt["result_sha256"] != response["result_sha256"]
            or sha256_file(folder / "answer.jsonl") != receipt["result_sha256"]
            or [entry["count"] for entry in receipt["repositories"]] != frozen["counts"]):
        raise ValueError(f"{label}: published response failed the run checks")
    return receipt["result_sha256"]


def hit_bytes(path):
    with path.open("rb") as stream:
        return [raw for raw in stream if strict_json(raw)["type"] == "hit"]


def omission(args, repos, manifest_hash, frozen, baseline):
    good = args.run_dir / baseline / "answer.jsonl"
    raw_hits = hit_bytes(good)
    witnessed = [strict_json(raw) for raw in raw_hits]
    victim = witnessed[0]
    changed_repo = next(repo for repo in repos if repo["snapshot"]["repository"] == victim["repository"])
    def source_packs():
        return {path.relative_to(args.sources).as_posix(): sha256_file(path)
                for path in sorted(args.sources.glob("*.git/objects/pack/*.pack"))}

    source_hashes = source_packs()
    copy = args.run_dir / "omission-index"
    shutil.copytree(args.index, copy)
    original_db = args.index / (changed_repo["id"] + ".sqlite")
    before_hash = sha256_file(original_db)
    damaged = copy / original_db.name
    literal = frozen["literal"]
    with closing(sqlite3.connect(damaged)) as db, db:
        replacement, = db.execute("SELECT oid FROM blobs WHERE instr(data, ?) = 0 ORDER BY id LIMIT 1",
                                  (literal.encode("ascii"),)).fetchone()
        update = db.execute("UPDATE paths SET oid = ? WHERE path = ? AND oid = ?",
                            (replacement, victim["path"].encode("utf-8", "surrogateescape"), victim["blob_id"]))
        if update.rowcount != 1:
            raise ValueError("did not alter exactly one indexed path mapping")

    diagnostic = args.run_dir / "omission-candidate"
    diagnostic.mkdir()
    bad = diagnostic / "answer.jsonl"
    candidate(repos, copy, literal, manifest_hash, bad)
    if hit_bytes(bad) != raw_hits[1:]:
        raise ValueError("the shortened candidate differs by more than one original record")
    by_repo = {repo["snapshot"]["repository"]: {} for repo in repos}
    for hit in witnessed[1:]:
        by_repo[hit["repository"]][hit["path"]] = (hit["blob_id"], hit["byte_offset"], hit["line"])
    shortened, _ = compare_corpus(bad, repos, literal, manifest_hash, list(by_repo.values()))
    bad_hash = sha256_file(bad)
    bad_row = invoke(args, copy, "omission-rejected", literal)
    failure = bad_row["response"]
    if ((bad_row["returncode"], failure["status"], bad_row["published"]) != (2, "MISMATCH", False)
            or failure["candidate_sha256"] != bad_hash or len(raw_hits) != shortened + 1):
        raise ValueError("public verification did not reject the exact shortened candidate")

    recovery = invoke(args, args.index, "omission-recovery", literal)
    recovered = verified(args, "omission-recovery", recovery, manifest_hash, frozen)
    if (recovered != sha256_file(good) or (args.run_dir / "omission-recovery" / "answer.jsonl").read_bytes()
            != good.read_bytes() or sha256_file(original_db) != before_hash or source_packs() != source_hashes):
        raise ValueError("recovery differs from the original bytes")
    return {"literal": literal, "omitted_hit": victim, "replacement_indexed_blob": replacement,
            "complete_count": len(raw_hits), "candidate_count": shortened,
            "remaining_hit_records_identical_in_order": True, "candidate_sections_and_counts_valid": True,
            "rejection": bad_row, "candidate_sha256": bad_hash, "original_index_sha256": before_hash,
            "source_pack_sha256": source_hashes, "source_pack_hashes_unchanged": True,
            "recovery": recovery, "recovered_bytes_identical": True}


def measure(args):
    repos = read_manifest(args.manifest)
    digest = sha256_file(args.manifest)
    queries = strict_json(args.queries.read_bytes())["queries"]
    args.run_dir.mkdir(parents=True)
    rows, hashes = [], {}
    for repeat in range(1, 4):
        for query in queries:
            key = query["id"]
            label = f"{key}-{repeat:02d}"
            row = invoke(args, args.index, label, query["literal"])
            result_hash = verified(args, label, row, digest, query)
            if hashes.setdefault(key, result_hash) != result_hash:
                raise ValueError("answer bytes varied between repeated trials")
            rows.append(row)
    summary = {}
    for query in queries:
        key = query["id"]
        series = [row for row in rows if row["literal"] == query["literal"]]
        times = [row["wall_seconds"] for row in series]
        summary[key] = {"literal": query["literal"], "counts": query["counts"], "first": times[0],
                        "median": median(times), "min": min(times), "max": max(times),
                        "search_median": median(row["response"]["seconds"]["search"] for row in series),
                        "git_scan_median": median(row["response"]["seconds"]["git_scan"] for row in series),
                        "comparison_median": median(row["response"]["seconds"]["comparison"] for row in series),
                        "publication_median": median(row["response"]["publication_seconds"] for row in series)}
    write_json(args.run_dir / "measurements.json", {"manifest_sha256": digest, "queries_sha256": sha256_file(args.queries),
               "filesystem_cache": "enabled, not cleared; first means first timed trial", "trials": rows, "summary": summary})
    cross = next(query for query in queries if query["id"] == "cross")
    evidence = omission(args, repos, digest, cross, "cross-01")
    write_json(args.run_dir / "omission-evidence.json", evidence)


def recon(args):
    args.run_dir.mkdir(parents=True)
    rows = []
    for index, literal in enumerate(args.literal, 1):
        name = f"probe-{index:02d}"
        result = []
        for repo in read_manifest(args.manifest):
            shard = repo["id"]
            candidate = git_search.query(args.index / f"{shard}.sqlite", repo["snapshot"], literal,
                                         args.run_dir / f"{name}-{shard}.jsonl", 0, directories=repo["directories"])
            result.append(candidate["count"])
        rows.append({"literal": literal, "counts": result})
        print(json.dumps(rows[-1]), flush=True)
    write_json(args.run_dir / "reconnaissance.json", {"method": "index-only discovery; not timed trials", "rows": rows})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="phase", required=True)
    probe = commands.add_parser("recon")
    probe.add_argument("--literal", nargs="+", required=True)
    tests = commands.add_parser("measure")
    tests.add_argument("--queries", type=Path, required=True)
    tests.add_argument("--sources", type=Path, required=True)
    for subparser in (probe, tests):
        for name in ("manifest", "index", "run-dir"):
            subparser.add_argument("--" + name, type=lambda raw: Path(raw).resolve(), required=True)
    args = parser.parse_args()
    if args.phase == "recon":
        recon(args)
    else:
        args.sources = args.sources.resolve()
        measure(args)


if __name__ == "__main__":
    main()
