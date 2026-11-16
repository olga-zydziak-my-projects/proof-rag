"""Reproducible measurement/regression driver and evidence-derived status."""
import os
import sys
if __name__=='__main__' and '--clean-bytecode' not in sys.argv:
    base=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache=os.path.join(base,'local','stage9','driver-bytecode-'+str(os.getpid()))
    os.makedirs(cache,exist_ok=False)
    os.environ['PYTHONPYCACHEPREFIX']=cache
    os.environ['PYTHONPATH']=os.pathsep.join(os.path.join(base,p) for p in ('src','scripts','local/stage8-deps'))
    raise SystemExit(os.spawnv(os.P_WAIT,sys.executable,[sys.executable,'-B','-S','-X','pycache_prefix='+cache,__file__,*sys.argv[1:],'--clean-bytecode']))

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import statistics
import shutil
import subprocess
import time

PROJECT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'scripts'),str(PROJECT/'local/stage8-deps')]
from stage9 import read,write,digest,validate_prepared,verify_modules,answer_rows,identities,contextual_rules
from stage9_export import audit_query
from repo_proof.stage8_graph import search,reverse_index,reference
from types import SimpleNamespace
from stage6_regressions import prepare_regression_view,verify_regression_view,code_inventory


def parse_results(log):
    spec=importlib.util.spec_from_file_location('stage8_close_reader',PROJECT/'verification/stage8-close-09.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.parse_results(log)


def regression(folder,lean):
    folder.mkdir(parents=True,exist_ok=False)
    view_record=prepare_regression_view(PROJECT,folder/'view')
    view=Path(view_record['directory'])
    shutil.copytree(PROJECT/'local/stage8-deps',view/'local/stage8-deps',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(view/'src'),str(view/'tests'),str(PROJECT/'local/stage8-deps'))),REPO_PROOF_LEAN=str(lean))
    enumerate_code=('import unittest,json; s=unittest.TestLoader().discover("tests"); '
                    'f=lambda x: [i for y in x for i in f(y)] if isinstance(x,unittest.TestSuite) else [x.id()]; print(json.dumps(f(s)))')
    names=json.loads(subprocess.check_output([sys.executable,'-B','-c',enumerate_code],cwd=view,env=env))
    if len(names)!=len(set(names)) or any('_FailedTest' in s for s in names):raise ValueError('discovery failed')
    old=read(PROJECT/'verification/stage8-full-09.json')
    historical=set(old['results'])
    if len(historical)!=180 or not historical.issubset(names):raise ValueError('historical 180 names missing')
    write(folder/'discovered-tests.json',sorted(names))
    config=read(PROJECT/'verification/stage9-config.json'); config['limits']['timeout_seconds']=2400
    write(folder/'config.json',config)
    command=[sys.executable,'-B',str(PROJECT/'scripts/stage8_supervise.py'),'--config',str(folder/'config.json'),
             '--run-dir',str(folder/'process'),'--artifact-root',str(folder),'--',sys.executable,'-B','-m','unittest','discover','-s','tests','-v']
    started=time.perf_counter()
    result=subprocess.run(command,cwd=view,env=env,capture_output=True)
    resources=read(folder/'process/resource-report.json')
    log=(folder/'process/stderr.log').read_text(encoding='utf-8')
    results=parse_results(log)
    verify_regression_view(PROJECT,view_record)
    exact=sorted(results)==sorted(names) and all(v=='ok' for v in results.values())
    report={'status':'REGRESSION_PASS' if result.returncode==0 and resources['status']=='PROCESS_PASS' and resources['remaining_job_processes']==0 and exact else 'REGRESSION_FAILED',
            'tests':len(results),'discovered':sorted(names),'results':results,'historical_180_included':True,
            'seconds':time.perf_counter()-started,'resources':resources,'view':view_record,'code_and_tests':code_inventory(PROJECT)}
    write(PROJECT/'verification/stage9-regression.json',report)
    return report


