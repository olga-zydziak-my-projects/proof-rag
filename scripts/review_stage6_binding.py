"""Independent literal audit for a new root over the anchored source cache.

No Stage 6 exporter or search routine is imported. This reconstructs every
witness, edge hint, root and output ID; the authenticated Stage 5 path mapping
supplies decoding. Kernel checking is a separate required operation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from review_stage4_binding import TreeParser, block_names, require, section, typed


def audit_export_form(text, n, edge_count, witnesses):
    """Closed, auditor-owned grammar covering the entire module.

    Each data body was independently parsed and compared before this call.
    Exact framing binds those bodies to their types and declaration order.
    Proof commands are consumed individually, including indentation and EOF.
    No exporter implementation is imported or called.
    """
    position = 0

    def consume(line):
        nonlocal position
        token = line + '\n'
        require(text.startswith(token, position),
                'export outside complete reviewed grammar at offset ' + str(position))
        position += len(token)

    def definition(name, declaration, multiline=False):
        body = section(text, name)
        prefix = 'def ' + name + declaration + ' :='
        if multiline:
            consume(prefix)
            consume('  ' + body)
        else:
            consume(prefix + ' ' + body)

    def interval(start, length, limit, indent):
        if length <= limit:
            consume(indent + 'timed_kernel_decide')
            return
        half = length // 2
        consume(indent + f"apply all_range'_split {start} {half} {length - half}")
        consume(indent + '·')
        interval(start, half, limit, indent + '  ')
        consume(indent + '·')
        interval(start + half, length - half, limit, indent + '  ')

    for line in ('import ChromiumSource', 'import ProofTiming',
                 'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
                 'namespace QueryProof', 'open RepoProof RepoProof.SourceBinding RepoProof.AnswerBinding'):
        consume(line)
    definition('graph', f' : BlockedGraph {n}')
    definition('root', f' : Fin {n}')
    for name in witnesses:
        definition(name, f' (v : Fin {n}) : Option (EnhancedWitness {n})', True)
    definition('certificate', f' : EnhancedCertificate {n}')
    consume('theorem accepted : fastCheck graph root certificate = true := by')
    consume('  apply fastCheck_of_parts')
    consume('  · timed_kernel_decide')
    consume('  ·')
    interval(0, n, 64, '    ')
    blocks = [f'ChromiumFast.edgeBlock{i}' for i in range((edge_count + 63) // 64)]
    consume('  · change ([' + ', '.join(blocks) + ']).all (fun b => b.all (fastClosure certificate)) = true')
    for _ in blocks:
        consume('    apply all_cons_true')
        consume('    · timed_kernel_decide')
    consume('    rfl')
    consume('theorem erased_accepted : check (eraseGraph graph) root (eraseHints certificate) = true :=')
    consume('  fastCheck_refines graph root certificate accepted')
    definition('resultIDs', f' : List (Fin {n})')
    definition('payloadPaths', ' : List Path')
    consume('theorem answer_checked : answerOK SourceNames.names certificate resultIDs payloadPaths = true := by')
    consume('  apply answerOK_of_parts')
    consume('  · apply allVertices_of_range')
    interval(0, n, 16, '    ')
    for line in ('  · timed_kernel_decide', '  · rfl',
                 'theorem paths_unique : payloadPaths.Nodup :=',
                 '  answer_nodup _ _ SourceNames.mapping_checked _ _ _ answer_checked',
                 'theorem source_to_answer (p : Path) :',
                 '    p ∈ payloadPaths ↔ ∃ v, SourceNames.names v = p ∧',
                 '      Reach (ReverseEdge (Import SourceNames.names ChromiumSource.files)) root v :=',
                 '  RepoProof.AnswerBinding.source_to_answer _ _ _ _ _ _ _ _',
                 '    ChromiumSource.source_bound accepted answer_checked p', 'end QueryProof'):
        consume(line)
    for name in ('accepted', 'erased_accepted', 'paths_unique', 'source_to_answer'):
        consume('#print axioms QueryProof.' + name)
    require(position == len(text), 'unparsed export suffix')


def audit_query(source_text, graph, root, certificate):
    text = source_text
    preamble = ["import ChromiumSource", "import ProofTiming",
                "set_option maxRecDepth 100000", "set_option maxHeartbeats 0",
                "namespace QueryProof", "open RepoProof RepoProof.SourceBinding RepoProof.AnswerBinding"]
    lines = text.splitlines()
    require(lines[:len(preamble)] == preamble, "unreviewed query preamble")
    require(len(re.findall(r"\bset_option\b", text)) == 2, "unexpected Lean option")
    require(len(re.findall(r"\bopen\b", text)) == 1, "unexpected name resolution command")
    forbidden = r"\b(?:axiom|admit|sorry|native_decide|unsafe|local|scoped|notation|infix|infixl|infixr|prefix|postfix|macro|syntax|elab|opaque|abbrev|instance|variable|constant|attribute|section|implemented_by|extern)\b"
    require(not re.search(forbidden, text), "unreviewed declaration, notation or proof escape")
    for line in lines[len(preamble):]:
        if not line.strip():
            continue
        if line[0].isspace():
            require(not re.match(r"\s*(?:def|theorem|namespace|end|import|open|set_option|#)", line),
                    "indented top-level command")
        else:
            require(line.startswith(("def ", "theorem ", "#print axioms QueryProof."))
                    or line == "end QueryProof", "unreviewed top-level command")
    require(isinstance(graph, dict) and set(graph) == {"nodes", "edges"}, "graph schema")
    require(isinstance(graph["nodes"], list)
            and all(isinstance(name, str) and name for name in graph["nodes"]), "graph names")
    require(isinstance(graph["edges"], list)
            and all(isinstance(edge, list) and len(edge) == 2
                    and all(isinstance(name, str) and name for name in edge)
                    for edge in graph["edges"]), "graph edges")
    names = sorted(graph["nodes"])
    require(names and len(names) == len(set(names)), "nonempty unique query universe required")
    require(root in names, "independent query root outside universe")
    edges = sorted(tuple(edge) for edge in graph["edges"])
    require(len(edges) == len(set(edges)), "duplicate query graph edge")
    require(all(a in names and b in names for a, b in edges), "unknown graph endpoint")
    n = len(names)
    ids = {name: i for i, name in enumerate(names)}
    require(isinstance(certificate, dict)
            and set(certificate) == {"format", "graph_sha256", "query", "candidates"}, "certificate schema")
    digest = hashlib.sha256(json.dumps({"nodes": names, "edges": [list(edge) for edge in edges]},
                                      sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
    require(certificate["format"] == "repo-proof-certificate-v1"
            and certificate["graph_sha256"] == digest, "certificate graph identity")
    require(isinstance(certificate["candidates"], list), "candidate list")
    candidate_names = set()
    for record in certificate["candidates"]:
        require(isinstance(record, dict) and set(record) == {"node", "parent", "rank"}, "candidate schema")
        require(isinstance(record["node"], str) and record["node"] in ids
                and record["node"] not in candidate_names, "unknown or repeated candidate")
        candidate_names.add(record["node"])
        require(type(record["rank"]) is int and record["rank"] >= 0, "non-natural candidate rank")
        if record["node"] == root:
            require(record["parent"] is None and record["rank"] == 0, "candidate root encoding")
        else:
            require(isinstance(record["parent"], str) and record["parent"] in ids, "candidate parent")
    require(root in candidate_names, "root candidate omitted")
    require(re.findall(r"^import (\S+)$", text, re.M) == ["ChromiumSource", "ProofTiming"],
            "unreviewed import or missing source proof")
    require(re.findall(r"^namespace (\S+)$", text, re.M) == ["QueryProof"]
            and re.findall(r"^end (\S+)$", text, re.M) == ["QueryProof"], "query namespace")
    typed(text, "graph", rf"\s*:\s*BlockedGraph\s+{n}")
    require(section(text, "graph") == "ChromiumFast.graph", "graph is not the anchored graph")
    typed(text, "root", rf"\s*:\s*Fin\s+{n}")
    literal = re.fullmatch(r"⟨\s*(\d+),\s*by decide \+kernel\s*⟩", section(text, "root"))
    require(literal is not None and int(literal.group(1)) == ids[root], "independent root mismatch")
    require(certificate["query"] == {"kind": "reverse_reachability_including_root", "root": root},
            "certificate belongs to another query")

    witnesses = block_names(text, "witnessBlock")
    require(len(witnesses) == (n + 63) // 64, "incomplete witness table")
    records = []
    for i, name in enumerate(witnesses):
        typed(text, name, rf"\s*\(v\s*:\s*Fin\s+{n}\)\s*:\s*Option\s*\(EnhancedWitness\s+{n}\)")
        parser = TreeParser(section(text, name))
        records += parser.witnesses(i * 64, min((i + 1) * 64, n))
        parser.complete()
    typed(text, "certificate", rf"\s*:\s*EnhancedCertificate\s+{n}")
    wrapper = re.fullmatch(r"⟨\s*fun v\s*=>\s*(.*)\s*⟩", section(text, "certificate"), re.S)
    require(wrapper is not None, "certificate wrapper")
    routing = TreeParser(wrapper.group(1))
    routing.routes(0, len(witnesses))
    routing.complete()

    reconstructed = []
    edge_hints = 0
    for index, record in enumerate(records):
        if record is None:
            continue
        parent, rank, hint = record
        require(0 <= parent < n, "invalid witness parent")
        if index == ids[root]:
            require(parent == index and rank == 0 and hint is None, "invalid root witness")
        else:
            require(hint is not None, "nonroot witness lacks an edge hint")
            block, offset = hint
            location = block * 64 + offset
            require(0 <= offset < 64 and 0 <= location < len(edges), "invalid edge hint")
            require(edges[location] == (names[index], names[parent]), "hint identifies a different edge")
            edge_hints += 1
        reconstructed.append({"node": names[index], "parent": None if index == ids[root] else names[parent],
                              "rank": rank})
    expected = sorted(certificate["candidates"], key=lambda item: item["node"])
    require(reconstructed == expected, "full candidate/parent/rank mismatch")

    typed(text, "resultIDs", rf"\s*:\s*List\s*\(Fin\s+{n}\)")
    raw = section(text, "resultIDs")
    require(raw.startswith("[") and raw.endswith("]"), "output ID list syntax")
    pattern = r"⟨\s*(\d+),\s*by decide \+kernel\s*⟩"
    result_ids = [int(i) for i in re.findall(pattern, raw)]
    require(not re.sub(r"[\s,\[\]]", "", re.sub(pattern, "", raw)), "unparsed output ID syntax")
    expected_ids = [ids[item["node"]] for item in expected]
    require(result_ids == expected_ids and len(result_ids) == len(set(result_ids)), "complete output IDs changed")
    typed(text, "payloadPaths", r"\s*:\s*List\s+Path")
    require(section(text, "payloadPaths") == "resultIDs.map SourceNames.names", "output decoding changed")
    require([names[i] for i in result_ids] == [item["node"] for item in expected], "decoded paths changed")

    expected_definitions = ["graph", "root", *witnesses, "certificate", "resultIDs", "payloadPaths"]
    require(re.findall(r"^def (\w+)\b", text, re.M) == expected_definitions, "unexpected or duplicate definitions")
    require(re.findall(r"^theorem (\w+)\b", text, re.M) ==
            ["accepted", "erased_accepted", "answer_checked", "paths_unique", "source_to_answer"],
            "unexpected or missing query theorem")
    signatures = {
        "accepted": ": fastCheck graph root certificate = true",
        "erased_accepted": ": check (eraseGraph graph) root (eraseHints certificate) = true",
        "answer_checked": ": answerOK SourceNames.names certificate resultIDs payloadPaths = true",
        "paths_unique": ": payloadPaths.Nodup",
        "source_to_answer": "(p : Path) : p ∈ payloadPaths ↔ ∃ v, SourceNames.names v = p ∧ "
                            "Reach (ReverseEdge (Import SourceNames.names ChromiumSource.files)) root v",
    }
    for name, expected_signature in signatures.items():
        matches = re.findall(r"^theorem " + name + r"\b(.*?)\s*:=", text, re.M | re.S)
        require(len(matches) == 1 and " ".join(matches[0].split()) == expected_signature,
                "changed or weakened theorem signature: " + name)
    require(re.findall(r"^#print axioms (\S+)$", text, re.M) ==
            ["QueryProof.accepted", "QueryProof.erased_accepted", "QueryProof.paths_unique", "QueryProof.source_to_answer"],
            "incomplete query axiom audit")
    audit_export_form(text, n, len(edges), witnesses)
    return {"passed": True, "root": root, "root_id": ids[root], "nodes_compared": n,
            "edges_reused": len(edges), "witnesses_compared": len(expected),
            "actual_edge_hints_checked": edge_hints, "output_paths_compared": len(result_ids),
            "boundary": "Full query data comparison; graph/path source cache authentication and kernel proof are separate."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True)
    p.add_argument("--graph", required=True)
    p.add_argument("--certificate", required=True)
    p.add_argument("--root", required=True)
    args = p.parse_args()
    from sys import path
    path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from repo_proof.extraction import read_json
    print(json.dumps(audit_query(Path(args.source).read_text(encoding="utf-8"),
                                read_json(args.graph), args.root, read_json(args.certificate)), indent=2))


if __name__ == "__main__":
    main()
