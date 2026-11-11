"""Fail-closed Stage 5 prerequisites. This is NOT a source-semantics proof.

The supplied inventory claim conflicts with the accepted Git checkpoint.
No fallback, release, source theorem, or successful answer is implemented here.
"""
from dataclasses import asdict,dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
from time import perf_counter

from .extraction import ExpectedInputs,load_snapshot,read_json

BASELINE='e4984110743131d04ad984eaaa48d33d72867336'
STAGE3='3184813'
CONTRACT_SHA256='5c323f4e9c2ae8d3bb498cd2b267e57ba8d4e76d09e2673c5d46979d3f44161d'
INVENTORY_SHA256='3c0ecccc19d58ea9473b0ff4d468978cc8b123246401e1dbc94336b40b44af47'
ROOT='mojo/public/mojom/base/time.mojom'


@dataclass(frozen=True)
class Pin:
    repository: str
    commit: str
    tree: str


INVENTORY_CLAIM=Pin('https://github.com/chromium/chromium',
    '1ab171af2976555a2b12b9bca8b984c204962ba8',
    '9e5b002b0ce384a82f6cb836fd3abaebab8a7da6')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin_differences(claim,anchor):
    return {k:{'claim':v,'accepted_anchor':asdict(anchor)[k]}
            for k,v in asdict(claim).items() if v!=asdict(anchor)[k]}


def _git(project,*args):
    env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    run=subprocess.run(['git','-c','safe.directory='+str(project),*args],cwd=project,
                       env=env,capture_output=True,timeout=120)
    if run.returncode:
        raise ValueError('local Git audit failed: '+run.stderr.decode('utf-8','replace'))
    return run.stdout


def accepted_anchor(project):
    """Read the expected lock from immutable accepted history, not a producer bundle."""
    project=Path(project).resolve()
    _git(project,'merge-base','--is-ancestor',STAGE3,BASELINE)
    _git(project,'merge-base','--is-ancestor',BASELINE,'HEAD')
    raw=_git(project,'show',BASELINE+':corpus.lock.json')
    if (project/'corpus.lock.json').read_bytes()!=raw:
        # A CRLF checkout may have different bytes while preserving JSON; the
        # baseline inventory below still enforces the original observed bytes.
        if read_json(project/'corpus.lock.json')!=json.loads(raw):
            raise ValueError('working lock differs from accepted checkpoint')
    lock=json.loads(raw)
    return Pin(lock['repository'],lock['commit'],lock['root_tree_object_id']),lock


def preservation(project):
    project=Path(project)
    frozen=(project/'verification/stage5-baseline.json').read_bytes()
    if digest(frozen)!=INVENTORY_SHA256:
        raise ValueError('frozen before-run inventory changed')
    if digest((project/'docs/stage5-contract.md').read_bytes())!=CONTRACT_SHA256:
        raise ValueError('frozen Stage 5 acceptance contract changed')
    inventory=json.loads(frozen)
    changed=[]
    for name,entry in inventory['files'].items():
        path=project/name
        if not path.is_file() or digest(path.read_bytes())!=entry['sha256']:
            changed.append(name)
    return {'preserved':not changed,'changed_baseline_files':changed,
            'tracked_files_checked':len(inventory['files']),
            'initial_status_porcelain':inventory['initial_status_porcelain'],
            'baseline_stage4':BASELINE,'stage3_ancestor':STAGE3}


