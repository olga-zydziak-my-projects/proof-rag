"""Strict graph validation and canonical identity, without graph traversal.

The format describes a finite directed graph, not source-code semantics.
An edge [importer, imported] points toward a dependency.
"""

import hashlib
import json


class ValidationError(ValueError):
    """Invalid input or certificate; errors contains all safely detectable errors."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def validate_graph(graph):
    errors = []
    if not isinstance(graph, dict):
        raise ValidationError(["graph must be an object"])
    if set(graph) != {"nodes", "edges"}:
        errors.append("graph must contain exactly nodes and edges")
    raw_nodes = graph.get("nodes")
    raw_edges = graph.get("edges")
    if not isinstance(raw_nodes, list):
        errors.append("nodes must be a list")
        raw_nodes = []
    nodes = set()
    for index, node in enumerate(raw_nodes):
        if not isinstance(node, str) or not node:
            errors.append(f"nodes[{index}] must be a nonempty string")
        elif node in nodes:
            errors.append(f"duplicate node: {node!r}")
        else:
            nodes.add(node)
    if not isinstance(raw_edges, list):
        errors.append("edges must be a list")
        raw_edges = []
    edges = set()
    for index, edge in enumerate(raw_edges):
        if (not isinstance(edge, list) or len(edge) != 2
                or any(not isinstance(item, str) or not item for item in edge)):
            errors.append(f"edges[{index}] must be two nonempty string endpoints")
            continue
        pair = tuple(edge)
        if pair in edges:
            errors.append(f"duplicate edge: {pair!r}")
        edges.add(pair)
        for endpoint in pair:
            if endpoint not in nodes:
                errors.append(f"unknown edge endpoint: {endpoint!r}")
    if errors:
        raise ValidationError(errors)
    return nodes, edges


def graph_sha256(graph):
    """Hash sorted nodes/edges as UTF-8 canonical JSON; order is not identity."""
    nodes, edges = validate_graph(graph)
    canonical = {"nodes": sorted(nodes), "edges": [list(e) for e in sorted(edges)]}
    data = json.dumps(canonical, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()
