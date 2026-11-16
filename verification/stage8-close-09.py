"""Separately reviewed Stage 8 closure control; never modifies frozen core code.

Runs the original unittest suite under the unchanged Windows Job Object
supervisor. No affinity, priority, test, or timeout overrides are applied.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts'),
                str(PROJECT / 'local/stage8-deps')]
import psutil
from stage6_regressions import code_inventory, prepare_regression_view, verify_regression_view
from check_stage8 import historical_report_inventory
from repo_proof.stage8_artifacts import inventory, verify

ROOT = PROJECT / 'local/stage8/close-09'
LEAN = Path(r'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe')
DIFFERENTIAL = 'test_lean_export.LeanExportTests.test_differential'


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    Path(path).write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    indent=2).encode('utf-8') + b'\n')


def info(path):
    raw = Path(path).read_bytes()
    return {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}


def anchor(path):
    return {'path': str(Path(path).resolve()), **info(path)}


def wsl():
    rows = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'ps',
        '-eo', 'pid,ppid,pcpu,rss,etimes,comm', '--sort=-pcpu'],
        capture_output=True, timeout=15)
    liquid = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec',
        'pgrep', '-f', '[o]rto_r4.py'], capture_output=True, timeout=15)
    return {'ps_exit': rows.returncode,
            'top_processes': rows.stdout.decode('utf-8', errors='replace').splitlines()[:25],
            'liquidpatrol_pids': liquid.stdout.decode().splitlines(),
            'pgrep_exit': liquid.returncode}


def environment():
    proc = psutil.Process()
    return {'utc': datetime.now(timezone.utc).isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'available_ram_bytes': psutil.virtual_memory().available,
        'free_disk_bytes': psutil.disk_usage(str(ROOT)).free,
        'priority_class': int(proc.nice()), 'affinity': proc.cpu_affinity(),
        'wsl': wsl()}


def validate_minute(observation):
    samples = observation.get('samples', [])
    times = [r['elapsed_seconds'] for r in samples]
    if (len(samples) < 6 or not 59 <= times[-1] <= 90
            or times[0] > 15 or any(not 0 < b - a <= 15 for a, b in zip(times, times[1:]))
            or any(r['cpu_percent'] >= 35 or r['available_ram_bytes'] < 7 * 1024**3 for r in samples)
            or any(observation[key]['ps_exit'] != 0 or observation[key]['pgrep_exit'] != 1
                   or observation[key]['liquidpatrol_pids'] for key in ('wsl_before', 'wsl_after'))):
        raise ValueError('complete minute does not establish sustained quiet host')


def parse_results(log):
    """Verbose unittest results, including Fetching output inside two records."""
    header = re.compile(r'^(test_\w+) \(([^)]+)\) \.\.\. (.*)$')
    statuses = re.compile(r'^(ok|ERROR|FAIL|skipped(?: .*)?)$')
    results, pending = {}, None
    for line in log.splitlines():
        match = header.fullmatch(line)
        if match:
            if pending is not None:
                raise ValueError('new test while previous result is pending: ' + pending)
            method, name, tail = match.groups()
            if name.rsplit('.', 1)[-1] != method or name in results:
                raise ValueError('invalid or duplicate test: ' + name)
            pending = name
            if statuses.fullmatch(tail):
                results[pending], pending = tail, None
            elif tail not in ('', 'Fetching 1 selected/reference blob objects',
                              'Fetching pinned commit and complete tree metadata (blob:none)'):
                raise ValueError('unknown inline unittest output: ' + tail)
        elif statuses.fullmatch(line):
            if pending is None:
                raise ValueError('unattributed unittest status: ' + line)
            results[pending], pending = line, None
    if pending is not None:
        raise ValueError('test missing result: ' + pending)
    return results


def original_test_identity(view):
    raw = subprocess.check_output(['git', 'show',
        'd0af2aecc6baf0ec870f51de6ab62d586bc5805d:tests/test_lean_export.py'], cwd=PROJECT)
    if raw != (PROJECT / 'tests/test_lean_export.py').read_bytes() or raw != (view / 'tests/test_lean_export.py').read_bytes():
        raise ValueError('historical differential test changed')
    return {'baseline_commit': 'd0af2aecc6baf0ec870f51de6ab62d586bc5805d',
            'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def copied_files(view):
    """Verify every initial copied input, beyond the core code inventory."""
    receipt = {}
    for base in ('src', 'scripts', 'tests', 'formal', 'vendor', 'verification',
                 'docs', 'examples', 'local/stage2'):
        for p in (view / base).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                name = p.relative_to(view).as_posix()
                receipt[name] = info(p)
                if receipt[name] != info(PROJECT / name):
                    raise ValueError('unexpected content override: ' + name)
    for name in ('.gitattributes', '.gitignore', 'corpus.lock.json', 'lean-toolchain', 'pyproject.toml'):
        receipt[name] = info(view / name)
        if receipt[name] != info(PROJECT / name):
            raise ValueError('unexpected root file override: ' + name)
    return receipt


def run(kind):
    if kind not in ('single', 'full'):
        raise ValueError('expected single or full')
    if kind == 'full':
        single = read(PROJECT / 'verification/stage8-single-09.json')
        start = read(single['start_receipt']['path'])
        if (single['status'] != 'REGRESSION_PASS' or single['tests'] != 1
                or single['results'] != {DIFFERENTIAL: 'ok'}
                or single['code_and_tests'] != code_inventory(PROJECT)
                or anchor(LEAN) != start['lean'] or anchor(__file__) != start['driver']
                or anchor(single['start_receipt']['path']) != single['start_receipt']):
            raise ValueError('unchanged standalone differential must pass first')
        verify(single['artifact_directory'], single['artifact_inventory'])
    folder = ROOT / kind
    folder.mkdir(exist_ok=False)
    before = code_inventory(PROJECT)
    if before != read(PROJECT / 'verification/stage8-final-06.json')['code_and_tests']:
        raise ValueError('core differs from frozen final-06')
    history = historical_report_inventory()
    view_evidence = prepare_regression_view(PROJECT, folder / 'view')
    view = Path(view_evidence['directory'])
    copied = copied_files(view)
    original = original_test_identity(view)
    env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'USERPROFILE', 'COMSPEC') if k in os.environ}
    env.update(PYTHONPATH=os.pathsep.join((str(view / 'src'), str(view / 'tests'),
                                         str(PROJECT / 'local/stage8-deps'))),
               REPO_PROOF_LEAN=str(LEAN))
    enumeration = ('import json,unittest; '
        's=unittest.TestLoader().discover("tests"); '
        'flatten=lambda x: [i for y in x for i in flatten(y)] if isinstance(x,unittest.TestSuite) else [x.id()]; '
        'print(json.dumps(flatten(s)))')
    ids = json.loads(subprocess.check_output([sys.executable, '-c', enumeration], cwd=view, env=env))
    if len(ids) != len(set(ids)) or any('_FailedTest' in x for x in ids):
        raise ValueError('test discovery failed or duplicate test names')
    expected = sorted(ids if kind == 'full' else [DIFFERENTIAL])
    if DIFFERENTIAL not in ids:
        raise ValueError('differential absent from current discovery')
    write(folder / 'expected-tests.json', {'discovered': sorted(ids), 'selected': expected})
    observation = read(ROOT / 'environment-before.json')
    validate_minute(observation)
    pre = environment()
    if (pre['cpu_percent'] >= 35 or pre['available_ram_bytes'] < 7 * 1024**3
            or pre['wsl']['liquidpatrol_pids'] or pre['wsl']['pgrep_exit'] != 1
            or pre['wsl']['ps_exit'] != 0):
        raise ValueError('host not quiet or WSL state unknown: ' + json.dumps(pre))
    expected_affinity = pre['affinity']
    if pre['priority_class'] != 32 or len(expected_affinity) != psutil.cpu_count():
        raise ValueError('coordinator does not have normal priority and all logical CPUs')
    config = read(PROJECT / 'local/stage8/final-06/regression-config.json')
    config['limits']['timeout_seconds'] = 660 if kind == 'single' else 2400
    if config['limits']['tree_memory_bytes'] != 6 * 1024**3:
        raise ValueError('memory profile changed')
    config_path = folder / 'config.json'
    write(config_path, config)
    lean_before = anchor(LEAN)
    version = subprocess.check_output([str(LEAN), '--version']).decode().strip()
    command = [sys.executable, str(PROJECT / 'scripts/stage8_supervise.py'),
        '--config', str(config_path), '--run-dir', str(folder / 'process'),
        '--artifact-root', str(folder), '--', sys.executable, '-m', 'unittest']
    command += ['-v', DIFFERENTIAL] if kind == 'single' else ['discover', '-s', 'tests', '-v']
    start_record = {'kind': kind, 'driver': anchor(__file__), 'environment': pre,
        'minute_observation': anchor(ROOT / 'environment-before.json'),
        'lean': lean_before, 'lean_version': version, 'code_and_tests': before,
        'historical_reports': history, 'view': view_evidence,
        'original_differential_test': original, 'copied_inputs': copied,
        'expected_tests': expected, 'config': anchor(config_path), 'command': command,
        'profile_note': 'Unchanged base supervisor; inherited normal priority and all CPUs; observed read-only below.'}
    write(folder / 'start.json', start_record)
    profiles, timings, host, tracked = {}, {}, [], {}
    t = time.monotonic()
    with (folder / 'supervisor.stdout').open('wb') as out, (folder / 'supervisor.stderr').open('wb') as err:
        process = subprocess.Popen(command, cwd=view, env=env, stdout=out, stderr=err)
        observer = psutil.Process(process.pid)
        psutil.cpu_percent()
        try:
            while process.poll() is None:
                elapsed = time.monotonic() - t
                if elapsed > config['limits']['timeout_seconds'] + 60:
                    raise RuntimeError('outer supervisor deadline exceeded')
                try:
                    for child in observer.children(recursive=True):
                        try:
                            tracked[(child.pid, child.create_time())] = child
                            if child.name().lower() in ('python.exe', 'lean.exe'):
                                value = {'pid': child.pid, 'parent_pid': child.ppid(),
                                    'created': child.create_time(), 'name': child.name(),
                                    'exe': child.exe(), 'priority_class': int(child.nice()),
                                    'affinity': child.cpu_affinity()}
                                key = str(child.pid) + ':' + str(child.create_time()) + ':' + str(value['priority_class']) + ':' + str(value['affinity'])
                                if key not in profiles:
                                    profiles[key] = {**value, 'first_observed_seconds': elapsed}
                        except psutil.Error:
                            pass
                except psutil.Error:
                    pass
                logpath = folder / 'process/stderr.log'
                if logpath.exists():
                    log = logpath.read_bytes().decode('utf-8', errors='replace')
                    prefix = 'test_differential (' + DIFFERENTIAL + ') ... '
                    if prefix in log:
                        timings.setdefault('differential_start_observed_seconds', elapsed)
                        if prefix + 'ok' in log:
                            timings.setdefault('differential_pass_observed_seconds', elapsed)
                if not host or elapsed - host[-1]['elapsed_seconds'] >= 5:
                    host.append({'elapsed_seconds': elapsed, 'cpu_percent': psutil.cpu_percent(),
                                 'available_ram_bytes': psutil.virtual_memory().available})
                    write(folder / 'live-observation.json', {'profiles': list(profiles.values()), 'timings': timings, 'host': host})
                time.sleep(0.25)
        except BaseException as exc:
            if process.poll() is None:
                process.kill()  # retained Windows handle; Job Object kill-on-close drains its members
            process.wait(timeout=30)
            deadline = time.monotonic() + 15
            remaining = []
            while True:
                remaining = [p.pid for p in tracked.values() if p.is_running()]
                if not remaining or time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
            write(folder / 'observer-failure.json', {'error': type(exc).__name__ + ': ' + str(exc),
                'supervisor_exit_code': process.returncode, 'remaining_observed_descendants': remaining,
                'cleanup_basis': 'retained supervisor handle and unchanged Job Object kill-on-close',
                'profiles': list(profiles.values())})
            raise
    resource = read(folder / 'process/resource-report.json')
    raw = (folder / 'process/stderr.log').read_bytes()
    log = raw.decode('utf-8', errors='replace')
    results = parse_results(log)
    summary = re.search(r'^Ran (\d+) tests? in ([\d.]+)s\s*$', log, re.M)
    exact = sorted(results) == expected
    root_profiles = [p for p in profiles.values() if p['parent_pid'] == process.pid]
    lean_profiles = [p for p in profiles.values() if p['name'].lower() == 'lean.exe']
    standard_profile = bool(root_profiles and lean_profiles) and all(
        p['priority_class'] == 32 and p['affinity'] == expected_affinity
        for p in root_profiles + lean_profiles)
    native = all(Path(p['exe']).resolve() == LEAN.resolve() for p in lean_profiles)
    identity = verify_regression_view(PROJECT, view_evidence) and code_inventory(PROJECT) == before
    copied_unchanged = all(info(view / name) == value for name, value in copied.items())
    preserved = historical_report_inventory() == history
    anchors_equal = anchor(LEAN) == lean_before and anchor(config_path) == start_record['config'] and anchor(__file__) == start_record['driver']
    passed = (process.returncode == 0 and resource['status'] == 'PROCESS_PASS'
        and resource['exit_code'] == 0 and resource['remaining_job_processes'] == 0
        and exact and all(x == 'ok' for x in results.values()) and summary is not None
        and int(summary.group(1)) == len(expected) and identity and preserved
        and anchors_equal and standard_profile and native and copied_unchanged)
    result = {'schema': 'stage8-closure-regression-v1', 'kind': kind,
        'status': 'REGRESSION_PASS' if passed else 'REGRESSION_NOT_ACCEPTED',
        'exit_code': process.returncode, 'tests': len(results),
        'unittest_seconds': float(summary.group(2)) if summary else None,
        'expected_tests': expected, 'results': results, 'exact_coverage': exact,
        'no_skips': all(not x.startswith('skipped') for x in results.values()),
        'differential_1547': results.get(DIFFERENTIAL) == 'ok',
        'identity': identity, 'historical_reports_preserved': preserved,
        'copied_inputs_unchanged': copied_unchanged,
        'anchors_unchanged': anchors_equal, 'standard_profile_verified': standard_profile,
        'native_lean_verified': native, 'profiles': list(profiles.values()),
        'timings': timings, 'host_during_test': host, 'resources': resource,
        'code_and_tests': before, 'view': view_evidence, 'start_receipt': anchor(folder / 'start.json'),
        'stdout': anchor(folder / 'process/stdout.log'), 'stderr': anchor(folder / 'process/stderr.log'),
        'environment_after': environment()}
    write(folder / 'observation.json', {'profiles': list(profiles.values()), 'timings': timings, 'host': host})
    result['artifact_inventory'] = inventory(folder)
    result['artifact_directory'] = str(folder)
    write(PROJECT / ('verification/stage8-' + kind + '-09.json'), result)
    print(result['status'], result['tests'], result['unittest_seconds'], flush=True)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(run(sys.argv[1]))
