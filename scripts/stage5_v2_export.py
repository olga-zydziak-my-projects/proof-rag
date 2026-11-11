import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.stage5_v2 import capture,canonical,snapshot_payload,export_names,export_groups

p=argparse.ArgumentParser()
p.add_argument('--run-dir',required=True)
a=p.parse_args()
out=Path(a.run_dir); out.mkdir(parents=True,exist_ok=False)
c=capture(Path.cwd())
(out/'snapshot.json').write_bytes(canonical(snapshot_payload(c)))
(out/'graph.json').write_bytes(canonical(c.graph))
(out/'certificate.json').write_bytes(canonical(c.certificate))
(out/'lean').mkdir()
export_names(c,out/'lean')
inventory=export_groups(c,out/'lean')
(out/'source-module-inventory.json').write_bytes(canonical(inventory))
print(json.dumps({'files':len(c.blobs),'source_bytes':sum(len(b.data) for b in c.blobs),
                  'pieces':sum(x['pieces'] for x in inventory),'modules':len(set(x['module'] for x in inventory))}))
