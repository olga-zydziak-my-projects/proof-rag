"""Materialize pinned Git objects and deterministic import closure without checkout.

Scope is the complete two declared source directories plus all transitive imports.
Queries are chosen only after this script writes its frozen manifest.
"""
import argparse
import base64
from hashlib import sha1, sha256
import json
from pathlib import Path
import subprocess
import sys

from stage8_public_data import PublicData

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from repo_proof.source_bytes_v2 import certificate


def git(folder, *args, data=None):
    return subprocess.check_output(['git', '-c', 'core.hooksPath=', '-C', str(folder), *args],
                                   input=data, stderr=subprocess.PIPE, timeout=120)


class Objects:
    def __init__(self, folder, name, meta, public):
        self.folder = folder / ('git-' + name)
        self.name, self.meta, self.public = name, meta, public
        self.trees = {}
        if not self.folder.exists():
            subprocess.run(['git', '-c', 'core.hooksPath=', 'init', '--bare', str(self.folder)], check=True)
        try:
            git(self.folder, 'cat-file', '-e', meta['commit'] + '^{commit}')
        except subprocess.CalledProcessError:
            git(self.folder, 'fetch', '--no-tags', '--depth=1', '--filter=tree:0',
                'https://github.com/' + meta['repository'] + '.git', meta['commit'])

    def tree(self, path=''):
        if path in self.trees:
            return self.trees[path]
        if self.name == 'chromium':
            url = 'https://chromium.googlesource.com/chromium/src/+/' + self.meta['commit'] + '/' + path + '?format=JSON'
            obj = json.loads(self.public.get(url).split(b'\n', 1)[1])
            entries = [{'path': e['name'], 'sha': e['id'], 'mode': format(e['mode'], 'o'),
                        'type': e['type']} for e in obj['entries']]
            expected = obj['id']
        else:
            if not path:
                oid = self.meta['tree']
            else:
                parent, _, basename = path.rpartition('/')
                oid = next(e['sha'] for e in self.tree(parent) if e['path'] == basename)
            obj = self.public.json('https://api.github.com/repos/' + self.meta['repository'] + '/git/trees/' + oid)
            entries, expected = obj['tree'], obj['sha']
        # Git tree sort treats directory names as if terminated by '/'.
        entries.sort(key=lambda e: (e['path'] + ('/' if e['type'] == 'tree' else '')).encode())
        raw = b''.join(e['mode'].lstrip('0').encode() + b' ' + e['path'].encode() + b'\0' + bytes.fromhex(e['sha']) for e in entries)
        actual = git(self.folder, 'hash-object', '-w', '-t', 'tree', '--stdin', data=raw).decode().strip()
        if actual != expected:
            raise ValueError('downloaded tree identity mismatch: ' + path)
        self.trees[path] = entries
        if path:
            self.tree(path.rpartition('/')[0])
        return entries

    def blob(self, path):
        parent, _, basename = path.rpartition('/')
        entry = next(e for e in self.tree(parent) if e['path'] == basename)
        if entry['type'] != 'blob' or entry['mode'].lstrip('0') not in ('100644', '100755'):
            raise ValueError('source is not a regular Git blob')
        url = 'https://raw.githubusercontent.com/' + self.meta['repository'] + '/' + self.meta['commit'] + '/' + path
        raw = self.public.get(url)
        actual = git(self.folder, 'hash-object', '-w', '--stdin', data=raw).decode().strip()
        if actual != entry['sha']:
            raise ValueError('downloaded blob identity mismatch: ' + path)
        return raw, actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recon')
    args = parser.parse_args()
    folder = Path(args.recon).resolve()
    report = json.loads((folder / 'recon.json').read_bytes())
    public = PublicData(folder / 'http-cache')
    objects = {name: Objects(folder, name, meta, public) for name, meta in report['projects'].items()}
    queue = [(name, entry['path']) for name, meta in report['projects'].items()
             for entry in meta.get('source_scope_inventory', [])
             if entry['type'] == 'blob' and entry['path'].endswith('.mojom')]
    files, events, source_bytes = {}, [], 0
    index = 0
    while index < len(queue):
        name, path = queue[index]
        index += 1
        if (name, path) in files:
            continue
        raw, blob = objects[name].blob(path)
        source_bytes += len(raw)
        files[name, path] = {'path': path, 'blob': blob, 'sha256': sha256(raw).hexdigest()}
        _, imports = certificate(raw)
        for ordinal, literal in enumerate(imports):
            if literal.startswith('brave/'):
                target = ('brave', literal[len('brave/'):])
            elif literal.startswith('electron/'):
                target = ('electron', literal[len('electron/'):])
            else:
                target = ('chromium', literal)
            if target not in files:
                queue.append(target)
            events.append({'repo': name, 'path': path, 'ordinal': ordinal, 'literal': literal,
                           'target_repo': target[0], 'target_path': target[1]})
        print(index, len(queue), name, path, flush=True)
    configs = []
    for name, paths in [('electron', ['DEPS', 'BUILD.gn', 'shell/common/BUILD.gn', 'patches/config.json', 'script/lib/patches.py']),
                        ('brave', ['package.json', 'build/commands/lib/config.js',
                                   'build/commands/scripts/sync.js', 'build/commands/lib/applyPatches.js',
                                   'build/commands/lib/gitPatcher.js', 'build/commands/lib/syncUtils.js',
                                   'build/commands/lib/util.js',
                                   'components/ai_chat/core/common/mojom/BUILD.gn']),
                        ('chromium', ['chrome/VERSION'])]:
        for path in paths:
            raw, blob = objects[name].blob(path)
            configs.append({'id': name + '-' + path.replace('/', '-'), 'repo_id': name,
                            'commit': report['projects'][name]['commit'], 'path': path,
                            'blob': blob, 'sha256': sha256(raw).hexdigest()})
    repositories = []
    for name, meta in report['projects'].items():
        selected = [value for (repo, _), value in sorted(files.items()) if repo == name]
        scope = meta.get('source_scope_prefix')
        prefixes = ([scope] if scope else []) + [entry['path'] for entry in selected
                                                  if not scope or not entry['path'].startswith(scope)]
        repositories.append({'repo_id': name, 'commit': meta['commit'], 'tree': meta['tree'],
                             'url': 'https://github.com/' + meta['repository'], 'prefixes': prefixes,
                             'files': selected})
    rules = []
    for repo in repositories:
        name = repo['repo_id']
        prefixes = sorted({event['literal'].split('/')[0] + '/' for event in events if event['repo'] == name})
        for prefix in prefixes:
            target = 'brave' if prefix == 'brave/' else 'electron' if prefix == 'electron/' else 'chromium'
            rules.append({'id': name + '-' + prefix[:-1], 'from': [name, repo['commit']], 'prefix': prefix,
                          'to': [target, report['projects'][target]['commit']], 'target_prefix': '',
                          'evidence': 'brave-package.json' if name == 'brave' else 'electron-DEPS'})
            if target == 'chromium':
                rules[-1]['target_prefix'] = prefix
    manifest = {'schema': 'stage8-corpus-v1', 'origin': 'real', 'repositories': repositories,
                'rules': rules, 'configs': configs}
    (folder / 'candidate-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (folder / 'locations.json').write_text(json.dumps([
        {'repo_id': name, 'commit': obj.meta['commit'], 'directory': str(obj.folder)} for name, obj in objects.items()
    ], indent=2), encoding='utf-8')
    (folder / 'scope-freeze.json').write_text(json.dumps({
        'selection': 'complete declared Electron GN target source inventories and Brave components/ai_chat/core/common/mojom/ directory, plus least import closure',
        'queries_selected': False, 'files': len(files), 'source_bytes': source_bytes,
        'events': events, 'manifest_sha256': sha256((folder / 'candidate-manifest.json').read_bytes()).hexdigest(),
        'status': 'UNACCEPTED_PENDING_PATCH_CONTEXT_AUDIT'
    }, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
