"""Independent full-content audit of Lean literals against stage-2 artifacts.

This deliberately does not import the exporter, generator, or graph checker.
It is a tested external binding check, not a proof of serialization correctness.
"""
import argparse
import json
from pathlib import Path
import re

EXPECTED_ROOT = "mojo/public/mojom/base/time.mojom"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def section(text, name):
    match = re.search(r"^def " + re.escape(name) + r"\b.*?:=\s*(.*?)(?=^def |^theorem |^end |\Z)",
                      text, re.MULTILINE | re.DOTALL)
    require(match is not None, "missing Lean definition: " + name)
    return match.group(1).strip()


def array_blocks(text, prefix, expression, type_pattern):
    blocks = re.findall(r"^def (" + prefix + r"\d+)\b", text, re.MULTILINE)
    require(blocks == [prefix + str(i) for i in range(len(blocks))] and blocks,
            "duplicate, missing, or unordered blocks: " + prefix)
    require(re.fullmatch(prefix + r"\d+(?:\s*\+\+\s*" + prefix + r"\d+)*", expression)
            is not None, "unparsed block references: " + prefix)
    require(re.findall(prefix + r"\d+", expression) == blocks,
            "all blocks must be used exactly once in order: " + prefix)
    literals = []
    for block in blocks:
        require(re.search(r"^def " + block + r"\s*:\s*" + type_pattern + r"\s*:=", text,
                          re.MULTILINE) is not None, "invalid block type: " + block)
        literal = section(text, block)
        require(literal.startswith("#[") and literal.endswith("]"), "invalid array block wrapper")
        literals.append(literal[2:-1])
    return literals


