"""One diagnostic query profiles final publication, outside the 6x3 sample."""
from hashlib import sha256
import json
import os
from pathlib import Path
import pstats
import subprocess
import sys
import time
PROJECT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'scripts'),str(PROJECT/'local/stage8-deps')]
from stage9 import read,write

folder=Path(sys.argv[1]).resolve(); folder.mkdir(parents=True,exist_ok=False)
root=read(PROJECT/'verification/stage9-queries.json')['roots'][0]
trusted=read(PROJECT/'verification/stage9-preparation.json')['receipt_sha256']
lean=sys.argv[2]
manifest_sha=read(PROJECT/'verification/stage9-manifest-anchor.json')['sha256']
command=[sys.executable,'-B','-S','-X','pycache_prefix='+str(folder/'empty-bytecode'),'-m','cProfile','-o',str(folder/'parent.prof'),
    str(PROJECT/'scripts/stage9.py'),'query','--clean-bytecode','--manifest',str(PROJECT/'verification/stage9-manifest.json'),
    '--manifest-sha256',manifest_sha,'--locations',str(PROJECT/'local/stage9/acquire-03/data/locations.json'),
    '--lean',lean,'--run-dir',str(folder/'work'),'--prepared-dir',str(PROJECT/'local/stage9/prepare-03/work'),
    '--prepared-sha256',trusted,'--repo-id',root['project'],'--commit',root['commit'],'--context',root['context'],'--path',root['path']]
env=dict(os.environ,PYTHONPATH=os.pathsep.join(str(PROJECT/p) for p in ('src','scripts','local/stage8-deps')),
         PYTHONPYCACHEPREFIX=str(folder/'empty-bytecode'))
start=time.perf_counter(); result=subprocess.run(command,env=env,capture_output=True)
(folder/'stdout.log').write_bytes(result.stdout);(folder/'stderr.log').write_bytes(result.stderr)
if result.returncode:raise ValueError('diagnostic actual query failed')
q=read(folder/'work/query.json'); answer=read(folder/'work/answer.json')
reference=read(PROJECT/'local/stage9/queries-01/q1-r1/work/answer.json')
if q['status']!='SOURCE_TO_ANSWER_PASS' or any(answer[k]!=reference[k] for k in ('root','scope','corpus_manifest_sha256','results','verification_level','formally_verified')):
    raise ValueError('complete diagnostic answer mismatch')
stats=pstats.Stats(str(folder/'parent.prof')).stats
entries=[(key,value) for key,value in stats.items() if key[0].replace('\\','/').endswith('/scripts/stage9.py') and key[2]=='finalize_run']
if len(entries)!=1 or entries[0][1][0]!=1:raise ValueError('finalize_run not profiled exactly once')
write(PROJECT/'verification/stage9-publication-profile.json',{
    'schema':'stage9-publication-profile-v1','status':'PUBLICATION_PROFILE_PASS','manifest_sha256':manifest_sha,
    'prepared_receipt_sha256':trusted,'query_report_path':str(folder/'work/query.json'),
    'query_report_sha256':sha256((folder/'work/query.json').read_bytes()).hexdigest(),
    'publication_coordinator_seconds':entries[0][1][3],'diagnostic_wall_seconds':time.perf_counter()-start,
    'full_final_answer_matches_accepted_reference':True,'profiler_code_path':str(Path(__file__).resolve()),
    'profiler_code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
    'note':'Additional real fresh-kernel query, excluded from the six roots x three latency sample. cProfile instruments only the coordinator, including final JSON write/readback, whole-answer equality and atomic publication. Worker kernel checks are uninstrumented. Resource profile remains unchanged; OS cache not controlled.'})
print('PUBLICATION_PROFILE_PASS',flush=True)
