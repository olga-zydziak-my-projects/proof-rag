"""Instrumented IO/extraction decomposition; never a proof acceptance path."""
import cProfile
from hashlib import sha256
import json
from pathlib import Path
import pstats
import sys
import time

PROJECT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'scripts'),str(PROJECT/'local/stage8-deps')]
from stage9 import read,write,inputs
from repo_proof.stage8_sources import capture
from repo_proof.stage8_store import build
from repo_proof.stage8_corpus_audit import verify_corpus
import pyarrow.parquet as pq
import numpy as np

folder=Path(sys.argv[1]).resolve(); prepared=Path(sys.argv[2]).resolve()
folder.mkdir(parents=True,exist_ok=False)
manifest=read(PROJECT/'verification/stage9-manifest.json')
source=folder/'source-manifest.json'; write(source,manifest['sources'])
anchor=sha256(source.read_bytes()).hexdigest()
locations={(r['repo_id'],r['commit']):r['directory'] for r in read(PROJECT/'local/stage9/acquire-03/data/locations.json')}
timer=time.perf_counter()
plain=capture(source,anchor,locations,spool_dir=folder,file_prefixes=True)
plain_seconds=time.perf_counter()-timer
profiler=cProfile.Profile()
timer=time.perf_counter()
captured=profiler.runcall(capture,source,anchor,locations,spool_dir=folder,file_prefixes=True)
profiled_seconds=time.perf_counter()-timer
profiler.dump_stats(str(folder/'capture.prof'))
files,edges,facts=captured
if not files.equals(plain[0]) or not np.array_equal(edges,plain[1]) or facts!=plain[2]:
    raise ValueError('instrumented output differs in complete data')
if not files.equals(pq.read_table(prepared/'index/files.parquet')):
    raise ValueError('full file inventory differs from actual prepared index')
et=pq.read_table(prepared/'index/edges.parquet')
if not np.array_equal(edges,np.column_stack([et[k].to_numpy() for k in ('importer','imported')])):
    raise ValueError('all profiled edges differ from prepared index')
for name,rows in facts.items():
    expected=[json.loads(s) for s in pq.read_table(prepared/'index'/(name+'.parquet'))['payload'].to_pylist()]
    if list(rows)!=expected:raise ValueError('full facts mismatch: '+name)
stats=pstats.Stats(profiler).stats
groups={}
for label,function in [('git_metadata_and_configs','git'),('batch_blob_read','read'),('byte_projection','import_events'),('resolver','resolve_event')]:
    groups[label]=sum(v[3] for (path,line,name),v in stats.items() if path.endswith('stage8_sources.py') and name==function)
groups['other_capture_checks_and_setup']=max(0,profiled_seconds-sum(groups.values()))
timer=time.perf_counter()
corpus=verify_corpus(PROJECT/'verification/stage8-connected-corpus-manifest-04.json',manifest['baseline_manifest_sha256'],
                     PROJECT/'verification/stage8-connected-corpus-evidence-04.json')
context_seconds=time.perf_counter()-timer
(folder/'index').mkdir()
timer=time.perf_counter();build(folder/'index',files,edges,facts,read(PROJECT/'verification/stage9-config.json')['limits'])
index_seconds=time.perf_counter()-timer
write(PROJECT/'verification/stage9-source-profile.json',{
    'schema':'stage9-source-cost-profile-v1','status':'FULL_DATA_MATCH',
    'manifest_sha256':sha256((PROJECT/'verification/stage9-manifest.json').read_bytes()).hexdigest(),
    'prepared_directory':str(prepared),'prepared_receipt_sha256':sha256((prepared/'prepare.json').read_bytes()).hexdigest(),
    'source_tools':facts['metadata'][0]['tools'],
    'profiler_code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
    'profiler_code_path':str(Path(__file__).resolve()),'plain_capture_seconds':plain_seconds,
    'instrumented_capture_seconds':profiled_seconds,'instrumented_phase_seconds':groups,
    'context_audit_seconds':context_seconds,'index_write_seconds':index_seconds,
    'nodes':len(files),'edges':len(edges),'all_files_edges_facts_match_prepared_and_uninstrumented':True,
    'note':'cProfile perturbs timings. Phase totals include instrumentation overhead; reader startup and hashing remain in other_capture_checks_and_setup. Formal acceptance used the separate uninstrumented supervised preparation. OS caches not controlled.'})
print(json.dumps(groups),flush=True)
