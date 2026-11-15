"""Measure complete Git source capture, separately from graph-array benchmarks."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage5_v2 import canonical
from repo_proof.stage8_sources import capture, git


def synthetic(folder, count):
    """Every generated .mojom is committed and included in the declared scope."""
    repo = folder/'repository'
    repo.mkdir()
    def mutate(*args):
        subprocess.run(['git', '-c', 'core.hooksPath=', '-c', 'user.name=Stage8 fixture',
                        '-c', 'user.email=fixture@example.invalid', '-C', str(repo), *args],
                       check=True, capture_output=True, timeout=120)
    mutate('init', '--quiet')
    entries = []
    for i in range(count):
        path = f'sources/f{i:07d}.mojom'
        data = (f'module synthetic; import "sources/f{i-1:07d}.mojom";\n' if i
                else 'module synthetic;\n').encode()
        target = repo/path
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
        entries.append({'path': path, 'sha256': sha256(data).hexdigest()})
    (repo/'resolver.json').write_bytes(b'{"synthetic":true,"root":"sources/"}\n')
    mutate('add', '.')
    mutate('commit', '-qm', 'Explicit synthetic Git source indexing benchmark')
    rev = git(repo, 'rev-parse', 'HEAD').decode().strip()
    tree = git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip()
    blobs = {}
    for row in git(repo, 'ls-tree', '-rz', rev).split(b'\0'):
        if row:
            header, path = row.split(b'\t', 1)
            blobs[path.decode()] = header.decode().split()[2]
    for entry in entries:
        entry['blob'] = blobs[entry['path']]
    manifest = {'schema': 'stage8-corpus-v1', 'origin': 'synthetic-fixture',
        'repositories': [{'repo_id': 'synthetic', 'commit': rev, 'tree': tree,
            'url': 'synthetic-fixture://index-benchmark', 'prefixes': ['sources/'], 'files': entries}],
        'configs': [{'id': 'config', 'repo_id': 'synthetic', 'commit': rev,
            'path': 'resolver.json', 'blob': blobs['resolver.json'],
            'sha256': sha256((repo/'resolver.json').read_bytes()).hexdigest()}],
        'rules': [{'id': 'local', 'from': ['synthetic', rev], 'prefix': 'sources/',
            'to': ['synthetic', rev], 'target_prefix': 'sources/', 'evidence': 'config'}]}
    path = folder/'manifest.json'
    path.write_bytes(canonical(manifest))
    return path, {('synthetic', rev): str(repo)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--synthetic-files', type=int)
    parser.add_argument('--manifest')
    parser.add_argument('--manifest-sha256')
    parser.add_argument('--locations')
    args = parser.parse_args()
    folder = Path(args.run_dir)
    folder.mkdir(parents=True, exist_ok=False)
    generation = time.perf_counter()
    if args.synthetic_files:
        if args.synthetic_files < 1 or args.manifest:
            raise ValueError('choose synthetic sources or a real manifest')
        path, locations = synthetic(folder, args.synthetic_files)
        anchor = sha256(path.read_bytes()).hexdigest()
    else:
        path, anchor = Path(args.manifest), args.manifest_sha256
        locations = {(r['repo_id'], r['commit']): r['directory']
                     for r in json.loads(Path(args.locations).read_bytes())}
    generation = time.perf_counter()-generation
    started = time.perf_counter()
    files, edges, facts = capture(path, anchor, locations, spool_dir=folder)
    elapsed = time.perf_counter()-started
    report = {'status': 'SOURCE_INDEX_PASS', 'origin': facts['metadata'][0]['manifest']['origin'],
        'files': len(files), 'edges': len(edges), 'events': len(facts['events']),
        'source_bytes': facts['metadata'][0]['source_bytes'], 'generation_seconds': generation,
        'capture_seconds': elapsed, 'manifest_sha256': anchor,
        'tools': facts['metadata'][0]['tools'], 'git': git(next(iter(locations.values())), '--version').decode().strip(),
        'python': sys.version, 'measurement': 'full Git universe, blobs, hashes, configs, scanner and resolver'}
    (folder/'index-benchmark.json').write_bytes(canonical(report))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
