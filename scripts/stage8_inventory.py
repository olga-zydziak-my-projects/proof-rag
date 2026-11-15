"""Read complete Gitiles inventories at the already recorded candidate commits."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import sys
import urllib.request


def main():
    source, output = map(Path, sys.argv[1:3])
    output.mkdir(parents=True, exist_ok=False)
    candidates = json.loads((source/'discovery.json').read_bytes())['candidates_not_a_selected_corpus']
    def fetch(entry):
        if 'commit' not in entry:
            return entry
        url = entry['url']+'/+/'+entry['commit']+'/?format=JSON&recursive=1'
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read(8_000_001)
            if len(data) > 8_000_000:
                raise ValueError('inventory bound')
            (output/(entry['repo_id']+'.json')).write_bytes(data)
            rows = json.loads(data.split(b'\n', 1)[1])['entries']
            return {'repo_id': entry['repo_id'], 'commit': entry['commit'], 'tree': entry['tree'],
                'url': url, 'sha256': sha256(data).hexdigest(), 'entries': len(rows),
                'mojom_paths': [r['name'] for r in rows if r['name'].endswith('.mojom')],
                'note': 'candidate versions are NOT a compatible selected corpus'}
        except Exception as exc:
            return {'repo_id': entry['repo_id'], 'url': url, 'error': str(exc)}
    # Metadata only: no build or extracted code execution.
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch, candidates))
    (output/'inventory-summary.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    for row in rows:
        print(row['repo_id'], row.get('entries'), len(row.get('mojom_paths', [])), row.get('error', ''))


if __name__ == '__main__':
    main()
