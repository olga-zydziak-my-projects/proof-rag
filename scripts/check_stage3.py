"""Reproduce stage 3. Program execution and kernel acceptance are separate checks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lean',required=True)
p.add_argument('--report',default='verification/stage3-checks.json')
a=p.parse_args()
project=Path(__file__).resolve().parents[1]
os.chdir(project)
env=dict(os.environ,PYTHONPATH=str(project/'src'),LEAN_PATH=str(project/'formal'),REPO_PROOF_LEAN=a.lean)
checks=[]
def audit(output, names, allowed):
    for name in names:
        clean=f"'{name}' does not depend on any axioms"
        match=re.search(re.escape("'"+name+"' depends on axioms: [")+r'([^\]]*)\]',output)
        if clean in output:
            used=set()
        elif match:
            used={s.strip() for s in match.group(1).split(',') if s.strip()}
        else:
            raise RuntimeError('missing axiom audit: '+name)
        if not used <= allowed:
            raise RuntimeError('unexpected axioms: '+name+' '+str(used))
def run(name, cmd, timeout=1200):
    start=time.perf_counter()
    try:
        r=subprocess.run(cmd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
        item=dict(name=name,seconds=time.perf_counter()-start,passed=r.returncode==0,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
    except (OSError,subprocess.TimeoutExpired) as e:
        item=dict(name=name,seconds=time.perf_counter()-start,passed=False,error=str(e))
    checks.append(item)
    print(name, item['passed'], round(item['seconds'],3),flush=True)
    Path(a.report).write_text(json.dumps({'complete':False,'checks':checks},indent=2),encoding='utf-8')
    if not item['passed']: raise RuntimeError(name+' failed; see '+a.report)
    return item
version=run('lean_version',[a.lean,'--version'])
if 'version 4.35.0,' not in version['stdout']:
    raise RuntimeError('requires pinned Lean 4.35.0')
run('pinned_parser_runtime',[sys.executable,'scripts/vendor_mojom_parser.py','--check'])
for module in ['Reachability','Checker','ProofTiming']:
    item=run(module,[a.lean,'-o',f'formal/{module}.olean',f'formal/{module}.lean'])
    if module=='Reachability':
        audit(item['stdout'],['RepoProof.'+s for s in ['complete','exact_reachability','soundness_from_ranked_witnesses','ranked_exact_reachability','reachability_has_certificate','exact_dependents']],set())
    if module=='Checker':
        audit(item['stdout'],['RepoProof.'+s for s in ['check_exact','member','rank','localCheck','check','all_split','indexCheck']],{'propext','Classical.choice','Quot.sound'})
run('export',[sys.executable,'scripts/export_stage3.py'])
exported=Path('formal/Chromium.lean').read_bytes()
run('export_repeat',[sys.executable,'scripts/export_stage3.py'])
if exported != Path('formal/Chromium.lean').read_bytes():
    raise RuntimeError('nondeterministic exported Lean bytes')
run('independent_full_binding',[sys.executable,'scripts/review_stage3_binding.py'])
inst=run('instance_kernel',[a.lean,'-o','formal/Chromium.olean','formal/Chromium.lean'])
audit(inst['stdout'],['Chromium.accepted','Chromium.exact'],{'propext','Classical.choice','Quot.sound'})
if not re.search(r'proof_construction_ms=\d+; kernel_check_and_insert_ms=\d+',inst['stdout']):
    raise RuntimeError('missing proof timers')
runtime=run('checker_execution',[a.lean,'--run','formal/RunChecker.lean'])
if runtime['stdout'].splitlines()[0]!='true' or 'checker_and_output_ms=' not in runtime['stdout']:
    raise RuntimeError('checker did not accept or missing execution timer')
run('python_and_lean_differential_tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
run('source_binding_and_edge_deletion_demo',[sys.executable,'scripts/mojom_experiment.py','tamper','--root','mojo/public/mojom/base/time.mojom','--artifact-dir','local/stage2','--report','verification/stage3-tampering.json'])
report={'complete':True,'checks':checks,'timing_scope':{'export':'Python process including artifact reads, strict validation, deterministic rendering and write','instance_kernel':'Lean process including data elaboration, proof construction and kernel check; internal timers separate proof construction from kernel check plus lemma insertion','checker_execution':'Lean --run VM execution; internal timer includes checker and printing its Boolean; excludes module import/startup','tests':'differential agreement is testing, not a proof of Python refinement'},'trusted_boundary':['Lean kernel and standard logical axioms in audit','Mojom parser and extraction','Git, manifest, hashes and file IO','Python serializer and independent path-to-ID audit','displayed answer binding']}
timings=[tuple(map(int,pair)) for pair in re.findall(r'proof_construction_ms=(\d+); kernel_check_and_insert_ms=(\d+)',inst['stdout'])]
report['checked_at_utc']=datetime.now(timezone.utc).isoformat()
report['proof_leaf_timing']={'leaves':len(timings),'construction_ms_sum':sum(t[0] for t in timings),'kernel_check_and_insert_ms_sum':sum(t[1] for t in timings),'scope':'Only acceptance proof leaves; excludes data bound proofs and final combination with all_split; integer millisecond resolution.'}
report['source_sha256']={p.as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['formal','scripts','src','tests'] for p in sorted(Path(folder).rglob('*')) if p.suffix in ['.py','.lean']}
Path(a.report).write_text(json.dumps(report,indent=2),encoding='utf-8')
print('complete=True',flush=True)