def queries(folder,prepared,lean,locations,prepared_sha256):
    folder.mkdir(parents=True,exist_ok=False)
    roots=read(PROJECT/'verification/stage9-queries.json')['roots']
    anchor=read(PROJECT/'verification/stage9-manifest-anchor.json')['sha256']
    receipt=prepared_sha256
    if digest(prepared/'prepare.json')!=receipt:raise ValueError('independent preparation anchor mismatch')
    samples=[]
    for number,root in enumerate(roots):
        for repeat in range(3):
            run=folder/f'q{number+1}-r{repeat+1}'/'work'
            command=[sys.executable,'-B',str(PROJECT/'scripts/stage9.py'),'query','--manifest',str(PROJECT/'verification/stage9-manifest.json'),
                '--manifest-sha256',anchor,'--locations',str(locations),'--lean',str(lean),'--prepared-dir',str(prepared),
                '--prepared-sha256',receipt,'--repo-id',root['project'],'--commit',root['commit'],'--context',root['context'],
                '--path',root['path'],'--run-dir',str(run)]
            begin=time.perf_counter(); result=subprocess.run(command,capture_output=True)
            query=read(run/'query.json')
            samples.append({'root':root,'repeat':repeat+1,'wall_seconds':time.perf_counter()-begin,
                            'report':str(run/'query.json'),'sha256':digest(run/'query.json'),
                            'status':query['status'],'phases_seconds':query.get('phases_seconds',{})})
            write(folder/'samples.json',samples)
            if result.returncode or query['status']!='SOURCE_TO_ANSWER_PASS':
                write(PROJECT/'verification/stage9-measurements.json',{'status':'QUERIES_FAILED','samples':samples}); return
    groups=[]
    for number,root in enumerate(roots):
        subset=samples[number*3:number*3+3]
        times=[s['wall_seconds'] for s in subset]
        search_times=[s['phases_seconds']['search_and_certificate'] for s in subset]
        groups.append({'root':root,'full_verified_answer_seconds':{'median':statistics.median(times),'range':[min(times),max(times)]},
                       'search_and_certificate_seconds':{'median':statistics.median(search_times),'range':[min(search_times),max(search_times)]}})
    write(PROJECT/'verification/stage9-measurements.json',{'status':'QUERIES_PASS','samples':samples,'summaries':groups,'os_file_cache_controlled':False})


def checked_resource(seal,timeout,artifact_root):
    path=Path(seal['path'])
    if digest(path)!=seal['sha256']:raise ValueError('supervision receipt changed')
    report=read(path)
    limits=read(PROJECT/'verification/stage9-config.json')['limits']
    limits={**limits,'timeout_seconds':timeout}
    if (report['status']!='PROCESS_PASS' or report['exit_code']!=0 or report['remaining_job_processes']!=0
            or report['limits']!=limits or Path(report['artifact_root']).resolve()!=artifact_root.resolve()
            or report['elapsed_seconds']>timeout+2 or report['peak_tree_private']>limits['tree_memory_bytes']
            or report['peak_tree_rss']>limits['tree_memory_bytes'] or report['peak_artifact_bytes']>limits['artifact_bytes']
            or report['final_artifact_bytes']>limits['artifact_bytes']):
        raise ValueError('resource execution/profile did not satisfy frozen budget')
    return report


