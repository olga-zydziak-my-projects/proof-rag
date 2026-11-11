"""Finish this concrete proof run after its independent group jobs complete.

This records a source-instance proof, not the complete Stage 5 gate result.
It does not release an answer while any compilation/audit is missing or fails.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from stage5_support import run_process
from stage4_support import audit as audit_axioms, file_info
from stage5_v2_audit_bytes import audit as audit_bytes
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.stage5_v2 import capture,canonical
from repo_proof.stage5_answer_v2 import expected_answer,check_answer,render_answer,check_human

p=argparse.ArgumentParser()
p.add_argument('--run-dir',required=True)
p.add_argument('--lean',required=True)
p.add_argument('--wait',action='store_true')
a=p.parse_args()
folder=Path(a.run_dir).resolve()
report=folder/'source-instance-result.json'
if report.exists(): raise SystemExit('choose a fresh result location; existing result preserved')
env=dict(os.environ,LEAN_PATH=str(folder/'lean')+';'+str(Path('formal').resolve()))
c=capture(Path.cwd())
checks=[]
started=time.perf_counter()

def compile_one(name):
    source=folder/'lean'/(name+'.lean')
    before=file_info(source)
    entry=run_process(name,[a.lean,'-o',str(source.with_suffix('.olean')),str(source)],env,folder,timeout=7200)
    entry['source_before']=before
    entry['source_after']=file_info(source)
    checks.append(entry)
    if not entry['passed'] or before!=entry['source_after']:
        raise ValueError('compilation failed or source changed: '+name)
    return entry

try:
    while True:
        missing=[]
        for i in range(1,30):
            path=folder/'group-receipts'/f'SourceGroup{i:03}.json'
            if not path.exists(): missing.append(i); continue
            # A receipt is written only at completion; an incomplete write is retried.
            try: receipt=json.loads(path.read_bytes())
            except json.JSONDecodeError: missing.append(i); continue
            if not receipt['passed']: raise ValueError('source group failed: '+str(i))
        if not missing: break
        if not a.wait: raise ValueError('source group compilation incomplete')
        if time.perf_counter()-started>28800: raise ValueError('waiting for source groups timed out')
        time.sleep(2)
    before_audit=audit_bytes(folder,c)
    # Group zero had an exploratory compile; this is its measured fresh compile.
    zero=compile_one('SourceGroup000')
    audit_axioms(zero['stdout'],['SourceGroup000.f0_ok','SourceGroup000.f63_ok'])
    master=compile_one('ChromiumSource')
    axioms=audit_axioms(master['stdout'],['ChromiumSource.source_bound',
        'ChromiumSource.paths_unique','ChromiumSource.source_to_answer'])
    after_audit=audit_bytes(folder,c)
    value=expected_answer(c)
    check_answer(value,c)
    human=render_answer(value)
    check_human(human,c)
    # Keep these as checked instance artifacts. Stage-wide release still requires
    # the attack, reproduction and preservation gates in the final orchestrator.
    with (folder/'checked-instance-answer.json').open('xb') as target: target.write(canonical(value))
    with (folder/'checked-instance-answer.txt').open('xb') as target: target.write(human.encode('utf-8'))
    result={'status':'SOURCE_INSTANCE_KERNEL_PASS','stage5_pass':False,
        'note':'Complete stage gates and clean operational reproduction are not certified by this script.',
        'checks':checks,'byte_audit_before':before_audit,'byte_audit_after':after_audit,
        'axioms':axioms,'files':len(c.blobs),'paths':len(value['paths'])}
except Exception as error:
    result={'status':'SOURCE_INSTANCE_FAILED','stage5_pass':False,'error':str(error),'checks':checks}
with report.open('xb') as target: target.write(canonical(result))
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','axioms')}),flush=True)
raise SystemExit(0 if result['status']=='SOURCE_INSTANCE_KERNEL_PASS' else 1)
