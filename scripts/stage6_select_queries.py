"""Independent, deterministic selection and fixed-point oracle for Stage 6.

This script imports no project generator, certificate checker or exporter. It
scans all supplied edges until a set reaches a fixed point, independently for
every root. Its results are external test evidence about the supplied graph,
not a source-binding proof or an authority for the snapshot identity.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


SELECTION = (
    ("regression_maximum", "mojo/public/mojom/base/time.mojom"),
    ("isolated", "android_webview/common/mojom/renderer.mojom"),
    ("singleton_with_imports", "android_webview/common/mojom/frame.mojom"),
    ("same_count_a", "ash/public/mojom/accelerator_configuration.mojom"),
    ("same_count_b", "ash/style/mojom/color_scheme.mojom"),
    ("small", "ash/public/mojom/accelerator_actions.mojom"),
    ("ten", "cc/mojom/render_frame_metadata.mojom"),
    ("twenty", "chromeos/ash/experiences/arc/mojom/gfx.mojom"),
    ("medium", "third_party/blink/public/mojom/blob/serialized_blob.mojom"),
    ("hundred", "url/mojom/scheme_host_port.mojom"),
    ("deep", "mojo/public/mojom/base/values.mojom"),
    ("large", "mojo/public/mojom/base/unguessable_token.mojom"),
)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def fixed_point(root, edges):
    """Reverse reachability, including root; synchronous full-edge scans."""
    current = {root}
    rounds = 0
    while True:
        extended = current | {importer for importer, imported in edges
                              if imported in current}
        if extended == current:
            return sorted(current), rounds
        current = extended
        rounds += 1


def inspect_graph(graph):
    if not isinstance(graph, dict) or set(graph) != {"nodes", "edges"}:
        raise ValueError("graph schema")
    nodes = graph["nodes"]
    raw_edges = graph["edges"]
    if not isinstance(nodes, list) or not nodes or any(type(n) is not str for n in nodes):
        raise ValueError("node list")
    if len(set(nodes)) != len(nodes):
        raise ValueError("duplicate node")
    if not isinstance(raw_edges, list):
        raise ValueError("edge list")
    universe = set(nodes)
    edges = []
    for row in raw_edges:
        if (not isinstance(row, list) or len(row) != 2
                or any(type(n) is not str or n not in universe for n in row)):
            raise ValueError("invalid edge")
        edges.append(tuple(row))
    if len(set(edges)) != len(edges):
        raise ValueError("duplicate edge")
    return sorted(nodes), sorted(edges)


def build_selection(raw_graph):
    graph = json.loads(raw_graph, object_pairs_hook=unique_object)
    nodes, edges = inspect_graph(graph)
    results = {root: fixed_point(root, edges) for root in nodes}
    endpoint_set = {endpoint for edge in edges for endpoint in edge}
    isolated = sorted(set(nodes) - endpoint_set)
    incoming = Counter(imported for _, imported in edges)
    outgoing = Counter(importer for importer, _ in edges)
    same_ancestors = defaultdict(list)
    for root, (paths, _) in results.items():
        same_ancestors[tuple(paths)].append(root)
    # Two vertices have identical ancestor closures iff they are mutually
    # reachable. These equivalence classes are the strongly connected parts.
    nontrivial_components = sorted(
        (members for members in same_ancestors.values() if len(members) > 1),
        key=lambda members: members[0])
    self_loops = [a for a, b in edges if a == b]
    chosen = []
    for label, root in SELECTION:
        if root not in results:
            raise ValueError("representative root missing: " + root)
        paths, rounds = results[root]
        chosen.append({"label": label, "root": root, "count": len(paths),
                       "paths": paths, "root_included": root in paths,
                       "result_sha256": hashlib.sha256(canonical(paths)).hexdigest(),
                       "strict_growth_rounds": rounds,
                       "incoming_edges": incoming[root],
                       "outgoing_edges": outgoing[root],
                       "isolated": root in isolated})
    by_label = {entry["label"]: entry for entry in chosen}
    if not by_label["isolated"]["isolated"]:
        raise ValueError("isolated selection no longer isolated")
    singleton = by_label["singleton_with_imports"]
    if singleton["count"] != 1 or singleton["outgoing_edges"] == 0:
        raise ValueError("singleton-with-imports selection changed category")
    a, b = by_label["same_count_a"], by_label["same_count_b"]
    if a["count"] != b["count"] or a["paths"] == b["paths"]:
        raise ValueError("same-count distinct-output pair unavailable")
    histogram = Counter(len(paths) for paths, _ in results.values())
    return {
        "schema": "stage6-independent-query-selection-v1",
        "method": "synchronous fixed point by scanning every original edge; no project generator/checker/exporter imports",
        "boundary": "independent expected graph answers, not source provenance or a Lean proof",
        "graph_file_sha256": hashlib.sha256(raw_graph).hexdigest(),
        "graph_canonical_sha256": hashlib.sha256(canonical(graph)).hexdigest(),
        "summary": {"nodes": len(nodes), "edges": len(edges),
                    "isolated_nodes": len(isolated), "selected_queries": len(chosen),
                    "minimum_result_count": min(histogram),
                    "maximum_result_count": max(histogram),
                    "maximum_strict_growth_rounds": max(rounds for _, rounds in results.values()),
                    "nontrivial_strongly_connected_components": nontrivial_components,
                    "self_loops": self_loops,
                    "actual_graph_has_cycles": bool(nontrivial_components or self_loops),
                    "result_count_histogram": {str(k): v for k, v in sorted(histogram.items())}},
        "all_root_counts": [{"root": root, "count": len(results[root][0]),
                             "strict_growth_rounds": results[root][1]} for root in nodes],
        "same_count_swap_pair": [a["root"], b["root"]],
        "queries": chosen,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", default="local/stage2/graph.json")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    target = Path(args.report)
    if target.exists():
        parser.error("report already exists; choose a new path")
    result = build_selection(Path(args.graph).read_bytes())
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as output:
        output.write(canonical(result))
    print(json.dumps({"report": str(target), "queries": len(result["queries"]),
                      "counts": [q["count"] for q in result["queries"]],
                      "nodes": result["summary"]["nodes"],
                      "actual_graph_has_cycles": result["summary"]["actual_graph_has_cycles"]}))


if __name__ == "__main__":
    main()
