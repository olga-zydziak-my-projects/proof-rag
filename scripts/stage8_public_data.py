"""Bounded cached public-source reads for stage 8 reconnaissance.

Downloaded configuration is data. This module never evaluates it.
"""
from hashlib import sha256
import json
from pathlib import Path
import time
import urllib.error
import urllib.request


class PublicData:
    def __init__(self, folder, max_bytes=16_000_000, attempts=3):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.attempts = attempts

    def get(self, url):
        key = sha256(url.encode()).hexdigest()
        target = self.folder / (key + '.bin')
        if target.exists():
            return target.read_bytes()
        for attempt in range(self.attempts):
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'RepoProofLab-stage8-readonly'})
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = response.read(self.max_bytes + 1)
                if len(data) > self.max_bytes:
                    raise ValueError('public response exceeds configured byte limit')
                target.write_bytes(data)
                (self.folder / (key + '.json')).write_text(json.dumps({
                    'url': url, 'bytes': len(data), 'sha256': sha256(data).hexdigest()
                }, indent=2), encoding='utf-8')
                return data
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt + 1 == self.attempts:
                    raise
                delay = min(60, max(2 ** attempt, int(exc.headers.get('Retry-After', '0'))))
                time.sleep(delay)
            except (TimeoutError, urllib.error.URLError):
                if attempt + 1 == self.attempts:
                    raise
                time.sleep(2 ** attempt)

    def json(self, url):
        return json.loads(self.get(url))

    def github_tree(self, repository, commit, prefix=''):
        """Complete enumeration, recursively splitting GitHub truncated trees."""
        api = 'https://api.github.com/repos/' + repository + '/git/trees/'
        root = self.json(api + commit)
        for component in prefix.rstrip('/').split('/') if prefix else []:
            entry = next(e for e in root['tree'] if e['path'] == component and e['type'] == 'tree')
            root = self.json(api + entry['sha'])
        def walk(tree, base):
            recursive = self.json(api + tree['sha'] + '?recursive=1')
            if not recursive.get('truncated', False):
                return [{**entry, 'path': base + entry['path']} for entry in recursive['tree']]
            rows = []
            for entry in tree['tree']:
                path = base + entry['path']
                rows.append({**entry, 'path': path})
                if entry['type'] == 'tree':
                    rows.extend(walk(self.json(api + entry['sha']), path + '/'))
            return rows
        return walk(root, prefix.rstrip('/') + '/' if prefix else '')
