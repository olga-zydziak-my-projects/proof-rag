"""Measure full public R2 CLI responses from simultaneous clients on Windows."""

import argparse
from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import closing
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from statistics import median
import subprocess
import sys
from threading import Barrier
from time import perf_counter_ns

import psutil

from fineract_r2 import PROJECT, sha256_file, strict_json, write_json
from fineract_r2_current import R2, compatible_shard, git, manifest_for, selected_heads
from run_r2_freshness_experiment import CURRENT, bare, call, require


LITERALS = (
    "BUILD=7339", "chrome://", "R2_SCALE_ABSENCE_SENTINEL_5F4C9029F1A6", "electron::",
    "navigator.clipboard", "namespace content", "140.0.7339.133", "mojom::", "X-Frame-Options",
    "content::BrowserContext", "namespace blink", "brave://", "test::", "chrome-extension://",
    "BUILDFLAG(IS_WIN)", "RenderFrameHost", "BrowserWindow", "electron_api", "addEventListener(", "std::move(",
)
LEVELS = (1, 2, 4, 8, 12, 16, 20)
REPEATS = 3
CLIENT_TIMEOUT = 300
SAMPLE_SECONDS = 0.025


def utc():
    return datetime.now(timezone.utc).isoformat()


def seconds(nanoseconds):
    return nanoseconds / 1e9


def read(path):
    return strict_json(path.read_bytes())


def setup(root, scale, *, first_search=False):
    frozen = PROJECT / "verification/r2-scale-manifest.json"
    repositories = read(frozen)["repositories"]
    sources = scale / "sources"
    index = scale / "index-01"
    config_repos, pins = [], []
    for entry in repositories:
        name, snapshot = entry["id"], entry["snapshot"]
        objects = (sources / (name + ".git") / "objects").resolve(strict=True)
        remote = root / "server" / (name + ".git")
        bare(remote, objects)
        if not first_search:
            bare(root / "agent/sources" / (name + ".git"), objects)
        branch = "bench/" + name
        git(remote, "update-ref", "refs/heads/" + branch, snapshot["commit"])
        repo = {"id": name, "repository": snapshot["repository"], "url": snapshot["url"],
                "directories": entry["directories"], "remote": remote.as_uri(), "branch": branch}
        config_repos.append(repo)
        pins.append({**repo, "commit": snapshot["commit"], "root_tree": snapshot["root_tree"],
                     "regular_paths": snapshot["regular_paths"], "git_objects": str(objects)})
    write_json(root / "config.json", {"corpora": {"default": {"workspace": "agent", "seed_index": str(index),
                                                              "repositories": config_repos}}})
    os.environ["REPO_PROOF_CURRENT_CONFIG"] = str(root / "config.json")
    manifest = root / "manifest.json"
    write_json(manifest, manifest_for(repositories))
    metadata = {"pins": pins, "regular_paths": sum(pin["regular_paths"] for pin in pins),
                "config": str(root / "config.json"), "manifest": str(manifest),
                "manifest_sha256": sha256_file(manifest), "original_index": str(index), "original_sources": str(sources)}
    write_json(root / "corpus.json", metadata)
    check_heads(metadata)
    return metadata


def seed_inventory(corpus):
    build = read(PROJECT / "verification/r2-scale-build.json")["response"]["shards"]
    index = Path(corpus["original_index"])
    proof = {}
    for repo in read(Path(corpus["manifest"]))["repositories"]:
        name = repo["id"]
        shard = index / f"{name}.sqlite"
        require(compatible_shard(shard, repo), f"Incompatible seed shard {shard}")
        digest = sha256_file(shard)
        require(digest == build[name]["sha256"], f"Seed bytes differ from the recorded build: {shard}")
        proof[name] = {"path": str(shard), "sha256": digest}
    return proof


