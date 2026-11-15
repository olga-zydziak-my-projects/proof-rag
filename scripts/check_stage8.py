"""Frozen-code Stage 8 validation with explicit whole-stage acceptance gates."""
import argparse
from hashlib import sha1, sha256
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
from repo_proof.stage8_acceptance import evaluate, formal_ladder_complete
from repo_proof.stage8_artifacts import inventory, verify
from stage6 import new_directory
from stage6_regressions import code_inventory, prepare_regression_view, verify_regression_view
from stage8 import prepare, query
from stage8_lean_check import check as lean_check, check_sources, check_ladder

BASE = 'd0af2aecc6baf0ec870f51de6ab62d586bc5805d'


def historical_report_inventory():
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
        '--', 'verification', 'docs/stage8-results.md', 'docs/stage8-review.md',
        'docs/stage8-reconnaissance.md'], cwd=PROJECT).decode().splitlines()
    result = {}
    for path in paths:
        original = subprocess.check_output(['git', 'show', BASE+':'+path], cwd=PROJECT)
        raw = (PROJECT/path).read_bytes()
        # Historical text blobs include both LF and CRLF in Git itself.
        # Accept existing checkout line endings, then anchor exact raw bytes.
        if raw.replace(b'\r\n', b'\n') != original.replace(b'\r\n', b'\n'):
            raise ValueError('historical report differs from baseline: '+path)
        blob = sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()
        result[path] = {'git_blob': blob, 'raw_sha256': sha256(raw).hexdigest()}
    return result


