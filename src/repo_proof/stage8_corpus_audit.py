"""Pinned corpus evidence audit. Mapping semantics remain a reviewed specification.

The audit reconstructs complete patch/overlay Git trees, checks patch bytes,
and rejects a selected source touched by either patch context. No build executes.
"""
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

from .source_bytes_v2 import certificate


REVIEWED_CONFIG_PATHS = {
    'electron': ['DEPS', 'BUILD.gn', 'shell/common/BUILD.gn', 'patches/config.json', 'script/lib/patches.py'],
    'brave': ['package.json', 'build/commands/lib/config.js', 'build/commands/scripts/sync.js',
              'build/commands/lib/applyPatches.js', 'build/commands/lib/gitPatcher.js',
              'build/commands/lib/syncUtils.js', 'build/commands/lib/util.js',
              'components/ai_chat/core/common/mojom/BUILD.gn'],
    'chromium': ['chrome/VERSION'],
}


def check_reviewed_rules(manifest, source_imports):
    """Execute the accepted mount specification independently of supplied rules."""
    repos = {repo['repo_id']: repo for repo in manifest['repositories']}
    expected = []
    for name, repo in repos.items():
        prefixes = sorted({literal.split('/')[0] + '/' for literal in source_imports[name]})
        for prefix in prefixes:
            target = 'brave' if prefix == 'brave/' else 'electron' if prefix == 'electron/' else 'chromium'
            expected.append({'id': name + '-' + prefix[:-1], 'from': [name, repo['commit']], 'prefix': prefix,
                             'to': [target, repos[target]['commit']],
                             'target_prefix': prefix if target == 'chromium' else '',
                             'evidence': 'brave-package.json' if name == 'brave' else 'electron-DEPS'})
    if sorted(manifest['rules'], key=lambda r: r['id']) != sorted(expected, key=lambda r: r['id']):
        raise ValueError('resolver rules differ from reviewed source-root mount specification')


def _git(folder, *args):
    environment = dict(os.environ, GIT_NO_LAZY_FETCH='1')
    return subprocess.check_output(['git', '--no-replace-objects', '-c', 'core.hooksPath=',
                                   '-C', str(folder), *args], stderr=subprocess.PIPE, timeout=60, env=environment)


def _oid(kind, data):
    return sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def check_inventory(rows, prefix, expected):
    """Validate every directory and the complete subtree against its Git tree ID."""
    entries = {row['path']: row for row in rows}
    if len(entries) != len(rows) or any(not path.startswith(prefix + '/') for path in entries):
        raise ValueError('duplicate or out-of-scope inventory path')
    trees = {prefix: expected, **{path: row['sha'] for path, row in entries.items() if row['type'] == 'tree'}}
    for path, expected_oid in trees.items():
        children = [row for name, row in entries.items() if name.rpartition('/')[0] == path]
        children.sort(key=lambda row: (row['path'].rsplit('/', 1)[1] + ('/' if row['type'] == 'tree' else '')).encode())
        raw = b''.join(row['mode'].lstrip('0').encode() + b' ' + row['path'].rsplit('/', 1)[1].encode()
                       + b'\0' + bytes.fromhex(row['sha']) for row in children)
        if _oid('tree', raw) != expected_oid:
            raise ValueError('incomplete or substituted inventory tree: ' + path)
    if any(path.rpartition('/')[0] not in trees for path in entries):
        raise ValueError('inventory entry lacks parent directory')


def _patch_paths(raw):
    paths = set()
    for line in raw.decode('utf-8').splitlines():
        if line.startswith('diff --git '):
            tokens = shlex.split(line)
            if len(tokens) != 4 or not tokens[2].startswith('a/') or not tokens[3].startswith('b/'):
                raise ValueError('unsupported patch path syntax')
            paths.update((tokens[2][2:], tokens[3][2:]))
    if not paths:
        raise ValueError('patch lacks complete Git diff headers')
    return paths


