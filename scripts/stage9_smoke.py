"""Small actual kernel integration; never evidence for the real corpus size."""
import sys
from pathlib import Path
import shutil
import time
import numpy as np
from stage9 import DEPENDENCIES,compile_module,write,PROJECT
from stage9_export import export_sources,export_query
from repo_proof.stage8_graph import reverse_index,search

folder=Path(sys.argv[1]).resolve(); lean=Path(sys.argv[2]).resolve()
folder.mkdir(parents=True,exist_ok=False); (folder/'lean').mkdir()
names=[('a@upstream','1'*40,'a.mojom'),('b@default','2'*40,'b.mojom'),('c@default','3'*40,'c.mojom')]
sources=[b'module a;',b'module b; import "a/a.mojom";',b'module c; import "a/a.mojom";']
rules=[{'id':str(i),'from':list(names[i][:2]),'prefix':'a/','to':list(names[0][:2]),'target_prefix':'','evidence':'config'} for i in (1,2)]
edges=np.array([[1,0],[2,0]],dtype=np.int64)
export_sources(folder/'lean',names,sources,rules,edges)
ids,p,r=search(3,reverse_index(3,edges),0)
export_query(folder/'lean',3,edges,0,ids,p[ids],r[ids])
for name in DEPENDENCIES:shutil.copyfile(PROJECT/'formal'/(name+'.lean'),folder/'lean'/(name+'.lean'))
report={}
for name in (*DEPENDENCIES,'SourceNames','CorpusGraph','SourceGroup0000','SourceCorpus','QueryGraph','QueryAnswer'):
    report[name]=compile_module(folder,name,lean,[folder/'lean'])
    write(folder/'smoke.json',report)
    print(name,report[name]['seconds'],flush=True)
