"""Read complete Gitiles inventories at the already recorded candidate commits."""
from concurrent.futures import ThreadPoolExecutor
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import urllib.request
import subprocess
from stage8_public_data import PublicData


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--repo', action='append', help='restrict candidate IDs')
    parser.add_argument('--local', action='append', default=[], metavar='REPO_ID=GIT_DIRECTORY',
                        help='enumerate complete pinned local Git trees without HTTP limits')
    args = parser.parse_args()
    source, output = args.source, args.output
    output.mkdir(parents=True, exist_ok=False)
    candidates = json.loads((source/'discovery.json').read_bytes())['candidates_not_a_selected_corpus']
    candidates = [entry for entry in candidates if not args.repo or entry['repo_id'] in args.repo]
    local = dict(value.split('=', 1) for value in args.local)
    public = PublicData(output / 'http-cache', max_bytes=8_000_000)
    def gitiles(entry, prefix=''):
        base = entry['url']+'/+/'+entry['commit']+'/' + prefix
        try:
            data = public.get(base + '?format=JSON&recursive=1')
            return json.loads(data.split(b'\n', 1)[1])['entries']
        except ValueError as exc:
            if 'byte limit' not in str(exc):
                raise
        # A response cap requires complete subtree enumeration, not rejection
        # of the repository or a claim that there are no imports.
        data = public.get(base + '?format=JSON')
        rows = []
        for item in json.loads(data.split(b'\n', 1)[1])['entries']:
            if item['type'] == 'tree':
                children = gitiles(entry, prefix + item['name'] + '/')
                rows.extend({**child, 'name': item['name'] + '/' + child['name']} for child in children)
            else:
                rows.append(item)
        return rows
    def fetch(entry):
        if 'commit' not in entry:
            return entry
        url = entry['url']+'/+/'+entry['commit']+'/?format=JSON&recursive=1'
        try:
            if entry['repo_id'] in local:
                command = ['git', '--no-replace-objects', '-c', 'core.hooksPath=', '-C', local[entry['repo_id']]]
                tree = subprocess.check_output(command + ['rev-parse', entry['commit']+'^{tree}'], timeout=60).decode().strip()
                if tree != entry['tree']:
                    raise ValueError('local pinned tree differs from discovery')
                raw = subprocess.check_output(command + ['ls-tree', '-rz', '--full-tree', entry['commit']], timeout=120)
                rows = []
                for item in raw.split(b'\0'):
                    if item:
                        header, path = item.split(b'\t', 1)
                        mode, kind, oid = header.decode().split()
                        rows.append({'name': path.decode(), 'type': kind, 'mode': mode, 'id': oid})
                url = 'local-git-object-enumeration'
            elif entry['url'].startswith('https://github.com/'):
                repository = entry['url'].removeprefix('https://github.com/').removesuffix('.git')
                rows = [{**item, 'name': item['path'], 'id': item['sha']} for item in public.github_tree(repository, entry['commit'])]
                url = 'https://api.github.com/repos/' + repository + '/git/trees/' + entry['commit']
            else:
                rows = gitiles(entry)
            data = json.dumps({'entries': rows}, sort_keys=True).encode()
            (output/(entry['repo_id']+'.json')).write_bytes(data)
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
