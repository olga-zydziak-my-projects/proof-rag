"""Sharded source layer and fresh query composition; closed export audits.

The independent Stage 8 parser reads every source byte and rule after lossless
reassembly of the shards. Extra shard framing and new proof glue are closed
grammars, with no arbitrary Lean commands or unchecked suffixes.
"""
import re
from pathlib import Path
import numpy as np
from repo_proof.stage8_lean import render_source, render_scalable
from repo_proof.stage5_v2 import tree, range_proof
from repo_proof.stage8_graph import reverse_index, search
from stage8_proof_audit import audit_source, audit_graph
from stage5_v2_audit_bytes import route_body

HEADER = ('import ContextualSourceBinding\nimport GraphProof\n'
          'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n'
          'namespace Stage8Source\nopen RepoProof RepoProof.Contextual\n')
GROUP = 8
FIN = lambda i: f'⟨{int(i)}, by decide +kernel⟩'


def ranges(start, count, indent='  '):
    if count <= 16:
        return [indent + 'decide +kernel']
    half = count // 2
    return [indent + f"apply all_range'_split {start} {half} {count-half}", indent + '·'] + ranges(start, half, indent + '  ') + [indent + '·'] + ranges(start + half, count-half, indent + '  ')


def inverse_text(n):
    lines = ['def identityKey (p : Identity) : List UInt8 := p.repository ++ [0] ++ p.commit ++ [0] ++ p.path',
             f'def inverse (p : Identity) : Option (Fin {n}) :=']
    lines += tree(0, n, lambda i: f'if p == identity{i} then some {FIN(i)} else none', '  ',
                  lambda m: f'compare (identityKey p) (identityKey identity{m}) == .lt')
    lines += ['theorem mapping_checked : RepoProof.SourceBinding.allVertices (fun v => inverse (names v) == some v) = true := by',
              '  apply RepoProof.SourceBinding.allVertices_of_range'] + ranges(0, n)
    lines += ['theorem names_injective : Function.Injective names :=',
              '  RepoProof.Stage9.inverse_injective names inverse mapping_checked']
    return '\n'.join(lines) + '\n'


def audit_inverse(text,n):
    """Independent recursive reader; never calls tree/inverse_text/ranges."""
    lines=text.splitlines(); cursor=0
    def consume(value):
        nonlocal cursor
        if cursor>=len(lines) or lines[cursor]!=value:
            raise ValueError('inverse closed grammar at line '+str(cursor))
        cursor+=1
    consume('def identityKey (p : Identity) : List UInt8 := p.repository ++ [0] ++ p.commit ++ [0] ++ p.path')
    consume(f'def inverse (p : Identity) : Option (Fin {n}) :=')
    def node(lo,hi,indent):
        if hi-lo==1:
            consume(indent+f'if p == identity{lo} then some ⟨{lo}, by decide +kernel⟩ else none')
            return
        mid=(lo+hi)//2
        consume(indent+f'if compare (identityKey p) (identityKey identity{mid}) == .lt then')
        node(lo,mid,indent+'  ')
        consume(indent+'else')
        node(mid,hi,indent+'  ')
    node(0,n,'  ')
    consume('theorem mapping_checked : RepoProof.SourceBinding.allVertices (fun v => inverse (names v) == some v) = true := by')
    consume('  apply RepoProof.SourceBinding.allVertices_of_range')
    def proof(start,count,indent):
        if count<=16:
            consume(indent+'decide +kernel'); return
        half=count//2
        consume(indent+f"apply all_range'_split {start} {half} {count-half}")
        consume(indent+'·'); proof(start,half,indent+'  ')
        consume(indent+'·'); proof(start+half,count-half,indent+'  ')
    proof(0,n,'  ')
    consume('theorem names_injective : Function.Injective names :=')
    consume('  RepoProof.Stage9.inverse_injective names inverse mapping_checked')
    consume('end Stage8Source')
    consume('#print axioms Stage8Source.names_injective')
    if cursor!=len(lines):raise ValueError('extra inverse suffix')


