"""Manifest-anchored multi-repository byte projection. IO checks, not Lean proofs."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import numpy as np
import pyarrow as pa
from .source_bytes_v2 import certificate
from .stage5_v2 import canonical
from .extraction import read_json

SPEC = 'SourceBytes byte import projection v2 + contextual exact prefix resolver v8.1'


def git(folder, *args):
    return subprocess.check_output(['git', '--no-replace-objects', '-c', 'core.hooksPath=',
        '-c', 'safe.directory='+str(Path(folder).resolve()), '-C', str(folder), *args],
        stderr=subprocess.PIPE, timeout=60)


def path_ok(path):
    return (type(path) is str and bool(path) and not any(ord(c) < 32 for c in path)
            and '\\' not in path and ':' not in path and '"' not in path
            and all(p not in ('', '.', '..') for p in path.split('/')))


def identity(repo, commit, path):
    if (not re.fullmatch(r'[a-zA-Z0-9_-]+', repo) or not re.fullmatch(r'[0-9a-f]{40}', commit)
            or not path_ok(path)):
        raise ValueError('invalid file identity')
    return repo+'@'+commit+':'+path


def tool_identity():
    import duckdb, pyarrow, numpy
    base = Path(__file__).parent
    return {'spec': SPEC, 'duckdb': duckdb.__version__, 'pyarrow': pyarrow.__version__,
        'numpy': numpy.__version__, 'code': {name: sha256((base/name).read_bytes()).hexdigest()
        for name in ('stage8_sources.py', 'stage8_store.py', 'stage8_graph.py', 'source_bytes_v2.py', 'source_scanner_v2.py')}}


def resolve_event(importer, literal, rules, universe):
    """All matching rules count. No implicit own-repo fallback or longest match."""
    if not path_ok(literal):
        raise ValueError('noncanonical import')
    matches = [r for r in rules if r['from'] == list(importer[:2]) and literal.startswith(r['prefix'])]
    if len(matches) != 1:
        raise ValueError('missing or ambiguous resolver rule: '+literal)
    rule = matches[0]
    if rule['to'] is None:
        return None, rule['id']
    path = rule['target_prefix']+literal[len(rule['prefix']):]
    target = (*rule['to'], path)
    if not path_ok(path) or target not in universe:
        raise ValueError('required target repository/version/file absent: '+repr(target))
    return target, rule['id']


def capture(manifest_path, expected_sha, locations):
    raw = Path(manifest_path).read_bytes()
    if sha256(raw).hexdigest() != expected_sha:
        raise ValueError('manifest differs from independent caller anchor')
    m = read_json(manifest_path)
    if set(m) != {'schema', 'origin', 'repositories', 'rules', 'configs'} or m['schema'] != 'stage8-corpus-v1':
        raise ValueError('manifest schema')
    if m['origin'] not in ('real', 'synthetic-fixture') or not m['repositories']:
        raise ValueError('manifest origin/universe')
    universe, blobs, repositories = {}, {}, []
    versions = set()
    for repo in m['repositories']:
        if set(repo) != {'repo_id', 'commit', 'tree', 'url', 'prefixes', 'files'}:
            raise ValueError('repository schema')
        rid, rev = repo['repo_id'], repo['commit']
        key = (rid, rev)
        if key in versions:
            raise ValueError('duplicate repository version')
        versions.add(key)
        if key not in locations:
            raise ValueError('missing repository location')
        folder = Path(locations[key])
        actual_tree = git(folder, 'rev-parse', rev+'^{tree}').decode().strip()
        if actual_tree != repo['tree']:
            raise ValueError('commit/tree substitution')
        tree = git(folder, 'ls-tree', '-rz', '--full-tree', rev)
        selected = {}
        for row in tree.split(b'\0'):
            if not row:
                continue
            header, filename = row.split(b'\t', 1)
            mode, kind, oid = header.decode().split()
            path = filename.decode('utf-8')
            if any(path.startswith(p) for p in repo['prefixes']) and path.endswith('.mojom'):
                if mode not in ('100644', '100755') or kind != 'blob' or not path_ok(path):
                    raise ValueError('unsupported source entry')
                selected[path] = oid
        declared = repo['files']
        if (len({f['path'] for f in declared}) != len(declared)
                or {f['path']: f['blob'] for f in declared} != selected):
            raise ValueError('manifest does not cover complete selected Git universe')
        for f in declared:
            if set(f) != {'path', 'blob', 'sha256'}:
                raise ValueError('file schema')
            name = identity(rid, rev, f['path'])
            data = git(folder, 'cat-file', 'blob', f['blob'])
            if sha256(data).hexdigest() != f['sha256']:
                raise ValueError('source bytes changed')
            keyfile = (rid, rev, f['path'])
            universe[keyfile] = name
            blobs[keyfile] = data
        repositories.append(repo)
    if not universe:
        raise ValueError('empty source universe')
    configs = []
    for config in m['configs']:
        if set(config) != {'id', 'repo_id', 'commit', 'path', 'blob', 'sha256'}:
            raise ValueError('config schema')
        folder = locations[(config['repo_id'], config['commit'])]
        oid = git(folder, 'rev-parse', config['commit']+':'+config['path']).decode().strip()
        data = git(folder, 'cat-file', 'blob', oid)
        if oid != config['blob'] or sha256(data).hexdigest() != config['sha256']:
            raise ValueError('resolver configuration changed')
        configs.append(config)
    config_ids = {c['id'] for c in configs}
    if len(config_ids) != len(configs):
        raise ValueError('duplicate config identity')
    rule_ids = set()
    for rule in m['rules']:
        if (set(rule) != {'id', 'from', 'prefix', 'to', 'target_prefix', 'evidence'}
                or rule['id'] in rule_ids or rule['evidence'] not in config_ids
                or tuple(rule['from']) not in versions
                or (rule['to'] is not None and tuple(rule['to']) not in versions)
                or not isinstance(rule['prefix'], str) or not isinstance(rule['target_prefix'], str)):
            raise ValueError('resolver rule schema/version/evidence')
        for prefix in (rule['prefix'], rule['target_prefix']):
            if prefix and (not prefix.endswith('/') or not path_ok(prefix[:-1])):
                raise ValueError('noncanonical prefix')
        rule_ids.add(rule['id'])
    keys = sorted(universe)
    ids = {key: i for i, key in enumerate(keys)}
    files = pa.Table.from_pylist([{'id': i, 'repo_id': k[0], 'commit': k[1], 'path': k[2],
            'blob': next(f['blob'] for r in repositories if (r['repo_id'], r['commit']) == k[:2]
                         for f in r['files'] if f['path'] == k[2]),
            'sha256': sha256(blobs[k]).hexdigest()} for i, k in enumerate(keys)])
    events, resolutions, external, edges = [], [], [], set()
    for key in keys:
        _, emitted = certificate(blobs[key])
        for ordinal, literal in enumerate(emitted):
            event = {'importer': ids[key], 'ordinal': ordinal, 'literal': literal,
                     'source_sha256': sha256(blobs[key]).hexdigest()}
            events.append(event)
            target, rule = resolve_event(key, literal, m['rules'], universe)
            row = {**event, 'rule': rule, 'target': ids[target] if target else None,
                   'status': 'resolved' if target else 'external'}
            resolutions.append(row)
            if target:
                edges.add((ids[key], ids[target]))
            else:
                external.append(row)
    facts = {'repositories': repositories, 'events': events, 'resolutions': resolutions,
             'external': external, 'configs': configs,
             'metadata': [{'manifest_sha256': expected_sha, 'manifest': m, 'tools': tool_identity(),
                           'source_bytes': sum(map(len, blobs.values()))}]}
    return files, np.array(sorted(edges), dtype=np.int64).reshape((-1, 2)), facts
