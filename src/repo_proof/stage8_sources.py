"""Manifest-anchored multi-repository byte projection. IO checks, not Lean proofs."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from contextlib import contextmanager
import numpy as np
import pyarrow as pa
from .source_bytes_v2 import utf8_step
from .source_scanner_v2 import initial, step, finish
from .stage5_v2 import canonical
from .extraction import read_json
from .stage8_rows import FactRows

SPEC = 'SourceBytes byte import projection v2 + contextual exact prefix resolver v8.2'


def import_events(data):
    """Run the byte specification without allocating proof-transition witnesses."""
    data.decode('utf-8', errors='strict')
    state = initial()
    state['utf8'] = 0
    for byte in data:
        if state['good']:
            state['utf8'] = utf8_step(state['utf8'], byte)
            if state['utf8'] == 255:
                state['good'] = False
        event = step(state, chr(byte))
        if event is not None:
            yield event.encode('latin1').decode('utf-8', errors='strict')
    if not finish(state) or state['utf8'] != 0:
        raise ValueError('source outside import-projection byte specification')


@contextmanager
def blob_reader(folder):
    """One Git process per repository, retaining at most one source blob."""
    command = ['git', '--no-replace-objects', '-c', 'core.hooksPath=',
               '-c', 'safe.directory='+str(Path(folder).resolve()), '-C', str(folder),
               'cat-file', '--batch']
    environment = dict(os.environ, GIT_NO_LAZY_FETCH='1')
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, env=environment)
    def read(oid):
        if not re.fullmatch(r'[0-9a-f]{40}', oid):
            raise ValueError('invalid blob identity')
        process.stdin.write((oid+'\n').encode('ascii'))
        process.stdin.flush()
        header = process.stdout.readline().split()
        if len(header) != 3 or header[:2] != [oid.encode(), b'blob']:
            raise ValueError('missing or invalid Git blob')
        size = int(header[2])
        data = process.stdout.read(size)
        if len(data) != size or process.stdout.read(1) != b'\n':
            raise ValueError('truncated Git blob')
        return data
    try:
        yield read
    finally:
        process.stdin.close()
        process.stdout.close()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def git(folder, *args):
    return subprocess.check_output(['git', '--no-replace-objects', '-c', 'core.hooksPath=',
        '-c', 'safe.directory='+str(Path(folder).resolve()), '-C', str(folder), *args],
        stderr=subprocess.PIPE, timeout=60, env=dict(os.environ, GIT_NO_LAZY_FETCH='1'))


def path_ok(path):
    return (type(path) is str and bool(path) and not any(ord(c) < 32 for c in path)
            and '\\' not in path and ':' not in path and '"' not in path
            and all(p not in ('', '.', '..') for p in path.split('/')))


def identity(repo, commit, path):
    if (not re.fullmatch(r'[a-zA-Z0-9_-]+', repo) or not re.fullmatch(r'[0-9a-f]{40}', commit)
            or not path_ok(path)):
        raise ValueError('invalid file identity')
    return repo+'@'+commit+':'+path


def scope_pathspecs(folder, revision, prefixes):
    """Expand partial basename prefixes without walking unrelated subtrees."""
    if '' in prefixes:
        return []
    parents, selected = {}, set()
    for prefix in prefixes:
        if prefix.endswith('/'):
            selected.add(prefix.rstrip('/'))
            continue
        parent, _, _ = prefix.rpartition('/')
        if parent not in parents:
            tree = revision+':'+parent if parent else revision
            children = []
            for row in git(folder, 'ls-tree', '-z', tree).split(b'\0'):
                if row:
                    _, filename = row.split(b'\t', 1)
                    children.append((parent+'/' if parent else '')+filename.decode('utf-8'))
            parents[parent] = children
        selected.update(path for path in parents[parent] if path.startswith(prefix))
    return sorted(selected)


def tool_identity():
    import duckdb, pyarrow, numpy
    base = Path(__file__).parent
    return {'spec': SPEC, 'duckdb': duckdb.__version__, 'pyarrow': pyarrow.__version__,
        'numpy': numpy.__version__, 'code': {name: sha256((base/name).read_bytes()).hexdigest()
        for name in ('stage8_sources.py', 'stage8_store.py', 'stage8_rows.py', 'stage8_graph.py', 'source_bytes_v2.py', 'source_scanner_v2.py')}}


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


def capture(manifest_path, expected_sha, locations, spool_dir=None, *, file_prefixes=False):
    raw = Path(manifest_path).read_bytes()
    if sha256(raw).hexdigest() != expected_sha:
        raise ValueError('manifest differs from independent caller anchor')
    m = read_json(manifest_path)
    if set(m) != {'schema', 'origin', 'repositories', 'rules', 'configs'} or m['schema'] != 'stage8-corpus-v1':
        raise ValueError('manifest schema')
    if m['origin'] not in ('real', 'synthetic-fixture') or not m['repositories']:
        raise ValueError('manifest origin/universe')
    universe, file_metadata, repositories = {}, {}, []
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
        if not repo['prefixes'] or any(not isinstance(p, str) or
                (p != '' and not path_ok(p.rstrip('/'))) for p in repo['prefixes']):
            raise ValueError('invalid source scope')
        # Preserve startswith scope semantics, including partial basenames.
        # Literal pathspecs prevent wildcard interpretation.
        scope = repo['prefixes']
        pathspecs = scope_pathspecs(folder, rev, scope)
        tree = (git(folder, '--literal-pathspecs', 'ls-tree', '-rz', '--full-tree', rev,
                    '--', *pathspecs) if pathspecs or '' in scope else b'')
        selected = {}
        for row in tree.split(b'\0'):
            if not row:
                continue
            header, filename = row.split(b'\t', 1)
            mode, kind, oid = header.decode().split()
            path = filename.decode('utf-8')
            if any(path.startswith(p) for p in scope) and path.endswith('.mojom'):
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
            keyfile = (rid, rev, f['path'])
            universe[keyfile] = name
            file_metadata[keyfile] = f
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
            directory = prefix.endswith('/') and path_ok(prefix[:-1])
            literal_file = file_prefixes and prefix.endswith('.mojom') and path_ok(prefix)
            if prefix and not (directory or literal_file):
                raise ValueError('noncanonical prefix')
        rule_ids.add(rule['id'])
    keys = sorted(universe)
    ids = {key: i for i, key in enumerate(keys)}
    files = pa.Table.from_pylist([{'id': i, 'repo_id': k[0], 'commit': k[1], 'path': k[2],
            'blob': file_metadata[k]['blob'],
            'sha256': file_metadata[k]['sha256']} for i, k in enumerate(keys)])
    events, resolutions, external, edges = FactRows(spool_dir), FactRows(spool_dir), FactRows(spool_dir), set()
    source_bytes = 0
    from contextlib import ExitStack
    with ExitStack() as stack:
        readers = {version: stack.enter_context(blob_reader(locations[version]))
                   for version in sorted(versions)}
        for key in keys:
            data = readers[key[:2]](file_metadata[key]['blob'])
            source_bytes += len(data)
            source_hash = sha256(data).hexdigest()
            if source_hash != file_metadata[key]['sha256']:
                raise ValueError('source bytes changed')
            emitted = list(import_events(data))
            del data
            for ordinal, literal in enumerate(emitted):
                event = {'importer': ids[key], 'ordinal': ordinal, 'literal': literal,
                         'source_sha256': source_hash}
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
                           'source_bytes': source_bytes}]}
    return files, np.array(sorted(edges), dtype=np.int64).reshape((-1, 2)), facts