def corroborate_baseline_bytes(data_dir,anchor,lock):
    """External audit ONLY under the accepted baseline pin, never inventory claim.

    load_snapshot checks the complete Git tree and selected blob bytes. Each
    receipt content hash below is separately computed from the captured bytes.
    There is no extraction, Lean export, or answer consumer after this capture.
    """
    snapshot=load_snapshot(data_dir,ExpectedInputs(anchor.commit,lock['manifest_sha256'],ROOT))
    if snapshot.diagnostics:
        raise ValueError('baseline source capture has missing/modified/unsupported data: '+
                         json.dumps(snapshot.diagnostics))
    entries=sorted(snapshot.source_entries,key=lambda e:e['path'])
    paths=[e['path'] for e in entries]
    if len(paths)!=len(set(paths)) or set(paths)!=set(snapshot.source_bytes):
        raise ValueError('selected inventory and captured bytes differ')
    receipt=[]
    for e in entries:
        path=e['path']; path.encode('utf-8',errors='strict')
        data=snapshot.source_bytes[path]
        receipt.append({'path':path,'mode':e['mode'],'git_blob_oid':e['object_id'],
                        'bytes':len(data),'independent_content_sha256':digest(data)})
    return {'schema':'stage5-baseline-byte-corroboration-v1',
            'scope':'Diagnostic corroboration of accepted Stage 2-4 pin only; NOT Stage 5 acceptance',
            'source_semantics_proved':False,'accepted_pin':asdict(anchor),
            'actual_git_checked_tree':snapshot.manifest['root_tree_object_id'],
            'manifest_sha256':lock['manifest_sha256'],'selected_files':receipt,
            'selected_file_count':len(receipt),'captured_source_bytes':sum(e['bytes'] for e in receipt),
            'non_ascii_selected_paths':sum(not p.isascii() for p in paths),
            'git_modes':sorted({e['mode'] for e in receipt}),
            'assumptions':['Git tree/object validation implementation','SHA-1/SHA-256 collision resistance',
                           'OS and file IO','Python execution'],
            'not_proved':['Mojom source semantics','byte export to Lean','source-to-graph correctness',
                          'answer decoding or delivery']}


def diagnose(project,config_path,output):
    """A blocked preflight can emit evidence, never a successful answer envelope."""
    project=Path(project).resolve(); output=Path(output).resolve()
    if not output.is_relative_to(project):
        raise ValueError('run directory must stay within the project')
    output.mkdir(parents=True,exist_ok=False)
    start=perf_counter()
    evidence={'schema':'stage5-preflight-v1','success':False,'answer_released':False,
              'baseline_stage4':BASELINE,'contract_sha256':CONTRACT_SHA256,
              'inventory_claim':asdict(INVENTORY_CLAIM),'stage5_source_theorem':None,
              'stage5_fresh_instance_seconds':None,'whole_successful_pipeline_seconds':None}
    try:
        before=preservation(project)
        if not before['preserved']: raise ValueError('baseline preservation failed')
        anchor,lock=accepted_anchor(project)
        differences=pin_differences(INVENTORY_CLAIM,anchor)
        evidence.update(accepted_anchor=asdict(anchor),pin_conflicts=differences,preservation_before=before)
        if not differences:
            # Even an agreeing pin is insufficient while the source theorem
            # has not been implemented. There is deliberately no PASS branch.
            evidence['status']='STAGE5_BLOCKED__SOURCE_PROOF'
        else:
            evidence['status']='BLOCKED_PIN_CONFLICT'
        config=read_json(config_path)
        if (not isinstance(config,dict) or set(config)!={'repository','commit','data_dir'}
                or any(not isinstance(config[k],str) or not config[k] for k in config)):
            raise ValueError('unsupported producer configuration schema')
        if config.get('repository')!=anchor.repository or config.get('commit')!=anchor.commit:
            evidence['config_error']='producer configuration differs from accepted anchor'
        else:
            t=perf_counter()
            try:
                receipt=corroborate_baseline_bytes(Path(config['data_dir']),anchor,lock)
                raw=(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(',',':'))+'\n').encode('utf-8')
                (output/'baseline-source-receipt.json').write_bytes(raw)
                evidence['baseline_byte_audit']={'succeeded':True,'receipt_sha256':digest(raw),
                    'selected_file_count':receipt['selected_file_count'],
                    'captured_source_bytes':receipt['captured_source_bytes'],
                    'non_ascii_selected_paths':receipt['non_ascii_selected_paths']}
            except (ValueError,OSError,subprocess.SubprocessError) as exc:
                evidence['baseline_byte_audit']={'succeeded':False,'error':str(exc)}
            evidence['baseline_provenance_seconds']=perf_counter()-t
        after=preservation(project)
        evidence['preservation_after']=after
        if not after['preserved']: raise ValueError('baseline changed during diagnostic audit')
        code=3
    except (ValueError,OSError,subprocess.SubprocessError,KeyError) as exc:
        evidence.update(status='STAGE5_FAIL__PREFLIGHT',error=str(exc)); code=2
    evidence['blocked_preflight_seconds']=perf_counter()-start
    (output/'diagnostic.json').write_bytes((json.dumps(evidence,indent=2)+'\n').encode('utf-8'))
    return evidence,code
