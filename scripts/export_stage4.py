"""Export the unchanged Chromium instance with independently checked edge hints."""
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from repo_proof.fast_export import render_fast
from repo_proof.lean_export import load_json

start=time.perf_counter()
artifacts=Path('local/stage2')
source=render_fast(load_json(artifacts/'graph.json'),'mojo/public/mojom/base/time.mojom',
                   load_json(artifacts/'certificate.json'))
Path('formal/ChromiumFast.lean').write_text(source,encoding='utf-8')
print({'export_seconds':time.perf_counter()-start})
