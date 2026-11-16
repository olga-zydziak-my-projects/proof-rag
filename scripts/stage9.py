"""Public Stage 9 CLI: prepare a checked source layer, then prove each answer.

Each command is supervised as one Windows process tree. An independently
retained preparation receipt hash is required for reuse; it anchors an actual
fresh kernel execution, not a caller-authored PASS flag. All receipt members,
exports, source bytes, graph rows, logs, code, tools and dependencies are
checked again before and after every fresh query proof.
"""
import os
import sys
# -B alone still reads old .pyc. Re-exec the CLI before importing any project
# or third-party module with a new empty cache prefix; descendants inherit it.
if __name__=='__main__' and '--clean-bytecode' not in sys.argv:
    run=sys.argv[sys.argv.index('--run-dir')+1] if '--run-dir' in sys.argv else os.path.join(os.getcwd(),'local','stage9','help')
    cache=os.path.abspath(run+'-bytecode-'+str(os.getpid()))
    os.makedirs(cache,exist_ok=False)
    os.environ['PYTHONPYCACHEPREFIX']=cache
    base=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.environ['PYTHONPATH']=os.pathsep.join(os.path.join(base,p) for p in ('src','scripts','local/stage8-deps'))
    raise SystemExit(os.spawnv(os.P_WAIT,sys.executable,[sys.executable,'-B','-S','-X','pycache_prefix='+cache,__file__,*sys.argv[1:],'--clean-bytecode']))

import argparse
from contextlib import ExitStack
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT/'src'), str(PROJECT/'scripts'),str(PROJECT/'local/stage8-deps')]
import numpy as np
from repo_proof.stage8_sources import capture, blob_reader, git, tool_identity
from repo_proof.stage8_store import build, load, digest
from repo_proof.stage8_graph import reverse_index, search, reference, check_certificate
from repo_proof.stage8_corpus_audit import verify_corpus
from stage9_recon import GENERATED, GENERATED_CONFIGS
from repo_proof.stage5_v2 import canonical
from stage8_lean_check import _audit_module
from stage9_export import export_sources, audit_sources, export_query, audit_query

CONTEXTS = {'chromium': 'upstream', 'electron': 'electron-default', 'brave': 'brave-default'}
DEPENDENCIES = ('Reachability', 'Checker', 'FastChecker', 'ProofTiming',
                'SourceByteScanner', 'SourceGraphBinding', 'ContextualSourceBinding', 'Stage9Binding')


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    Path(path).write_bytes(canonical(value))


def anchored(path, expected):
    if digest(path) != expected:
        raise ValueError('independent anchor mismatch: ' + str(path))
    return read(path)


def identities(rows, contexts):
    if contexts != CONTEXTS:
        raise ValueError('unaccepted project/context mapping')
    return [(r['repo_id'] + '@' + contexts[r['repo_id']], r['commit'], r['path']) for r in rows]


def contextual_rules(rules, contexts):
    def version(v):
        return [v[0] + '@' + contexts[v[0]], v[1]]
    return [{**r, 'from': version(r['from']), 'to': None if r['to'] is None else version(r['to'])} for r in rules]


def source_bytes(rows, locations):
    # Batch reads replace n Git process startups. At this scale the complete
    # raw corpus is only a few MB; large Lean exports are persisted per shard.
    with ExitStack() as stack:
        readers = {v: stack.enter_context(blob_reader(p)) for v, p in locations.items()}
        return [readers[r['repo_id'], r['commit']](r['blob']) for r in rows]


