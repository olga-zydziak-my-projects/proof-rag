"""Separately frozen optional experiment, 256-node chain, real Souffle 2.5 in WSL.

Does not modify or participate in the core Stage8 frozen-code measurements.
Linux ulimit and timeout bound this WSL experiment; Windows psutil is NOT used
to claim measurement of Linux process memory.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
from statistics import median
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[2]


def linux(path):
    path = Path(path).resolve()
    return '/mnt/'+path.drive[0].lower()+'/'+path.as_posix()[3:]


def main():
    folder = Path(sys.argv[1]).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    binary = PROJECT/'local/stage8/souffle-tool/extracted/usr/bin/souffle'
    source = Path(__file__).with_name('reverse.dl')
    before = {str(f.relative_to(PROJECT)): sha256(f.read_bytes()).hexdigest() for f in (Path(__file__), source, binary)}
    began = time.perf_counter()
    (folder/'edge.facts').write_text(''.join(str(i)+'\t'+str(i-1)+'\n' for i in range(1, 256)), encoding='utf-8')
    (folder/'root.facts').write_text('0\n128\n255\n', encoding='utf-8')
    prep = time.perf_counter()-began
    expected = {(r, v) for r in (0, 128, 255) for v in range(r, 256)}
    report = {'status': 'IN_PROGRESS', 'origin': 'synthetic', 'nodes': 256, 'edges': 255,
        'roots': [0, 128, 255], 'tool': 'Souffle 2.5 official ubuntu2404 package, interpreter',
        'identities_before': before, 'prepare_fact_files_seconds': prep,
        'source_to_answer': False, 'lean': False, 'variants': [],
        'limits': {'linux_address_space_KiB': 1048576, 'cpu_seconds': 60, 'wall_seconds': 65, 'threads': 1},
        'measurement_scope': 'WSL launch + parse/import/query/output; profile loadtime and runtime separated; OS cache uncontrolled'}
    for magic in (False, True):
        rows = []
        for i in range(3):
            run = folder/(('magic' if magic else 'baseline')+'-'+str(i))
            run.mkdir()
            args = [linux(binary), '--no-preprocessor', '-j', '1', '-F', linux(folder),
                    '-D', linux(run), '-p', linux(run/'profile.json')]
            if magic:
                args += ['--magic-transform=*']
            args += [linux(source)]
            # Pass arguments separately to bash; never interpolate them as code.
            wrapper = ['wsl', '-d', 'Ubuntu-24.04', '--exec', 'bash', '-c',
                'ulimit -v 1048576; ulimit -t 60; exec timeout 65 /usr/bin/time -v "$@"', 'stage8', *args]
            started = time.perf_counter()
            result = subprocess.run(wrapper, capture_output=True, timeout=75)
            elapsed = time.perf_counter()-started
            (run/'stdout.log').write_bytes(result.stdout)
            (run/'stderr.log').write_bytes(result.stderr)
            if result.returncode:
                raise ValueError('optional variant failed, see '+str(run))
            actual = [tuple(map(int, line.split())) for line in (run/'answer.csv').read_text().splitlines()]
            if len(actual) != len(set(actual)) or set(actual) != expected:
                raise ValueError('complete Souffle result differs')
            profile = json.loads((run/'profile.json').read_bytes())
            memory = re.search(rb'Maximum resident set size \(kbytes\):\s*(\d+)', result.stderr)
            rows.append({'wall_seconds': elapsed, 'peak_linux_rss_KiB': int(memory.group(1)) if memory else None,
                         'full_answer_match': True, 'count': len(actual), 'profile': profile})
        report['variants'].append({'magic_sets': magic, 'runs': rows,
            'median_wall_seconds': median(r['wall_seconds'] for r in rows),
            'range_wall_seconds': [min(r['wall_seconds'] for r in rows), max(r['wall_seconds'] for r in rows)]})
    after = {str(f.relative_to(PROJECT)): sha256(f.read_bytes()).hexdigest() for f in (Path(__file__), source, binary)}
    report['identities_unchanged'] = before == after
    report['status'] = 'OPTIONAL_SOUFFLE_PASS' if before == after else 'FAILED_CODE_CHANGED'
    (folder/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(report['status'], [(r['magic_sets'], r['median_wall_seconds']) for r in report['variants']])


if __name__ == '__main__':
    main()
