"""Source-bound instance verification. Never calls the generator or its search.

Re-executing the same parser detects substitution, not shared parser mistakes.
The mathematical guarantee in Lean remains relative to the supplied graph.
"""
import hashlib
from pathlib import Path
from time import perf_counter

from .checker import verify_certificate
from .corpus import encoded
from .extraction import SourceBindingError, artifact_sha256, extract_corpus

TIME_ROOT = "mojo/public/mojom/base/time.mojom"
FILE_INFO = "mojo/public/mojom/base/file_info.mojom"
URL_LOADER = "services/network/public/mojom/url_loader.mojom"
URL_RESPONSE = "services/network/public/mojom/url_response_head.mojom"
_UNSUPPLIED = object()


def certificate_path(certificate, start, root):
    """Display a path only AFTER the independent checker accepted witnesses."""
    records = {item["node"]: item for item in certificate["candidates"]}
    if start not in records:
        return None
    path, current = [start], start
    while current != root:
        current = records[current]["parent"]
        path.append(current)
        if len(path) > len(records):
            raise SourceBindingError("invalid certificate parent path")
    return path


def result_from_checked(extraction, expected, certificate):
    nodes = sorted(item["node"] for item in certificate["candidates"])
    edges = {tuple(edge) for edge in extraction["graph"]["edges"]}
    examples = []
    if expected.root == TIME_ROOT:
        for path in ([FILE_INFO, TIME_ROOT], [URL_LOADER, URL_RESPONSE, TIME_ROOT]):
            examples.append({"path": path,
                             "all_edges_reconstructed": all(pair in edges for pair in zip(path, path[1:])),
                             "all_nodes_in_result": all(node in nodes for node in path)})
    folder = Path(__file__).resolve().parent
    return {
        "format": "repo-proof-source-query-v1",
        "status": ("complete_for_declared_scope" if extraction["extraction_status"] == "complete"
                   else "unresolved"),
        "source_complete": extraction["coverage"]["source_complete"],
        "graph_certificate_status": "accepted_for_reconstructed_graph",
        "query": {"kind": "reverse_reachability_including_root", "root": expected.root},
        "binding": {**extraction["binding"], "graph_sha256": extraction["graph_sha256"],
                    "extraction_sha256": artifact_sha256(extraction),
                    "certificate_sha256": artifact_sha256(certificate)},
        "source_reconstruction_matches_artifacts": True,
        "result_count": len(nodes), "result": nodes,
        "contract_examples": examples,
        "certificate_witness_paths": [path for node in (FILE_INFO, URL_LOADER)
                                      if (path := certificate_path(certificate, node, expected.root)) is not None],
        "verification_implementation_sha256": {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in ("instance.py", "checker.py", "graph.py")},
        "guarantee_boundary": [
            "Certificate accepted by tested Python checker for reconstructed finite graph.",
            "Re-extraction uses the same pinned parser and is not an independent parser correctness proof.",
            "Lean checks the graph-certificate theorem; Python refinement and source extraction remain unproved.",
        ],
    }


def verify_instance(data_dir, expected, extraction, certificate, *, graph=_UNSUPPLIED, result=_UNSUPPLIED):
    """All expected identity/root values come from the caller, never the producer.

Return (deterministic result, operational timings), or raise on substitution /
invalid certificate. Data/syntax uncertainty remains an honest unresolved result.
"""
    started = perf_counter()
    rebuilt, measurements = extract_corpus(data_dir, expected)
    if not isinstance(extraction, dict) or encoded(extraction.get("graph")) != encoded(rebuilt["graph"]):
        raise SourceBindingError("supplied graph differs from graph reconstructed from verified source bytes")
    if graph is not _UNSUPPLIED and encoded(graph) != encoded(rebuilt["graph"]):
        raise SourceBindingError("standalone graph differs from source-reconstructed graph")
    if encoded(extraction) != encoded(rebuilt):
        raise SourceBindingError("extraction binding/provenance/diagnostics differ from source reconstruction")
    if expected.root not in rebuilt["graph"]["nodes"]:
        raise SourceBindingError("expected query root is out_of_scope")
    before_certificate = perf_counter()
    verify_certificate(rebuilt["graph"], expected.root, certificate)
    certificate_checked = perf_counter()
    verified_result = result_from_checked(rebuilt, expected, certificate)
    if result is not _UNSUPPLIED and encoded(result) != encoded(verified_result):
        raise SourceBindingError("supplied query result differs from source-bound certificate result")
    return verified_result, {
        "full_instance_verification_seconds": perf_counter() - started,
        "repeated_corpus_verification_seconds": measurements["corpus_verification_seconds"],
        "repeated_parse_and_graph_seconds": measurements["parse_and_graph_seconds"],
        "repeated_certificate_verification_seconds": certificate_checked - before_certificate,
    }