def fresh_agent(root, label, corpus, seeds, *, checked=None):
    workspace = root / "agents" / label
    workspace.mkdir(parents=True)
    config = read(Path(corpus["config"]))
    entry = config["corpora"]["default"]
    entry["workspace"] = "."
    if checked is not None:
        entry["checked_index"] = checked
    config_path = workspace / "config.json"
    write_json(config_path, config)
    os.environ["REPO_PROOF_CURRENT_CONFIG"] = str(config_path)
    shards = {}
    for repo in read(Path(corpus["manifest"]))["repositories"]:
        name = repo["id"]
        pin = repo["snapshot"]
        store = workspace / "sources" / f"{name}.git"
        objects = Path(next(entry["git_objects"] for entry in corpus["pins"] if entry["id"] == name))
        bare(store, objects)
        require(git(store, "rev-parse", "--verify", pin["commit"] + "^{tree}").decode("ascii").strip()
                == pin["root_tree"], f"Git objects missing for {name}")
        shard = Path(seeds[name]["path"])
        require(compatible_shard(shard, repo), f"Incompatible seed shard {shard}")
        with closing(sqlite3.connect(shard.as_uri() + "?mode=ro", uri=True)) as db:
            (paths,) = db.execute("SELECT count(*) FROM paths").fetchone()
            (blobs,) = db.execute("SELECT count(*) FROM blobs").fetchone()
        require((paths, blobs) == (pin["regular_paths"], repo["distinct_regular_blobs"]),
                f"Seed inventory differs for {name}")
        shards[name] = {**seeds[name], "regular_paths": paths, "distinct_regular_blobs": blobs,
                        "commit": pin["commit"], "root_tree": pin["root_tree"], "directories": repo["directories"]}
    return {"workspace": str(workspace), "config": str(config_path), "shards": shards,
            **({"checked_index": checked} if checked is not None else {})}


def first_search_controls(root, corpus, control_run):
    if control_run is None:
        controls = {literal: control_answer(root, corpus, number, literal)
                    for number, literal in enumerate(LITERALS, 1)}
    else:
        previous = read(control_run / "corpus.json")
        require(Path(previous["manifest"]).read_bytes() == Path(corpus["manifest"]).read_bytes(),
                "The control run did not use the exact same corpus manifest")
        controls = read(control_run / "controls.json")
    require(set(controls) == set(LITERALS), "The controls must cover all measured literals")
    expected = [(pin["repository"], pin["regular_paths"]) for pin in corpus["pins"]]
    for literal, control in controls.items():
        artifact = Path(control["answer"]).resolve(strict=True)
        require(not artifact.is_relative_to(root / "agents"), "A control is inside a measured agent workspace")
        receipt = read(artifact.with_name("verification.json"))
        inventories = [(row["repository"], row["regular_paths"]) for row in receipt["inventories"]]
        require(control["literal"] == receipt["literal"] == literal and receipt["status"] == "VERIFIED"
                and receipt["manifest_sha256"] == corpus["manifest_sha256"] and inventories == expected
                and Path(receipt["output_directory"]).samefile(artifact.parent)
                and receipt["result_sha256"] == control["result_sha256"] == sha256_file(artifact)
                and receipt["count"] == control["count"], f"Invalid full Git control for {literal!r}")
    return controls


def inspect_first_search(workspace, shards):
    runs = {}
    for run in sorted((workspace / "runs").glob("*")):
        build = (run / "build-log").exists() or (run / "index-manifest.json").exists()
        reused = {}
        for name, seed in shards.items():
            path = run / "index" / f"{name}.sqlite"
            if path.is_file():
                if path.samefile(seed["path"]):
                    reused[name] = "hardlink"
                elif sha256_file(path) == seed["sha256"]:
                    reused[name] = "identical_copy"
                else:
                    reused[name] = "different"
        runs[run.name] = {"build_detected": build, "index_shards": reused, "answer_exists": (run / "answer").is_dir()}
    return runs


def branch_identity(selection):
    return [(repo["id"], repo["repository"], repo["remote"], repo["branch"], repo["commit"]) for repo in selection]


def check_heads(corpus):
    heads = selected_heads(corpus["pins"])
    require(branch_identity(heads) == branch_identity(corpus["pins"]), "Configured branches changed")
    return heads


