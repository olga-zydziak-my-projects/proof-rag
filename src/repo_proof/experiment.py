"""Offline Mojom extraction/query experiment and source-bound replay CLI."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

from . import corpus
from .checker import verify_certificate
from .extraction import (CONTRACT, ExpectedInputs, SourceBindingError,
                         extract_corpus, read_json)
from .generator import generate_certificate
from .graph import ValidationError, graph_sha256
from .instance import FILE_INFO, TIME_ROOT, verify_instance

ARTIFACTS = ("extraction.json", "graph.json", "certificate.json", "query.json")


def independent_inputs(config_path, lock_path, root):
    """These files/CLI arguments are verifier trust inputs, outside the bundle."""
    config, lock = read_json(config_path), read_json(lock_path)
    if (lock.get("repository") != corpus.REPOSITORY or config.get("repository") != corpus.REPOSITORY
            or lock.get("commit") != corpus.COMMIT or config.get("commit") != corpus.COMMIT):
        raise SourceBindingError("independent local config/lock differs from pinned Chromium repository/commit")
    expected = ExpectedInputs(lock["commit"], lock["manifest_sha256"], root, CONTRACT)
    expected.validate()
    return Path(config["data_dir"]).resolve(), expected


def file_hashes(directory):
    return {name: hashlib.sha256((Path(directory) / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def base_report(expected, directory):
    return {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "artifact_dir": str(Path(directory).resolve()), "commit": expected.commit,
            "expected_manifest_sha256": expected.manifest_sha256, "expected_root": expected.root,
            "expected_contract_version": expected.contract_version,
            "artifact_file_sha256": file_hashes(directory),
            "timing_note": "Single observed wall-clock runs; replay repeats corpus verification and the same parser, not an independent parser proof."}


def run_experiment(data_dir, expected, directory):
    extraction, times = extract_corpus(data_dir, expected)
    if expected.root not in extraction["graph"]["nodes"]:
        raise SourceBindingError("expected query root is out_of_scope")
    before_search = perf_counter()
    certificate = generate_certificate(extraction["graph"], expected.root)
    after_search = perf_counter()
    verify_certificate(extraction["graph"], expected.root, certificate)
    after_certificate = perf_counter()
    result, full_times = verify_instance(data_dir, expected, extraction, certificate,
                                         graph=extraction["graph"])
    values = (extraction, extraction["graph"], certificate, result)
    directory = Path(directory)
    for name, value in zip(ARTIFACTS, values):
        corpus.atomic_write(directory / name, corpus.encoded(value))
    return {**base_report(expected, directory), "status": result["status"],
            "coverage": extraction["coverage"], "result_count": result["result_count"],
            "graph_sha256": extraction["graph_sha256"],
            "graph_certificate_status": result["graph_certificate_status"],
            "contract_examples": result["contract_examples"],
            "unresolved_files": [{"path": r["path"], "diagnostics": r["diagnostics"]}
                                 for r in extraction["files"] if r["status"] == "unresolved"],
            "corpus_diagnostics": extraction["corpus_diagnostics"],
            "outside_scope": [item for r in extraction["files"] for item in r["imports"]
                              if item["status"] == "outside_scope"],
            "timings_seconds": {**times,
                                "search_and_certificate": after_search - before_search,
                                "graph_certificate_verification": after_certificate - after_search,
                                **full_times}}


def verify_bundle(data_dir, expected, directory):
    directory = Path(directory)
    extraction, graph, certificate, supplied_result = [read_json(directory / name) for name in ARTIFACTS]
    result, times = verify_instance(data_dir, expected, extraction, certificate,
                                    graph=graph, result=supplied_result)
    return {**base_report(expected, directory), "status": result["status"],
            "coverage": extraction["coverage"], "result_count": result["result_count"],
            "graph_sha256": extraction["graph_sha256"],
            "graph_certificate_status": result["graph_certificate_status"],
            "contract_examples": result["contract_examples"], "timings_seconds": times}


def tampering_demo(data_dir, expected, directory):
    directory = Path(directory)
    extraction, graph, certificate, supplied_result = [read_json(directory / name) for name in ARTIFACTS]
    verify_instance(data_dir, expected, extraction, certificate, graph=graph, result=supplied_result)
    included = {item["node"] for item in certificate["candidates"]}
    removable = sorted(included - {expected.root})
    extras = sorted(set(graph["nodes"]) - included)
    if not removable or not extras:
        raise SourceBindingError("tampering demo needs non-root result and an unreachable node")
    omissions = copy.deepcopy(certificate)
    omissions["candidates"] = [i for i in omissions["candidates"] if i["node"] != removable[0]]
    addition = copy.deepcopy(certificate)
    addition["candidates"].append({"node": extras[0], "parent": expected.root, "rank": 1})
    cases = []
    for name, changed in (("omitted_result", omissions), ("spurious_result", addition)):
        try:
            verify_certificate(graph, expected.root, changed)
        except ValidationError as exc:
            cases.append({"case": name, "rejected": True, "layer": "graph_checker", "errors": exc.errors})
        else:
            raise RuntimeError("graph checker accepted altered certificate: " + name)
    edge = [FILE_INFO, TIME_ROOT] if [FILE_INFO, TIME_ROOT] in graph["edges"] else graph["edges"][0]
    changed = copy.deepcopy(extraction)
    changed["graph"]["edges"].remove(edge)
    changed["graph_sha256"] = graph_sha256(changed["graph"])
    changed["coverage"]["unique_edges"] = len(changed["graph"]["edges"])
    dishonest_certificate = generate_certificate(changed["graph"], expected.root)
    graph_only_accepted = verify_certificate(changed["graph"], expected.root, dishonest_certificate)
    try:
        verify_instance(data_dir, expected, changed, dishonest_certificate, graph=changed["graph"])
    except SourceBindingError as exc:
        cases.append({"case": "edge_deleted_before_certificate_generation", "removed_edge": edge,
                      "graph_checker_accepted_modified_graph": graph_only_accepted,
                      "source_binding_rejected": True, "rejected": True,
                      "layer": "source_reconstruction", "error": str(exc),
                      "modified_graph_sha256": changed["graph_sha256"],
                      "modified_result_count": len(dishonest_certificate["candidates"])})
    else:
        raise RuntimeError("source verifier accepted an edge-deleted graph")
    return {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "commit": expected.commit,
            "expected_root": expected.root, "original_result_count": len(included),
            "original_graph_sha256": extraction["graph_sha256"],
            "all_tampering_rejected": all(c["rejected"] for c in cases), "cases": cases}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "verify", "tamper"):
        sub = commands.add_parser(name)
        sub.add_argument("--config", type=Path, default=corpus.PROJECT / "local" / "corpus.json")
        sub.add_argument("--lock", type=Path, default=corpus.PROJECT / "corpus.lock.json")
        sub.add_argument("--root", required=True, help="Independent expected canonical Git path")
        sub.add_argument("--artifact-dir", type=Path, required=True)
        sub.add_argument("--report", type=Path)
    compare = commands.add_parser("compare")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)
    compare.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            first, second = file_hashes(args.first), file_hashes(args.second)
            if first != second:
                raise SourceBindingError("repeated artifact bytes are not deterministic")
            report = {"status": "byte_identical", "artifact_file_sha256": first,
                      "first": str(args.first.resolve()), "second": str(args.second.resolve())}
        else:
            data_dir, expected = independent_inputs(args.config, args.lock, args.root)
            function = {"run": run_experiment, "verify": verify_bundle, "tamper": tampering_demo}[args.command]
            report = function(data_dir, expected, args.artifact_dir)
        if args.report:
            corpus.atomic_write(args.report, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        # Full provenance/result stays in files; stdout is a concise run receipt.
        receipt = {k: v for k, v in report.items() if k not in ("outside_scope", "unresolved_files", "corpus_diagnostics")}
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 3 if report.get("status") == "unresolved" else 0
    except (SourceBindingError, ValidationError, corpus.CorpusError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