def passed_test(log, test_id):
    method = test_id.rsplit('.', 1)[-1]
    return method+' ('+test_id+') ... ok' in log.splitlines()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--report', required=True)
    p.add_argument('--lean', required=True)
    p.add_argument('--independent-only', action='store_true',
                   help='exit success for independent checks, without stage acceptance')
    p.add_argument('--manifest')
    p.add_argument('--manifest-sha256')
    p.add_argument('--locations')
    p.add_argument('--corpus-evidence', help='pinned version and patch audit evidence')
    p.add_argument('--review', help='independent review anchored to current code inventory')
    p.add_argument('--regression-memory-bytes', type=int, default=4294967296,
                   help='explicit regression-only memory experiment, default 4 GiB')
    a = p.parse_args()
    folder = new_directory(PROJECT, a.run_dir)
    output = Path(a.report)
    if output.exists():
        raise ValueError('report must be new')
    config_path = PROJECT/'verification/stage8-benchmark-config.json'
    config = read_json(config_path)
    before = code_inventory(PROJECT)
    report = {'status': 'IN_PROGRESS', 'mode': 'independent-only' if a.independent_only else 'whole-stage',
              'corpus_status': 'NOT_VALIDATED',
              'formal_bridge': {'status': 'NOT_VALIDATED'},
              'pilot_status': 'NOT_RUN', 'source_to_answer_lean': False,
              'code_and_tests': before, 'config_sha256': digest(config_path),
              'corpus_manifest_sha256': digest(PROJECT/'verification/stage8-corpus.json'),
              'benchmark_variants': [], 'fixture_queries': [], 'checked_artifacts': []}
    if a.regression_memory_bytes <= 0:
        raise ValueError('regression memory limit must be positive')
    report['historical_reports_before'] = historical_report_inventory()
    if a.review:
        review = read_json(a.review)
        if review.get('code_and_tests') != before:
            raise ValueError('independent review code anchor is stale')
        report['independent_review'] = review
    report['input_anchors'] = {name: {'path': str(Path(value).resolve()), 'sha256': digest(value)}
        for name, value in (('manifest', a.manifest), ('locations', a.locations),
                            ('corpus_evidence', a.corpus_evidence), ('review', a.review)) if value}
    if a.manifest and report['input_anchors']['manifest']['sha256'] != a.manifest_sha256:
        raise ValueError('actual manifest differs from independent anchor')
    def save():
        output.write_bytes(canonical(report))
    def preserve_artifacts(destination):
        report['checked_artifacts'].append({'directory': str(destination.resolve()),
                                           'inventory': inventory(destination)})
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
            preserve_artifacts(folder/('limit-'+kind))
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
                preserve_artifacts(destination)
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
            preserve_artifacts(Path(args.run_dir))
        preserve_artifacts(folder/'fixture-index')
        report['lean_graph'] = lean_check(folder/'lean-graph', Path(a.lean).resolve(), config_path)
        preserve_artifacts(folder/'lean-graph')
        first = manifest['repositories'][0]
        bridge = check_sources(folder/'source-bridge-fixture', Path(a.lean).resolve(), config_path,
            fixture/'manifest.json', anchor, locations,
            (first['repo_id'], first['commit'], first['files'][0]['path']))
        report['formal_bridge'] = {'status': 'SOURCE_BRIDGE_PASS'
            if bridge['status'] == 'SOURCE_TO_ANSWER_PASS' else 'FAILED', 'evidence': bridge}
        preserve_artifacts(folder/'source-bridge-fixture')
        preserve_artifacts(fixture)
        report['lean_ladder'] = check_ladder(folder/'lean-ladder', Path(a.lean).resolve(), config_path)['runs']
        preserve_artifacts(folder/'lean-ladder')
        if a.manifest:
            from stage8_pilot import run as run_pilot
            from repo_proof.stage8_corpus_audit import verify_corpus
            if not a.manifest_sha256 or not a.locations:
                raise ValueError('real pilot requires manifest anchor and locations')
            real_locations = {(r['repo_id'], r['commit']): r['directory'] for r in read_json(a.locations)}
            if not a.corpus_evidence:
                raise ValueError('real pilot requires pinned version and patch evidence')
            evidence = verify_corpus(a.manifest, a.manifest_sha256, a.corpus_evidence, real_locations)
            report['corpus_evidence'] = evidence
            report['pilot'] = run_pilot(folder/'real-pilot', Path(a.lean).resolve(), config_path,
                Path(a.manifest).resolve(), a.manifest_sha256, real_locations)
            report['pilot']['version_and_patch_evidence_checked'] = evidence['status'] == 'CORPUS_EVIDENCE_CHECKED'
            preserve_artifacts(folder/'real-pilot')
            report['corpus_status'] = 'CONNECTED_SOURCE_IO_CHECKED' if report['pilot']['connected_projects'] else 'REJECTED'
        else:
            report['corpus_status'] = 'MISSING_REAL_MANIFEST'
        # These are real process tests, including suspended assignment failure,
        # monitor crash and orphaned grandchildren. Record their complete log.
        integration_destination = folder/'supervisor-integration'
        integration = supervise(integration_destination, [sys.executable, '-m', 'unittest', 'discover',
            '-s', 'tests', '-p', 'test_stage8_supervise.py', '-v'])
        integration_log = (integration_destination/'stderr.log').read_bytes()
        (folder/'supervisor-tests.log').write_bytes(integration_log)
        supervisor_count = re.search(rb'^Ran (\d+) tests? in ', integration_log, re.M)
        report['supervisor_integration_pass'] = (integration['status'] == 'PROCESS_PASS' and supervisor_count is not None
            and int(supervisor_count.group(1)) >= 11 and b'skipped' not in integration_log)
        preserve_artifacts(integration_destination)
        report['source_index_measurements'] = []
        measurements = [('synthetic', ['--synthetic-files', '10000'])]
        if a.manifest:
            if not a.manifest_sha256 or not a.locations:
                raise ValueError('real manifest requires independent anchor and locations')
            measurements.append(('real', ['--manifest', str(Path(a.manifest).resolve()),
                '--manifest-sha256', a.manifest_sha256, '--locations', str(Path(a.locations).resolve())]))
        for label, arguments in measurements:
            destination = folder/('index-'+label)
            resource = supervise(destination, [sys.executable, str(PROJECT/'scripts/stage8_index_benchmark.py'),
                '--run-dir', str(destination/'work'), *arguments])
            path = destination/'work/index-benchmark.json'
            detail = read_json(path) if path.exists() else {'status': 'FAILED'}
            detail.update(resource=resource, artifact_verified=resource['status'] == 'PROCESS_PASS' and path.exists())
            report['source_index_measurements'].append(detail)
            preserve_artifacts(destination)
        save()
        view = prepare_regression_view(PROJECT, folder/'regression-view')
        # Explicit nonsecret process variables; no API credentials are read.
        env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'USERPROFILE', 'COMSPEC') if k in os.environ}
        env.update(PYTHONPATH=os.pathsep.join((str(Path(view['directory'])/'src'), str(PROJECT/'local/stage8-deps'))),
                   REPO_PROOF_LEAN=str(Path(a.lean).resolve()))
        regression_config = read_json(config_path)
        regression_config['limits']['timeout_seconds'] = 2400
        regression_config['limits']['tree_memory_bytes'] = a.regression_memory_bytes
        regression_config_path = folder/'regression-config.json'
        regression_config_path.write_bytes(canonical(regression_config))
        regression_destination = folder/'regression-process'
        regression = subprocess.run([sys.executable, str(PROJECT/'scripts/stage8_supervise.py'),
            '--config', str(regression_config_path), '--run-dir', str(regression_destination),
            '--artifact-root', str(folder), '--', sys.executable, '-m', 'unittest',
            'discover', '-s', 'tests', '-v'], cwd=view['directory'], env=env,
            capture_output=True, timeout=2460)
        stdout = (regression_destination/'stdout.log').read_bytes()
        stderr = (regression_destination/'stderr.log').read_bytes()
        (folder/'regressions.stdout').write_bytes(stdout)
        (folder/'regressions.stderr').write_bytes(stderr)
        log = stderr.decode('utf-8', errors='replace')
        count = re.search(r'^Ran (\d+) tests? in ', log, re.M)
        report['regressions'] = {'exit_code': regression.returncode, 'tests': int(count.group(1)) if count else None,
            'no_skips': 'skipped=' not in log and '... skipped ' not in log,
            'identity': verify_regression_view(PROJECT, view), 'view': view,
            'differential_1547': 'test_differential (test_lean_export.LeanExportTests.test_differential) ... ok' in log,
            'stderr_sha256': sha256(stderr).hexdigest(),
            'resources': read_json(regression_destination/'resource-report.json'),
            'limit_note': 'regression timeout 2400 seconds, explicit memory bytes '+str(a.regression_memory_bytes)+
                          ', artifact limit '+str(regression_config['limits']['artifact_bytes'])}
        preserve_artifacts(regression_destination)
        # Acceptance uses individual recorded test names, so a missing test or
        # an unrelated passing suite cannot stand in for a required rejection.
        negative_names = {
            'sources': 'test_stage8_sources_streaming.StreamingSourceTests.test_reanchored_source_hash_substitution_is_rejected',
            'mapping': 'test_stage8.Stage8Tests.test_bad_semantics_even_with_new_manifest_hash',
            'versions': 'test_stage8.Stage8Tests.test_collision_versions_and_missing_resolution',
            'certificates': 'test_stage8.Stage8Tests.test_rejects_incomplete_or_substituted_certificates',
            'answers': 'test_stage8_formal.Stage8FormalTests.test_contextual_source_export_bytes_rules_universe_and_answer',
            'proofs': 'test_stage8_formal.Stage8FormalTests.test_contextual_source_export_bytes_rules_universe_and_answer'}
        report['negative_test_cases'] = negative_names
        report['negative_tests'] = {kind: passed_test(log, name)
                                    for kind, name in negative_names.items()}
        report['code_identity_after'] = before == code_inventory(PROJECT)
        report['config_identity_after'] = digest(config_path) == report['config_sha256']
        report['manifest_identity_after'] = (digest(PROJECT/'verification/stage8-corpus.json') == report['corpus_manifest_sha256']
            and all(Path(v['path']).is_file() and digest(v['path']) == v['sha256']
                    for v in report['input_anchors'].values()))
        if a.manifest:
            evidence_after = verify_corpus(a.manifest, a.manifest_sha256, a.corpus_evidence, real_locations)
            report['manifest_identity_after'] &= evidence_after == report['corpus_evidence']
        report['historical_reports_preserved'] = historical_report_inventory() == report['historical_reports_before']
        for receipt in report['checked_artifacts']:
            verify(receipt['directory'], receipt['inventory'])
        for receipt in report.get('pilot', {}).get('queries', []):
            verify(receipt['artifact_directory'], receipt['artifact_inventory'])
        report['artifacts_complete_after'] = True
        changed = subprocess.check_output(['git', 'diff', '--no-renames', '--diff-filter=CDMRTUXB',
            '--name-only', '9d590b5b7538fb20f1061ef31e266f1ee9f221e8', '--'], cwd=PROJECT).decode().splitlines()
        report['historical_changes'] = changed
        report['scaling_status'] = {str(n): ('GRAPH_PASS' if len([v for v in report['benchmark_variants'] if v['nodes'] == n]) == 3
                                         and all(v['passed'] for v in report['benchmark_variants'] if v['nodes'] == n)
                                         else 'NOT_PASSED') for n in config['sizes']}
        report['independent_parts_pass'] = (all(v['passed'] for v in report['benchmark_variants'])
            and all(v['passed'] for v in report['resource_enforcement_tests'])
            and report['lean_graph']['status'] == 'LEAN_GRAPH_PASS' and regression.returncode == 0
            and report['regressions']['no_skips'] and report['regressions']['differential_1547']
            and report['code_identity_after'] and report['config_identity_after'] and report['manifest_identity_after']
            and report['deterministic_source_fixture']
            and report['artifacts_complete_after']
            and report['formal_bridge']['status'] == 'SOURCE_BRIDGE_PASS'
            and formal_ladder_complete(report['lean_ladder'])
            and report['supervisor_integration_pass']
            and all(v.get('status') == 'SOURCE_INDEX_PASS' and v.get('artifact_verified') is True
                    for v in report['source_index_measurements'])
            and all(path == 'README.md' or path.startswith(('docs/stage8', 'scripts/stage8',
                'scripts/check_stage8', 'src/repo_proof/stage8', 'tests/test_stage8',
                'formal/ContextualSourceBinding.lean', 'verification/stage8')) for path in changed)
            and report['historical_reports_preserved'])
        report['acceptance'] = evaluate(report)
        components = report['acceptance']['components']
        report['corpus_status'] = 'CORPUS_PASS' if components['corpus'] else 'CORPUS_NOT_ACCEPTED'
        report['implementation_status'] = 'SOURCE_BRIDGE_PASS' if components['formal_bridge'] else 'SOURCE_BRIDGE_NOT_ACCEPTED'
        report['pilot_status'] = 'STAGE8_PILOT_PASS' if components['pilot'] else 'PILOT_NOT_ACCEPTED'
        report['source_to_answer_lean'] = components['pilot']
        report['regression_status'] = 'REGRESSION_PASS' if components['regressions'] else 'REGRESSION_NOT_ACCEPTED'
        report['status'] = report['acceptance']['status']
    except Exception as exc:
        report.update(status='STAGE8_FAILED', error=type(exc).__name__+': '+str(exc))
    finally:
        save()
    print(report['status'], flush=True)
    passed = report['status'] == 'STAGE8_PASS'
    if a.independent_only:
        passed = report.get('independent_parts_pass', False)
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