def master_text(n):
    lines = ['import CorpusGraph'] + [f'import SourceGroup{k:04}' for k in range((n+GROUP-1)//GROUP)]
    lines += ['set_option maxHeartbeats 0', 'set_option maxRecDepth 100000',
              'namespace Stage8Source', 'open RepoProof RepoProof.Contextual',
              f'def files (v : Fin {n}) : File {n} :=']
    lines += tree(0, n, lambda i: f'file{i}', '  ', lambda m: f'v.val < {m}')
    lines += ['theorem all_files_checked : RepoProof.SourceBinding.allVertices (fun v => fileOK names rules v (files v)) = true := by',
              '  apply RepoProof.SourceBinding.allVertices_of_range']
    lines += [line.replace('range_cons','RepoProof.SourceBinding.range_cons').replace('index_from','RepoProof.SourceBinding.index_from') for line in range_proof(0, n, lambda i: f'exact index_from (fun v => fileOK names rules v (files v)) {FIN(i)} file{i}_checked')]
    lines += [f'theorem files_checked (v : Fin {n}) : fileOK names rules v (files v) = true :=',
              '  RepoProof.SourceBinding.allVertices_at _ all_files_checked v',
              'theorem graph_checked : (graphOfFiles files).edges = (eraseGraph Stage9CorpusGraph.graph).edges := by decide +kernel',
              'end Stage8Source', '#print axioms Stage8Source.files_checked', '#print axioms Stage8Source.graph_checked']
    return '\n'.join(lines) + '\n'


def graph_parts(text):
    return text.split('def root :', 1)


def export_sources(folder, identities, sources, rules, edges):
    n = len(identities)
    ids, p, r = search(n, reverse_index(n, edges), 0)
    original = render_source(identities, sources, rules, edges, 0, ids, p[ids], r[ids])
    # Audit before splitting, then audit actual persisted shards independently.
    audit_source(original, identities, sources, rules, edges, ids)
    names, rest = original.split('def file0 :', 1)
    names = names.replace(HEADER, 'import Stage9Binding\nset_option maxRecDepth 100000\nset_option maxHeartbeats 0\nnamespace Stage8Source\nopen RepoProof RepoProof.Contextual\n', 1)
    (folder/'SourceNames.lean').write_text(names + inverse_text(n) + 'end Stage8Source\n#print axioms Stage8Source.names_injective\n', encoding='utf-8', newline='\n')
    rest = 'def file0 :' + rest
    files_part = rest.split('def files (', 1)[0]
    chunks = re.split(r'(?=^def file[0-9]+ :)', files_part, flags=re.M)[1:]
    if len(chunks) != n:
        raise ValueError('source shard coverage')
    for start in range(0, n, GROUP):
        tail = min(n, start+GROUP)
        text = ('import SourceNames\nnamespace Stage8Source\nopen RepoProof RepoProof.Contextual\n'
                'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n' + ''.join(chunks[start:tail]) +
                'end Stage8Source\n' + ''.join(f'#print axioms Stage8Source.file{i}_checked\n' for i in range(start, tail)))
        (folder/f'SourceGroup{start//GROUP:04}.lean').write_text(text, encoding='utf-8', newline='\n')
    graph = render_scalable(n, edges, 0, ids, p[ids], r[ids])
    prefix, _ = graph_parts(graph)
    (folder/'CorpusGraph.lean').write_text(prefix.replace('Stage8Graph', 'Stage9CorpusGraph') + 'end Stage9CorpusGraph\n', encoding='utf-8', newline='\n')
    (folder/'SourceCorpus.lean').write_text(master_text(n), encoding='utf-8', newline='\n')
    audit_sources(folder, identities, sources, rules, edges)


def audit_sources(folder, identities, sources, rules, edges):
    n = len(identities)
    ids, p, r = search(n, reverse_index(n, edges), 0)
    # Only audited names and file bodies are reassembled. Framing and all new
    # proof commands must match closed, data-free schemas for this domain.
    names = (folder/'SourceNames.lean').read_text(encoding='utf-8')
    head = 'import Stage9Binding\nset_option maxRecDepth 100000\nset_option maxHeartbeats 0\nnamespace Stage8Source\nopen RepoProof RepoProof.Contextual\n'
    split=names.find('def identityKey (p : Identity)')
    if not names.startswith(head) or split<0:
        raise ValueError('names/inverse outside closed grammar')
    audit_inverse(names[split:],n)
    names = HEADER + names[len(head):split]
    actual = []
    groups = list(sorted(folder.glob('SourceGroup*.lean')))
    if [x.name for x in groups] != [f'SourceGroup{k:04}.lean' for k in range((n+GROUP-1)//GROUP)]:
        raise ValueError('source group coverage')
    for k, path in enumerate(groups):
        text = path.read_text(encoding='utf-8')
        begin = ('import SourceNames\nnamespace Stage8Source\nopen RepoProof RepoProof.Contextual\n'
                 'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n')
        end = 'end Stage8Source\n' + ''.join(f'#print axioms Stage8Source.file{i}_checked\n' for i in range(k*GROUP, min(n,(k+1)*GROUP)))
        if not text.startswith(begin) or not text.endswith(end):
            raise ValueError('source group framing/axioms changed')
        actual.append(text[len(begin):-len(end)])
    # The original auditor also parses the balanced routes and every literal.
    template = render_source(identities, sources, rules, edges, 0, ids, p[ids], r[ids])
    suffix = 'def files (' + template.split('def files (', 1)[1]
    audit_source(names + ''.join(actual) + suffix, identities, sources, rules, edges, ids)
    master = (folder/'SourceCorpus.lean').read_text(encoding='utf-8')
    route=master.split(f'def files (v : Fin {n}) : File {n} :=\n',1)[1].split('theorem all_files_checked',1)[0]
    if route_body(route,r'file\d+',n)!=[f'file{i}' for i in range(n)]:
        raise ValueError('actual master file routing mismatch')
    if master != master_text(n):
        raise ValueError('shared corpus proof outside closed grammar')
    rawgraph = (folder/'CorpusGraph.lean').read_text(encoding='utf-8')
    ending = 'end Stage9CorpusGraph\n'
    if not rawgraph.endswith(ending):
        raise ValueError('corpus graph suffix')
    full = rawgraph[:-len(ending)].replace('Stage9CorpusGraph', 'Stage8Graph') + 'def root :' + graph_parts(render_scalable(n, edges, 0, ids, p[ids], r[ids]))[1]
    audit_graph(full, n, edges, 0, ids, p[ids], r[ids])
    return True


def query_source(n, ids):
    answer = ', '.join(FIN(i) for i in ids)
    lines = ['import SourceCorpus', 'import QueryGraph', 'set_option maxHeartbeats 0',
             'set_option maxRecDepth 100000', 'namespace Stage9Answer',
             'open RepoProof RepoProof.Contextual Stage8Source',
             f'def answer : List (Fin {n}) := [{answer}]',
             'theorem mask : RepoProof.SourceBinding.allVertices (fun v => decide (v ∈ answer) == fastMember Stage9QueryGraph.certificate v) = true := by',
             '  apply RepoProof.SourceBinding.allVertices_of_range'] + ranges(0, n)
    lines += [f'theorem answer_checked (v : Fin {n}) : v ∈ answer ↔ fastMember Stage9QueryGraph.certificate v = true := by',
              '  have h := RepoProof.SourceBinding.allVertices_at _ mask v', '  cases hb : fastMember Stage9QueryGraph.certificate v <;> simpa [hb] using h',
              'def payload : List Identity := answer.map names',
              'theorem source_to_answer (p : Identity) : p ∈ payload ↔ ∃ v, names v = p ∧',
              '    Reach (ReverseEdge (Import names rules files)) Stage9QueryGraph.root v :=',
              '  answer_exact names rules files Stage9QueryGraph.graph Stage9QueryGraph.root Stage9QueryGraph.certificate',
              '    names_injective files_checked graph_checked Stage9QueryGraph.accepted answer answer_checked p',
              'end Stage9Answer', '#print axioms Stage9Answer.answer_checked', '#print axioms Stage9Answer.source_to_answer']
    return '\n'.join(lines) + '\n'


def export_query(folder, n, edges, root, ids, parents, ranks):
    full = render_scalable(n, edges, root, ids, parents, ranks)
    audit_graph(full, n, edges, root, ids, parents, ranks)
    prefix, rest = graph_parts(full)
    head = ('import CorpusGraph\nimport FastChecker\nimport ProofTiming\n'
            'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n'
            f'namespace Stage9QueryGraph\nopen RepoProof Stage9CorpusGraph\ndef graph : BlockedGraph {n} := Stage9CorpusGraph.graph\n')
    text = head + ('def root :' + rest).replace('Stage8Graph', 'Stage9QueryGraph')
    (folder/'QueryGraph.lean').write_text(text, encoding='utf-8', newline='\n')
    (folder/'QueryAnswer.lean').write_text(query_source(n, ids), encoding='utf-8', newline='\n')
    audit_query(folder, n, edges, root, ids, parents, ranks)


def audit_query(folder, n, edges, root, ids, parents, ranks):
    text = (folder/'QueryGraph.lean').read_text(encoding='utf-8')
    head = ('import CorpusGraph\nimport FastChecker\nimport ProofTiming\n'
            'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n'
            f'namespace Stage9QueryGraph\nopen RepoProof Stage9CorpusGraph\ndef graph : BlockedGraph {n} := Stage9CorpusGraph.graph\n')
    if not text.startswith(head):
        raise ValueError('query import/graph substitution')
    prefix, _ = graph_parts(render_scalable(n, edges, root, ids, parents, ranks))
    audit_graph(prefix + text[len(head):].replace('Stage9QueryGraph', 'Stage8Graph'), n, edges, root, ids, parents, ranks)
    actual=(folder/'QueryAnswer.lean').read_text(encoding='utf-8')
    match=re.search(r'^def answer : List \(Fin ([0-9]+)\) := \[(.*)\]$',actual,re.M)
    fin=r'⟨([0-9]+), by decide \+kernel⟩'
    if not match or int(match[1])!=n or not re.fullmatch(fin+r'(?:, '+fin+r')*',match[2]) or [int(v) for v in re.findall(fin,match[2])]!=list(map(int,ids)):
        raise ValueError('actual full query answer literal mismatch')
    if actual != query_source(n, ids):
        raise ValueError('query answer/closed proof grammar changed')
    return True
