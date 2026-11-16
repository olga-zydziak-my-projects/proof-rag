"""Pinned, bounded public-source acquisition; no checkout, hooks or builds."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1, sha256
import json
from pathlib import Path
import shutil
import sys
import time
import zlib

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts')]
from stage8_public_data import PublicData
from stage8_materialize_candidate import Objects, git
from repo_proof.stage8_sources import import_events

MODULES = ('components', 'content', 'device', 'gpu', 'media', 'mojo/public/mojom',
           'printing', 'services', 'third_party/blink/public/mojom', 'ui', 'url/mojom')
GENERATED = ('third_party/blink/public/mojom/runtime_feature_state/runtime_feature.mojom',
             'third_party/blink/public/mojom/origin_trials/origin_trial_feature.mojom')
GENERATED_CONFIGS = ('third_party/blink/public/mojom/runtime_feature_state/BUILD.gn',
    'third_party/blink/public/mojom/origin_trials/BUILD.gn',
    'third_party/blink/renderer/build/scripts/make_runtime_feature_mojom_defs.py',
    'third_party/blink/renderer/build/scripts/make_origin_trial_feature_mojom_defs.py',
    'third_party/blink/renderer/build/scripts/templates/runtime_feature.mojom.tmpl',
    'third_party/blink/renderer/build/scripts/templates/origin_trial_feature.mojom.tmpl')


def write(path, obj):
    Path(path).write_bytes(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True).encode() + b'\n')


def store(folder, kind, raw, expected=None):
    framed = kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw
    oid = sha1(framed).hexdigest()
    if expected is not None and oid != expected:
        raise ValueError('downloaded/reconstructed Git identity mismatch')
    target = folder / 'objects' / oid[:2] / oid[2:]
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zlib.compress(framed))
    return oid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--reuse', type=Path)
    a = parser.parse_args()
    root = a.run_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    old = PROJECT / 'local/stage8/connected-recon-01'
    recon = json.loads((old / 'recon.json').read_bytes())
    base = json.loads((PROJECT / 'verification/stage8-connected-corpus-manifest-04.json').read_bytes())
    write(root / 'selection-before-acquisition.json', {
        'schema': 'stage9-scope-selection-v1', 'modules': MODULES,
        'selection': 'all regular .mojom under every complete listed Chromium module, plus least literal import closure; unchanged two Electron GN targets and complete Brave AI Chat GN target',
        'contexts': 'Chromium upstream only; Electron/Brave dependency equivalence checked for their complete closure, not for other upstream files',
        'queries_selected': False})
    if a.reuse:
        shutil.copytree(a.reuse/'http-cache',root/'http-cache')
    public = PublicData(root / 'http-cache', max_bytes=32_000_000)
    objects = {}
    for name, meta in recon['projects'].items():
        shutil.copytree((a.reuse or old) / ('git-' + name), root / ('git-' + name))
        objects[name] = Objects(root, name, meta, public)
    chromium = objects['chromium']
    commit = chromium.meta['commit']
    inventory = {}
    acquired = time.perf_counter()
    for module in MODULES:
        url = f'https://chromium.googlesource.com/chromium/src/+/{commit}/{module}/?format=JSON&recursive=1'
        data = json.loads(public.get(url).split(b'\n', 1)[1])
        # Recursive Gitiles returns every leaf, including non-Mojom: reconstruct
        # every intermediate tree and bind the complete scope to its original ID.
        dirs = {'': []}
        for entry in data['entries']:
            path = entry['name']
            if entry['type'] == 'tree':
                raise ValueError('unexpected non-leaf recursive inventory')
            parent, _, name = path.rpartition('/')
            parts = parent.split('/') if parent else []
            for k in range(len(parts) + 1):
                dirs.setdefault('/'.join(parts[:k]), [])
            dirs[parent].append((name, format(entry['mode'], 'o'), entry['type'], entry['id']))
            if path.endswith('.mojom'):
                if entry['type'] != 'blob' or entry['mode'] not in (0o100644, 0o100755):
                    raise ValueError('unsupported Mojom source')
                inventory[module + '/' + path] = entry['id']
        for path in sorted(dirs, key=lambda p: (p.count('/'), len(p)), reverse=True):
            entries = sorted(dirs[path], key=lambda e: (e[0] + ('/' if e[2] == 'tree' else '')).encode())
            raw = b''.join(mode.lstrip('0').encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)
                           for name, mode, kind, oid in entries)
            oid = store(chromium.folder, 'tree', raw)
            if path:
                parent, _, name = path.rpartition('/')
                dirs[parent].append((name, '40000', 'tree', oid))
            else:
                if oid != data['id'] or git(chromium.folder, 'rev-parse', commit + ':' + module).decode().strip() != oid:
                    raise ValueError('module tree does not match pinned commit')
        print('inventory', module, len(inventory), flush=True)
    write(root / 'chromium-mojom-inventory.json', inventory)
    # Existing blobs are reused only by exact Git object ID. The old corpora
    # remain read-only. Public missing blobs use at most four HTTP readers.
    prior = json.loads((PROJECT/'local/corpus.json').read_bytes())
    candidates = [old / 'git-chromium', Path(prior['data_dir'])/'git']
    def fetch(item):
        path, oid = item
        for repo in [chromium.folder, *candidates]:
            if repo.exists():
                try:
                    raw = git(repo, 'cat-file', 'blob', oid)
                    store(chromium.folder, 'blob', raw, oid)
                    return path, raw, 'local'
                except Exception:
                    pass
        raw = public.get(f'https://raw.githubusercontent.com/chromium/chromium/{commit}/{path}')
        store(chromium.folder, 'blob', raw, oid)
        return path, raw, 'download'
    files = {(repo['repo_id'], f['path']): f for repo in base['repositories'] for f in repo['files']}
    events, local_count, download_count = {}, 0, 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        for number, (path, raw, origin) in enumerate(pool.map(fetch, sorted(inventory.items())), 1):
            files['chromium', path] = {'path': path, 'blob': inventory[path], 'sha256': sha256(raw).hexdigest()}
            events['chromium', path] = list(import_events(raw))
            local_count += origin == 'local'
            download_count += origin == 'download'
            if number % 100 == 0:
                print('blobs', number, flush=True)
    # Least closure never marks a difficult target external.
    queue = list(files)
    cursor = 0
    while cursor < len(queue):
        name, path = queue[cursor]
        cursor += 1
        if (name, path) not in events:
            try:
                oid = git(objects[name].folder,'rev-parse',objects[name].meta['commit']+':'+path).decode().strip()
                raw = git(objects[name].folder,'cat-file','blob',oid)
            except Exception:
                try:
                    raw, oid = objects[name].blob(path)
                except Exception as exc:
                    raise ValueError('required source absent: '+name+':'+path) from exc
            files[name, path] = {'path': path, 'blob': oid, 'sha256': sha256(raw).hexdigest()}
            events[name, path] = list(import_events(raw))
        for literal in events[name, path]:
            if literal in GENERATED:
                continue
            target = ('brave', literal[6:]) if literal.startswith('brave/') else ('electron', literal[9:]) if literal.startswith('electron/') else ('chromium', literal)
            if target not in queue:
                queue.append(target)
    repositories = []
    for repo in base['repositories']:
        name = repo['repo_id']
        selected = [v for (rid, path), v in sorted(files.items()) if rid == name]
        scope = [m + '/' for m in MODULES] if name == 'chromium' else repo['prefixes']
        prefixes = scope + [f['path'] for f in selected if not any(f['path'].startswith(p) for p in scope)]
        repositories.append({**repo, 'prefixes': prefixes, 'files': selected})
    rules = []
    for repo in repositories:
        name = repo['repo_id']
        literals = sorted({s for (rid, _), es in events.items() if rid == name for s in es})
        def category(literal):
            return 'external' if literal in GENERATED else 'brave' if literal.startswith('brave/') else 'electron' if literal.startswith('electron/') else 'chromium'
        def partition(values, prefix=''):
            kinds={category(s) for s in values}
            if kinds=={'external'}:
                return [(s,'external') for s in values]
            if prefix and len(kinds)==1:
                return [(prefix,next(iter(kinds)))]
            groups={}
            for value in values:
                suffix=value[len(prefix):]
                part=suffix.split('/')[0]+('/' if '/' in suffix else '')
                groups.setdefault(prefix+part,[]).append(value)
            return [rule for part,group in sorted(groups.items()) for rule in partition(group,part)]
        for prefix,target in partition(literals) if literals else []:
            tp=prefix[6:] if target=='brave' else prefix[9:] if target=='electron' else prefix
            rules.append({'id': name + '-' + prefix, 'from': [name, repo['commit']], 'prefix': prefix,
                          'to': None if target=='external' else [target, objects[target].meta['commit']],
                          'target_prefix': '' if target=='external' else tp,
                          'evidence': ('chromium-'+prefix.rpartition('/')[0].replace('/','-')+'-BUILD.gn') if target=='external' else 'brave-package.json' if name=='brave' else 'electron-DEPS'})
    # The excluded targets are build outputs, witnessed by pinned BUILD.gn and
    # templates; they are not missing committed Mojom inputs or a fallback.
    for path in GENERATED_CONFIGS:
        raw,oid=chromium.blob(path)
        base['configs'].append({'id':'chromium-'+path.replace('/','-'),'repo_id':'chromium','commit':commit,
                                'path':path,'blob':oid,'sha256':sha256(raw).hexdigest()})
    manifest = {**base, 'repositories': repositories, 'rules': rules}
    write(root / 'manifest.json', manifest)
    write(root / 'locations.json', [{'repo_id': name, 'commit': obj.meta['commit'], 'directory': str(obj.folder)} for name, obj in objects.items()])
    write(root / 'acquisition.json', {'seconds': time.perf_counter() - acquired, 'reused_blobs': local_count,
          'downloaded_module_blobs': download_count, 'files': len(files), 'events': sum(map(len, events.values())),
          'manifest_sha256': sha256((root / 'manifest.json').read_bytes()).hexdigest(), 'queries_selected': False})
    print('complete', len(files), flush=True)


if __name__ == '__main__':
    main()
