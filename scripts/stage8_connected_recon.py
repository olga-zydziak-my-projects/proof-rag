"""Pin and inspect the Electron/Brave shared Chromium candidate, without builds."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from concurrent.futures import ThreadPoolExecutor
from stage8_public_data import PublicData


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output')
    parser.add_argument('--download-patches', action='store_true')
    parser.add_argument('--electron-common-targets', action='store_true', help='freeze complete plugin and web_contents_utility GN target sources')
    args = parser.parse_args()
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=True)
    data = PublicData(folder / 'http-cache')
    report = {'schema': 'stage8-connected-recon-v1', 'status': 'CANDIDATE_UNACCEPTED',
              'limits': {'response_bytes': data.max_bytes, 'attempts': data.attempts}, 'projects': {}}
    for name, repository, tag in [('electron', 'electron/electron', 'v38.1.2'),
                                  ('brave', 'brave/brave-core', 'v1.82.166')]:
        meta = data.json('https://api.github.com/repos/' + repository + '/commits/' + tag)
        commit = meta['sha']
        root = folder / name
        root.mkdir(exist_ok=True)
        entry = {'repository': repository, 'tag': tag, 'commit': commit,
                 'tree': meta['commit']['tree']['sha'], 'files': []}
        report['projects'][name] = entry
        paths = ['DEPS', 'patches/config.json', 'script/lib/patches.py', 'BUILD.gn', 'shell/common/BUILD.gn'] if name == 'electron' else [
            'package.json', 'docs/patching_and_chromium_src.md', 'build/commands/lib/config.js',
            'build/commands/scripts/sync.js', 'build/commands/lib/applyPatches.js',
            'build/commands/lib/gitPatcher.js', 'build/commands/lib/syncUtils.js',
            'build/commands/lib/util.js',
            'components/ai_chat/core/common/mojom/BUILD.gn']
        for path in paths:
            url = 'https://raw.githubusercontent.com/' + repository + '/' + commit + '/' + path
            try:
                raw = data.get(url)
            except Exception as exc:
                entry['files'].append({'path': path, 'url': url, 'error': str(exc)})
                continue
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            entry['files'].append({'path': path, 'url': url, 'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)})
        if name == 'electron':
            text = (root / 'DEPS').read_text(encoding='utf-8')
            entry['chromium_tag'] = re.search(r"'chromium_version'\s*:\s*'([^']+)'", text)[1]
        else:
            entry['chromium_tag'] = json.loads((root / 'package.json').read_bytes())['config']['projects']['chrome']['tag']
        # Full pinned patch and overlay inventory. Recursive responses are split if truncated.
        entry['patch_inventory'] = data.github_tree(repository, commit, 'patches')
        if name == 'brave':
            entry['overlay_inventory'] = data.github_tree(repository, commit, 'chromium_src')
        prefix = 'shell/common/api' if name == 'electron' else 'components/ai_chat/core/common/mojom'
        entry['source_scope_inventory'] = data.github_tree(repository, commit, prefix)
        entry['source_scope_prefix'] = prefix + '/'
        if name == 'electron' and args.electron_common_targets:
            selected = {'shell/common/plugin.mojom', 'shell/common/web_contents_utility.mojom'}
            entry['source_scope_inventory'] = [e for e in data.github_tree(repository, commit, 'shell/common') if e['path'] in selected]
            if {e['path'] for e in entry['source_scope_inventory']} != selected:
                raise ValueError('incomplete selected Electron GN target source inventory')
            entry['source_scope_prefix'] = None
            entry['source_scope_targets'] = ['//electron/shell/common:plugin', '//electron/shell/common:web_contents_utility']
        download_paths = [e['path'] for e in entry['source_scope_inventory'] if e['type'] == 'blob']
        if args.download_patches:
            download_paths += [e['path'] for e in entry['patch_inventory'] if e['type'] == 'blob']
            if name == 'brave':
                download_paths += ['chromium_src/mojo/public/tools/mojom/mojom_parser.py']
        def download(path):
            raw = data.get('https://raw.githubusercontent.com/' + repository + '/' + commit + '/' + path)
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            return {'path': path, 'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
        with ThreadPoolExecutor(max_workers=4) as pool:
            entry['downloaded_scope_and_patches'] = list(pool.map(download, download_paths))
        (folder / 'recon.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(name, commit, entry['chromium_tag'], flush=True)
    tags = {entry['chromium_tag'] for entry in report['projects'].values()}
    if len(tags) != 1:
        raise ValueError('candidate contexts pin different Chromium tags')
    tag = tags.pop()
    url = 'https://chromium.googlesource.com/chromium/src/+/' + tag + '?format=JSON'
    chromium = json.loads(data.get(url).split(b'\n', 1)[1])
    report['projects']['chromium'] = {'repository': 'chromium/chromium', 'tag': tag,
                                    'commit': chromium['commit'], 'tree': chromium['tree']}
    mirror = data.json('https://api.github.com/repos/brave/chromium/commits/' + tag)
    report['brave_chromium_mirror'] = {'repository': 'brave/chromium', 'tag': tag,
                                      'commit': mirror['sha'], 'tree': mirror['commit']['tree']['sha']}
    if (mirror['sha'], mirror['commit']['tree']['sha']) != (chromium['commit'], chromium['tree']):
        raise ValueError('Brave Chromium mirror differs from official pinned commit/tree')
    report['status'] = 'PINNED_CANDIDATE_PATCH_AUDIT_REQUIRED'
    (folder / 'recon.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
