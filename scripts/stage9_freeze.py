"""Freeze acquired sources/contexts, audit all rows, then select six roots."""
import argparse
from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from stage9 import PROJECT,read,write,inputs,CONTEXTS,identities,contextual_rules,source_bytes
from stage9_recon import GENERATED
from repo_proof.stage8_graph import reference
from repo_proof.stage8_sources import git,blob_reader
from repo_proof.stage8_lean import render_source
from stage9_export import audit_source

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--acquisition',type=Path,required=True)
p.add_argument('--run-dir',type=Path,required=True)
a=p.parse_args()
folder=a.run_dir.resolve(); folder.mkdir(parents=True,exist_ok=False)
sources=read(a.acquisition/'manifest.json')
# Retain acquisition reports. The frozen manifest refines generated boundaries
# to dedicated full-literal rules, with their own pinned GN evidence.
rules=[]
for rule in sources['rules']:
    if rule['to'] is not None:
        rules.append(rule); continue
    for literal in GENERATED:
        if literal.startswith(rule['prefix']):
            rules.append({**rule,'id':rule['from'][0]+'-'+literal,'prefix':literal,
                'evidence':'chromium-'+literal.rpartition('/')[0].replace('/','-')+'-BUILD.gn'})
sources['rules']=rules
baseline=PROJECT/'verification/stage8-connected-corpus-manifest-04.json'
manifest={'schema':'stage9-context-corpus-v1','sources':sources,'contexts':CONTEXTS,
          'scope_policy':read(PROJECT/'verification/stage9-scope-policy.json'),
          'baseline_manifest_sha256':sha256(baseline.read_bytes()).hexdigest()}
target=PROJECT/'verification/stage9-manifest.json'
write(target,manifest)
anchor=sha256(target.read_bytes()).hexdigest()
write(PROJECT/'verification/stage9-manifest-anchor.json',{'path':'verification/stage9-manifest.json','sha256':anchor,
    'selection_before_acquisition':read(a.acquisition/'selection-before-acquisition.json'),'queries_selected':False})
args=SimpleNamespace(manifest=target,manifest_sha256=anchor,locations=a.acquisition/'locations.json')
started=time.perf_counter()
m,files,edges,facts,rows,raw,locations,corpus=inputs(args,folder)
phases={'full_source_audit_and_extraction':time.perf_counter()-started}
records=[]
for i,row in enumerate(rows):
    answer=reference(len(rows),edges,i).tolist()
    records.append({'id':i,'size':len(answer),'projects':len({rows[j]['repo_id'] for j in answer}),
                    'identity':(row['repo_id'],row['commit'],row['path'])})
cross=sorted((r for r in records if r['projects']>1),key=lambda r:(-r['projects'],-r['size'],r['identity']))
if len(cross)<3 or cross[0]['projects']!=3:raise ValueError('required connected answers unavailable')
selected=[cross[i] for i in (0,len(cross)//2,len(cross)-1)]
ordered=sorted(records,key=lambda r:(r['size'],r['identity']))
for position in (0,len(ordered)//2,len(ordered)-1):
    while ordered[position%len(ordered)]['id'] in {r['id'] for r in selected}:position+=1
    selected.append(ordered[position%len(ordered)])
roots=[{**r,'project':r['identity'][0],'commit':r['identity'][1],'path':r['identity'][2],
        'context':CONTEXTS[r['identity'][0]]} for r in selected]
write(PROJECT/'verification/stage9-queries.json',{'manifest_sha256':anchor,'rule':m['scope_policy']['query_selection'],
    'frozen_before_measurements':True,'roots':roots})
# Measure the actual Stage8 IO/export costs over this extended corpus without
# performing an unbounded historical all-in-one kernel compilation.
started=time.perf_counter()
per_file=[git(locations[r['repo_id'],r['commit']],'cat-file','blob',r['blob']) for r in rows]
phases['stage8_per_file_git_reads']=time.perf_counter()-started
started=time.perf_counter(); batch=source_bytes(rows,locations)
phases['stage9_batch_git_reads']=time.perf_counter()-started
if per_file!=batch or batch!=raw:raise ValueError('batch source bytes differ')
from repo_proof.stage8_graph import search,reverse_index
ids,parent,rank=search(len(rows),reverse_index(len(rows),edges),roots[0]['id'])
names=identities(rows,m['contexts']); rules=contextual_rules(m['sources']['rules'],m['contexts'])
started=time.perf_counter(); text=render_source(names,raw,rules,edges,roots[0]['id'],ids,parent[ids],rank[ids])
phases['stage8_monolithic_source_export']=time.perf_counter()-started
started=time.perf_counter(); audit_source(text,names,raw,rules,edges,ids)
phases['stage8_complete_source_export_audit']=time.perf_counter()-started
within=sum(rows[int(a)]['repo_id']==rows[int(b)]['repo_id'] for a,b in edges)
report={'status':'CORPUS_IO_AUDIT_PASS','manifest_sha256':anchor,'projects':len({r['repo_id'] for r in rows}),
    'pinned_versions':len(m['sources']['repositories']),'real_distinct_files':len({(r['repo_id'],r['commit'],r['path']) for r in rows}),
    'files_by_project':dict(Counter(r['repo_id'] for r in rows)),'context_records':len(rows),'additional_context_variants':0,
    'unique_contents':len({sha256(data).hexdigest() for data in raw}),'source_bytes':sum(map(len,raw)),
    'edges':len(edges),'within_project_edges':within,'cross_project_edges':len(edges)-within,
    'external_events':list(facts['external']),'corpus_audit':corpus,'phases_seconds':phases,
    'monolithic_export_bytes':len(text.encode()),'all_sources_byte_comparison':True,'query_selection':roots}
write(PROJECT/'verification/stage9-corpus.json',report)
print(report['real_distinct_files'],report['source_bytes'],report['edges'],phases,flush=True)
