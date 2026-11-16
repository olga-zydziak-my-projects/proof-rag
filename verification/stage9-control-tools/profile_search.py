"""Pure BFS and certificate timings, separately from verified CLI latency."""
from hashlib import sha256
from pathlib import Path
import statistics
import sys
import time
from types import SimpleNamespace
PROJECT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(PROJECT/'src'),str(PROJECT/'scripts'),str(PROJECT/'local/stage8-deps')]
from stage9 import read,write,validate_prepared,answer_rows
from repo_proof.stage8_graph import reverse_index,traverse,search,reference,check_certificate

folder=Path(sys.argv[1]).resolve(); folder.mkdir(parents=True,exist_ok=False)
prepared=Path(sys.argv[2]).resolve(); measured=Path(sys.argv[3]).resolve(); lean=Path(sys.argv[4]).resolve()
trusted=read(PROJECT/'verification/stage9-preparation.json')['receipt_sha256']
args=SimpleNamespace(prepared_dir=prepared,prepared_sha256=trusted,manifest=PROJECT/'verification/stage9-manifest.json',
    manifest_sha256=read(PROJECT/'verification/stage9-manifest-anchor.json')['sha256'],
    locations=PROJECT/'local/stage9/acquire-03/data/locations.json',lean=lean,config=PROJECT/'verification/stage9-config.json')
receipt,values=validate_prepared(args,folder)
manifest,files,edges,facts,rows,sources,locations,corpus=values
start=time.perf_counter(); incoming=reverse_index(len(rows),edges); csr_seconds=time.perf_counter()-start
roots=read(PROJECT/'verification/stage9-queries.json')['roots']; summaries=[]
for number,root in enumerate(roots,1):
    public_path=measured/f'q{number}-r1/work/answer.json'
    public=read(public_path)
    if not public['formally_verified'] or public['proof']['preparation_receipt_sha256']!=trusted or public['root']!=answer_rows(rows,[root['id']])[0]:
        raise ValueError('benchmark requires actually accepted public answer')
    oracle=reference(len(rows),edges,root['id'])
    samples=[]; cert_samples=[]; check_samples=[]
    for repeat in range(3):
        start=time.perf_counter(); ids=traverse(len(rows),incoming,root['id']); samples.append(time.perf_counter()-start)
        if ids.tolist()!=oracle.tolist() or answer_rows(rows,ids)!=public['results']:
            raise ValueError('complete pure BFS result differs from DFS or accepted answer')
        start=time.perf_counter(); ids,parent,rank=search(len(rows),incoming,root['id']); cert_samples.append(time.perf_counter()-start)
        start=time.perf_counter(); check_certificate(len(rows),edges,root['id'],ids,parent[ids],rank[ids]); check_samples.append(time.perf_counter()-start)
        if answer_rows(rows,ids)!=public['results']:raise ValueError('full certificate answer differs')
    summary=lambda ss:{'samples':ss,'median':statistics.median(ss),'range':[min(ss),max(ss)]}
    summaries.append({'root':root,'accepted_answer_path':str(public_path),'accepted_answer_sha256':sha256(public_path.read_bytes()).hexdigest(),
                      'pure_search_seconds':summary(samples),'search_and_certificate_seconds':summary(cert_samples),
                      'certificate_check_seconds':summary(check_samples),'complete_reference_and_public_answer_match':True})
write(PROJECT/'verification/stage9-search-profile.json',{'schema':'stage9-pure-search-profile-v1','status':'SEARCH_PROFILE_PASS',
    'verification_level':'GRAPH_RESULT_COMPARISON_ONLY; formal proofs are the separate 18 public CLI runs',
    'manifest_sha256':args.manifest_sha256,'prepared_receipt_sha256':trusted,'measured_directory':str(measured),'nodes':len(rows),'edges':len(edges),
    'reverse_index_build_seconds':csr_seconds,'query_roots_sha256':sha256((PROJECT/'verification/stage9-queries.json').read_bytes()).hexdigest(),
    'profiler_code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'profiler_code_path':str(Path(__file__).resolve()),
    'summaries':summaries,'os_file_cache_controlled':False})
print('SEARCH_PROFILE_PASS',flush=True)
