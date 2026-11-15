"""Frozen-code validation of independent Stage8 parts; corpus remains BLOCKED."""
import argparse
from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.extraction import read_json
from repo_proof.stage5_v2 import canonical
from repo_proof.stage8_fixture import create
from repo_proof.stage8_store import digest
from repo_proof.stage8_sources import identity
from stage6 import new_directory
from stage6_regressions import code_inventory, prepare_regression_view, verify_regression_view
from stage8 import prepare, query
from stage8_lean_check import check as lean_check


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--report', required=True)
    p.add_argument('--lean', required=True)
    a = p.parse_args()
    folder = new_directory(PROJECT, a.run_dir)
    output = Path(a.report)
    if output.exists():
        raise ValueError('report must be new')
    config_path = PROJECT/'verification/stage8-benchmark-config.json'
    config = read_json(config_path)
    before = code_inventory(PROJECT)
    report = {'status': 'IN_PROGRESS', 'corpus_status': 'STAGE8_CORPUS_BLOCKED',
              'pilot_status': 'NOT_RUN_CORPUS_BLOCKED', 'source_to_answer_lean': False,
              'code_and_tests': before, 'config_sha256': digest(config_path),
              'corpus_manifest_sha256': digest(PROJECT/'verification/stage8-corpus.json'),
              'benchmark_variants': [], 'fixture_queries': []}
    def save():
        output.write_bytes(canonical(report))
    def supervise(destination, command, cfg=config_path):
        result = subprocess.run([sys.executable, str(PROJECT/'scripts/stage8_supervise.py'),
            '--config', str(cfg), '--run-dir', str(destination), '--', *command],
            cwd=PROJECT, capture_output=True, timeout=config['limits']['timeout_seconds']+60)
        return read_json(destination/'resource-report.json')
    save()
    try:
        # Small deliberate timeout/resource-limit tests are not benchmarks.
        report['resource_enforcement_tests'] = []
        for kind in ('timeout', 'memory'):
            modified = read_json(config_path)
            modified['limits']['timeout_seconds'] = 0.15 if kind == 'timeout' else 10
            if kind == 'memory':
                modified['limits']['tree_memory_bytes'] = 1
            path = folder/(kind+'-test-config.json')
            path.write_bytes(canonical(modified))
            controlled = supervise(folder/('limit-'+kind), [sys.executable, '-c', 'import time; time.sleep(5)'], path)
            expected = 'TIMEOUT' if kind == 'timeout' else 'RESOURCE_LIMIT'
            report['resource_enforcement_tests'].append({'kind': kind, 'expected': expected,
                'actual': controlled['status'], 'passed': controlled['status'] == expected})
        # Each variant has its own process. No parallel heavy jobs or OS-cold claim.
        for n in config['sizes']:
            for family in config['families']:
                destination = folder/(str(n)+'-'+family)
                resource = supervise(destination, [sys.executable, str(PROJECT/'scripts/stage8.py'),
                    'benchmark', '--nodes', str(n), '--family', family,
                    '--config', str(config_path), '--run-dir', str(destination/'work')])
                detail = read_json(destination/'work/benchmark.json') if (destination/'work/benchmark.json').exists() else {}
                row = {'nodes': n, 'family': family, 'resource': resource, 'benchmark': detail,
                    'passed': resource['status'] == 'PROCESS_PASS' and detail.get('status') == 'GRAPH_PASS'}
                report['benchmark_variants'].append(row)
                save()
                print(n, family, resource['status'], detail.get('status'), flush=True)
        # Genuine source bytes, but manufactured local repos: NOT a real pilot.
        fixture = folder/'synthetic-source-fixture'
        manifest, anchor, locations = create(fixture)
        args = SimpleNamespace(manifest=str(fixture/'manifest.json'), manifest_sha256=anchor,
            locations=str(fixture/'locations.json'), config=str(config_path), run_dir=str(folder/'fixture-index'))
        report['fixture_prepare'] = prepare(args)
        first_answer = None
        for i, (repo, path) in enumerate([('a', 'local/a.mojom'), ('b', 'local/shared.mojom'),
                                        ('c', 'local/shared.mojom'), ('a', 'local/isolated.mojom'),
                                        ('a', 'local/a.mojom')]):
            rev = next(r['commit'] for r in manifest['repositories'] if r['repo_id'] == repo)
            args.repo_id, args.commit, args.path = repo, rev, path
            args.index_dir, args.run_dir = str(folder/'fixture-index'), str(folder/('fixture-query-'+str(i)))
            outcome = query(args)
            answer = read_json(Path(args.run_dir)/'answer.json')
            if i == 0:
                first_answer = canonical(answer)
                first_cert = (Path(args.run_dir)/'certificate.parquet').read_bytes()
            if i == 4:
                report['deterministic_source_fixture'] = (first_answer == canonical(answer)
                    and first_cert == (Path(args.run_dir)/'certificate.parquet').read_bytes())
            report['fixture_queries'].append({'outcome': outcome, 'answer': answer})
        report['lean_graph'] = lean_check(folder/'lean-graph', Path(a.lean).resolve(), config_path)
        save()
        view = prepare_regression_view(PROJECT, folder/'regression-view')
        # Explicit nonsecret process variables; no API credentials are read.
        env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'USERPROFILE', 'COMSPEC') if k in os.environ}
        env.update(PYTHONPATH=os.pathsep.join((str(Path(view['directory'])/'src'), str(PROJECT/'local/stage8-deps'))),
                   REPO_PROOF_LEAN=str(Path(a.lean).resolve()))
        regression = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
            cwd=view['directory'], env=env, capture_output=True, timeout=2400)
        (folder/'regressions.stdout').write_bytes(regression.stdout)
        (folder/'regressions.stderr').write_bytes(regression.stderr)
        log = regression.stderr.decode('utf-8', errors='replace')
        count = re.search(r'^Ran (\d+) tests? in ', log, re.M)
        report['regressions'] = {'exit_code': regression.returncode, 'tests': int(count.group(1)) if count else None,
            'no_skips': 'skipped=' not in log and '... skipped ' not in log,
            'identity': verify_regression_view(PROJECT, view), 'view': view,
            'differential_1547': 'test_differential (test_lean_export.LeanExportTests.test_differential) ... ok' in log,
            'stderr_sha256': sha256(regression.stderr).hexdigest()}
        report['code_identity_after'] = before == code_inventory(PROJECT)
        report['config_identity_after'] = digest(config_path) == report['config_sha256']
        report['manifest_identity_after'] = digest(PROJECT/'verification/stage8-corpus.json') == report['corpus_manifest_sha256']
        changed = subprocess.check_output(['git', 'diff', '--no-renames', '--diff-filter=CDMRTUXB',
            '--name-only', '9d590b5b7538fb20f1061ef31e266f1ee9f221e8', '--'], cwd=PROJECT).decode().splitlines()
        report['historical_changes'] = changed
        report['scaling_status'] = {str(n): ('GRAPH_PASS' if all(v['passed'] for v in report['benchmark_variants'] if v['nodes'] == n)
                                         else 'NOT_PASSED') for n in config['sizes']}
        report['independent_parts_pass'] = (all(v['passed'] for v in report['benchmark_variants'])
            and all(v['passed'] for v in report['resource_enforcement_tests'])
            and report['lean_graph']['status'] == 'LEAN_GRAPH_PASS' and regression.returncode == 0
            and report['regressions']['no_skips'] and report['regressions']['differential_1547']
            and report['code_identity_after'] and report['config_identity_after'] and report['manifest_identity_after']
            and report['deterministic_source_fixture'] and changed == ['README.md'])
        # Corpus blockage takes precedence over synthetic successes; never STAGE8_PASS.
        report['status'] = 'STAGE8_CORPUS_BLOCKED' if report['independent_parts_pass'] else 'STAGE8_FAILED'
    except Exception as exc:
        report.update(status='STAGE8_FAILED', error=type(exc).__name__+': '+str(exc))
    finally:
        save()
    print(report['status'], flush=True)
    return 0 if report.get('independent_parts_pass') else 2


if __name__ == '__main__':
    raise SystemExit(main())