def audit(source, artifact_dir):
    text = Path(source).read_text(encoding="utf-8")
    read = lambda name: json.loads((Path(artifact_dir) / name).read_text(encoding="utf-8"))
    graph, cert = read("graph.json"), read("certificate.json")
    extraction, query = read("extraction.json"), read("query.json")
    path_literal = section(text, "nodePaths")
    require(re.search(r"^def nodePaths\s*:\s*Array String\s*:=", text, re.MULTILINE),
            "invalid path table type")
    if path_literal.startswith('#['):
        paths = json.loads(path_literal[1:])
    else:
        paths = []
        for literal in array_blocks(text, "pathBlock", path_literal, r"Array String"):
            block_paths = json.loads("[" + literal + "]")
            require(0 < len(block_paths) <= 64, "invalid path block size")
            paths.extend(block_paths)
    require(isinstance(paths, list) and all(isinstance(p, str) for p in paths), "bad node table")
    require(len(paths) == len(set(paths)), "duplicate node table entry")
    require(paths == sorted(graph["nodes"]), "full node table mismatch")
    count = len(paths)
    for name, typename in (("graph", "FiniteGraph"), ("certificate", "FiniteCertificate"), ("root", "Fin")):
        require(re.search(r"^def " + name + r"\s*:\s*" + typename + r"\s+" + str(count) + r"\s*:=", text,
                          re.MULTILINE) is not None, "Lean universe size mismatch: " + name)
    graph_text = section(text, "graph")
    edge_pattern = r"\(⟨(\d+), by decide(?: \+kernel)?⟩, ⟨(\d+), by decide(?: \+kernel)?⟩\)"
    blocks = re.findall(r"^def (edgeBlock\d+)\b", text, re.MULTILINE)
    raw_edges = []
    if blocks:
        require(blocks == ["edgeBlock" + str(i) for i in range(len(blocks))],
                "duplicate, missing, or unordered edge block definitions")
        require(re.fullmatch(r"⟨\s*edgeBlock\d+(?:\s*\+\+\s*edgeBlock\d+)*\s*⟩", graph_text)
                is not None, "unparsed graph block references")
        require(re.findall(r"edgeBlock\d+", graph_text) == blocks,
                "graph must reference every block exactly once in definition order")
        for block in blocks:
            require(re.search(r"^def " + block + r"\s*:\s*List\s*\(Fin\s+" + str(count) +
                              r"\s*×\s*Fin\s+" + str(count) + r"\s*\)\s*:=", text,
                              re.MULTILINE) is not None, "edge block universe mismatch: " + block)
            literal = section(text, block)
            require(literal.startswith("[") and literal.endswith("]"), "invalid edge block wrapper")
            pairs = re.findall(edge_pattern, literal)
            require(0 < len(pairs) <= 64, "invalid edge block size")
            residue = re.sub(edge_pattern, "", literal)
            require(not re.sub(r"[\s,\[\]]", "", residue), "unparsed edge block literal")
            raw_edges.extend(pairs)
    else:
        raw_edges = re.findall(edge_pattern, graph_text)
        residue = re.sub(edge_pattern, "", graph_text)
        require(not re.sub(r"[\s,\[\]⟨⟩]", "", residue), "unparsed graph literal")
    edge_ids = [tuple(map(int, pair)) for pair in raw_edges]
    require(all(0 <= v < count for edge in edge_ids for v in edge), "out-of-range edge")
    edges = [(paths[a], paths[b]) for a, b in edge_ids]
    require(len(edges) == len(set(edges)), "duplicate Lean edge")
    expected_edges = [tuple(pair) for pair in graph["edges"]]
    require(len(expected_edges) == len(set(expected_edges)), "duplicate artifact edge")
    require(edges == sorted(expected_edges), "full ordered edge mismatch")
    root_literal = section(text, "root")
    match = re.fullmatch(r"⟨(\d+), by decide(?: \+kernel)?⟩", root_literal)
    require(match is not None, "unparsed root literal")
    root = int(match.group(1))
    require(0 <= root < count and paths[root] == EXPECTED_ROOT, "independent expected root mismatch")
    certificate_text = section(text, "certificate")
    record_pattern = r"none|some ⟨⟨(\d+), by decide(?: \+kernel)?⟩, (\d+)⟩"
    blocks = re.findall(r"^def (witnessBlock\d+)\b", text, re.MULTILINE)
    require(blocks == ["witnessBlock" + str(i) for i in range(len(blocks))] and blocks,
            "duplicate, missing, or unordered witness blocks")
    records = []
    expected_routes = []
    for index, block in enumerate(blocks):
        require(re.search(r"^def " + block + r"\s*\(v\s*:\s*Fin\s+" + str(count) +
                          r"\)\s*:\s*Option\s*\(Witness\s+" + str(count) + r"\)\s*:=", text,
                          re.MULTILINE), "invalid witness function type: " + block)
        lines = [line.strip() for line in section(text, block).splitlines()]
        require(lines[-1] == "none" and 1 <= len(lines) - 1 <= 64, "invalid witness block body")
        for line in lines[:-1]:
            row = re.fullmatch(r"if v\.val == (\d+) then (.+) else", line)
            require(row is not None, "unparsed witness row")
            require(int(row.group(1)) == len(records), "witness rows must cover consecutive exact IDs")
            value = re.fullmatch(record_pattern, row.group(2))
            require(value is not None, "invalid witness value")
            records.append(value)
        if index + 1 < len(blocks):
            expected_routes.append(f"if v.val < {len(records)} then {block} v else")
        else:
            expected_routes.append(f"{block} v")
    expected_certificate = "⟨fun v => " + " ".join(expected_routes) + "⟩"
    require(" ".join(certificate_text.split()) == expected_certificate,
            "certificate routing must select every dense block exactly once at its exact boundary")
    require(len(records) == count, "certificate function domain coverage mismatch")
    reconstructed = []
    for node, record in enumerate(records):
        if record.group(0) == "none":
            continue
        parent, rank = map(int, record.groups())
        require(0 <= parent < count, "out-of-range parent")
        if node == root:
            require(parent == root and rank == 0, "invalid root encoding")
        reconstructed.append({"node": paths[node], "parent": None if node == root else paths[parent], "rank": rank})
    require(sorted(reconstructed, key=lambda r: r["node"]) ==
            sorted(cert["candidates"], key=lambda r: r["node"]), "full witness/result mismatch")
    require(cert["query"]["root"] == query["query"]["root"] == EXPECTED_ROOT, "artifact root mismatch")
    require(extraction["graph"] == graph, "extraction graph mismatch")
    result = {record["node"] for record in reconstructed}
    require(len(query["result"]) == len(result) and set(query["result"]) == result, "displayed result mismatch")
    reachable = {EXPECTED_ROOT}
    while True:
        enlarged = reachable | {a for a, b in expected_edges if b in reachable}
        if enlarged == reachable:
            break
        reachable = enlarged
    require(reachable == result, "independent fixed-point result mismatch")
    return {"passed": True, "nodes_compared": count, "edges_compared": len(edges),
            "witnesses_compared": len(reconstructed), "root": EXPECTED_ROOT,
            "boundary": "External full-content comparison; not a formal exporter proof."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="formal/Chromium.lean")
    parser.add_argument("--artifact-dir", default="local/stage2")
    args = parser.parse_args()
    print(json.dumps(audit(args.source, args.artifact_dir), indent=2))


if __name__ == "__main__":
    main()