def inputs(a, folder):
    manifest = anchored(a.manifest, a.manifest_sha256)
    if (set(manifest) != {'schema', 'sources', 'contexts', 'scope_policy', 'baseline_manifest_sha256'}
            or manifest['schema'] != 'stage9-context-corpus-v1' or manifest['contexts'] != CONTEXTS):
        raise ValueError('stage9 context manifest schema')
    policy = read(PROJECT/'verification/stage9-scope-policy.json')
    if manifest['scope_policy'] != policy:
        raise ValueError('scope rule changed')
    path = folder/'source-manifest.json'
    write(path, manifest['sources'])
    anchor = digest(path)
    locations = {(r['repo_id'], r['commit']): r['directory'] for r in read(a.locations)}
    files, edges, facts = capture(path, anchor, locations, spool_dir=folder, file_prefixes=True)
    rows = files.to_pylist()
    sources = source_bytes(rows, locations)
    imports = {r['repo_id']: [] for r in rows}
    for event in facts['events']:
        imports[rows[event['importer']]['repo_id']].append(event['literal'])
    versions={repo['repo_id']:repo['commit'] for repo in manifest['sources']['repositories']}
    for row in facts['resolutions']:
        literal=row['literal']
        if literal in GENERATED:
            if row['target'] is not None or row['status']!='external':
                raise ValueError('generated boundary substitution')
            rule=next(r for r in manifest['sources']['rules'] if r['id']==row['rule'])
            if rule['prefix']!=literal or rule['evidence']!='chromium-'+literal.rpartition('/')[0].replace('/','-')+'-BUILD.gn':
                raise ValueError('generated literal/GN evidence changed')
        else:
            project='brave' if literal.startswith('brave/') else 'electron' if literal.startswith('electron/') else 'chromium'
            path=literal[6:] if project=='brave' else literal[9:] if project=='electron' else literal
            target=rows[row['target']] if row['target'] is not None else None
            if target is None or (target['repo_id'],target['commit'],target['path'])!=(project,versions[project],path):
                raise ValueError('resolver differs from accepted contextual mount mapping')
    baseline = PROJECT/'verification/stage8-connected-corpus-manifest-04.json'
    if manifest['baseline_manifest_sha256'] != digest(baseline):
        raise ValueError('baseline corpus anchor changed')
    # Rechecks original commits, configs, complete patch/overlay inventories,
    # drivers, pin compatibility and all bytes in the shared dependency closure.
    corpus = verify_corpus(baseline, manifest['baseline_manifest_sha256'],
                           PROJECT/'verification/stage8-connected-corpus-evidence-04.json')
    original = read(baseline)
    configs=manifest['sources']['configs']
    expected_paths={(c['repo_id'],c['commit'],c['path']) for c in original['configs']} | {('chromium',versions['chromium'],p) for p in GENERATED_CONFIGS}
    if {(c['repo_id'],c['commit'],c['path']) for c in configs}!=expected_paths or len(configs)!=len(expected_paths):
        raise ValueError('complete pinned mapping/generated-boundary configs changed')
    for c in original['configs']:
        if c not in configs:
            raise ValueError('original mapping config identity changed')
    pinned = {r['repo_id']: r for r in original['repositories']}
    for repo in manifest['sources']['repositories']:
        base = pinned[repo['repo_id']]
        if any(repo[k] != base[k] for k in ('commit', 'tree', 'url')):
            raise ValueError('project/version context substitution')
        if repo['repo_id'] != 'chromium' and repo != base:
            raise ValueError('application GN scope changed')
        if repo['repo_id']=='chromium':
            required={p+'/' for p in policy['chromium_complete_modules']}
            if not required.issubset(repo['prefixes']):
                raise ValueError('complete frozen Chromium module omitted')
    if len(rows)<policy['minimum_real_distinct_files']:
        raise ValueError('real corpus below frozen threshold')
    seeds={i for i,row in enumerate(rows) if row['repo_id']!='chromium' or
           any(row['path'].startswith(p+'/') for p in policy['chromium_complete_modules'])}
    outgoing={}
    for a,b in edges:outgoing.setdefault(int(a),[]).append(int(b))
    pending=list(seeds); visited=set(seeds)
    for v in pending:
        for target in outgoing.get(v,[]):
            if target not in visited:visited.add(target); pending.append(target)
    if len(visited)!=len(rows):
        raise ValueError('unjustified file outside complete modules and least import closure')
    by_identity = {(r['repo_id'], r['commit'], r['path']): i for i,r in enumerate(rows)}
    base_keys = {(r['repo_id'],r['commit'],f['path']) for r in original['repositories'] for f in r['files']}
    shared = {by_identity[k] for k in base_keys}
    # Shared targets must retain their entire closure inside the audited set.
    if any(int(a) in shared and int(b) not in shared for a,b in edges):
        raise ValueError('Electron/Brave equivalence closure escaped audited inputs')
    if any(e['literal'] not in GENERATED for e in facts['external']):
        raise ValueError('unaccepted external import event')
    return manifest, files, edges, facts, rows, sources, locations, corpus


