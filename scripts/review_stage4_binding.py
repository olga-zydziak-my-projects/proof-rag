"""Independent, full-content audit of the optimized Lean instance.

No exporter, search generator, or checker implementation is imported. The old
auditor establishes that the preserved stage-3 literals equal the original
artifacts; this parser reconstructs every new path, edge, witness and hint and
compares against those same complete artifacts. This is an external audit,
not a formal proof of parsing, export, or source extraction.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re


EXPECTED_ROOT = "mojo/public/mojom/base/time.mojom"
BLOCK_SIZE = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def section(text, name):
    matches = list(re.finditer(
        r"^def " + re.escape(name) + r"\b.*?:=\s*(.*?)(?=^def |^theorem |^end |\Z)",
        text, re.MULTILINE | re.DOTALL))
    require(len(matches) == 1, "missing or duplicated definition: " + name)
    return matches[0].group(1).strip()


def block_names(text, prefix):
    names = re.findall(r"^def (" + prefix + r"\d+)\b", text, re.MULTILINE)
    require(names and names == [prefix + str(i) for i in range(len(names))],
            "missing, repeated, or unordered blocks: " + prefix)
    return names


def typed(text, name, pattern):
    require(re.search(r"^def " + re.escape(name) + pattern + r"\s*:=", text,
                      re.MULTILINE) is not None, "invalid type: " + name)


class TreeParser:
    """Restricted grammar; every branch must cover its exact prescribed range."""

    def __init__(self, source):
        self.source = source
        self.position = 0

    def consume(self, pattern):
        match = re.match(r"\s*(?:" + pattern + r")", self.source[self.position:])
        require(match is not None,
                "unparsed balanced-tree syntax near: " + self.source[self.position:self.position + 90])
        self.position += match.end()
        return match

    def complete(self):
        require(not self.source[self.position:].strip(), "unparsed balanced-tree suffix")

    def witnesses(self, lo, hi):
        require(lo < hi, "empty witness interval")
        if hi - lo == 1:
            value = self.consume(
                r"none\b|some\s+⟨\s*⟨\s*(\d+)\s*,\s*by decide(?:\s+\+kernel)?\s*⟩\s*,"
                r"\s*(\d+)\s*,\s*(none|some\s*\(\s*(\d+)\s*,\s*(\d+)\s*\))\s*⟩")
            if value.group(0).strip() == "none":
                return [None]
            parent, rank = int(value.group(1)), int(value.group(2))
            hint = None if value.group(3) == "none" else (int(value.group(4)), int(value.group(5)))
            return [(parent, rank, hint)]
        mid = (lo + hi) // 2
        guard = self.consume(r"if\s+v\.val\s*<\s*(\d+)\s+then\b")
        require(int(guard.group(1)) == mid, "wrong witness-tree boundary")
        left = self.witnesses(lo, mid)
        self.consume(r"else\b")
        return left + self.witnesses(mid, hi)

    def routes(self, lo, hi):
        require(lo < hi, "empty routing interval")
        if hi - lo == 1:
            leaf = self.consume(r"witnessBlock(\d+)\s+v\b")
            require(int(leaf.group(1)) == lo, "missing, duplicated, or substituted witness route")
            return
        mid = (lo + hi) // 2
        guard = self.consume(r"if\s+v\.val\s*<\s*(\d+)\s+then\b")
        require(int(guard.group(1)) == mid * BLOCK_SIZE, "wrong block-routing boundary")
        self.routes(lo, mid)
        self.consume(r"else\b")
        self.routes(mid, hi)


def audit(source, baseline="formal/Chromium.lean", artifact_dir="local/stage2"):
    spec = importlib.util.spec_from_file_location(
        "preserved_stage3_auditor", Path(__file__).with_name("review_stage3_binding.py"))
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    baseline_audit = old.audit(baseline, artifact_dir)
    text = Path(source).read_text(encoding="utf-8")
    read = lambda name: json.loads((Path(artifact_dir) / name).read_text(encoding="utf-8"))
    graph, cert = read("graph.json"), read("certificate.json")
    extraction, query = read("extraction.json"), read("query.json")

    path_blocks = block_names(text, "pathBlock")
    typed(text, "nodePaths", r"\s*:\s*Array String")
    require(" ".join(section(text, "nodePaths").split()) == " ++ ".join(path_blocks),
            "path table must use every path block exactly once in order")
    paths = []
    for name in path_blocks:
        typed(text, name, r"\s*:\s*Array String")
        literal = section(text, name)
        require(literal.startswith("#[") and literal.endswith("]"), "invalid path array")
        values = json.loads(literal[1:])
        require(isinstance(values, list) and 0 < len(values) <= BLOCK_SIZE and
                all(isinstance(v, str) for v in values), "invalid path block")
        paths.extend(values)
    require(paths == sorted(graph["nodes"]) and len(paths) == len(set(paths)),
            "full node table mismatch")
    count = len(paths)
    for name, typename in (("graph", "BlockedGraph"), ("certificate", "EnhancedCertificate"),
                           ("root", "Fin")):
        typed(text, name, r"\s*:\s*" + typename + r"\s+" + str(count))

    edge_names = block_names(text, "edgeBlock")
    graph_literal = section(text, "graph")
    require("".join(graph_literal.split()) == "⟨[" + ",".join(edge_names) + "]⟩",
            "graph must use every edge block exactly once in order")
    pattern = r"\(\s*⟨\s*(\d+)\s*,\s*by decide(?:\s+\+kernel)?\s*⟩\s*,\s*⟨\s*(\d+)\s*,\s*by decide(?:\s+\+kernel)?\s*⟩\s*\)"
    edge_blocks = []
    for name in edge_names:
        typed(text, name, r"\s*:\s*List\s*\(Fin\s+" + str(count) + r"\s*×\s*Fin\s+" + str(count) + r"\s*\)")
        literal = section(text, name)
        require(literal.startswith("[") and literal.endswith("]"), "invalid edge list")
        pairs = [tuple(map(int, pair)) for pair in re.findall(pattern, literal)]
        require(0 < len(pairs) <= BLOCK_SIZE, "invalid edge block size")
        require(not re.sub(r"[\s,\[\]]", "", re.sub(pattern, "", literal)), "unparsed edge literal")
        require(all(0 <= v < count for pair in pairs for v in pair), "invalid edge endpoint")
        edge_blocks.append(pairs)
    edge_ids = [pair for block in edge_blocks for pair in block]
    edges = [(paths[a], paths[b]) for a, b in edge_ids]
    require(len(edges) == len(set(edges)) and edges == sorted(tuple(e) for e in graph["edges"]),
            "full ordered edge mismatch")

    root_literal = re.fullmatch(r"⟨\s*(\d+)\s*,\s*by decide(?:\s+\+kernel)?\s*⟩", section(text, "root"))
    require(root_literal is not None, "invalid root literal")
    root = int(root_literal.group(1))
    require(0 <= root < count and paths[root] == EXPECTED_ROOT, "independent root mismatch")

    witnesses = block_names(text, "witnessBlock")
    require(len(witnesses) == (count + BLOCK_SIZE - 1) // BLOCK_SIZE, "incomplete witness table")
    records = []
    for index, name in enumerate(witnesses):
        typed(text, name, r"\s*\(v\s*:\s*Fin\s+" + str(count) + r"\)\s*:\s*Option\s*\(EnhancedWitness\s+" + str(count) + r"\)")
        parser = TreeParser(section(text, name))
        records.extend(parser.witnesses(index * BLOCK_SIZE, min((index + 1) * BLOCK_SIZE, count)))
        parser.complete()
    require(len(records) == count, "incomplete witness domain")
    certificate = section(text, "certificate")
    wrapper = re.fullmatch(r"⟨\s*fun v\s*=>\s*(.*)\s*⟩", certificate, re.DOTALL)
    require(wrapper is not None, "invalid certificate wrapper")
    routing = TreeParser(wrapper.group(1))
    routing.routes(0, len(witnesses))
    routing.complete()

    reconstructed = []
    hints = 0
    for node, record in enumerate(records):
        if record is None:
            continue
        parent, rank, hint = record
        require(0 <= parent < count, "invalid witness parent")
        if node == root:
            require(parent == root and rank == 0 and hint is None, "invalid root witness")
        else:
            require(hint is not None, "missing non-root edge hint")
            block, position = hint
            require(0 <= block < len(edge_blocks), "invalid edge block hint")
            require(0 <= position < len(edge_blocks[block]), "invalid edge position hint")
            require(edge_blocks[block][position] == (node, parent), "hint points at wrong actual edge")
            hints += 1
        reconstructed.append({"node": paths[node], "parent": None if node == root else paths[parent], "rank": rank})
    require(reconstructed == sorted(cert["candidates"], key=lambda r: r["node"]),
            "full result/parent/rank mismatch")
    require(extraction["graph"] == graph, "extraction graph mismatch")
    require(cert["query"]["root"] == query["query"]["root"] == EXPECTED_ROOT, "artifact root mismatch")
    result = {r["node"] for r in reconstructed}
    require(len(query["result"]) == len(result) and set(query["result"]) == result,
            "displayed answer mismatch")
    return {"passed": True, "nodes_compared": count, "edges_compared": len(edges),
            "witnesses_compared": len(reconstructed), "actual_edge_hints_checked": hints,
            "root": EXPECTED_ROOT, "baseline_full_content_audit": baseline_audit,
            "boundary": "External full-content equality against stage 3 via the same complete artifacts; not a formal exporter proof."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="formal/ChromiumFast.lean")
    parser.add_argument("--baseline", default="formal/Chromium.lean")
    parser.add_argument("--artifact-dir", default="local/stage2")
    args = parser.parse_args()
    print(json.dumps(audit(args.source, args.baseline, args.artifact_dir), indent=2))


if __name__ == "__main__":
    main()
