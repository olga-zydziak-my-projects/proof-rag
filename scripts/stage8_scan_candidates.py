"""Bounded download of .mojom candidate sources, explicitly NOT a joined corpus."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import base64
import json
from pathlib import Path
import sys
import time
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.source_bytes_v2 import certificate


def main():
    discovery, inventory, destination = map(Path, sys.argv[1:4])
    previous = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    destination.mkdir(parents=True, exist_ok=False)
    candidates = {r['repo_id']: r for r in json.loads((discovery/'discovery.json').read_bytes())['candidates_not_a_selected_corpus']}
    tasks = [(candidates[r['repo_id']], path) for r in json.loads((inventory/'inventory-summary.json').read_bytes())
             if r['repo_id'] in ('platform2', 'libchrome', 'libcamera') for path in r['mojom_paths']]
    def scan(task):
        repo, path = task
        url = repo['url']+'/+/'+repo['commit']+'/'+path+'?format=TEXT'
        row = {'repo_id': repo['repo_id'], 'commit': repo['commit'], 'path': path, 'url': url}
        try:
            cached = previous/repo['repo_id']/path if previous else None
            if cached is not None and cached.exists():
                data = cached.read_bytes()
            else:
                if previous:
                    time.sleep(0.5)
                with urllib.request.urlopen(url, timeout=30) as response:
                    raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ValueError('source download bound')
                data = base64.b64decode(raw)
            target = destination/repo['repo_id']/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            row.update(bytes=len(data), sha256=sha256(data).hexdigest())
            _, imports = certificate(data)
            row['imports'] = imports
        except Exception as exc:
            row['error'] = type(exc).__name__+': '+str(exc)
        return row
    with ThreadPoolExecutor(max_workers=1 if previous else 4) as pool:
        rows = list(pool.map(scan, tasks))
    report = {'origin': 'candidate_sources_not_selected_corpus', 'files': rows,
              'bytes': sum(r.get('bytes', 0) for r in rows),
              'complete_byte_projection': all('error' not in r for r in rows)}
    (destination/'scan.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('files',len(rows),'errors',sum('error' in r for r in rows),'bytes',report['bytes'])
    for rid in ('platform2', 'libchrome', 'libcamera'):
        literals = [i for r in rows if r['repo_id'] == rid for i in r.get('imports', [])]
        print(rid, 'imports',len(literals),'include/libcamera',sum(i.startswith('include/libcamera/') for i in literals))


if __name__ == '__main__':
    main()
