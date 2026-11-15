"""Bounded download of .mojom candidate sources, explicitly NOT a joined corpus."""
from concurrent.futures import ThreadPoolExecutor
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('discovery', type=Path)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('previous', nargs='?', type=Path)
    parser.add_argument('--repo', action='append', help='restrict repo IDs, defaults to every inventoried candidate')
    args = parser.parse_args()
    discovery, inventory, destination, previous = args.discovery, args.inventory, args.destination, args.previous
    destination.mkdir(parents=True, exist_ok=False)
    candidates = {r['repo_id']: r for r in json.loads((discovery/'discovery.json').read_bytes())['candidates_not_a_selected_corpus']}
    tasks = [(candidates[r['repo_id']], path) for r in json.loads((inventory/'inventory-summary.json').read_bytes())
             if (not args.repo or r['repo_id'] in args.repo) for path in r.get('mojom_paths', [])]
    def scan(task):
        repo, path = task
        github = repo['url'].startswith('https://github.com/')
        url = ('https://raw.githubusercontent.com/' + repo['url'].removeprefix('https://github.com/').removesuffix('.git')
               + '/' + repo['commit'] + '/' + path) if github else repo['url']+'/+/'+repo['commit']+'/'+path+'?format=TEXT'
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
                data = raw if github else base64.b64decode(raw)
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
    for rid in sorted({row['repo_id'] for row in rows}):
        literals = [i for r in rows if r['repo_id'] == rid for i in r.get('imports', [])]
        print(rid, 'imports',len(literals))


if __name__ == '__main__':
    main()
