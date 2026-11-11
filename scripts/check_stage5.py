"""Reproduce a BLOCKED Stage 5 preflight and diagnostic baseline regressions.

No successful source-to-answer pipeline is claimed or implemented while its
source pin conflicts and the source theorem is unavailable. Exit 3 = BLOCKED.
"""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import sys
from time import perf_counter

from stage4_support import audit,file_info
from stage5_support import run_process

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'src'))
from repo_proof.stage5_preflight import BASELINE,CONTRACT_SHA256,preservation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean',required=True)
    p.add_argument('--run-dir',required=True)
    p.add_argument('--report',default='verification/stage5-checks.json')
    a=p.parse_args(); os.chdir(PROJECT)
    run_dir=Path(a.run_dir).resolve(); target=Path(a.report).resolve()
    if (not run_dir.is_relative_to(PROJECT) or not target.is_relative_to(PROJECT)
            or run_dir.exists() or target.exists()):
        p.error('choose fresh run/report paths within the project; no overwrites')
    run_dir.mkdir(parents=True,exist_ok=False); target.parent.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PYTHONPATH=str(PROJECT/'src'),LEAN_PATH=str(PROJECT/'formal'),REPO_PROOF_LEAN=a.lean)
    start=perf_counter()
    report={'status':'IN_PROGRESS','stage5_pass':False,'contract_sha256':CONTRACT_SHA256,
            'stage4_commit':BASELINE,'run_dir':str(run_dir),'checks':[],
            'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'timings_seconds':{'source_semantics_validation':None,'generation':None,
               'stage5_fresh_instance':None,'answer_validation':None,'successful_whole_pipeline':None}}
    def save(): target.write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    def run(name,cmd,expected=0):
        entry=run_process('stage5_'+name,cmd,env,run_dir)
        entry['expected_exit_code']=expected
        entry['exit_matched_expectation']=entry['exit_code']==expected and not entry['timed_out']
        report['checks'].append(entry); save()
        print(name,entry['exit_code'],round(entry['seconds'],3),flush=True)
        if not entry['exit_matched_expectation']: raise RuntimeError(name+' unexpected failure')
        return entry
    try:
        report['preservation_before']=preservation(PROJECT)
        preflight=run('preflight',[sys.executable,'scripts/stage5_preflight.py','--run-dir',str(run_dir/'preflight')],3)
        diagnostic=json.loads((run_dir/'preflight/diagnostic.json').read_bytes())
        if diagnostic['status']!='BLOCKED_PIN_CONFLICT' or diagnostic['answer_released']:
            raise RuntimeError('expected documented pin conflict, never success')
        report['preflight']=diagnostic
        report['timings_seconds']['blocked_preflight_process']=preflight['seconds']
        report['timings_seconds']['accepted_baseline_provenance_diagnostic']=diagnostic.get('baseline_provenance_seconds')
        version=run('lean_version',[a.lean,'--version'])
        if 'version 4.35.0,' not in version['stdout']: raise RuntimeError('Lean4.35.0 required')
        prepared=[]
        for module in ['Reachability','Checker','ProofTiming','FastChecker']:
            prepared.append(run(module,[a.lean,'-o',f'formal/{module}.olean',f'formal/{module}.lean']))
        report['timings_seconds']['generic_module_processes_sum']=sum(x['seconds'] for x in prepared)
        report['precompiled_for_baseline_diagnostic']={f'formal/{m}.olean':file_info(f'formal/{m}.olean')
            for m in ['Reachability','Checker','ProofTiming','FastChecker']}
        names=re.findall(r'^#print axioms (\S+)',Path('formal/FastChecker.lean').read_text(encoding='utf-8'),re.M)
        report['existing_generic_axioms']=audit(prepared[-1]['stdout'],names)
        graph=run('existing_graph_fresh_instance',[a.lean,'-o',str(run_dir/'baseline-graph.olean'),'formal/ChromiumFast.lean'])
        report['existing_instance_axioms']=audit(graph['stdout'],['ChromiumFast.'+s for s in ['accepted','erased_accepted','exact']])
        report['timings_seconds']['diagnostic_baseline_graph_fresh_instance']=graph['seconds']
        report['baseline_instance_scope']='Fresh Stage4 graph theorem only, relative to existing supplied graph; not a Stage5 source theorem. Standard SDK plus listed generics precompiled.'
        run('existing_binding_audit',[sys.executable,'scripts/review_stage4_binding.py'])
        tests=run('all_tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
        match=re.search(r'Ran (\d+) tests',tests['stderr']); report['test_count']=int(match.group(1)) if match else None
        run('baseline_tampering',[sys.executable,'scripts/mojom_experiment.py','tamper','--root',
            'mojo/public/mojom/base/time.mojom','--artifact-dir','local/stage2','--report',str(run_dir/'baseline-tampering.json')])
        report['preservation_after']=preservation(PROJECT)
        if not report['preservation_after']['preserved']: raise RuntimeError('baseline changed')
        report['status']='BLOCKED_PIN_CONFLICT'
        report['additional_blocker']='STAGE5_BLOCKED__SOURCE_PROOF (not implemented: pin prerequisite unresolved)'
        report['gates']={
            'G1':{'status':'PASS','reason':'Checkpoint and observed baseline files preserved; existing regressions pass.'},
            'G2':{'status':'BLOCKED','reason':'BLOCKED_PIN_CONFLICT; accepted baseline bytes corroborated only under different pin.'},
            'G3':{'status':'BLOCKED','reason':'No Stage5 source theorem; essential pin unresolved.'},
            'G4':{'status':'BLOCKED','reason':'Existing graph exactness checked, but source composition and full answer decoding not proved.'},
            'G5':{'status':'BLOCKED','reason':'No newly successful canonical or human-readable answer released.'},
            'G6':{'status':'BLOCKED','reason':'Existing regressions and preflight faults pass; full Stage5 A-L boundaries not reached.'},
            'G7':{'status':'BLOCKED','reason':'Reproduced blocked preflight, not a clean successful source-to-answer run or canonical answer regeneration.'},
            'G8':{'status':'PASS','reason':'No source proof, new speedup, or successful release claimed; assumptions and blocks explicit.'}}
        code=3
    except (OSError,ValueError,RuntimeError,KeyError) as exc:
        report.update(status='STAGE5_FAIL__DIAGNOSTIC_DRIVER',error=str(exc)); code=2
    report['timings_seconds']['whole_blocked_diagnostic_driver']=perf_counter()-start
    report['new_stage5_theorems']=[]
    report['source_sha256']={str(f):file_info(f)['sha256'] for folder in ['src','scripts','tests']
                           for f in sorted(Path(folder).rglob('*')) if f.suffix=='.py'}
    save(); print(report['status'],flush=True)
    return code


if __name__=='__main__': raise SystemExit(main())
