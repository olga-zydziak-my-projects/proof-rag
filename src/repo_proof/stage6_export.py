"""Fresh query proofs over the already verified Stage 5 source snapshot.

The caller must authenticate every imported source proof and its graph/path
mapping. This exporter is an IO boundary, not a proved serializer. The new Lean
module reuses only the source binding and proves a fresh answer for its root.
"""
from .fast_export import _tree
from .graph import validate_graph
from .lean_export import render as validate_serialization


def _range_proof(start, length, maximum, indent):
    if length <= maximum:
        return [indent + "timed_kernel_decide"]
    left = length // 2
    right = length - left
    return ([indent + f"apply all_range'_split {start} {left} {right}", indent + "·"]
            + _range_proof(start, left, maximum, indent + "  ")
            + [indent + "·"]
            + _range_proof(start + left, right, maximum, indent + "  "))


def render_query(graph, root, certificate):
    """Emit QueryProof; its successful compilation remains mandatory.

    All graph edges and their block ordering must equal ChromiumFast.graph in
    the authenticated cache. The separate preparation and literal audits check
    that precondition; the kernel checks actual imported edges for each query.
    """
    validate_serialization(graph, root, certificate, "SerializationOnly")
    nodes, edge_set = validate_graph(graph)
    names = sorted(nodes)
    ids = {name: i for i, name in enumerate(names)}
    n = len(names)
    edges = sorted(edge_set)
    locations = {edge: (i // 64, i % 64) for i, edge in enumerate(edges)}
    records = {record["node"]: record for record in certificate["candidates"]}
    selected = sorted(ids[name] for name in records)
    fin = lambda i: f"⟨{i}, by decide +kernel⟩"
    lines = [
        "import ChromiumSource", "import ProofTiming",
        "set_option maxRecDepth 100000", "set_option maxHeartbeats 0",
        "namespace QueryProof", "open RepoProof RepoProof.SourceBinding RepoProof.AnswerBinding",
        f"def graph : BlockedGraph {n} := ChromiumFast.graph",
        f"def root : Fin {n} := {fin(ids[root])}",
    ]

    def witness(i):
        name = names[i]
        record = records.get(name)
        if record is None:
            return "none"
        parent = root if record["parent"] is None else record["parent"]
        location = None if name == root else locations.get((name, parent))
        hint = "none" if location is None else f"some ({location[0]}, {location[1]})"
        return f'some ⟨{fin(ids[parent])}, {record["rank"]}, {hint}⟩'

    witnesses = []
    for start in range(0, n, 64):
        name = f"witnessBlock{len(witnesses)}"
        witnesses.append(name)
        lines.append(f"def {name} (v : Fin {n}) : Option (EnhancedWitness {n}) :=")
        lines += _tree(start, min(start + 64, n), witness, "  ")
    lines.append(f"def certificate : EnhancedCertificate {n} := ⟨fun v =>")
    lines += _tree(0, len(witnesses), lambda i: witnesses[i] + " v", "  ", lambda mid: mid * 64)
    lines[-1] += "⟩"
    lines += [
        "theorem accepted : fastCheck graph root certificate = true := by",
        "  apply fastCheck_of_parts", "  · timed_kernel_decide", "  ·",
    ]
    lines += _range_proof(0, n, 64, "    ")
    edge_blocks = [f"ChromiumFast.edgeBlock{i}" for i in range((len(edges) + 63) // 64)]
    lines.append("  · change ([" + ", ".join(edge_blocks)
                 + "]).all (fun b => b.all (fastClosure certificate)) = true")
    for _ in edge_blocks:
        lines += ["    apply all_cons_true", "    · timed_kernel_decide"]
    lines += [
        "    rfl",
        "theorem erased_accepted : check (eraseGraph graph) root (eraseHints certificate) = true :=",
        "  fastCheck_refines graph root certificate accepted",
        f"def resultIDs : List (Fin {n}) := [" + ", ".join(fin(i) for i in selected) + "]",
        "def payloadPaths : List Path := resultIDs.map SourceNames.names",
        "theorem answer_checked : answerOK SourceNames.names certificate resultIDs payloadPaths = true := by",
        "  apply answerOK_of_parts", "  · apply allVertices_of_range",
    ]
    lines += _range_proof(0, n, 16, "    ")
    lines += [
        "  · timed_kernel_decide", "  · rfl",
        "theorem paths_unique : payloadPaths.Nodup :=",
        "  answer_nodup _ _ SourceNames.mapping_checked _ _ _ answer_checked",
        "theorem source_to_answer (p : Path) :",
        "    p ∈ payloadPaths ↔ ∃ v, SourceNames.names v = p ∧",
        "      Reach (ReverseEdge (Import SourceNames.names ChromiumSource.files)) root v :=",
        "  RepoProof.AnswerBinding.source_to_answer _ _ _ _ _ _ _ _",
        "    ChromiumSource.source_bound accepted answer_checked p",
        "end QueryProof",
        "#print axioms QueryProof.accepted",
        "#print axioms QueryProof.erased_accepted",
        "#print axioms QueryProof.paths_unique",
        "#print axioms QueryProof.source_to_answer",
    ]
    return "\n".join(lines) + "\n"
