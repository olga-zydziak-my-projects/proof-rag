import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.source_bytes_v2 import certificate,piece
from repo_proof.corpus import read_blob

r=json.loads(Path('verification/stage5-source-receipt.json').read_bytes())
cfg=json.loads(Path('local/corpus.json').read_bytes())
e=next(x for x in r['selected_files'] if x['bytes']>3000)
cs,es=certificate(read_blob(Path(cfg['data_dir']),e['git_blob_oid']))
cs=cs[:12]
lines=['import SourceByteScanner','import ProofTiming','open RepoProof.SourceBytes',
       'set_option maxHeartbeats 0','set_option maxRecDepth 100000','namespace SmokeBytes']
for i,p in enumerate(cs): lines.append(f'def p{i} : Piece := '+piece(p))
lines+=['def pieces := ['+', '.join('p'+str(i) for i in range(len(cs)))+']',
        'theorem checked_all : checked initial pieces = true := by']
for i in range(len(cs)): lines+=['  apply checked_cons','  · timed_kernel_decide','  · timed_kernel_decide']
lines+=['  rfl','end SmokeBytes','#print axioms SmokeBytes.checked_all']
Path('local/stage5-v2/ByteSmoke.lean').write_text('\n'.join(lines)+'\n',encoding='utf-8')
