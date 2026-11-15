"""Explicit SYNTHETIC source fixture: three new local Git repositories."""
from hashlib import sha256
from pathlib import Path
import subprocess
from .stage5_v2 import canonical


def create(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    repositories, locations, configs, rules = [], [], [], []
    definitions = {
        'a': {'local/a.mojom': b'module a; import "b/shared.mojom"; struct A {};\n',
              'local/isolated.mojom': b'module a; struct Isolated {};\n'},
        'b': {'local/shared.mojom': b'module b; import "c/shared.mojom"; struct B {};\n'},
        'c': {'local/shared.mojom': b'module c; import "a/a.mojom"; import "external/no.mojom"; struct C {};\n'}}
    for rid, sources in definitions.items():
        directory = folder/rid
        directory.mkdir()
        def git(*args):
            return subprocess.check_output(['git', '-c', 'core.hooksPath=', '-c', 'user.name=Stage8 fixture',
                '-c', 'user.email=fixture@example.invalid', '-C', str(directory), *args], stderr=subprocess.PIPE).decode().strip()
        git('init', '--quiet')
        for path, data in sources.items():
            target = directory/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (directory/'resolver.json').write_bytes(b'{"fixture":true,"aliases":["a/","b/","c/","external/"]}\n')
        git('add', '.')
        git('commit', '-qm', 'Synthetic Stage8 fixture; not a real ecosystem corpus')
        commit, tree = git('rev-parse', 'HEAD'), git('rev-parse', 'HEAD^{tree}')
        files = [{'path': path, 'blob': git('rev-parse', commit+':'+path),
                  'sha256': sha256(data).hexdigest()} for path, data in sorted(sources.items())]
        repositories.append({'repo_id': rid, 'commit': commit, 'tree': tree,
            'url': 'synthetic-fixture://'+rid, 'prefixes': ['local/'], 'files': files})
        locations.append({'repo_id': rid, 'commit': commit, 'directory': str(directory.resolve())})
        configs.append({'id': rid+'-config', 'repo_id': rid, 'commit': commit, 'path': 'resolver.json',
            'blob': git('rev-parse', commit+':resolver.json'),
            'sha256': sha256((directory/'resolver.json').read_bytes()).hexdigest()})
    versions = {r['repo_id']: r['commit'] for r in repositories}
    for rid in definitions:
        for target in definitions:
            rules.append({'id': rid+'-'+target, 'from': [rid, versions[rid]], 'prefix': target+'/',
                'to': [target, versions[target]], 'target_prefix': 'local/', 'evidence': rid+'-config'})
        rules.append({'id': rid+'-external', 'from': [rid, versions[rid]], 'prefix': 'external/',
                      'to': None, 'target_prefix': '', 'evidence': rid+'-config'})
    manifest = {'schema': 'stage8-corpus-v1', 'origin': 'synthetic-fixture',
                'repositories': repositories, 'rules': rules, 'configs': configs}
    raw = canonical(manifest)
    (folder/'manifest.json').write_bytes(raw)
    (folder/'locations.json').write_bytes(canonical(locations))
    return manifest, sha256(raw).hexdigest(), {(r['repo_id'], r['commit']): r['directory'] for r in locations}
