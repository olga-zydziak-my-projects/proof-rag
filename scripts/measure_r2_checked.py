"""Measure first searches through the shared checked index and reproduce an exact omission."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import sqlite3

import psutil

from fineract_r2 import PROJECT, sha256_file, write_json
from fineract_r2_corpus import candidate, compare_corpus, read_manifest
from measure_r2_concurrency import (
    check_heads, control_answer, fresh_agent, read, seed_inventory, setup, summarize, utc, validate, wave,
)
from repo_proof.checked_index import checked_receipt
from run_r2_freshness_experiment import CURRENT, call, require


def hit_lines(path):
    rows = [(line, json.loads(line)) for line in path.read_bytes().splitlines(keepends=True)]
    return [(line, row) for line, row in rows if row["type"] == "hit"]


def omission(root, corpus, controls, seeds, checked):
    agent = fresh_agent(root, "omission", corpus, seeds, checked=checked)
    workspace = Path(agent["workspace"])
    config = Path(agent["config"])
    normal = Path(corpus["original_index"])
    repos = read_manifest(Path(corpus["manifest"]))
    for literal, control in controls.items():
        reference = hit_lines(Path(control["answer"]))
        electron = next((row for _, row in reference if row["repository"] == "electron/electron"), None)
        if electron is not None and len(reference) > 1:
            break
    else:
        raise ValueError("Omission needs a literal with multiple hits, including Electron")

    good = call(CURRENT, "query", literal)
    validate(good["stdout"], corpus, control, "query-checked")
    [latest] = (workspace / "latest").glob("*.json")
    pointer_before = latest.read_bytes()
    after_success = {path.name for path in (workspace / "runs").iterdir() if (path / "answer").exists()}
    damaged = root / "damaged-candidate"
    damaged.mkdir()
    shard = "electron.sqlite"
    for name in seeds:
        source = normal / f"{name}.sqlite"
        if source.name == shard:
            shutil.copyfile(source, damaged / source.name)
        else:
            os.link(source, damaged / source.name)
    verifier = Path(checked["directory"]) / shard
    copy = damaged / shard
    origin = normal / shard
    require(not copy.samefile(origin) and not copy.samefile(verifier) and not verifier.samefile(origin),
            "Omission must alter a physically separate candidate shard")
    hashes_before = {str(path): sha256_file(path) for path in (origin, verifier, copy)}
    require(hashes_before[str(origin)] == hashes_before[str(copy)], "Candidate copy differs before mutation")
    with closing(sqlite3.connect(copy)) as db, db:
        (oid,) = db.execute("SELECT oid FROM blobs WHERE instr(data, ?) = 0 LIMIT 1", (literal.encode("ascii"),)).fetchone()
        update = db.execute("UPDATE paths SET oid=? WHERE path=? AND oid=?",
                            (oid, electron["path"].encode("utf-8", "surrogateescape"), electron["blob_id"]))
        require(update.rowcount == 1, "Omission changed more or less than one path")

    staged = root / "omission-candidate" / "bundle" / "answer.jsonl"
    staged.parent.mkdir(parents=True)
    candidate(repos, damaged, literal, corpus["manifest_sha256"], staged)
    expected = [(line, row) for line, row in reference if row != electron]
    actual = hit_lines(staged)
    require(len(reference) == len(actual) + 1 and expected == actual, "Candidate does not omit exactly one hit")
    sections = [{row["path"]: (row["blob_id"], row["byte_offset"], row["line"]) for _, row in expected
                 if row["repository"] == repo["snapshot"]["repository"]} for repo in repos]
    shortened, _ = compare_corpus(staged, repos, literal, corpus["manifest_sha256"], sections, strict_order=True)
    candidate_hash = sha256_file(staged)

    original_config = read(config)
    changed = read(config)
    changed["corpora"]["default"]["seed_index"] = str(damaged)
    temporary = config.with_suffix(".tmp")

    def replace_config(data):
        write_json(temporary, data)
        os.replace(temporary, config)

    replace_config(changed)
    try:
        rejected = call(CURRENT, "query", literal, code=2)
        response = rejected["stdout"]
        require(response["status"] == "MISMATCH" and response["candidate_sha256"] == candidate_hash
                and response["checked_index_sha256"] == checked["receipt_sha256"]
                and response["full_git_scans"] == 0 and "result omits 1 Git path(s)" in response["reason"]
                and sum(row["count"] for row in response["candidate_counts"]) == shortened
                and sum(row["count"] for row in response["git_counts"]) == len(reference)
                and "output_directory" not in response
                and latest.read_bytes() == pointer_before
                and {path.name for path in (workspace / "runs").iterdir() if (path / "answer").exists()} == after_success,
                "Incomplete answer was published, changed latest, or failed outside answer comparison")
    finally:
        replace_config(original_config)

    restored = call(CURRENT, "query", literal)
    validate(restored["stdout"], corpus, control, "query-checked")
    hashes_after = {str(path): sha256_file(path) for path in (origin, verifier, copy)}
    require(all(hashes_before[str(path)] == hashes_after[str(path)] for path in (origin, verifier))
            and hashes_before[str(copy)] != hashes_after[str(copy)], "Unexpected index SHA-256 after omission")
    return {"literal": literal, "omitted": electron, "replacement_oid": oid, "full_count": len(reference),
            "candidate_count": shortened, "candidate_sha256": candidate_hash, "candidate": str(staged),
            "control": control, "only_difference_is_omitted_hit": True, "physical_copy": True,
            "hashes_before": hashes_before, "hashes_after": hashes_after, "rejection": rejected,
            "latest_before_rejection": json.loads(pointer_before), "latest_unchanged_after_rejection": True,
            "no_publication_on_rejection": True, "recovery_sha256": restored["stdout"]["result_sha256"],
            "recovery_output": restored["stdout"]["output_directory"], "recovery_byte_equal": True}


def measure(args, root, scale):
    checked = {"directory": str(args.checked_index.resolve(strict=True)),
               "receipt_sha256": read(args.preparation)["receipt_sha256"]}
    receipt = checked_receipt(Path(checked["directory"]), checked["receipt_sha256"])
    plan = read(args.queries)
    literals = [row["literal"] for row in plan["queries"]]
    require(plan["checked_index_sha256"] == checked["receipt_sha256"]
            and datetime.fromisoformat(plan["selected_utc"]) > datetime.fromisoformat(plan["receipt_written_utc"])
            and len(literals) == len(set(literals)) == 20 and all(len(literal.encode("ascii")) >= 3 for literal in literals),
            "Expected 20 unique new literals selected after this index was prepared")
    corpus = setup(root, scale, first_search=True)
    require(receipt["manifest_sha256"] == corpus["manifest_sha256"], "Checked index uses a different manifest")
    seeds = seed_inventory(corpus)
    initial_heads = check_heads(corpus)

    def control(item):
        position, literal = item
        reference = control_answer(root, corpus, position, literal)
        expected = plan["queries"][position - 1]["expected_counts_from_reconnaissance"]
        actual = read(Path(reference["answer"]).with_name("verification.json"))["repositories"]
        require([repo["count"] for repo in actual] == expected, f"Reconnaissance differs from full Git for {literal!r}")
        print(f"control {position}/20: {literal!r} {reference['count']} hits", flush=True)
        return literal, reference

    with ThreadPoolExecutor(max_workers=2) as workers:
        controls = dict(workers.map(control, enumerate(literals, 1)))
    write_json(root / "controls.json", controls)
    started = utc()
    solo = []
    for number, literal in enumerate(literals, 1):
        label = f"s{number:02}"
        solo.append(wave(root, label, [literal], corpus, controls, "checked-solo",
                         first_search=fresh_agent(root, label, corpus, seeds, checked=checked)))
    baselines = {w["requests"][0]["literal"]: w["wall_seconds"] for w in solo if w["verified"] == 1}
    checked_waves = []
    for repeat in range(1, 4):
        label = f"checked-{repeat}"
        checked_waves.append(wave(root, label, literals, corpus, controls, "checked", baselines,
                                  first_search=fresh_agent(root, label, corpus, seeds, checked=checked)))
        if repeat == 1:
            legacy = wave(root, "full-1", literals, corpus, controls, "full",
                          first_search=fresh_agent(root, "full-1", corpus, seeds))
    final_heads = check_heads(corpus)
    report = {"started_utc": started, "ended_utc": utc(), "sampled_host_ram_bytes": psutil.virtual_memory().total,
              "cache": "filesystem cache left active; no saved answers", "corpus": corpus,
              "heads_before": initial_heads, "heads_after": final_heads, "checked_index": checked,
              "preparation": read(args.preparation), "query_plan": plan, "controls": controls,
              "solo": solo, "checked": checked_waves, "full": legacy,
              "checked_summary": summarize(checked_waves), "full_summary": summarize([legacy])}
    write_json(args.measurements, report)
    write_json(args.omission, omission(root, corpus, controls, seeds, checked))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("work-dir", "checked-index", "preparation", "queries", "measurements", "omission"):
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    scale = (PROJECT / "local/r2-scale").resolve(strict=True)
    root = args.work_dir.resolve()
    require(root.is_relative_to(scale) and not args.measurements.exists() and not args.omission.exists(),
            "Use a new ignored work directory and new output paths")
    root.mkdir()
    os.environ["GIT_ALLOW_PROTOCOL"] = "file"
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    measure(args, root, scale)


if __name__ == "__main__":
    main()
