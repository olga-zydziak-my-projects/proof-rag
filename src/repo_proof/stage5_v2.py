"""Stage5 v2 immutable capture and proof-input export. No proof result is assumed."""
from dataclasses import dataclass
from dataclasses import field
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from time import perf_counter

from .extraction import ExpectedInputs,load_snapshot,build_extraction,read_json
from .generator import generate_certificate
from .source_bytes_v2 import certificate,piece,bytes_literal

BASELINE='e4984110743131d04ad984eaaa48d33d72867336'
CONTRACT='fcd136117c0a699a5b31b2553f5940ac95c2b4ffaecf187b7fa5d05ae93e8690'
ROOT='mojo/public/mojom/base/time.mojom'

def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(data): return (json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')

@dataclass(frozen=True)
class Blob:
    path: str
    data: bytes
    oid: str
    mode: str

@dataclass(frozen=True)
class Captured:
    pin: dict
    blobs: tuple
    graph: dict
    certificate: dict
    extraction: dict
    timings: dict = field(default_factory=dict)

def capture(project):
    start=perf_counter()
    project=Path(project)
    if sha((project/'docs/stage5-contract-v2.md').read_bytes())!=CONTRACT:
        raise ValueError('v2 contract changed')
    raw=subprocess.run(['git','show',BASELINE+':corpus.lock.json'],cwd=project,
                       capture_output=True,check=True).stdout
    lock=json.loads(raw)
    if (lock['commit']!='27cec857a08a0ee0e1b41f5eb18c07467a0ce093' or
            lock['root_tree_object_id']!='25131300fa459906dedb84bf592a8537b7848771'):
        raise ValueError('accepted history conflicts with authorized source pin')
    cfg=read_json(project/'local/corpus.json')
    if cfg['commit']!=lock['commit'] or cfg['repository']!=lock['repository']:
        raise ValueError('configuration differs from accepted anchor')
    expected=ExpectedInputs(lock['commit'],lock['manifest_sha256'],ROOT)
    snap=load_snapshot(Path(cfg['data_dir']),expected)
    if snap.diagnostics: raise ValueError('incomplete source snapshot')
    provenance_seconds=perf_counter()-start
    start=perf_counter()
    rebuilt=build_extraction(snap,expected)  # consumes THIS capture, never rereads source
    extraction_seconds=perf_counter()-start
    start=perf_counter()
    baseline=read_json(project/'local/stage2/extraction.json')
    if canonical(rebuilt)!=canonical(baseline): raise ValueError('captured source extraction differs from full baseline')
    if not rebuilt['coverage']['source_complete']: raise ValueError('source syntax/targets unresolved')
    blobs=[]
    for row in sorted(snap.source_entries,key=lambda x:x['path']):
        row['path'].encode('utf-8',errors='strict')
        blobs.append(Blob(row['path'],snap.source_bytes[row['path']],row['object_id'],row['mode']))
    cert=generate_certificate(rebuilt['graph'],ROOT)
    if canonical(cert)!=canonical(read_json(project/'local/stage2/certificate.json')): raise ValueError('certificate changed')
    return Captured({'repository':lock['repository'],'commit':lock['commit'],
        'tree':lock['root_tree_object_id'],'manifest_sha256':lock['manifest_sha256']},
        tuple(blobs),rebuilt['graph'],cert,rebuilt,
        {'provenance_seconds':provenance_seconds,'extraction_seconds':extraction_seconds,
         'baseline_and_certificate_seconds':perf_counter()-start})

def snapshot_payload(captured):
    return {'schema':'stage5-source-input-v2','pin':dict(captured.pin),'contract_sha256':CONTRACT,
      'files':[{'id':i,'path':b.path,'mode':b.mode,'oid':b.oid,'sha256':sha(b.data),
                'data_base64':base64.b64encode(b.data).decode('ascii')} for i,b in enumerate(captured.blobs)]}

def validate_snapshot(value,captured):
    # Full semantic/byte equality, independent of attacker-supplied hashes.
    expected=snapshot_payload(captured)
    if canonical(value)!=canonical(expected): raise ValueError('source inventory, metadata or actual source bytes changed')

def tree(lo,hi,leaf,indent,condition):
    if hi-lo==1: return [indent+leaf(lo)]
    mid=(lo+hi)//2
    return [indent+'if '+condition(mid)+' then']+tree(lo,mid,leaf,indent+'  ',condition)+[indent+'else']+tree(mid,hi,leaf,indent+'  ',condition)

def range_proof(start,length,leaf,indent='  '):
    if length>32:
        left=length//2
        return [indent+f"apply all_range'_split {start} {left} {length-left}",indent+'·']+range_proof(start,left,leaf,indent+'  ')+[indent+'·']+range_proof(start+left,length-left,leaf,indent+'  ')
    lines=[]
    for i in range(start,start+length):
        lines += [indent+f'apply range_cons {i} {start+length-i-1}',indent+'· '+leaf(i)]
    return lines+[indent+'rfl']

def export_names(captured,out):
    out=Path(out); n=len(captured.blobs)
    lines=['import SourceGraphBinding','import ProofTiming','open RepoProof RepoProof.SourceBinding',
           'set_option maxHeartbeats 0','set_option maxRecDepth 100000','namespace SourceNames']
    for i,b in enumerate(captured.blobs):
        raw=b.path.encode('utf-8')
        lines+=[f'def path{i} : Path := (⟨{len(raw)}, 0x{int.from_bytes(raw,"little"):x}⟩ : SourceBytes.Block).bytes']
    lines += [f'def names (v : Fin {n}) : Path :=']+tree(0,n,lambda i:f'path{i}','  ',lambda m:f'v.val < {m}')
    fin=lambda i:f'⟨{i}, by decide +kernel⟩'
    lines += [f'def inverse (p : Path) : Option (Fin {n}) :=']+tree(0,n,lambda i:f'if p == path{i} then some {fin(i)} else none','  ',lambda m:f'compare p path{m} == .lt')
    lines += ['theorem mapping_checked : mappingOK names inverse = true := by',
              '  apply allVertices_of_range']
    # Kernel reductions are direct short ranges; no global take/drop.
    def chunks(start,count,indent):
        if count<=32: return [indent+'timed_kernel_decide']
        k=count//2
        return [indent+f"apply all_range'_split {start} {k} {count-k}",indent+'·']+chunks(start,k,indent+'  ')+[indent+'·']+chunks(start+k,count-k,indent+'  ')
    lines+=chunks(0,n,'  ')
    lines+=['end SourceNames','#print axioms SourceNames.mapping_checked']
    with (out/'SourceNames.lean').open('xb') as target:
        target.write(('\n'.join(lines)+'\n').encode('utf-8'))

def export_groups(captured,out,group_size=64):
    out=Path(out); n=len(captured.blobs); ids={b.path:i for i,b in enumerate(captured.blobs)}
    targets={i:[] for i in range(n)}
    for a,b in captured.graph['edges']: targets[ids[a]].append(ids[b])
    old_imports={f['path']:[x['decoded_path'] for x in f['imports']] for f in captured.extraction['files']}
    fin=lambda i:f'⟨{i}, by decide +kernel⟩'
    inventory=[]
    for start in range(0,n,group_size):
        group=start//group_size; module=f'SourceGroup{group:03}'
        lines=['import SourceNames','open RepoProof RepoProof.SourceBinding',
               'set_option maxHeartbeats 0','set_option maxRecDepth 100000',f'namespace {module}']
        for i in range(start,min(start+group_size,n)):
            blob=captured.blobs[i]; ps,events=certificate(blob.data)
            if events!=old_imports[blob.path]: raise ValueError('scanner/import projection mismatch: '+blob.path)
            for j,p in enumerate(ps): lines+=[f'def f{i}p{j} : SourceBytes.Piece := '+piece(p)]
            resolved=[]
            for path in events:
                target='none' if path not in ids else 'some '+fin(ids[path])
                resolved.append('('+bytes_literal(path.encode('utf-8'))+', '+target+')')
            lines += [f'def f{i} : File {n} := ⟨['+', '.join(f'f{i}p{j}' for j in range(len(ps)))+'], ['+', '.join(resolved)+'], ['+', '.join(fin(v) for v in targets[i])+']⟩',
                f'theorem f{i}_steps : SourceBytes.checked SourceBytes.initial f{i}.pieces = true := by']
            for _ in ps:
                lines += ['  apply SourceBytes.checked_cons','  · timed_kernel_decide','  · timed_kernel_decide']
            lines += ['  rfl',f'theorem f{i}_ok : fileOK SourceNames.names f{i} = true := by',
                      '  apply fileOK_of_parts',f'  · exact f{i}_steps','  · timed_kernel_decide',
                      '  · timed_kernel_decide','  ·']
            # Preserve named resolution records; each element gets its checked proof.
            for path in events:
                lines+=['    apply all_cons_true']
                if path in ids: lines+=['    · timed_kernel_decide']
                else:
                    lines+=['    · apply resolve_none_of_inverse SourceNames.names SourceNames.inverse SourceNames.mapping_checked',
                            '      timed_kernel_decide']
            lines+=['    rfl','  · timed_kernel_decide','  · timed_kernel_decide']
            inventory.append({'id':i,'path':blob.path,'module':module,'pieces':len(ps),
                              'source_bytes':len(blob.data),'source_sha256':sha(blob.data),
                              'imports':len(events)})
        lines+=[f'end {module}',f'#print axioms {module}.f{start}_ok',
                f'#print axioms {module}.f{min(start+group_size,n)-1}_ok']
        with (out/(module+'.lean')).open('xb') as target:
            target.write(('\n'.join(lines)+'\n').encode('utf-8'))
    return inventory