def control_answer(root, corpus, position, literal):
    folder = root / "control" / f"{position:02}"
    answer = folder / "answer"
    measured = call(R2, "query-verified", "--sources", corpus["original_sources"],
                    "--manifest", corpus["manifest"], "--index", corpus["original_index"],
                    "--output-dir", answer, "--log-dir", folder / "log", f"--literal={literal}")
    response = measured["stdout"]
    receipt = read(answer / "verification.json")
    digest = sha256_file(answer / "answer.jsonl")
    require(response["status"] == receipt["status"] == "VERIFIED" and receipt["literal"] == literal
            and receipt["manifest_sha256"] == response["manifest_sha256"] == corpus["manifest_sha256"]
            and receipt["result_sha256"] == response["result_sha256"] == digest
            and Path(receipt["output_directory"]).samefile(answer), f"Invalid independent control for {literal!r}")
    write_json(folder / "process.json", measured)
    return {"literal": literal, "count": receipt["count"], "result_sha256": digest,
            "answer": str(answer / "answer.jsonl"), "seconds": measured["wall_seconds"]}


def validate(response, corpus, control, operation):
    literal = control["literal"]
    require(response["status"] == "VERIFIED" and response["operation"] == operation and response["literal"] == literal,
            "CLI did not return VERIFIED for the expected operation and literal")
    require(branch_identity(response["selection"]["repositories"]) == branch_identity(corpus["pins"]),
            "Selected repositories, branches or commits differ from the pinned corpus")
    answer = Path(response["output_directory"])
    manifest = Path(response["manifest"])
    require(manifest.samefile(answer.parent / "manifest.json") and manifest.read_bytes() == Path(corpus["manifest"]).read_bytes()
            and response["manifest_sha256"] == corpus["manifest_sha256"], "Published manifest differs")
    receipt = read(answer / "verification.json")
    payload = (answer / "answer.jsonl").read_bytes()
    require(Path(receipt["output_directory"]).samefile(answer)
            and receipt["status"] == "VERIFIED" and receipt["literal"] == literal
            and receipt["manifest_sha256"] == corpus["manifest_sha256"]
            and sha256(payload).hexdigest() == receipt["result_sha256"] == response["result_sha256"],
            "Standalone R2 receipt does not bind the published bytes")
    require(response["answer"] == [strict_json(line) for line in payload.splitlines()],
            "Complete stdout JSON differs from the published answer")
    require(payload == Path(control["answer"]).read_bytes()
            and receipt["result_sha256"] == control["result_sha256"]
            and response["count"] == receipt["count"] == control["count"], "Answer differs from the independent Git scan")
    if operation == "update-verified":
        require(response["base_result_sha256"] == control["result_sha256"]
                and response["base_manifest_sha256"] == corpus["manifest_sha256"]
                and all(download["fetches"] == 0 for download in response["downloads"])
                and all(row["git_objects_read"]["blob"]["count"] == 0 for row in response["delta"]),
                "Unexpected cold data, changed pins or blob scan in a warmed query")


def prepare(root, corpus):
    controls = {}
    (root / "warm").mkdir()
    with ThreadPoolExecutor(max_workers=2) as clients:
        for number, literal in enumerate(LITERALS, 1):
            control = clients.submit(control_answer, root, corpus, number, literal)
            warm = call(CURRENT, "query", literal)
            reference = control.result()
            validate(warm["stdout"], corpus, reference, "query-verified")
            write_json(root / "warm" / f"{number:02}.json", {
                "literal": literal, "seconds": warm["wall_seconds"], "output_directory": warm["stdout"]["output_directory"],
                "result_sha256": warm["stdout"]["result_sha256"], "status": warm["stdout"]["status"],
            })
            controls[literal] = reference
            print(f"prepared {number}/{len(LITERALS)}: {literal!r} ({reference['count']} hits)", flush=True)
    write_json(root / "controls.json", controls)
    return controls


def process_interval(process):
    # Popen keeps its Windows process handle open after communicate(), even after PID exit.
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    get_times = api.GetProcessTimes
    get_times.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
    get_times.restype = wintypes.BOOL
    created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
    if not get_times(int(process._handle), created, exited, kernel, user):
        raise ctypes.WinError(ctypes.get_last_error())
    return [(value.dwHighDateTime << 32) | value.dwLowDateTime for value in (created, exited)]


