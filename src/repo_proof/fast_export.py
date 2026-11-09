"""Stage-4 deterministic finite data, checked edge hints, and direct-block proof.

Serialization is checked separately; this Python exporter is not formally proved.
The Lean bridge establishes correctness of the typed Boolean checker.
"""
import json

from .graph import validate_graph
from .lean_export import render as validate_and_render_stage3


def _tree(lo, hi, leaf, indent, boundary=lambda mid: mid):
    if hi-lo == 1:
        return [indent+leaf(lo)]
    mid=(lo+hi)//2
    return ([indent+f'if v.val < {boundary(mid)} then']
            +_tree(lo,mid,leaf,indent+'  ',boundary)
            +[indent+'else']
            +_tree(mid,hi,leaf,indent+'  ',boundary))


def render_fast(graph, root, cert, namespace='ChromiumFast', hints=None):
    # Reuse the strict stage-3 schema/identity validator unchanged. The discarded
    # text does not assert that local witnesses satisfy either Lean checker.
    validate_and_render_stage3(graph,root,cert,'ValidationOnly')
    nodes,edge_set=validate_graph(graph)
    names=sorted(nodes)
    ids={s:i for i,s in enumerate(names)}
    edges=sorted(edge_set)
    n=len(names)
    records={w['node']:w for w in cert['candidates']}
    locations={edge:(i//64,i%64) for i,edge in enumerate(edges)}
    if hints is None:
        hints={}
    if not isinstance(hints,dict) or not set(hints)<=set(records):
        raise ValueError('hint overrides must name candidate records')
    for hint in hints.values():
        if hint is not None and (not isinstance(hint,(list,tuple)) or len(hint)!=2
                or any(type(i) is not int or i<0 for i in hint)):
            raise ValueError('hint must be null or a pair of natural indices')
    fin=lambda i:f'⟨{i}, by decide +kernel⟩'
    lines=['import FastChecker','import ProofTiming','set_option maxRecDepth 100000',
           'set_option maxHeartbeats 0',f'namespace {namespace}','open RepoProof']
    paths=[]
    for start in range(0,n,64):
        name=f'pathBlock{len(paths)}'; paths.append(name)
        chunk=names[start:start+64]
        lines+=[f'def {name} : Array String := #[']
        lines+=['  '+json.dumps(s,ensure_ascii=False)+(',' if i+1<len(chunk) else '')
                for i,s in enumerate(chunk)]
        lines+=[']']
    lines+=['def nodePaths : Array String := '+' ++ '.join(paths)]
    blocks=[]
    for start in range(0,len(edges),64):
        name=f'edgeBlock{len(blocks)}'; blocks.append(name)
        chunk=edges[start:start+64]
        lines+=[f'def {name} : List (Fin {n} × Fin {n}) := [']
        lines += [f'  ({fin(ids[a])}, {fin(ids[b])})'+(',' if i+1<len(chunk) else '')
                  for i,(a,b) in enumerate(chunk)]
        lines+=[']']
    lines += [f'def graph : BlockedGraph {n} := ⟨['+', '.join(blocks)+']⟩',
              f'def root : Fin {n} := {fin(ids[root])}']
    def value(i):
        node=names[i]; w=records.get(node)
        if w is None:
            return 'none'
        parent=w['parent'] if w['parent'] is not None else root
        hint=hints.get(node,None if node==root else locations.get((node,parent)))
        raw='none' if hint is None else f'some ({hint[0]}, {hint[1]})'
        return f'some ⟨{fin(ids[parent])}, {w["rank"]}, {raw}⟩'
    witnesses=[]
    for start in range(0,n,64):
        name=f'witnessBlock{len(witnesses)}'; witnesses.append(name)
        lines+=[f'def {name} (v : Fin {n}) : Option (EnhancedWitness {n}) :=']
        lines+=_tree(start,min(start+64,n),value,'  ')
    lines+=[f'def certificate : EnhancedCertificate {n} := ⟨fun v =>']
    lines+=_tree(0,len(witnesses),lambda i:witnesses[i]+' v','  ',lambda mid:mid*64)
    lines[-1]+='⟩'
    lines+=['theorem accepted : fastCheck graph root certificate = true := by',
            '  apply fastCheck_of_parts','  · timed_kernel_decide','  ·']
    def range_proof(start,length,indent):
        if length<=64:
            return [indent+'timed_kernel_decide']
        left=length//2; right=length-left
        return ([indent+f"apply all_range'_split {start} {left} {right}"]
                +[indent+'·']+range_proof(start,left,indent+'  ')
                +[indent+'·']+range_proof(start+left,right,indent+'  '))
    lines+=range_proof(0,n,'    ')
    lines+=['  · change (['+', '.join(blocks)+']).all (fun b => b.all (fastClosure certificate)) = true']
    # Apply the proved outer-list lemma, leaving each actual named block intact.
    for _ in blocks:
        lines+=['    apply all_cons_true','    · timed_kernel_decide']
    lines+=['    rfl',
            'theorem erased_accepted : check (eraseGraph graph) root (eraseHints certificate) = true :=',
            '  fastCheck_refines graph root certificate accepted',
            f'theorem exact (v : Fin {n}) :',
            '    fastMember certificate v = true ↔',
            '      Reach (ReverseEdge (fun a b => (a,b) ∈ (eraseGraph graph).edges)) root v :=',
            '  fastCheck_exact graph root certificate accepted v',f'end {namespace}',
            f'#print axioms {namespace}.accepted',f'#print axioms {namespace}.erased_accepted',
            f'#print axioms {namespace}.exact']
    return '\n'.join(lines)+'\n'
