"""Independent certificate checker: no search or generator imports.

Root plus reverse-edge closure proves completeness for the supplied graph.
Parent edges with strictly decreasing natural ranks prove soundness.
This Python implementation is not formally verified.
"""

from .graph import ValidationError, graph_sha256, validate_graph


def verify_certificate(graph, root, cert):
    """Return True, or raise ValidationError with safely detectable errors.

The caller supplies the expected graph and root independently of cert.
SHA-256 binds the finite graph under a cryptographic integrity assumption;
it does not establish completeness of extraction from repository source.
"""
    errors = []
    try:
        nodes, edges = validate_graph(graph)
    except ValidationError as exc:
        raise ValidationError(["graph: " + error for error in exc.errors]) from exc
    if not isinstance(root, str) or root not in nodes:
        errors.append("root must name an existing node")
    if not isinstance(cert, dict):
        raise ValidationError(errors + ["certificate must be an object"])
    if set(cert) != {"format", "graph_sha256", "query", "candidates"}:
        errors.append("certificate has missing or unexpected fields")
    if cert.get("format") != "repo-proof-certificate-v1":
        errors.append("unsupported certificate format")
    if cert.get("graph_sha256") != graph_sha256(graph):
        errors.append("graph snapshot hash mismatch")
    expected_query = {"kind": "reverse_reachability_including_root", "root": root}
    if cert.get("query") != expected_query:
        errors.append("query must match the expected kind and root exactly")
    raw = cert.get("candidates")
    if not isinstance(raw, list):
        errors.append("candidates must be a list")
        raw = []
    candidates = {}
    for index, item in enumerate(raw):
        prefix = f"candidates[{index}]"
        if not isinstance(item, dict):
            errors.append(prefix + " must be an object")
            continue
        if set(item) != {"node", "parent", "rank"}:
            errors.append(prefix + " must contain exactly node, parent, rank")
        node = item.get("node")
        if not isinstance(node, str) or node not in nodes:
            errors.append(prefix + " node must exist in graph")
            continue
        if node in candidates:
            errors.append(f"duplicate candidate: {node!r}")
            continue
        candidates[node] = item
        if type(item.get("rank")) is not int or item["rank"] < 0:
            errors.append(prefix + " rank must be a nonnegative integer, not bool")
        parent = item.get("parent")
        if parent is not None and not isinstance(parent, str):
            errors.append(prefix + " parent must be a node string or null")
    root_valid = isinstance(root, str) and root in nodes
    if root_valid and root not in candidates:
        errors.append("root must be included in candidates")
    for node, item in candidates.items():
        rank = item.get("rank")
        parent = item.get("parent")
        if node == root:
            if rank != 0 or type(rank) is not int or parent is not None:
                errors.append("root witness must have rank 0 and null parent")
            continue
        if not isinstance(parent, str) or parent not in candidates:
            errors.append(f"candidate {node!r} must have a candidate parent")
            continue
        if (node, parent) not in edges:
            errors.append(f"missing original parent edge: {node!r} -> {parent!r}")
        parent_rank = candidates[parent].get("rank")
        if (type(rank) is int and rank >= 0
                and type(parent_rank) is int and parent_rank >= 0
                and not parent_rank < rank):
            errors.append(f"rank must decrease toward root: {node!r}")
    for importer, imported in sorted(edges):
        if imported in candidates and importer not in candidates:
            errors.append(f"reverse closure missing importer: {importer!r} -> {imported!r}")
    if errors:
        raise ValidationError(errors)
    return True