def request(barrier, argv, literal):
    barrier.wait(timeout=30)
    row = {"literal": literal, "launch_ns": perf_counter_ns()}
    try:
        process = subprocess.Popen(argv, cwd=PROJECT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.DEVNULL)
    except OSError as exc:
        return {**row, "ended_ns": perf_counter_ns(), "error": f"Launch failed: {exc}"}, b"", b""
    with process:
        row["pid"] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=CLIENT_TIMEOUT)
        except subprocess.TimeoutExpired:
            row["error"] = f"Timeout after {CLIENT_TIMEOUT} s"
            try:
                children = psutil.Process(process.pid).children(recursive=True)
                for child in reversed(children):
                    try:
                        child.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            process.kill()
            stdout, stderr = process.communicate()
        row["ended_ns"] = perf_counter_ns()
        row["returncode"] = process.returncode
        try:
            row["process_filetime"] = process_interval(process)
        except OSError as exc:
            row["overlap_measurement_error"] = str(exc)
    return row, stdout, stderr


def snapshot(parent, start):
    rss = 0
    processes = parent.children(recursive=True)
    for process in processes:
        try:
            rss += process.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return {"seconds": seconds(perf_counter_ns() - start), "rss_bytes": rss, "processes": len(processes),
            "host_available_bytes": psutil.virtual_memory().available, "host_cpu_percent": psutil.cpu_percent()}


def max_overlap(rows):
    edges = sorted((instant, change) for row in rows if "process_filetime" in row
                   for instant, change in zip(row["process_filetime"], (1, -1), strict=True))
    active = peak = 0
    for _, change in edges:
        active += change
        peak = max(peak, active)
    return peak


