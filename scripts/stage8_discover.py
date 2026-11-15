"""Bounded, read-only Gitiles reconnaissance. Configuration is never executed."""
import base64
from hashlib import sha256
import json
from pathlib import Path
import sys
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]


def main():
    folder = PROJECT / sys.argv[1]
    folder.mkdir(parents=True, exist_ok=False)
    candidates = {
        'platform2': ('chromiumos/platform2', ['common-mk/mojom_bindings_generator.gni',
            'diagnostics/mojom/public/cros_healthd_probe.mojom', 'camera/mojo/camera3.mojom',
            'camera/common/BUILD.gn', 'federated/mojom/federated_service.mojom']),
        'libchrome': ('chromiumos/platform/libchrome', ['README', 'mojo/public/mojom/base/time.mojom']),
        'crosvm': ('crosvm/crosvm', ['Cargo.toml', 'devices/src/virtio/video/decoder/mod.rs']),
        'system_api': ('chromiumos/platform2/system_api', ['README.md']),
        'camera': ('chromiumos/platform/camera', ['README.md']),
        'libcamera': ('chromiumos/third_party/libcamera', ['include/libcamera/ipa/core.mojom']),
        'chromium': ('chromium/src', ['DEPS', 'chromeos/ash/services/federated/public/mojom/federated_service.mojom']),
        'manifest': ('chromiumos/manifest', ['default.xml'])}
    report = {'schema': 'stage8-discovery-v1', 'candidates_not_a_selected_corpus': []}
    def get(url):
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read(8_000_001)
        if len(raw) > 8_000_000:
            raise ValueError('metadata download size limit')
        return raw
    for name, (repo, files) in candidates.items():
        url = 'https://chromium.googlesource.com/' + repo
        entry = {'repo_id': name, 'url': url, 'files': []}
        try:
            revision = '27cec857a08a0ee0e1b41f5eb18c07467a0ce093' if name == 'chromium' else 'HEAD'
            raw = get(url + '/+/' + revision + '?format=JSON')
            meta = json.loads(raw.split(b'\n', 1)[1])
            entry.update(commit=meta['commit'], tree=meta['tree'], metadata=meta)
            for path in files:
                link = url + '/+/' + meta['commit'] + '/' + path + '?format=TEXT'
                item = {'path': path, 'url': link}
                try:
                    data = base64.b64decode(get(link), validate=False)
                    target = folder/name/path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    item.update(bytes=len(data), sha256=sha256(data).hexdigest(),
                        imports=[line.strip() for line in data.decode('utf-8').splitlines()
                                 if line.lstrip().startswith('import "')])
                except Exception as exc:
                    item['error'] = type(exc).__name__ + ': ' + str(exc)
                entry['files'].append(item)
        except Exception as exc:
            entry['error'] = type(exc).__name__ + ': ' + str(exc)
        report['candidates_not_a_selected_corpus'].append(entry)
        (folder/'discovery.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(name, entry.get('commit', entry.get('error')), flush=True)


if __name__ == '__main__':
    main()
