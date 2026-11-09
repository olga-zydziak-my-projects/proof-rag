"""Breadth-first certificate producer. It is not trusted by the checker."""

from collections import deque

from .graph import ValidationError, graph_sha256, validate_graph


def generate_certificate(graph, root):
    """Return all nodes with a directed path to root, including root itself."""
    nodes, edges = validate_graph(graph)
    if not isinstance(root, str) or root not in nodes:
        raise ValidationError(["root must name an existing node"])
    reverse = {node: [] for node in nodes}
    for importer, imported in sorted(edges):
        reverse[imported].append(importer)
    witnesses = {root: {"node": root, "parent": None, "rank": 0}}
    pending = deque([root])
    while pending:
        imported = pending.popleft()
        for importer in reverse[imported]:
            if importer in witnesses:
                continue
            witnesses[importer] = {
                "node": importer,
                "parent": imported,
                "rank": witnesses[imported]["rank"] + 1,
            }
            pending.append(importer)
    return {
        "format": "repo-proof-certificate-v1",
        "graph_sha256": graph_sha256(graph),
        "query": {"kind": "reverse_reachability_including_root", "root": root},
        "candidates": [witnesses[node] for node in sorted(witnesses)],
    }
