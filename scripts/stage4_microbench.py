"""Small repeated kernel experiments; never imports the Chromium proof.

Every measured proof is checked in a fresh Lean process. MicroData.olean is
prepared once and explicitly reused, as are stage-3 Checker/ProofTiming.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import time


def generate_data(n=256, block=32, witness_block=8):
    f = lambda i: f'⟨{i}, by decide +kernel⟩'
    lines = ['import ProofTiming', 'set_option maxHeartbeats 0',
             'set_option maxRecDepth 100000', 'open RepoProof',
             'namespace MicroData']
    names = []
    for start in range(0, n, block):
        name = f'b{len(names)}'; names.append(name)
        chunk = [(i, 0) for i in range(start, min(n, start+block))]
        lines.append(f'def {name} : List (Fin {n} × Fin {n}) := [')
        lines.extend('  ('+f(a)+', '+f(b)+')'+(',' if j+1<len(chunk) else '')
                     for j,(a,b) in enumerate(chunk))
        lines.append(']')
    lines += [f'def edgeEnd : List (Fin {n} × Fin {n}) := '+' ++ '.join(names),
              f'def target : Fin {n} × Fin {n} := ({f(n-1)}, {f(0)})',
              'def edgeBegin := target :: edgeEnd.take '+str(n-1)]
    wnames = []
    for start in range(0,n,witness_block):
        name=f'w{len(wnames)}'; wnames.append(name)
        lines.append(f'def {name} (v : Fin {n}) : Option (Witness {n}) :=')
        for i in range(start,min(n,start+witness_block)):
            lines.append(f'  if v.val == {i} then some ⟨{f(0)}, {i}⟩ else')
        lines.append('  none')
    lines.append(f'def linear : FiniteCertificate {n} := ⟨fun v =>')
    for i,name in enumerate(wnames):
        lines.append(f'  if v.val < {(i+1)*witness_block} then {name} v else'
                     if i+1<len(wnames) else f'  {name} v⟩')
    def balanced(lo,hi,indent):
        if hi-lo==1: return [indent+wnames[lo]+' v']
        mid=(lo+hi)//2
        return ([indent+f'if v.val < {mid*witness_block} then']+
                balanced(lo,mid,indent+'  ')+[indent+'else']+
                balanced(mid,hi,indent+'  '))
    lines.append(f'def balanced : FiniteCertificate {n} := ⟨fun v =>')
    lines.extend(balanced(0,len(wnames),'  '))
    lines[-1]+='⟩'
    lines += [f'def repeatedRead (c : FiniteCertificate {n}) (i : Nat) : Bool :=',
              f'  if h : i < {n} then member c ⟨i,h⟩ && decide (rank c ⟨i,h⟩ = i) else false',
              f'def cachedRead (c : FiniteCertificate {n}) (i : Nat) : Bool :=',
              f'  if h : i < {n} then',
              '    match c.entries ⟨i,h⟩ with | none => false | some w => decide (w.rank = i)',
              '  else false',
              f'def closure (c : FiniteCertificate {n}) (e : Fin {n} × Fin {n}) : Bool :=',
              '  !member c e.2 || member c e.1',
              f'def observe (c : FiniteCertificate {n}) (i : Nat) : Option (Nat × Nat) :=',
              f'  if h : i < {n} then (c.entries ⟨i,h⟩).map (fun w => (w.parent.val,w.rank)) else none',
              'theorem table_agreement : (List.range '+str(n)+').all',
              '    (fun i => decide (observe linear i = observe balanced i)) = true := by decide +kernel',
              'theorem blockLast_mem {e} (h : e ∈ '+names[-1]+') : e ∈ edgeEnd := by',
              '  simp only [edgeEnd, List.mem_append]',
              '  simp only [h, or_true]',
              'end MicroData', '#print axioms MicroData.table_agreement',
              '#print axioms MicroData.blockLast_mem']
    return '\n'.join(lines)+'\n', names


def split_proof(n,indent='  ',leaf=32):
    if n<=leaf: return [indent+'timed_kernel_decide']
    k=n//2
    return ([indent+f'apply RepoProof.all_split _ _ {k}',indent+'·']+
            split_proof(k,indent+'  ',leaf)+[indent+'·']+
            split_proof(n-k,indent+'  ',leaf))


def cases(n,block,names):
    end=names[-1]
    result={
        'edge_begin_contains': ('edgeBegin.contains target = true', ['  timed_kernel_decide']),
        'edge_end_contains': ('edgeEnd.contains target = true', ['  timed_kernel_decide']),
        'edge_end_checked_block_position': ('edgeEnd.contains target = true', [
            f'  have h : {end}[{block-1}]? = some target := by timed_kernel_decide',
            '  exact List.contains_iff_mem.mpr (blockLast_mem (List.mem_of_getElem? h))']),
        'read_early_linear': (f'(List.range {block}).all (repeatedRead linear) = true',['  timed_kernel_decide']),
        'read_late_linear': (f'((List.range {block}).map (· + {n-block})).all (repeatedRead linear) = true',['  timed_kernel_decide']),
        'read_late_cached_linear': (f'((List.range {block}).map (· + {n-block})).all (cachedRead linear) = true',['  timed_kernel_decide']),
        'read_late_balanced': (f'((List.range {block}).map (· + {n-block})).all (repeatedRead balanced) = true',['  timed_kernel_decide']),
        'closure_global_slice': (f'((edgeEnd.drop {n-block}).take {block}).all (closure linear) = true',['  timed_kernel_decide']),
        'closure_direct_block': (f'{end}.all (closure linear) = true',['  timed_kernel_decide']),
        'closure_direct_block_balanced': (f'{end}.all (closure balanced) = true',['  timed_kernel_decide']),
        'combine_global_take_drop': ('edgeEnd.all (closure linear) = true',split_proof(n,leaf=block)),
    }
    def join_proof(length,indent):
        if length==1: return [indent+'timed_kernel_decide']
        return ([indent+'rw [List.all_append]',indent+'apply Bool.and_eq_true_iff.mpr',indent+'constructor',indent+'·']+
                join_proof(length-1,indent+'  ')+[indent+'· timed_kernel_decide'])
    proof=['  unfold edgeEnd']+join_proof(len(names),'  ')
    result['combine_direct_blocks']=('edgeEnd.all (closure linear) = true',proof)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean',default=r'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe')
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--nodes',type=int,default=256)
    p.add_argument('--block',type=int,default=32)
    p.add_argument('--report',default='verification/stage4-microbench.json')
    a=p.parse_args()
    assert a.nodes%a.block==0 and a.nodes%8==0 and a.nodes>=a.block
    root=Path(__file__).resolve().parents[1]
    os.chdir(root)
    if Path(a.report).exists():
        p.error('report already exists; choose a fresh --report path to preserve measurements')
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    out=root/'local/stage4/micro'; out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,LEAN_PATH=str(out)+os.pathsep+str(root/'formal'))
    source,names=generate_data(a.nodes,a.block)
    (out/'MicroData.lean').write_text(source,encoding='utf-8')
    t=time.perf_counter()
    build=subprocess.run([a.lean,'-o',str(out/'MicroData.olean'),str(out/'MicroData.lean')],env=env,capture_output=True,text=True,encoding='utf-8',timeout=120)
    assert build.returncode==0,build.stdout+build.stderr
    data_build=dict(seconds=time.perf_counter()-t,stdout=build.stdout,stderr=build.stderr)
    measurements=[]
    for name,(claim,proof) in cases(a.nodes,a.block,names).items():
        path=out/(name+'.lean')
        path.write_text('import MicroData\nset_option maxHeartbeats 0\nset_option maxRecDepth 100000\nopen RepoProof MicroData\ntheorem measured : '+claim+' := by\n'+'\n'.join(proof)+'\n#print axioms measured\n',encoding='utf-8')
        runs=[]
        for rep in range(a.repeats):
            t=time.perf_counter()
            run=subprocess.run([a.lean,str(path)],env=env,capture_output=True,text=True,encoding='utf-8',timeout=120)
            seconds=time.perf_counter()-t
            assert run.returncode==0,(name,run.stdout,run.stderr)
            pairs=[tuple(map(int,m)) for m in re.findall(r'proof_construction_ms=(\d+); kernel_check_and_insert_ms=(\d+)',run.stdout)]
            assert pairs,(name,run.stdout)
            assert 'sorryAx' not in run.stdout
            runs.append(dict(repetition=rep+1,process_seconds=seconds,construction_ms=sum(x for x,y in pairs),kernel_and_insert_ms=sum(y for x,y in pairs),leaves=len(pairs),stdout=run.stdout,stderr=run.stderr))
        item=dict(name=name,claim=claim,runs=runs,median_process_seconds=statistics.median(r['process_seconds'] for r in runs),median_construction_ms=statistics.median(r['construction_ms'] for r in runs),median_kernel_and_insert_ms=statistics.median(r['kernel_and_insert_ms'] for r in runs))
        measurements.append(item)
        print(name,item['median_kernel_and_insert_ms'],'ms',flush=True)
    report=dict(nodes=a.nodes,edges=a.nodes,edge_block_size=a.block,witness_block_size=8,repetitions=a.repeats,data_build=data_build,measurements=measurements,scope='Fresh proof compiler process per repetition; imported precompiled MicroData.olean plus existing Reachability/Checker/ProofTiming. Whole process includes import/startup; internal millisecond timers measure proof term construction and synchronous kernel check+lemma insertion only. No Chromium proof imported or rerun.',equivalence='Beginning/end orderings contain identical edge sets. Indexed-edge variant proves exactly edgeEnd.contains target=true via checked block element and block-to-global membership lemma. Linear/balanced tables have kernel-checked full observational agreement. Global slice/direct block contain exactly same final block; combining variants prove identical entire edgeEnd closure.',limitations='Small deterministic inputs; three repeats; integer millisecond internal timing. Development processes may run concurrently; CPU isolation is not claimed. No full-instance or total-process speedup inferred from these micro results.')
    report['sources']={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in out.glob('*.lean')}
    report['precompiled_imports']={p.as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [Path('formal/Reachability.olean'),Path('formal/Checker.olean'),Path('formal/ProofTiming.olean'),out/'MicroData.olean']}
    Path(a.report).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__': main()
