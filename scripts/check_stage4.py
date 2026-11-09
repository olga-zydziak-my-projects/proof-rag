"""Fresh stage-4 verification; keeps historical data and reports unchanged."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import sys

from stage4_support import run_process,audit,file_info


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean',required=True)
    parser.add_argument('--report',default='verification/stage4-checks.json')
    args=parser.parse_args()
    project=Path(__file__).resolve().parents[1]; os.chdir(project)
    if Path(args.report).exists():
        raise FileExistsError('choose a new --report path; existing measurements are preserved')
    env=dict(os.environ,PYTHONPATH=str(project/'src'),LEAN_PATH=str(project/'formal'),
             REPO_PROOF_LEAN=args.lean)
    historical=[Path('formal/Checker.lean'),Path('formal/ProofTiming.lean'),
                Path('formal/Chromium.lean'),*Path('verification').glob('stage3-*')]
    before={str(p):file_info(p) for p in historical}
    report={'complete':False,'checks':[],'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'baseline_commit':'3184813','historical_files':before}
    destination=Path(args.report); destination.parent.mkdir(parents=True,exist_ok=True)
    def save(): destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def run(name,command,timeout=1200):
        item=run_process(name,command,env,timeout)
        report['checks'].append(item); save()
        print(name,item['passed'],round(item['seconds'],3),flush=True)
        if not item['passed']: raise RuntimeError(name+' failed or unresolved; see '+str(destination))
        return item
    version=run('lean_version',[args.lean,'--version'])
    if 'version 4.35.0,' not in version['stdout']: raise RuntimeError('requires Lean4.35.0')
    for module in ['Reachability','Checker','ProofTiming','FastChecker']:
        item=run(module,[args.lean,'-o',f'formal/{module}.olean',f'formal/{module}.lean'])
        if module=='FastChecker':
            names=re.findall(r'^#print axioms (\S+)',Path(f'formal/{module}.lean').read_text(encoding='utf-8'),re.M)
            report['general_axioms']=audit(item['stdout'],names)
    run('export',[sys.executable,'scripts/export_stage4.py'])
    data=Path('formal/ChromiumFast.lean').read_bytes()
    run('export_repeat',[sys.executable,'scripts/export_stage4.py'])
    if data!=Path('formal/ChromiumFast.lean').read_bytes(): raise RuntimeError('nondeterministic export')
    run('full_content_binding',[sys.executable,'scripts/review_stage4_binding.py'])
    report['precompiled_modules']={f'formal/{m}.olean':file_info(f'formal/{m}.olean')
                                  for m in ['Reachability','Checker','ProofTiming','FastChecker']}
    report['standard_imports']='Precompiled pinned SDK Std/Lean libraries. No Chromium.olean import.'
    instance=run('fresh_instance_kernel',[args.lean,'-o','formal/ChromiumFast.olean','formal/ChromiumFast.lean'])
    report['instance_axioms']=audit(instance['stdout'],['ChromiumFast.'+s for s in ['accepted','erased_accepted','exact']])
    timings=[tuple(map(int,t)) for t in re.findall(r'proof_construction_ms=(\d+); kernel_check_and_insert_ms=(\d+)',instance['stdout'])]
    if not timings: raise RuntimeError('missing kernel timers')
    report['proof_leaf_timing']={'leaves':len(timings),'construction_ms_sum':sum(x[0] for x in timings),
                               'kernel_check_and_insert_ms_sum':sum(x[1] for x in timings),
                               'scope':'Acceptance leaves only, same 1ms clock and mkAuxLemma as stage3; excludes data bounds and final assembly.'}
    report['artifact_sizes']={p:file_info(p) for p in ['formal/ChromiumFast.lean','formal/ChromiumFast.olean',
                                                   'formal/FastChecker.lean','formal/FastChecker.olean',
                                                   'formal/Chromium.lean','formal/Chromium.olean'] if Path(p).exists()}
    runtime=run('vm_execution',[args.lean,'--run','formal/RunFastChecker.lean'])
    if not runtime['stdout'].startswith('true\n'): raise RuntimeError('VM check did not accept')
    run('all_tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])
    run('source_tampering',[sys.executable,'scripts/mojom_experiment.py','tamper','--root',
                          'mojo/public/mojom/base/time.mojom','--artifact-dir','local/stage2',
                          '--report','verification/stage4-tampering.json'])
    if before!={str(p):file_info(p) for p in historical}: raise RuntimeError('historical files changed')
    report['source_sha256']={str(p):file_info(p)['sha256'] for folder in ['formal','scripts','src','tests']
                             for p in sorted(Path(folder).rglob('*')) if p.suffix in ['.py','.lean']}
    report['complete']=True; save(); print('complete=True',flush=True)


if __name__=='__main__': main()
