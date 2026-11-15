"""Kernel proof exports for graph certificates and contextual source bindings."""
import re
import numpy as np
from .stage8_graph import check_certificate

NAMES = ('Stage8Graph.accepted', 'Stage8Graph.exact', 'Stage8Graph.answer_mask')


def render_scalable(n, edges, root, ids, parents, ranks):
    """Reuse the verified blocked checker and balanced witness lookup from stage 4."""
    from .fast_export import render_fast
    from .graph import graph_sha256
    check_certificate(n, edges, root, ids, parents, ranks)
    width = len(str(n))
    names = [str(i).zfill(width) for i in range(n)]
    graph = {'nodes': names, 'edges': [[names[int(a)], names[int(b)]] for a, b in edges]}
    cert = {'format': 'repo-proof-certificate-v1', 'graph_sha256': graph_sha256(graph),
            'query': {'kind': 'reverse_reachability_including_root', 'root': names[root]},
            'candidates': [{'node': names[int(v)], 'parent': None if int(v) == root else names[int(p)],
                            'rank': int(r)} for v, p, r in zip(ids, parents, ranks)]}
    text = render_fast(graph, names[root], cert, namespace='Stage8Graph')
    answer = f'''def answer : List (Fin {n}) := (List.finRange {n}).filter (fastMember certificate)
theorem answer_exact (v : Fin {n}) : v ∈ answer ↔
    Reach (ReverseEdge (fun a b => (a,b) ∈ (eraseGraph graph).edges)) root v := by
  simpa [answer, List.mem_filter] using exact v
'''
    return text.replace('end Stage8Graph\n', answer + 'end Stage8Graph\n') + '#print axioms Stage8Graph.answer_exact\n'


def render_source(identities, sources, rules, edges, root, ids, parents, ranks):
    """Source theorem over complete bytes and manually accepted mapping rules.

    identities are ordered (repository, commit, path) triples. sources contains
    exactly one byte string per identity. GraphProof is a separately audited,
    freshly checked render_scalable export with the same numeric domain.
    """
    from .source_bytes_v2 import certificate, piece, bytes_literal
    from .stage8_sources import resolve_event
    from .fast_export import _tree
    n = len(identities)
    if len(sources) != n or len(set(identities)) != n:
        raise ValueError('source identity universe is incomplete or duplicated')
    check_certificate(n, edges, root, ids, parents, ranks)
    index = {identity: i for i, identity in enumerate(identities)}
    fin = lambda i: f'⟨{int(i)}, by decide +kernel⟩'
    raw = lambda value: bytes_literal(value.encode('utf-8'))
    lines = ['import ContextualSourceBinding', 'import GraphProof',
             'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
             'namespace Stage8Source', 'open RepoProof RepoProof.Contextual']
    for i, identity in enumerate(identities):
        lines.append(f'def identity{i} : Identity := ⟨' + ', '.join(map(raw, identity)) + '⟩')
    lines += [f'def names (v : Fin {n}) : Identity :=']
    lines += _tree(0, n, lambda i: f'identity{i}', '  ')
    lines += ['def rules : List Rule := [']
    rule_literals = []
    for rule in rules:
        target = 'none' if rule['to'] is None else 'some (' + ', '.join(map(raw, rule['to'])) + ')'
        rule_literals.append('  ⟨' + ', '.join([raw(rule['from'][0]), raw(rule['from'][1]),
            raw(rule['prefix']), target, raw(rule['target_prefix'])]) + '⟩')
    lines += [literal + (',' if i + 1 < len(rule_literals) else '') for i, literal in enumerate(rule_literals)]
    lines += [']']
    produced = set()
    for i, (identity, data) in enumerate(zip(identities, sources)):
        pieces, events = certificate(data)
        resolutions, targets = [], set()
        for event in events:
            target, _ = resolve_event(identity, event, rules, index)
            target_id = index[target] if target is not None else None
            resolutions.append('(' + raw(event) + ', ' + ('none' if target_id is None else 'some ' + fin(target_id)) + ')')
            if target_id is not None:
                targets.add(target_id)
                produced.add((i, target_id))
        piece_literals = ', '.join(map(piece, pieces))
        resolution_literals = ', '.join(resolutions)
        target_literals = ', '.join(fin(target) for target in sorted(targets))
        lines += [f'def file{i} : File {n} := ⟨[{piece_literals}], [{resolution_literals}], [{target_literals}]⟩',
            f'theorem file{i}_checked : fileOK names rules {fin(i)} file{i} = true := by',
            '  apply fileOK_of_parts', '  ·']
        for _ in pieces:
            lines += ['    apply SourceBytes.checked_cons', '    · decide +kernel',
                      '    · decide +kernel']
        lines += ['    rfl'] + ['  · decide +kernel'] * 5
    if produced != set(map(tuple, edges.tolist())):
        raise ValueError('source graph differs in one or both directions')
    lines += [f'def files (v : Fin {n}) : File {n} :='] + _tree(0, n, lambda i: f'file{i}', '  ')
    lines += [f'theorem names_injective : Function.Injective names := by',
              '  intro a b h', '  have checked : ∀ a b, names a = names b → a = b := by decide +kernel',
              '  exact checked a b h',
              f'theorem files_checked (v : Fin {n}) : fileOK names rules v (files v) = true := by']
    for i in range(n):
        lines += [f'  by_cases h{i} : v.val = {i}',
                  f'  · have hv : v = {fin(i)} := Fin.ext h{i}',
                  f'    subst v', f'    exact file{i}_checked']
    lines += ['  have bound := v.isLt', '  omega',
              'theorem graph_checked : (graphOfFiles files).edges = (eraseGraph Stage8Graph.graph).edges := by decide +kernel',
              f'def answer : List (Fin {n}) := [' + ', '.join(fin(i) for i in ids) + ']',
              f'theorem answer_checked (v : Fin {n}) : v ∈ answer ↔ fastMember Stage8Graph.certificate v = true := by',
              '  have checked : ∀ v, v ∈ answer ↔ fastMember Stage8Graph.certificate v = true := by decide +kernel',
              '  exact checked v',
              'def payload : List Identity := answer.map names',
              'theorem source_to_answer (p : Identity) : p ∈ payload ↔ ∃ v, names v = p ∧',
              '    Reach (ReverseEdge (Import names rules files)) Stage8Graph.root v :=',
              '  answer_exact names rules files Stage8Graph.graph Stage8Graph.root Stage8Graph.certificate',
              '    names_injective files_checked graph_checked Stage8Graph.accepted answer answer_checked p',
              'end Stage8Source', '#print axioms Stage8Source.names_injective',
              '#print axioms Stage8Source.files_checked', '#print axioms Stage8Source.graph_checked',
              '#print axioms Stage8Source.answer_checked', '#print axioms Stage8Source.source_to_answer']
    return '\n'.join(lines) + '\n'


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
