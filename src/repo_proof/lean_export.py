"""Deterministic strict serialization to finite Lean data (not a formal parser proof)."""
import json
from pathlib import Path
from repo_proof.graph import validate_graph, graph_sha256, ValidationError


def load_json(path):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)


def render(graph, root, cert, namespace='Chromium'):
    nodes, edges = validate_graph(graph)
    if not isinstance(root, str) or root not in nodes:
        raise ValueError('unknown root')
    if not isinstance(cert, dict) or set(cert) != {'format','graph_sha256','query','candidates'}:
        raise ValueError('certificate schema')
    if cert['format'] != 'repo-proof-certificate-v1' or cert['graph_sha256'] != graph_sha256(graph):
        raise ValueError('certificate identity')
    if cert['query'] != {'kind':'reverse_reachability_including_root','root':root}:
        raise ValueError('query mismatch')
    if not isinstance(cert['candidates'], list):
        raise ValueError('candidate list')
    records = {}
    for w in cert['candidates']:
        if not isinstance(w, dict) or set(w) != {'node','parent','rank'}:
            raise ValueError('witness schema')
        v, p, r = w['node'], w['parent'], w['rank']
        if not isinstance(v,str) or v not in nodes or v in records:
            raise ValueError('unknown or duplicate candidate')
        if type(r) is not int or r < 0:
            raise ValueError('non-natural rank')
        if v == root:
            if p is not None or r != 0:
                raise ValueError('invalid root encoding')
        elif not isinstance(p,str) or p not in nodes:
            raise ValueError('unknown parent')
        records[v] = w
    names = sorted(nodes)
    if any(any(ord(ch) < 32 or ord(ch) == 127 for ch in name) for name in names):
        raise ValueError('control characters in exported paths are unsupported')
    ids = {s:i for i,s in enumerate(names)}
    n = len(names)
    fin = lambda i: f'⟨{i}, by decide +kernel⟩'
    lines = ['import ProofTiming', 'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
             f'namespace {namespace}', 'open RepoProof']
    path_blocks=[]
    for start in range(0,n,64):
        name=f'pathBlock{len(path_blocks)}'
        path_blocks.append(name)
        chunk=names[start:start+64]
        lines += [f'def {name} : Array String := #[']
        lines += [('  ' + json.dumps(s, ensure_ascii=False) + (',' if i+1<len(chunk) else '')) for i,s in enumerate(chunk)]
        lines += [']']
    lines += ['def nodePaths : Array String := '+' ++ '.join(path_blocks)]
    es = sorted(edges)
    blocks=[]
    for start in range(0,len(es),64):
        name=f'edgeBlock{len(blocks)}'
        blocks.append(name)
        chunk=es[start:start+64]
        lines += [f'def {name} : List (Fin {n} × Fin {n}) := [']
        lines += [f'  ({fin(ids[a])}, {fin(ids[b])})' + (',' if i+1<len(chunk) else '') for i,(a,b) in enumerate(chunk)]
        lines += [']']
    edges_expr=' ++ '.join(blocks) if blocks else '[]'
    lines += [f'def graph : FiniteGraph {n} := ⟨{edges_expr}⟩', f'def root : Fin {n} := {fin(ids[root])}']
    witness_blocks=[]
    for i,s in enumerate(names):
        if i%64==0:
            block=f'witnessBlock{len(witness_blocks)}'
            witness_blocks.append(block)
            lines += [f'def {block} (v : Fin {n}) : Option (Witness {n}) :=']
        w = records.get(s)
        entry = 'none' if w is None else f'some ⟨{fin(ids[w["parent"]] if w["parent"] is not None else ids[root])}, {w["rank"]}⟩'
        end=i%64==63 or i+1==n
        lines.append(f'  if v.val == {i} then '+entry+' else')
        if end: lines += ['  none']
    def split_proof(length, indent):
        if length <= 64:
            return [indent + 'timed_kernel_decide']
        k = length // 2
        return ([indent + f'apply all_split _ _ {k}'] +
                [indent + '·'] + split_proof(k, indent+'  ') +
                [indent + '·'] + split_proof(length-k, indent+'  '))
    lines += [f'def certificate : FiniteCertificate {n} := ⟨fun v =>']
    for i,block in enumerate(witness_blocks):
        lines += [f'  if v.val < {(i+1)*64} then {block} v else' if i+1<len(witness_blocks) else '  '+block+' v⟩']
    lines += [
              'theorem accepted : check graph root certificate = true := by',
              '  unfold check', '  apply Bool.and_eq_true_iff.mpr', '  constructor',
              '  · apply Bool.and_eq_true_iff.mpr', '    constructor',
              '    · timed_kernel_decide', '    ·']
    lines += split_proof(n, '      ')
    lines += ['  ·'] + split_proof(len(es), '    ')
    lines += [
              'theorem exact (v : Fin '+str(n)+') :',
              '    member certificate v = true ↔ Reach (ReverseEdge (fun a b => (a,b) ∈ graph.edges)) root v :=',
              '  check_exact graph root certificate accepted v', f'end {namespace}',
              f'#print axioms {namespace}.accepted', f'#print axioms {namespace}.exact']
    return '\n'.join(lines)+'\n'
