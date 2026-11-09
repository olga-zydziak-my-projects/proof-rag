import sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.lean_export import load_json, render
start=time.perf_counter()
p=Path('local/stage2')
s=render(load_json(p/'graph.json'),'mojo/public/mojom/base/time.mojom',load_json(p/'certificate.json'))
Path('formal/Chromium.lean').write_text(s,encoding='utf-8')
print({'export_seconds':time.perf_counter()-start})
