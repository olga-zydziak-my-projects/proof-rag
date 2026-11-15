"""Bounded graph-only Lean certificate export. NO multi-repo source theorem."""
import re
import numpy as np
from .stage8_graph import check_certificate

NAMES = ('Stage8Graph.accepted', 'Stage8Graph.exact', 'Stage8Graph.answer_mask')


def render(n, edges, root, ids, parents, ranks):
    if n > 64 or len(edges) > 128:
        raise ValueError('bounded Lean graph pilot supports <=64 vertices, <=128 edges')
    check_certificate(n, edges, root, ids, parents, ranks)
    fin = lambda i: '⟨'+str(i)+', by decide +kernel⟩'
    es = ', '.join('('+fin(int(a))+', '+fin(int(b))+')' for a, b in edges)
    answer = ', '.join(fin(int(v)) for v in ids)
    witnesses = '\n'.join('  | '+str(int(v))+' => some ⟨'+fin(root if int(v) == root else int(p))+', '+str(int(r))+'⟩'
                          for v, p, r in zip(ids, parents, ranks))
    return f'''import Checker
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace Stage8Graph
open RepoProof
def graph : FiniteGraph {n} := ⟨[{es}]⟩
def root : Fin {n} := {fin(root)}
def certificate : FiniteCertificate {n} := ⟨fun v => match v.val with
{witnesses}
  | _ => none⟩
def answer : List (Fin {n}) := [{answer}]
theorem accepted : check graph root certificate = true := by decide +kernel
theorem exact (v : Fin {n}) :
    member certificate v = true ↔ Reach (ReverseEdge (fun a b => (a,b) ∈ graph.edges)) root v :=
  check_exact graph root certificate accepted v
theorem answer_mask : (List.finRange {n}).all (fun v => decide (v ∈ answer) == member certificate v) = true := by decide +kernel
end Stage8Graph
#print axioms Stage8Graph.accepted
#print axioms Stage8Graph.exact
#print axioms Stage8Graph.answer_mask
'''


def audit(text, n, edges, root, ids, parents, ranks):
    """Independent complete grammar, not exporter regeneration or substring scan."""
    fin = r'⟨([0-9]+), by decide \+kernel⟩'
    edge_item = r'\('+fin+', '+fin+r'\)'
    header = ('import Checker\nset_option maxRecDepth 100000\nset_option maxHeartbeats 0\n'
              'namespace Stage8Graph\nopen RepoProof\n')
    pattern = (re.escape(header)+r'def graph : FiniteGraph ([0-9]+) := ⟨\[(.*?)\]⟩\n'
        +r'def root : Fin ([0-9]+) := '+fin+r'\n'
        +r'def certificate : FiniteCertificate ([0-9]+) := ⟨fun v => match v.val with\n'
        +r'((?:  \| [0-9]+ => some ⟨⟨[0-9]+, by decide \+kernel⟩, [0-9]+⟩\n)+)'
        +r'  \| _ => none⟩\n'
        +r'def answer : List \(Fin ([0-9]+)\) := \[(.*?)\]\n'
        +re.escape('theorem accepted : check graph root certificate = true := by decide +kernel\n')
        +r'theorem exact \(v : Fin ([0-9]+)\) :\n'
        +re.escape('    member certificate v = true ↔ Reach (ReverseEdge (fun a b => (a,b) ∈ graph.edges)) root v :=\n'
                    '  check_exact graph root certificate accepted v\n')
        +r'theorem answer_mask : \(List.finRange ([0-9]+)\).all '
        +re.escape('(fun v => decide (v ∈ answer) == member certificate v) = true := by decide +kernel\n'
            'end Stage8Graph\n#print axioms Stage8Graph.accepted\n#print axioms Stage8Graph.exact\n#print axioms Stage8Graph.answer_mask\n'))
    m = re.fullmatch(pattern, text)
    if not m:
        raise ValueError('Lean export outside closed grammar')
    nn, rawedges, nr, rt, nc, witnesses, na, answer, ne, nm = m.groups()
    if any(int(v) != n for v in (nn, nr, nc, na, ne, nm)) or int(rt) != root:
        raise ValueError('Lean graph size/root mismatch')
    if rawedges and not re.fullmatch(edge_item+r'(?:, '+edge_item+')*', rawedges):
        raise ValueError('Lean edge syntax')
    decoded_edges = np.array([[int(a), int(b)] for a, b in re.findall(edge_item, rawedges)], dtype=np.int64).reshape((-1, 2))
    if not np.array_equal(edges, decoded_edges):
        raise ValueError('complete Lean edges mismatch')
    decoded = [(int(v), int(p), int(r)) for v, p, r in re.findall(
        r'  \| ([0-9]+) => some ⟨⟨([0-9]+), by decide \+kernel⟩, ([0-9]+)⟩\n', witnesses)]
    expected = [(int(v), root if int(v) == root else int(p), int(r)) for v, p, r in zip(ids, parents, ranks)]
    if decoded != expected:
        raise ValueError('complete Lean witnesses mismatch')
    if not re.fullmatch(fin+r'(?:, '+fin+')*', answer):
        raise ValueError('Lean answer syntax')
    if [int(v) for v in re.findall(fin, answer)] != ids.tolist():
        raise ValueError('complete Lean answer mismatch')
    return True