def wave(root, label, literals, corpus, controls, scenario, baseline=None, *, first_search=None):
    release_ns = None

    def release():
        nonlocal release_ns
        release_ns = perf_counter_ns()

    barrier = Barrier(len(literals) + 1, action=release)
    argv = [[sys.executable, "-B", "-X", "utf8", str(CURRENT), "query", literal] for literal in literals]
    operation = "update-verified"
    if first_search is not None:
        operation = "query-checked" if "checked_index" in first_search else "query-verified"
        workspace = Path(first_search["workspace"])
        entries = sorted(path.name for path in workspace.iterdir())
        require(entries == ["config.json", "sources"], f"Agent workspace is not fresh: {workspace}")
        first_search = {**first_search, "checked_utc": utc(), "entries_before": entries,
                        "publications_before": 0, "latest_before": 0}
    parent = psutil.Process()
    psutil.cpu_percent()
    with ThreadPoolExecutor(max_workers=len(literals)) as workers:
        futures = [workers.submit(request, barrier, command, literal)
                   for command, literal in zip(argv, literals, strict=True)]
        barrier.wait(timeout=30)
        samples = []
        while True:
            samples.append(snapshot(parent, release_ns))
            if not wait(futures, timeout=SAMPLE_SECONDS).not_done:
                break
        replies = [future.result() for future in futures]

    folder = root / "responses" / label
    folder.mkdir(parents=True)
    if first_search is not None:
        runs = inspect_first_search(workspace, first_search["shards"])
    rows = []
    for number, (row, stdout, stderr) in enumerate(replies, 1):
        row["user_seconds"] = seconds(row["ended_ns"] - release_ns)
        row["launch_delay_seconds"] = seconds(row.pop("launch_ns") - release_ns)
        row["stdout_bytes"], row["stderr_bytes"] = len(stdout), len(stderr)
        row["capture"] = str(folder / f"{number:02}.json")
        Path(row["capture"]).write_bytes(stdout)
        if stderr:
            (folder / f"{number:02}.err").write_bytes(stderr)
        try:
            response = strict_json(stdout)
            row.update({key: response[key] for key in ("status", "operation", "count", "current_seconds",
                                                       "result_sha256", "output_directory", "candidate_reads",
                                                       "verifier_reads", "full_git_scans", "git_repositories_scanned")
                        if key in response})
            if "inventories" in response:
                row["git_blob_reads"] = [{"repository": repo["repository"], "objects": repo["distinct_regular_blobs"],
                                          "blob_bytes": repo["distinct_regular_blob_bytes"]}
                                         for repo in response["inventories"]]
            if "selection" in response:
                row["branch_resolved_unix_ns"] = [repo["resolved_unix_ns"] for repo in response["selection"]["repositories"]]
                row["observation"] = response["selection"]["observation"]
            if "seconds" in response:
                row["r2_seconds"] = response["seconds"]
            if "publication_seconds" in response:
                row["publication_seconds"] = response["publication_seconds"]
            require("error" not in row and row["returncode"] == 0,
                    response.get("reason", f"CLI exit {row.get('returncode')}"))
            validate(response, corpus, controls[row["literal"]], operation)
            if first_search is not None:
                published = Path(response["output_directory"])
                require(published.parent.parent.samefile(workspace / "runs"), "Publication is outside the fresh workspace")
                proof = runs[published.parent.name]
                require(not proof["build_detected"] and proof["answer_exists"], "Unexpected build or absent publication")
                if operation == "query-checked":
                    require(response["checked_index_sha256"] == first_search["checked_index"]["receipt_sha256"]
                            and response["full_git_scans"] == 0 and not proof["index_shards"]
                            and len(response["verifier_reads"]) == len(corpus["pins"]),
                            "Query did not use the shared authenticated verification data")
                else:
                    require(set(proof["index_shards"]) == set(first_search["shards"])
                            and all(kind != "different" for kind in proof["index_shards"].values())
                            and all(download["commit_present_before_fetch"] and download["fetches"] == 0
                                    for download in response["downloads"]),
                            "Query did not reuse all seed shards and local Git objects")
            row["verified_equal"] = True
        except (OSError, ValueError, KeyError, TypeError) as exc:
            row["verified_equal"] = False
            row.setdefault("error", str(exc))
        if baseline and row["literal"] in baseline:
            row["solo_median_seconds"] = baseline[row["literal"]]
            row["relative_to_solo"] = row["user_seconds"] / row["solo_median_seconds"]
        rows.append(row)
    result = {"label": label, "scenario": scenario, "clients": len(rows), "release_perf_counter_ns": release_ns,
              "wall_seconds": max(row["user_seconds"] for row in rows), "max_overlap": max_overlap(rows),
              "overlap_intervals": sum("process_filetime" in row for row in rows),
              "peak_tree_rss_bytes": max(sample["rss_bytes"] for sample in samples),
              "host_min_available_bytes": min(sample["host_available_bytes"] for sample in samples),
              "peak_tree_processes": max(sample["processes"] for sample in samples),
              "samples": len(samples), "memory_samples": str(folder / "memory.json"),
              "verified": sum(row["verified_equal"] for row in rows), "requests": rows}
    if first_search is not None:
        result["first_search"] = first_search
        result["first_search_runs"] = runs
    write_json(folder / "memory.json", samples)
    write_json(folder / "wave.json", result)
    print(f"{label}: {result['verified']}/{len(rows)} verified, {result['max_overlap']} overlap, "
          f"{result['wall_seconds']:.3f} s", flush=True)
    return result


def summarize(waves):
    rows = [row for run in waves for row in run["requests"]]
    answers = sum(run["verified"] for run in waves)
    resolution = [row["current_seconds"]["resolve_branches"] for row in rows if "current_seconds" in row]
    return {"scenario": waves[0]["scenario"], "clients": waves[0]["clients"], "waves": len(waves),
            "requests": len(rows), "verified": answers, "errors": len(rows) - answers,
            "median_seconds": median(row["user_seconds"] for row in rows),
            "max_seconds": max(row["user_seconds"] for row in rows),
            "answers_per_second": answers / sum(run["wall_seconds"] for run in waves),
            "peak_tree_rss_bytes": max(run["peak_tree_rss_bytes"] for run in waves),
            "max_overlap_per_wave": [run["max_overlap"] for run in waves],
            "resolve_branches_median_seconds": median(resolution) if resolution else None,
            "wall_seconds_per_wave": [run["wall_seconds"] for run in waves]}


