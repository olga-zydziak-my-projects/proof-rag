"""One fresh, fail-closed Stage5 v2 source-to-answer run (Windows)."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import uuid

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'src'))
from repo_proof.stage5_v2 import capture,canonical,sha,snapshot_payload,export_names,export_groups
from repo_proof.stage5_run_v2 import seal,check_seal
from repo_proof.stage5_answer_v2 import expected_answer,check_answer,render_answer,check_human
from repo_proof.extraction import read_json
from stage5_support import run_process
from stage4_support import audit,file_info
from stage5_v2_audit_bytes import audit as byte_audit
from stage5_v2_export_master import export_master
from stage5_v2_verify_inputs import validate_inputs

BASE_MODULES=['Reachability','Checker','ProofTiming','FastChecker','ChromiumFast',
              'SourceByteScanner','SourceGraphBinding','AnswerBinding']

def preservation():
    baseline=read_json(PROJECT/'verification/stage5-v2-baseline.json')
    changed=[p for p,entry in baseline['preserved_files'].items()
             if not (PROJECT/p).exists() or file_info(PROJECT/p)!=entry]
    if changed: raise ValueError('preserved files changed: '+str(changed))
    return {'passed':True,'files':len(baseline['preserved_files'])}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean',required=True)
    parser.add_argument('--run-dir',required=True)
    parser.add_argument('--report',required=True)
    args=parser.parse_args()
    os.chdir(PROJECT)
    folder=Path(args.run_dir).resolve(); report_path=Path(args.report).resolve()
    if not folder.is_relative_to(PROJECT) or not report_path.is_relative_to(PROJECT):
        parser.error('run and report must be inside project')
    if report_path.is_relative_to(folder): parser.error('report must be outside sealed run directory')
    if folder.exists() or report_path.exists(): parser.error('fresh run and report paths required')
    folder.mkdir(parents=True); (folder/'lean').mkdir(); (folder/'evidence').mkdir()
    report_path.parent.mkdir(parents=True,exist_ok=True)
    nonce=uuid.uuid4().hex
    started=time.perf_counter()
    report={'status':'IN_PROGRESS','stage5_pass':False,'run_nonce':nonce,
            'run_dir':str(folder),'checks':[],'phases_seconds':{},'gates':{f'G{i}':'PENDING' for i in range(1,9)},
            'precompiled':'Main proof pipeline: Lean 4.35.0 SDK only; all project dependencies and concrete instances freshly compiled in the new run directory. Preserved differential regression additionally imports baseline formal/ caches and uses VM execution as tests, never proof.'}
    env=dict(os.environ,LEAN_PATH=str(folder/'lean'),PYTHONPATH=str(PROJECT/'src'),REPO_PROOF_LEAN=args.lean)
    compiled={}
    code_before={str(p.relative_to(PROJECT)).replace('\\','/'):file_info(p)
                 for base in ('src','scripts','formal','tests') for p in (PROJECT/base).rglob('*')
                 if p.suffix in ('.py','.lean')}
    for rel in ('docs/stage5-contract-v2.md','docs/stage5-source-spec-v2.md'):
        code_before[rel]=file_info(PROJECT/rel)
    report['code_at_start']=code_before
    def save(): report_path.write_bytes(canonical(report))
    def measure(name,fn):
        begin=time.perf_counter(); value=fn()
        report['phases_seconds'][name]=time.perf_counter()-begin; save()
        print(name,round(report['phases_seconds'][name],3),flush=True)
        return value
    def write(path,value):
        with path.open('xb') as target: target.write(canonical(value))
    def process(name,command):
        result=run_process(name,command,env,folder,timeout=7200)
        report['checks'].append(result)
        if not result['passed']: raise ValueError(name+' failed; see process logs')
        return result
    try:
        report['preservation_before']=preservation(); save()
        version=process('lean_version',[args.lean,'--version'])
        if 'version 4.35.0,' not in version['stdout']: raise ValueError('Lean 4.35.0 required')
        c=measure('snapshot_and_full_parser',lambda:capture(PROJECT))
        report['source_component_timings_seconds']=c.timings
        def generate(target):
            write(target/'snapshot.json',snapshot_payload(c))
            write(target/'graph.json',c.graph); write(target/'certificate.json',c.certificate)
            export_names(c,target/'lean')
            inventory=export_groups(c,target/'lean')
            write(target/'source-module-inventory.json',inventory)
            export_master(c,target)
            write(target/'expected-answer.json',expected_answer(c))
        measure('generation',lambda:generate(folder))
        repeat=folder/'regenerated'; repeat.mkdir(); (repeat/'lean').mkdir()
        measure('deterministic_regeneration',lambda:generate(repeat))
        generated=[p for p in repeat.rglob('*') if p.is_file()]
        if not all(p.read_bytes()==(folder/p.relative_to(repeat)).read_bytes() for p in generated):
            raise ValueError('deterministic generation mismatch')
        report['determinism']={'passed':True,'files':len(generated),'comparison':'full bytes of independently repeated generation from the same captured input'}
        for name in BASE_MODULES:
            shutil.copyfile(PROJECT/'formal'/(name+'.lean'),folder/'lean'/(name+'.lean'))
        # Projection fixtures are generated before the seal, and freshly kernel checked.
        process('generate_projection',[sys.executable,'scripts/stage5_v2_projection_cases.py','--output',str(folder/'lean/ProjectionCases.lean')])
        expected_seal=seal(folder,nonce)
        def boundary():
            check_seal(folder,expected_seal,nonce)
            # Every previously accepted imported module remains the actual compiled object.
            for name,expected in list(compiled.items()):
                if file_info(folder/'lean'/(name+'.olean'))!=expected:
                    raise ValueError('compiled dependency changed: '+name)
        def compile_module(name):
            boundary()
            source=folder/'lean'/(name+'.lean')
            before=file_info(source)
            entry=process(name,[args.lean,'-o',str(source.with_suffix('.olean')),str(source)])
            if file_info(source)!=before: raise ValueError('source changed during compilation: '+name)
            names=re.findall(r'^#print axioms ([\w.]+)\s*$',source.read_text(encoding='utf-8'),re.M)
            entry['axioms']=audit(entry['stdout'],names)
            entry['source']=before; entry['run_nonce']=nonce
            entry['compiled']=file_info(source.with_suffix('.olean'))
            compiled[name]=entry['compiled']
            return entry
        measure('fresh_project_dependencies',lambda:[compile_module(name) for name in BASE_MODULES])
        measure('filename_mapping',lambda:compile_module('SourceNames'))
        measure('lexical_kernel_cases',lambda:compile_module('ProjectionCases'))
        def groups():
            with ThreadPoolExecutor(max_workers=2) as executor:
                pending=[executor.submit(compile_module,f'SourceGroup{i:03}') for i in range(30)]
                for future in as_completed(pending):
                    entry=future.result(); save()
                    print(entry['name'],'PASS',round(entry['seconds'],3),flush=True)
        measure('all_source_groups_elapsed',groups)
        measure('master_instance',lambda:compile_module('ChromiumSource'))
        if not (folder/'lean/ChromiumSource.olean').exists(): raise ValueError('master missing')
        report['byte_audit']=measure('full_lean_byte_and_output_comparison',lambda:validate_inputs(folder,c,expected_seal,nonce))
        boundary()
        from stage5_v2_attacks import run_attacks
        attacks=measure('attacks_A_to_L',lambda:run_attacks(c,folder))
        write(folder/'evidence/attacks.json',attacks)
        if attacks['status']!='ATTACKS_A_L_PASS' or attacks['classes']!=list('ABCDEFGHIJKL'):
            raise ValueError('attack gate failed')
        report['attacks']=attacks
        tests=measure('final_regressions',lambda:process('all_tests',[sys.executable,'-m','unittest','discover','-s','tests','-v']))
        if 'OK' not in tests['stderr'] or '1547' not in tests['stderr']+tests['stdout']:
            # The differential test currently prints its case count to stdout.
            if not any('differential' in line.lower() and 'ok' in line.lower() for line in tests['stderr'].splitlines()):
                raise ValueError('differential regression evidence missing')
        report['review']=read_json(PROJECT/'verification/stage5-v2-review-final.json')
        if report['review']['status']!='PASS': raise ValueError('independent review unresolved')
        for rel,expected in report['review']['reviewed_files'].items():
            if file_info(PROJECT/rel)!=expected: raise ValueError('reviewed code changed: '+rel)
            if code_before.get(rel)!=expected: raise ValueError('executed run predates reviewed code: '+rel)
        def answer_roundtrip():
            boundary(); byte_audit(folder,c)
            value=read_json(folder/'expected-answer.json'); check_answer(value,c)
            pending=folder/'answer.pending.json'; write(pending,value)
            saved=read_json(pending); check_answer(saved,c)
            if pending.read_bytes()!=canonical(expected_answer(c)): raise ValueError('noncanonical saved answer')
            human=render_answer(saved)
            text=folder/'answer.pending.txt'; text.write_bytes(human.encode('utf-8'))
            check_human(text.read_text(encoding='utf-8'),c)
            if human.encode('utf-8')!=render_answer(expected_answer(c)).encode('utf-8'):
                raise ValueError('human deterministic rendering mismatch')
            boundary()
            return {'canonical':file_info(pending),'human':file_info(text),'paths':len(saved['paths'])}
        report['answer']=measure('answer_persisted_roundtrip',answer_roundtrip)
        report['preservation_after']=preservation()
        for rel,expected in code_before.items():
            if file_info(PROJECT/rel)!=expected: raise ValueError('project code changed during run: '+rel)
        report['regression']={'nodes':len(c.graph['nodes']),'edges':len(c.graph['edges']),
            'isolated':len(set(c.graph['nodes'])-{p for edge in c.graph['edges'] for p in edge}),
            'results':len(c.certificate['candidates']),'pin':c.pin}
        gate_conditions={
            'G1':report['preservation_before']['passed'] and report['preservation_after']['passed'],
            'G2':report['byte_audit']['passed'] and report['determinism']['passed'],
            'G3':all(f'SourceGroup{i:03}' in compiled for i in range(30)) and 'ChromiumSource' in compiled,
            'G4':'ChromiumFast' in compiled and 'ChromiumSource' in compiled,
            'G5':report['answer']['paths']==len(c.certificate['candidates']),
            'G6':attacks['status']=='ATTACKS_A_L_PASS' and attacks['classes']==list('ABCDEFGHIJKL') and tests['passed'],
            'G7':report['determinism']['passed'] and all(x['passed'] for x in report['checks']),
            'G8':report['review']['status']=='PASS' and all('axioms' in x for x in report['checks'] if x['name'] in compiled)}
        report['gate_conditions']=gate_conditions
        report['gates']={key:'PASS' if value else 'FAIL' for key,value in gate_conditions.items()}
        if not all(gate_conditions.values()): raise ValueError('acceptance gate failed')
        report['total_elapsed_seconds']=time.perf_counter()-started
        report['artifacts']={p.relative_to(folder).as_posix():file_info(p) for p in (folder/'lean').iterdir() if p.is_file()}
        report['process_memory_summary']={'definition':'maximum individual native process peak; not aggregate simultaneous system memory',
            'peak_working_set_bytes':max(x['memory']['peak_working_set_bytes'] for x in report['checks']),
            'peak_process_commit_bytes':max(x['memory']['peak_process_commit_bytes'] for x in report['checks'])}
        operational_receipt={'schema':'stage5-operational-receipt-v2','run_nonce':nonce,
            'seal':expected_seal,'compiled':compiled,'answer':report['answer'],'report':str(report_path)}
        operational_receipt['acceptance']='valid only with linked report status STAGE5_PASS'
        write(folder/'operational-receipt.json',operational_receipt)
        if canonical(read_json(folder/'operational-receipt.json'))!=canonical(operational_receipt):
            raise ValueError('persisted receipt mismatch')
        (folder/'answer.pending.json').rename(folder/'answer.json')
        (folder/'answer.pending.txt').rename(folder/'answer.txt')
        check_answer(read_json(folder/'answer.json'),c)
        check_human((folder/'answer.txt').read_text(encoding='utf-8'),c)
        report['total_elapsed_seconds']=time.perf_counter()-started
        report['status']='STAGE5_PASS'; report['stage5_pass']=True
    except Exception as error:
        report['status']='STAGE5_FAILED'; report['stage5_pass']=False; report['error']=str(error)
        for name in ('answer.json','answer.txt'):
            path=folder/name
            if path.exists(): path.rename(folder/name.replace('answer.','answer.failed.'))
        report['gates']['G5']='FAIL'; report['gates']['G7']='FAIL'
        report['total_elapsed_seconds']=time.perf_counter()-started
    save(); print(report['status'],report.get('error',''),flush=True)
    return 0 if report['stage5_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