def file_inventory(folder, predicate=lambda p: True):
    return {p.relative_to(folder).as_posix(): {'sha256':digest(p),'bytes':p.stat().st_size}
            for p in sorted(Path(folder).rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.part', '.tmp') and predicate(p)}


def environment(lean):
    # Complete Python sources/dependencies and Lean toolchain, not just version
    # labels. Bytecode is ignored: Python runs with -B; accepted .olean files
    # are included in the separately checked preparation artifact inventory.
    bytecode_policy()
    import duckdb,pyarrow,numpy,psutil
    for module in (duckdb,pyarrow,numpy,psutil):
        if not Path(module.__file__).resolve().is_relative_to(PROJECT/'local/stage8-deps'):
            raise ValueError('dependency loaded outside pinned local directory: '+module.__name__)
    code = {base:file_inventory(PROJECT/base, lambda p:p.suffix in ('.py','.lean')) for base in ('src','scripts','formal')}
    dependencies = file_inventory(PROJECT/'local/stage8-deps', lambda p:p.suffix not in ('.pyi',))
    toolchain = file_inventory(Path(lean).parent.parent)
    python = file_inventory(Path(sys.executable).parent, lambda p: 'site-packages' not in p.parts and 'Scripts' not in p.parts)
    git_exe = Path(shutil.which('git')).resolve()
    specs = {name:digest(PROJECT/name) for name in ('requirements-stage8.txt','verification/stage9-config.json',
             'verification/stage9-scope-policy.json','docs/stage9-contract.md','docs/stage9-source-spec.md')}
    git_runtime=file_inventory(git_exe.parent.parent)
    return {'code':code,'dependencies':dependencies,'lean_toolchain':toolchain,'python_runtime':python,'git_runtime':git_runtime,
            'lean_executable':str(Path(lean).resolve()),'lean_sha256':digest(lean),
            'lean_version':subprocess.check_output([str(lean),'--version']).decode().strip(),
            'git_exe':str(git_exe),'git_sha256':digest(git_exe),
            'git_version':subprocess.check_output([str(git_exe),'--version']).decode().strip(),
            'python_executable':str(Path(sys.executable).resolve()),'specifications':specs,'source_tools':tool_identity()}


def bytecode_policy():
    if not sys.dont_write_bytecode or not sys.flags.no_site or not sys.pycache_prefix or any(Path(sys.pycache_prefix).rglob('*.pyc')):
        raise ValueError('proof execution requires -B and an empty process-start bytecode prefix')


def validate_profile(path):
    config=read(path)
    limits=config['limits']
    if (limits['timeout_seconds']!=3600 or limits['tree_memory_bytes']!=6*1024**3
            or limits['artifact_bytes']!=20*1024**3 or limits['process_parallelism']!=1
            or config['query_timeout_seconds']!=600 or config['regression_timeout_seconds']!=2400
            or config['historical_differential_timeout_seconds']!=600):
        raise ValueError('Stage9 frozen resource profile differs')
    return config


def compile_module(folder, module, lean, lean_path):
    env = dict(os.environ, LEAN_PATH=os.pathsep.join(map(str,lean_path)))
    source = folder/'lean'/(module+'.lean')
    logs = folder/'logs'/module
    logs.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    with (logs/'stdout.log').open('wb') as out, (logs/'stderr.log').open('wb') as err:
        process = subprocess.Popen([str(lean), '-o', str(source.with_suffix('.olean')),
            '--root='+str(source.parent), str(source)], stdout=out, stderr=err, env=env,
            creationflags=subprocess.NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
        import psutil
        observed=psutil.Process(process.pid)
        profile={'priority':int(observed.nice()),'affinity':observed.cpu_affinity()}
        code=process.wait()
    if code:
        raise ValueError('kernel compilation failed: '+module+'; see '+str(logs))
    names = tuple(re.findall(r'^#print axioms (\S+)$', source.read_text(encoding='utf-8'), re.M))
    output = (logs/'stdout.log').read_text(encoding='utf-8')
    if not names and output.strip():
        raise ValueError('unparsed output in module without axiom declarations')
    axioms = _audit_module(output,names) if names else {}
    if (logs/'stderr.log').read_bytes():
        raise ValueError('unexpected Lean stderr: '+module)
    return {'seconds':time.perf_counter()-started,'axioms':axioms,'source_sha256':digest(source),'process_profile':profile,
            'olean_sha256':digest(source.with_suffix('.olean')),'theorems':list(names)}


def verify_modules(folder, records):
    actual_modules = {p.stem for p in (folder/'lean').glob('*.olean')}
    if actual_modules != set(records):
        raise ValueError('prepared module coverage changed')
    for module, record in records.items():
        source = folder/'lean'/(module+'.lean')
        if digest(source) != record['source_sha256'] or digest(source.with_suffix('.olean')) != record['olean_sha256']:
            raise ValueError('compiled/source artifact changed: '+module)
        names = tuple(re.findall(r'^#print axioms (\S+)$', source.read_text(encoding='utf-8'), re.M))
        if list(names) != record['theorems']:
            raise ValueError('axiom report declaration coverage changed')
        raw = (folder/'logs'/module/'stdout.log').read_text(encoding='utf-8')
        if not names and raw.strip():
            raise ValueError('unparsed output in module without axiom declarations')
        parsed = _audit_module(raw,names) if names else {}
        if parsed != record['axioms'] or (folder/'logs'/module/'stderr.log').read_bytes():
            raise ValueError('axiom report changed')


def prepare(a):
    folder = Path(a.run_dir).resolve()
    folder.mkdir(parents=True,exist_ok=False)
    (folder/'lean').mkdir()
    started = time.perf_counter()
    report = {'status':'PREPARING','source_to_graph':False,'modules':{},'phases_seconds':{}}
    try:
        stamp = time.perf_counter()
        initial = environment(a.lean)
        report['phases_seconds']['full_environment_identity'] = time.perf_counter()-stamp
        stamp = time.perf_counter()
        manifest, files, edges, facts, rows, sources, locations, corpus = inputs(a,folder)
        report['phases_seconds']['source_read_audit_extraction'] = time.perf_counter()-stamp
        stamp=time.perf_counter()
        (folder/'index').mkdir()
        build(folder/'index',files,edges,facts,read(a.config)['limits'])
        report['phases_seconds']['index_write'] = time.perf_counter()-stamp
        names=identities(rows,manifest['contexts'])
        rules=contextual_rules(manifest['sources']['rules'],manifest['contexts'])
        stamp=time.perf_counter()
        export_sources(folder/'lean',names,sources,rules,edges)
        for module in DEPENDENCIES:
            shutil.copyfile(PROJECT/'formal'/(module+'.lean'),folder/'lean'/(module+'.lean'))
        report['phases_seconds']['proof_export_and_audit'] = time.perf_counter()-stamp
        stamp=time.perf_counter()
        modules=[*DEPENDENCIES,'SourceNames','CorpusGraph',*[p.stem for p in sorted((folder/'lean').glob('SourceGroup*.lean'))],'SourceCorpus']
        write(folder/'progress.json',report)
        for module in modules:
            report['modules'][module] = compile_module(folder,module,a.lean,[folder/'lean'])
            write(folder/'progress.json',report)
            print('compiled',module,report['modules'][module]['seconds'],flush=True)
        report['phases_seconds']['formal_source_layer'] = time.perf_counter()-stamp
        audit_sources(folder/'lean',names,sources,rules,edges)
        verify_modules(folder,report['modules'])
        after=inputs(a,folder)
        if not files.equals(after[1]) or not np.array_equal(edges,after[2]) or facts != after[3] or sources != after[5] or initial != environment(a.lean):
            raise ValueError('preparation inputs changed during kernel run')
        report.update(status='KERNEL_SOURCE_LAYER_PASS',source_to_graph=True,manifest_sha256=a.manifest_sha256,
            environment=initial,nodes=len(rows),edges=len(edges),source_bytes=sum(map(len,sources)),corpus_audit=corpus)
        for factset in (facts,after[3]):
            for key in ('events','resolutions','external'):
                factset[key].close()
        report['artifact_inventory']=file_inventory(folder,lambda p:p.name not in ('prepare.json','progress.json'))
    except Exception as exc:
        report.update(status='PREPARE_FAILED',error=type(exc).__name__+': '+str(exc))
    report['seconds']=time.perf_counter()-started
    write(folder/('candidate-prepare.json' if report['status']=='KERNEL_SOURCE_LAYER_PASS' else 'prepare.json'),report)
    return report


def validate_prepared(a, folder):
    prepared=Path(a.prepared_dir).resolve()
    receipt=anchored(prepared/'prepare.json',a.prepared_sha256)
    if (receipt['status']!='SOURCE_LAYER_PASS' or not receipt['source_to_graph']
            or receipt['manifest_sha256']!=a.manifest_sha256):
        raise ValueError('preparation was not accepted for this corpus')
    resource=anchored(receipt['supervision']['path'],receipt['supervision']['sha256'])
    if resource['status']!='PROCESS_PASS' or resource['remaining_job_processes']!=0 or resource['exit_code']!=0:
        raise ValueError('preparation supervision did not pass')
    validate_profile(a.config)
    if receipt['config_sha256']!=digest(a.config):
        raise ValueError('preparation resource profile changed')
    if receipt['environment']!=environment(a.lean):
        raise ValueError('stale preparation: full code/dependency/tool/spec identity changed')
    if receipt['artifact_inventory']!=file_inventory(prepared,lambda p:p.name not in ('prepare.json','progress.json')):
        raise ValueError('prepared artifact inventory changed')
    verify_modules(prepared,receipt['modules'])
    values=inputs(a,folder)
    manifest,files,edges,facts,rows,sources,locations,corpus=values
    cached_files,cached_edges,cached_facts=load(prepared/'index',read(a.config)['limits'])
    if not files.equals(cached_files) or not np.array_equal(edges,cached_edges) or facts!=cached_facts:
        raise ValueError('complete source/index comparison failed')
    audit_sources(prepared/'lean',identities(rows,manifest['contexts']),sources,
                  contextual_rules(manifest['sources']['rules'],manifest['contexts']),edges)
    return receipt,values


def answer_rows(rows, ids):
    return [{'project':rows[int(i)]['repo_id'],'context':CONTEXTS[rows[int(i)]['repo_id']],
             'commit':rows[int(i)]['commit'],'path':rows[int(i)]['path']} for i in ids]


def query(a):
    folder=Path(a.run_dir).resolve()
    folder.mkdir(parents=True,exist_ok=False)
    (folder/'lean').mkdir()
    start=time.perf_counter()
    report={'status':'QUERY_FAILED','formally_verified':False,'phases_seconds':{}}
    try:
        stamp=time.perf_counter()
        receipt,values=validate_prepared(a,folder)
        manifest,files,edges,facts,rows,sources,locations,corpus=values
        report['phases_seconds']['validate_source_layer_reuse']=time.perf_counter()-stamp
        root_key=(a.repo_id,a.commit,a.path)
        if a.context!=CONTEXTS.get(a.repo_id):
            raise ValueError('wrong query context')
        root=[(r['repo_id'],r['commit'],r['path']) for r in rows].index(root_key)
        stamp=time.perf_counter()
        ids,p,r=search(len(rows),reverse_index(len(rows),edges),root)
        report['phases_seconds']['search_and_certificate']=time.perf_counter()-stamp
        stamp=time.perf_counter()
        oracle=reference(len(rows),edges,root)
        check_certificate(len(rows),edges,root,ids,p[ids],r[ids])
        if ids.tolist()!=oracle.tolist():
            raise ValueError('complete independent answer mismatch')
        report['phases_seconds']['independent_reference_and_certificate_check']=time.perf_counter()-stamp
        write(folder/'certificate.json',[[int(v),int(p[v]),int(r[v])] for v in ids])
        write(folder/'oracle.json',answer_rows(rows,oracle))
        stamp=time.perf_counter()
        export_query(folder/'lean',len(rows),edges,root,ids,p[ids],r[ids])
        report['phases_seconds']['proof_export_audit']=time.perf_counter()-stamp
        stamp=time.perf_counter()
        report['modules']={}
        for module in ('QueryGraph','QueryAnswer'):
            report['modules'][module]=compile_module(folder,module,a.lean,[folder/'lean',Path(a.prepared_dir)/'lean'])
        report['phases_seconds']['fresh_query_lean']=time.perf_counter()-stamp
        audit_query(folder/'lean',len(rows),edges,root,ids,p[ids],r[ids])
        # Every input including cache bytes is rechecked after Lean completes.
        validate_prepared(a,folder)
        stamp=time.perf_counter()
        expected=answer_rows(rows,ids)
        answer={'verification_level':'KERNEL_CHECKED_PENDING_SUPERVISOR','formally_verified':False,
                'root':answer_rows(rows,[root])[0], 'corpus_manifest_sha256':a.manifest_sha256,
                'scope':manifest['scope_policy'],'results':expected,
                'proof':{'preparation_receipt_sha256':a.prepared_sha256,'query_modules':report['modules']}}
        write(folder/'candidate-answer.json',answer)
        if read(folder/'candidate-answer.json')!=answer or answer['results']!=read(folder/'oracle.json'):
            raise ValueError('complete final answer roundtrip/oracle mismatch')
        report['phases_seconds']['answer_write_and_check']=time.perf_counter()-stamp
        report.update(status='KERNEL_QUERY_PASS',answer=answer,full_oracle_match=True)
    except Exception as exc:
        # A new directory is mandatory. Never return a previous answer or an
        # empty verified result following a failure.
        if (folder/'candidate-answer.json').exists():
            (folder/'candidate-answer.json').rename(folder/'rejected-answer.json')
        report.update(error=type(exc).__name__+': '+str(exc))
    report['seconds']=time.perf_counter()-start
    write(folder/'query.json',report)
    return report


def finalize_run(command, folder, resource_path, config, supervisor_exit=0):
    """Publish only after the complete supervised tree has exited successfully."""
    folder=Path(folder); resource_path=Path(resource_path)
    folder.mkdir(parents=True,exist_ok=True)
    resource=read(resource_path)
    passed=supervisor_exit==0 and resource['status']=='PROCESS_PASS' and resource.get('remaining_job_processes')==0 and resource.get('exit_code')==0
    supervision={'path':str(resource_path.resolve()),'sha256':digest(resource_path)}
    if command=='prepare':
        candidate=folder/'candidate-prepare.json'
        report=read(candidate) if candidate.exists() else {'status':'PREPARE_FAILED','source_to_graph':False}
        if passed and report['status']=='KERNEL_SOURCE_LAYER_PASS':
            report.update(status='SOURCE_LAYER_PASS',supervision=supervision,config_sha256=digest(config))
        else:
            report.update(status='PREPARE_FAILED',source_to_graph=False,supervision=supervision)
        if candidate.exists():candidate.rename(folder/'rejected-or-kernel-prepare.json')
        # The worker inventory was taken before its candidate receipt existed.
        # The retained kernel receipt is explicitly added to the accepted seal.
        if report['status']=='SOURCE_LAYER_PASS':
            report['artifact_inventory']=file_inventory(folder,lambda p:p.name not in ('prepare.json','progress.json'))
        write(folder/'prepare.json',report)
    else:
        report=read(folder/'query.json') if (folder/'query.json').exists() else {'status':'QUERY_FAILED','formally_verified':False}
        candidate=folder/'candidate-answer.json'
        if passed and report['status']=='KERNEL_QUERY_PASS' and candidate.exists():
            answer=read(candidate)
            if answer!=report['answer'] or answer['results']!=read(folder/'oracle.json'):
                raise ValueError('candidate full answer/oracle mismatch at publication')
            answer.update(formally_verified=True,verification_level='LEAN_SOURCE_TO_ANSWER',supervision=supervision)
            pending=folder/'final-answer.pending'
            write(pending,answer)
            if read(pending)!=answer or read(pending)['results']!=read(folder/'oracle.json'):
                pending.rename(folder/'rejected-final-answer.json')
                raise ValueError('final full answer roundtrip mismatch')
            pending.replace(folder/'answer.json')
            report.update(status='SOURCE_TO_ANSWER_PASS',formally_verified=True,answer=answer,answer_sha256=digest(folder/'answer.json'),supervision=supervision)
        else:
            report.update(status='QUERY_FAILED',formally_verified=False,supervision=supervision)
        if candidate.exists():candidate.rename(folder/'kernel-or-rejected-answer.json')
        write(folder/'query.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('prepare','query'))
    for name in ('manifest','manifest-sha256','locations','lean','run-dir'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--config',default=str(PROJECT/'verification/stage9-config.json'))
    p.add_argument('--prepared-dir'); p.add_argument('--prepared-sha256')
    p.add_argument('--repo-id'); p.add_argument('--commit'); p.add_argument('--context'); p.add_argument('--path')
    p.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    p.add_argument('--clean-bytecode',action='store_true',help=argparse.SUPPRESS)
    a=p.parse_args()
    if a.command=='query' and any(getattr(a,k) is None for k in ('prepared_dir','prepared_sha256','repo_id','commit','context','path')):
        p.error('query requires preparation receipt, full root identity and context')
    if not a.worker:
        # One supervisor encloses preparation/export/kernel, and all descendants.
        run=Path(a.run_dir).resolve()
        if run.exists() or run.with_name(run.name+'-control').exists():
            p.error('run and control directories must be new')
        control=run.with_name(run.name+'-control')
        control.mkdir(parents=True)
        config=validate_profile(a.config)
        config['limits']['timeout_seconds']=config['limits']['timeout_seconds'] if a.command=='prepare' else config['query_timeout_seconds']
        write(control/'config.json',config)
        command=[sys.executable,'-B','-S',str(PROJECT/'scripts/stage8_supervise.py'),'--config',str(control/'config.json'),
                 '--run-dir',str(control/'process'),'--artifact-root',str(run.parent),'--',sys.executable,'-B','-S',__file__,*sys.argv[1:],'--worker']
        result=subprocess.call(command)
        report=finalize_run(a.command,run,control/'process/resource-report.json',a.config,result)
        print(json.dumps({'status':report['status'],'error':report.get('error')}),flush=True)
        return 0 if report['status'] in ('SOURCE_LAYER_PASS','SOURCE_TO_ANSWER_PASS') else 2
    report=prepare(a) if a.command=='prepare' else query(a)
    print(json.dumps({'status':report['status'],'seconds':report['seconds'],'error':report.get('error')}),flush=True)
    return 0 if report['status'] in ('KERNEL_SOURCE_LAYER_PASS','KERNEL_QUERY_PASS') else 2


if __name__=='__main__':
    raise SystemExit(main())