def status(prepared,lean,locations,candidate=False,prepared_sha256=None):
    def optional(name):
        path=PROJECT/'verification'/name
        return read(path) if path.exists() else {}
    corpus=optional('stage9-corpus.json'); regression=optional('stage9-regression.json')
    measurements=optional('stage9-measurements.json')
    reviews={kind:optional(f'stage9-{kind}-review.json') for kind in ('corpus','formal')}
    preparation=read(prepared/'prepare.json') if (prepared/'prepare.json').exists() else {}
    roots=optional('stage9-queries.json').get('roots',[])
    anchor=optional('stage9-manifest-anchor.json').get('sha256')
    resources=[]; checked=[]; failures=[]; prep_ok=False; queries_ok=False; regression_ok=False
    count=corpus.get('real_distinct_files',0)
    audit_folder=PROJECT/'local/stage9'/('acceptance-audit-'+str(time.time_ns()))
    audit_folder.mkdir(parents=True)
    manifest_sha=digest(PROJECT/'verification/stage9-manifest.json')
    if anchor!=manifest_sha or corpus.get('manifest_sha256')!=anchor:raise ValueError('corpus manifest anchor changed')
    args=SimpleNamespace(prepared_dir=prepared,prepared_sha256=prepared_sha256 or '',
         manifest=PROJECT/'verification/stage9-manifest.json',manifest_sha256=anchor,locations=locations,lean=lean,
         config=PROJECT/'verification/stage9-config.json')
    if preparation.get('status')=='SOURCE_LAYER_PASS':
        try:
            receipt,values=validate_prepared(args,audit_folder)
            manifest,files,edges,facts,rows,sources,_,_=values
            resources.append(checked_resource(receipt['supervision'],3600,prepared.parent))
            if receipt['nodes']!=count or receipt['edges']!=corpus['edges'] or len(rows)!=count:
                raise ValueError('prepared scope differs from complete corpus')
            prep_ok=True
            expected_pairs={(i,r) for i in range(6) for r in range(1,4)}
            actual_pairs=set()
            root_index={(r['project'],r['context'],r['commit'],r['path']):i for i,r in enumerate(roots)}
            if len(root_index)!=6:raise ValueError('six frozen roots missing or duplicated')
            for sample in measurements.get('samples',[]):
                path=Path(sample['report'])
                if digest(path)!=sample['sha256']:raise ValueError('query receipt changed')
                q=read(path)
                if q['status']!='SOURCE_TO_ANSWER_PASS':raise ValueError('query did not pass')
                answer=read(path.parent/'answer.json')
                key=tuple(answer['root'][k] for k in ('project','context','commit','path'))
                if key not in root_index:raise ValueError('unselected query root')
                pair=(root_index[key],sample['repeat'])
                if pair in actual_pairs:raise ValueError('duplicated query repeat')
                actual_pairs.add(pair)
                numeric=[(r['repo_id'],r['commit'],r['path']) for r in rows].index((key[0],key[2],key[3]))
                ids,parent,rank=search(len(rows),reverse_index(len(rows),edges),numeric)
                oracle=reference(len(rows),edges,numeric)
                full=answer_rows(rows,oracle)
                if (answer!=q['answer'] or answer['results']!=full or read(path.parent/'oracle.json')!=full
                        or ids.tolist()!=oracle.tolist() or not answer['formally_verified']
                        or answer['verification_level']!='LEAN_SOURCE_TO_ANSWER' or answer['corpus_manifest_sha256']!=anchor
                        or answer['scope']!=manifest['scope_policy']
                        or answer['proof']['preparation_receipt_sha256']!=args.prepared_sha256
                        or answer['proof']['query_modules']!=q['modules']
                        or read(path.parent/'certificate.json')!=[[int(v),int(parent[v]),int(rank[v])] for v in ids]):
                    raise ValueError('complete query/certificate/answer binding failed')
                verify_modules(path.parent,q['modules'])
                audit_query(path.parent/'lean',len(rows),edges,numeric,ids,parent[ids],rank[ids])
                resources.append(checked_resource(q['supervision'],600,path.parent.parent))
                if any(m['process_profile']['priority']!=32 for m in q['modules'].values()):raise ValueError('non-Normal Lean query profile')
                checked.append(q)
            distinct={tuple(q['answer']['root'][k] for k in ('project','context','commit','path')):q for q in checked}
            projects=[len({r['project'] for r in q['answer']['results']}) for q in distinct.values()]
            sizes={len(q['answer']['results']) for q in distinct.values()}
            queries_ok=(actual_pairs==expected_pairs and len(checked)==18 and len(distinct)==6
                        and sum(p>1 for p in projects)>=3 and 3 in projects and len(sizes)>=3)
        except Exception as exc:failures.append('formal/reuse/query audit: '+str(exc))
    if regression.get('status')=='REGRESSION_PASS':
        try:
            results=parse_results((Path(regression['view']['directory']).parent/'process/stderr.log').read_text(encoding='utf-8'))
            expected=read(Path(regression['view']['directory']).parent/'discovered-tests.json')
            old=optional('stage8-full-09.json')['results']
            regression_ok=(results==regression['results'] and sorted(results)==expected and len(results)>=201
                and len(old)==180 and set(old).issubset(results) and all(v=='ok' for v in results.values())
                and regression['code_and_tests']==code_inventory(PROJECT))
            verify_regression_view(PROJECT,regression['view'])
            resource_path=Path(regression['view']['directory']).parent/'process/resource-report.json'
            resources.append(checked_resource({'path':str(resource_path),'sha256':digest(resource_path)},2400,resource_path.parent.parent))
        except Exception as exc:failures.append('regression audit: '+str(exc))
    corpus_review=reviews['corpus']
    corpus_ok=(corpus_review.get('status')=='CORPUS_REVIEW_PASS' and not corpus_review.get('blocking_findings')
               and corpus_review.get('manifest_sha256')==anchor)
    gates={
        'G1_real_three_project_corpus':count>=1000 and corpus.get('projects')==3 and corpus_ok,
        'G2_import_connections_contexts':corpus_ok,
        'G3_all_sources_formal':prep_ok,
        'G4_six_query_requirements':queries_ok,
        'G5_full_independent_answers':queries_ok,
        'G6_public_cli':prep_ok and queries_ok,
        'G7_export_axiom_answer_audit':prep_ok and queries_ok,
        'G8_rejection_cache_tests':regression_ok,
        'G9_full_regression':regression_ok,
        'G10_frozen_resource_measurements':prep_ok and queries_ok and regression_ok and not failures,
        'G11_exact_code_artifacts':prep_ok and queries_ok and regression_ok and not failures}
    dossier={'gates_without_final_review':gates,'manifest_sha256':anchor,'code_and_tests':code_inventory(PROJECT),
             'preparation_sha256':args.prepared_sha256,'regression_sha256':digest(PROJECT/'verification/stage9-regression.json') if regression else None,
             'measurements_sha256':digest(PROJECT/'verification/stage9-measurements.json') if measurements else None,
             'query_receipts':[{k:s[k] for k in ('report','sha256')} for s in measurements.get('samples',[])],
             'acceptance_audit_failures':failures}
    candidate_path=PROJECT/'verification/stage9-candidate.json'
    if candidate:write(candidate_path,dossier)
    formal_review=reviews['formal']
    review_ok=(candidate_path.exists() and read(candidate_path)==dossier and
        formal_review.get('status')=='FORMAL_REVIEW_PASS' and not formal_review.get('blocking_findings') and
        formal_review.get('candidate_sha256')==digest(candidate_path))
    gates['G12_independent_reviews']=corpus_ok and review_ok
    report={'status':'STAGE9_PASS' if all(gates.values()) else 'STAGE9_INCOMPLETE','gates':gates,
        'unsatisfied_gates':[k for k,v in gates.items() if not v],'corpus':corpus,'preparation_path':str(prepared/'prepare.json'),
        'preparation_status':preparation.get('status'),'prepared_modules':list(preparation.get('modules',{})),
        'accepted_queries':len(checked),'tests':regression.get('tests',0),'acceptance_audit_failures':failures,
        'largest_stage9_complete_source_formal_scope':count if prep_ok and checked else 0,
        'historical_complete_multirepo_source_scope':18,'code_and_tests':code_inventory(PROJECT),
        'resources':resources,'review_statuses':{k:r.get('status') for k,r in reviews.items()},'llm_api_calls':0}
    write(PROJECT/'verification/stage9-status.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('regression','queries','status'))
    p.add_argument('--run-dir',type=Path);p.add_argument('--prepared-dir',type=Path);p.add_argument('--lean',type=Path);p.add_argument('--locations',type=Path)
    p.add_argument('--prepared-sha256',help='independently retained anchor from actual successful preparation')
    p.add_argument('--candidate',action='store_true');p.add_argument('--clean-bytecode',action='store_true',help=argparse.SUPPRESS)
    a=p.parse_args()
    if a.command in ('queries','status') and not a.prepared_sha256:p.error('independent --prepared-sha256 is required')
    if a.command=='regression':result=regression(a.run_dir.resolve(),a.lean.resolve())
    elif a.command=='queries':result=queries(a.run_dir.resolve(),a.prepared_dir.resolve(),a.lean.resolve(),a.locations.resolve(),a.prepared_sha256)
    else:result=status(a.prepared_dir.resolve(),a.lean.resolve(),a.locations.resolve(),a.candidate,a.prepared_sha256)
    print(json.dumps({'status':result.get('status')} if result else {'status':'see measurements'}))


if __name__=='__main__':main()