def verify_corpus(manifest_path, expected_sha, evidence_path, locations=None):
    """Return checked facts, or raise on absent, stale, or contradictory evidence."""
    manifest_path, evidence_path = Path(manifest_path), Path(evidence_path)
    raw = manifest_path.read_bytes()
    if sha256(raw).hexdigest() != expected_sha:
        raise ValueError('corpus manifest anchor mismatch')
    manifest = json.loads(raw)
    evidence = json.loads(evidence_path.read_bytes())
    if evidence['schema'] != 'stage8-pinned-corpus-evidence-v1' or evidence['manifest_sha256'] != expected_sha:
        raise ValueError('corpus evidence schema/manifest mismatch')
    project = Path(__file__).resolve().parents[2]
    root = (project / evidence['data_directory']).resolve()
    recon_raw = (root / 'recon.json').read_bytes()
    if sha256(recon_raw).hexdigest() != evidence['recon_sha256']:
        raise ValueError('recon evidence changed')
    recon = json.loads(recon_raw)
    if locations is None:
        locations = {(row['repo_id'], row['commit']): row['directory']
                     for row in json.loads((root / 'locations.json').read_bytes())}
    repos = {repo['repo_id']: repo for repo in manifest['repositories']}
    if set(repos) != {'electron', 'brave', 'chromium'} or manifest['origin'] != 'real':
        raise ValueError('expected three original projects')
    selected = {f['path'] for f in repos['chromium']['files']}
    effective_paths = selected | {'brave/' + f['path'] for f in repos['brave']['files']} | {'electron/' + f['path'] for f in repos['electron']['files']}
    for name, repo in repos.items():
        meta = recon['projects'][name]
        if (repo['commit'], repo['tree'], repo['url']) != (meta['commit'], meta['tree'], 'https://github.com/' + meta['repository']):
            raise ValueError('repository/version evidence differs from manifest')
        folder = locations[name, repo['commit']]
        if _git(folder, 'rev-parse', repo['commit'] + '^{tree}').decode().strip() != repo['tree']:
            raise ValueError('original commit/tree missing')
    def blob(name, path):
        repo = repos[name]
        folder = locations[name, repo['commit']]
        return _git(folder, 'show', repo['commit'] + ':' + path)
    imports = {}
    for name, repo in repos.items():
        imports[name] = []
        for source in repo['files']:
            content = blob(name, source['path'])
            if _oid('blob', content) != source['blob'] or sha256(content).hexdigest() != source['sha256']:
                raise ValueError('corpus source bytes differ from pinned original Git blob')
            imports[name].extend(certificate(content)[1])
    check_reviewed_rules(manifest, imports)
    expected_configs = []
    for name, paths in REVIEWED_CONFIG_PATHS.items():
        for path in paths:
            content = blob(name, path)
            expected_configs.append({'id': name + '-' + path.replace('/', '-'), 'repo_id': name,
                                     'commit': repos[name]['commit'], 'path': path,
                                     'blob': _oid('blob', content), 'sha256': sha256(content).hexdigest()})
    if sorted(manifest['configs'], key=lambda c: c['id']) != sorted(expected_configs, key=lambda c: c['id']):
        raise ValueError('manifest configurations differ from complete reviewed pinned inputs')
    electron_version = re.search(rb"'chromium_version'\s*:\s*'([^']+)'", blob('electron', 'DEPS'))[1].decode()
    brave_version = json.loads(blob('brave', 'package.json'))['config']['projects']['chrome']['tag']
    if electron_version != brave_version or electron_version != recon['projects']['chromium']['tag']:
        raise ValueError('Chromium versions do not match')
    mirror = recon['brave_chromium_mirror']
    if (mirror['tag'], mirror['commit'], mirror['tree']) != (electron_version, repos['chromium']['commit'], repos['chromium']['tree']):
        raise ValueError('Brave mirror does not pin the identical Chromium commit/tree')
    # The Chromium commit's actual VERSION file anchors tag meaning independently
    # of mutable HTTP refs and the metadata report.
    version_text = blob('chromium', 'chrome/VERSION').decode()
    version = '.'.join(re.search(r'^' + key + r'=(\d+)$', version_text, re.M)[1]
                       for key in ('MAJOR', 'MINOR', 'BUILD', 'PATCH'))
    if version != electron_version:
        raise ValueError('Chromium commit VERSION disagrees with project pins')
    config = blob('brave', 'build/commands/lib/config.js')
    if b"const braveCoreDir = path.join(rootDir, 'src', 'brave')" not in config:
        raise ValueError('reviewed Brave source mount differs')
    required_evidence = [('electron', 'script/lib/patches.py'), ('brave', 'build/commands/lib/applyPatches.js'),
                         ('brave', 'build/commands/lib/gitPatcher.js'), ('brave', 'build/commands/lib/syncUtils.js'),
                         ('brave', 'build/commands/lib/util.js'),
                         ('brave', 'build/commands/scripts/sync.js')]
    for name, path in required_evidence:
        content = blob(name, path)
        item = next(item for item in recon['projects'][name]['files'] if item['path'] == path)
        if sha256(content).hexdigest() != item['sha256']:
            raise ValueError('patch application driver differs from reviewed pinned bytes')
    # Complete source lists of the selected GN targets are manually accepted
    # mapping evidence. These checks reject drift from those exact declarations.
    gn = blob('electron', 'shell/common/BUILD.gn').decode()
    for target, filename in [('plugin', 'plugin.mojom'), ('web_contents_utility', 'web_contents_utility.mojom')]:
        block = re.search(r'mojom\("' + target + r'"\)\s*\{(.*?)\n\}', gn, re.S)
        sources = re.search(r'sources\s*=\s*\[(.*?)\]', block[1], re.S)
        if re.findall(r'"([^"]+)"', sources[1]) != [filename]:
            raise ValueError('Electron target source scope changed')
    if {f['path'] for f in repos['electron']['files']} != {'shell/common/plugin.mojom', 'shell/common/web_contents_utility.mojom'}:
        raise ValueError('Electron declared scope differs from complete selected targets')
    brave_gn = blob('brave', 'components/ai_chat/core/common/mojom/BUILD.gn').decode()
    source_list = re.search(r'sources\s*=\s*\[(.*?)\]', brave_gn, re.S)[1]
    if {'components/ai_chat/core/common/mojom/' + path for path in re.findall(r'"([^"]+)"', source_list)} != {f['path'] for f in repos['brave']['files']}:
        raise ValueError('Brave declared scope differs from complete selected target')
    patch_counts, touched = {}, {}
    for name in ('electron', 'brave'):
        meta, repo = recon['projects'][name], repos[name]
        inventory = meta['patch_inventory']
        expected = _git(locations[name, repo['commit']], 'rev-parse', repo['commit'] + ':patches').decode().strip()
        check_inventory(inventory, 'patches', expected)
        mappings = {'patches': '', 'patches/v8': 'v8', 'patches/third_party/catapult': 'third_party/catapult',
                    'patches/third_party/devtools-frontend/src': 'third_party/devtools-frontend/src',
                    'patches/third_party/search_engines_data/resources': 'third_party/search_engines_data/resources',
                    # Retained in the pinned tree although util.js does not invoke
                    # a TFLite patcher. Include it conservatively in overlap checks.
                    'patches/third_party/tflite/src': 'third_party/tflite/src'}
        if name == 'electron':
            mappings = {row['patch_dir'].removeprefix('src/electron/'): row['repo'].removeprefix('src').lstrip('/')
                        for row in json.loads(blob('electron', 'patches/config.json'))}
        touched[name], count = set(), 0
        for entry in inventory:
            if entry['type'] == 'tree':
                continue
            raw_patch = (root / name / entry['path']).read_bytes()
            if _oid('blob', raw_patch) != entry['sha']:
                raise ValueError('pinned patch bytes changed or missing: ' + entry['path'])
            if not entry['path'].endswith('.patch'):
                continue
            count += 1
            patch_directory = entry['path'].rpartition('/')[0]
            if patch_directory not in mappings:
                raise ValueError('patch lacks unique pinned target-repository mapping')
            target_prefix = mappings[patch_directory]
            touched[name].update((target_prefix + '/' if target_prefix else '') + path for path in _patch_paths(raw_patch))
        patch_counts[name] = count
        overlap = effective_paths & touched[name]
        if overlap:
            raise ValueError('selected raw Chromium sources modified by ' + name + ' patches: ' + repr(sorted(overlap)))
    brave = repos['brave']
    overlay = recon['projects']['brave']['overlay_inventory']
    expected = _git(locations['brave', brave['commit']], 'rev-parse', brave['commit'] + ':chromium_src').decode().strip()
    check_inventory(overlay, 'chromium_src', expected)
    overlay_paths = {entry['path'].removeprefix('chromium_src/') for entry in overlay if entry['type'] == 'blob'}
    if effective_paths & overlay_paths:
        raise ValueError('selected Chromium source has a Brave AST overlay')
    parser_path = 'chromium_src/mojo/public/tools/mojom/mojom_parser.py'
    parser_raw = (root / 'brave' / parser_path).read_bytes()
    parser_oid = next(entry['sha'] for entry in overlay if entry['path'] == parser_path)
    if _oid('blob', parser_raw) != parser_oid:
        raise ValueError('Brave parser overlay evidence changed')
    if b"os.path.join(chromium_src_abspath, mojom_relpath)" not in parser_raw or b'if not os.path.isfile(brave_mojom_abspath):' not in parser_raw:
        raise ValueError('reviewed path-specific AST overlay mechanism changed')
    if not evidence.get('manual_mapping_specification'):
        raise ValueError('missing reviewed mapping specification')
    return {'status': 'CORPUS_EVIDENCE_CHECKED', 'projects': 3, 'chromium_version': version,
            'patch_counts': patch_counts, 'overlay_entries': len(overlay),
            'chromium_source_files_unchanged_in_both_contexts': len(selected),
            'mapping_semantics': 'manually accepted pinned specification',
            'recon_sha256': evidence['recon_sha256']}