def first_search_trials(root, corpus, controls, seeds):
    solo, baselines = {}, {}
    for number, literal in enumerate(LITERALS, 1):
        label = f"b{number:02}"
        trial = wave(root, label, [literal], corpus, controls, "first-solo",
                     first_search=fresh_agent(root, label, corpus, seeds))
        solo[literal] = [trial]
        if trial["verified"] == 1:
            baselines[literal] = trial["wall_seconds"]
    waves = []
    for repeat in range(1, REPEATS + 1):
        label = f"first-{repeat}"
        waves.append(wave(root, label, LITERALS, corpus, controls, "first-mixed", baselines,
                          first_search=fresh_agent(root, label, corpus, seeds)))
    return solo, baselines, waves, [summarize(waves)]


def warmed_trials(root, corpus, controls):
    solo, baselines = {}, {}
    for number, literal in enumerate(LITERALS, 1):
        solo[literal] = [wave(root, f"b{number:02}-{rep + 1}", [literal], corpus, controls, "solo")
                         for rep in range(REPEATS)]
        baseline = [run["wall_seconds"] for run in solo[literal] if run["verified"] == 1]
        if baseline:
            baselines[literal] = median(baseline)
    waves = []
    for count in LEVELS:
        for rep in range(REPEATS):
            scenarios = (("same", ["chrome://"] * count), ("mixed", LITERALS[:count]))
            for mode, literals in (scenarios if (rep + LEVELS.index(count)) % 2 == 0 else reversed(scenarios)):
                waves.append(wave(root, f"{mode}-{count:02}-{rep + 1}", literals, corpus, controls, mode, baselines))
    summary = [summarize([run for run in waves if (run["scenario"], run["clients"]) == (scenario, level)])
               for scenario in ("same", "mixed") for level in LEVELS]
    return solo, baselines, waves, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--first-search", action="store_true", help="measure with a fresh answer store for every wave")
    parser.add_argument("--control-run", type=Path, help="reuse independent full Git controls from this previous run")
    args = parser.parse_args()
    if args.control_run is not None and not args.first_search:
        parser.error("--control-run requires --first-search")
    require(sys.platform == "win32", "Windows process measurement is required")
    scale = (PROJECT / "local/r2-scale").resolve(strict=True)
    root = args.work_dir.resolve()
    require(root.is_relative_to(scale) and not args.measurements.exists(), "Use a new ignored work directory")
    root.mkdir()
    os.environ["GIT_ALLOW_PROTOCOL"] = "file"
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    corpus = setup(root, scale, first_search=args.first_search)
    if args.first_search:
        controls = first_search_controls(root, corpus, args.control_run)
        seeds = seed_inventory(corpus)
    else:
        controls = prepare(root, corpus)
    benchmark_started = utc()
    initial_heads = check_heads(corpus)
    if args.first_search:
        solo, baselines, waves, summary = first_search_trials(root, corpus, controls, seeds)
    else:
        solo, baselines, waves, summary = warmed_trials(root, corpus, controls)
    final_heads = check_heads(corpus)
    metadata = {"started_utc": benchmark_started, "ended_utc": utc(), "logical_cpus": psutil.cpu_count(),
                "physical_cpus": psutil.cpu_count(logical=False), "ram_bytes": psutil.virtual_memory().total,
                "python": sys.version, "git_protocol": "file",
                "cache": "filesystem cache left active; no saved answers" if args.first_search
                else "warmed; filesystem cache left active",
                "client_timeout_seconds": CLIENT_TIMEOUT, "sampler_wait_seconds": SAMPLE_SECONDS}
    report = {"corpus": corpus, "benchmark": metadata, "heads_before": initial_heads, "heads_after": final_heads,
              "controls": controls, "literal_order": LITERALS, "solo_medians_seconds": baselines,
              "solo": solo, "waves": waves, "summary": summary}
    if args.first_search:
        report["control_run"] = str(args.control_run.resolve() if args.control_run else root)
    write_json(args.measurements, report)


if __name__ == "__main__":
    main()
