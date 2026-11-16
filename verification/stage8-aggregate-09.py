"""Recheck frozen evidence and apply the unchanged Stage 8 acceptance function.

prepare writes a review candidate. finalize accepts only an independent review
bound to that exact candidate, both auxiliary tools, and the current core.
Neither phase executes Lean or modifies the historical evidence.
"""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT / 'src'), str(PROJECT / 'scripts'),
                str(PROJECT / 'local/stage8-deps')]
from repo_proof.stage8_acceptance import evaluate
from repo_proof.stage8_artifacts import verify
from stage6_regressions import code_inventory, verify_regression_view
from check_stage8 import historical_report_inventory, passed_test


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


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def controls():
    path = PROJECT / 'verification/stage8-close-09.py'
    spec = importlib.util.spec_from_file_location('closure_control_09', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def recheck():
    old_path = PROJECT / 'verification/stage8-final-06.json'
    old = read(old_path)
    code = code_inventory(PROJECT)
    reuse_path = PROJECT / 'verification/stage8-reuse-review-09.json'
    reuse = read(reuse_path)
    require(code == old['code_and_tests'] == reuse['code_and_tests'], 'frozen core identity')
    require(reuse['status'] == 'REUSE_REVIEW_PASS' and reuse['gaps'] == []
            and reuse['eligible_for_core_evidence_reuse'] is True
            and all(r['status'] == 'PASS' for r in reuse['checks']), 'reuse review not passed')
    for path, expected in reuse['used_reports'].items():
        require(info(path) == expected, 'reused report changed: ' + path)
    require(historical_report_inventory() == old['historical_reports_before'], 'historical reports changed')
    for value in old['input_anchors'].values():
        require(info(value['path'])['sha256'] == value['sha256'], 'input anchor changed')
    require(info(PROJECT / 'verification/stage8-corpus.json')['sha256'] == old['corpus_manifest_sha256'],
            'fixture manifest changed')
    require(info(PROJECT / 'verification/stage8-benchmark-config.json')['sha256'] == old['config_sha256'],
            'original configuration changed')
    for receipt in old['checked_artifacts']:
        verify(receipt['directory'], receipt['inventory'])
    for query in old['pilot']['queries']:
        verify(query['artifact_directory'], query['artifact_inventory'])
    control = controls()
    new = {}
    for kind in ('single', 'full'):
        path = PROJECT / ('verification/stage8-' + kind + '-09.json')
        if not path.exists():
            continue
        result = read(path)
        require(result['code_and_tests'] == code, 'regression core identity')
        verify(result['artifact_directory'], result['artifact_inventory'])
        start = read(result['start_receipt']['path'])
        require(anchor(result['start_receipt']['path']) == result['start_receipt'], 'start receipt changed')
        require(anchor(control.LEAN) == start['lean'], 'Lean changed')
        require(anchor(PROJECT / 'verification/stage8-close-09.py') == start['driver'], 'regression driver changed')
        require(anchor(start['config']['path']) == start['config'], 'regression config changed')
        require(verify_regression_view(PROJECT, result['view']), 'regression view identity')
        require(all(info(Path(result['view']['directory']) / name) == value
                    for name, value in start['copied_inputs'].items()), 'copied inputs changed')
        require(anchor(result['stdout']['path']) == result['stdout']
                and anchor(result['stderr']['path']) == result['stderr'], 'regression logs changed')
        log = Path(result['stderr']['path']).read_bytes().decode('utf-8', errors='replace')
        results = control.parse_results(log)
        discovery = read(Path(result['artifact_directory']) / 'expected-tests.json')
        expected = result['expected_tests']
        require(expected == start['expected_tests'] == discovery['selected'], 'coverage receipt mismatch')
        require(expected == (discovery['discovered'] if kind == 'full' else [control.DIFFERENTIAL]),
                'selected scope mismatch')
        require(len(discovery['discovered']) == len(set(discovery['discovered'])), 'duplicate discovered tests')
        require(results == result['results'] and sorted(results) == expected, 'test coverage mismatch')
        summary = re.search(r'^Ran (\d+) tests? in ([\d.]+)s\s*$', log, re.M)
        require(summary is not None and int(summary.group(1)) == len(expected) == result['tests']
                and float(summary.group(2)) == result['unittest_seconds'], 'unittest summary mismatch')
        if result['status'] == 'REGRESSION_PASS':
            require(all(v == 'ok' for v in results.values()) and re.search(r'^OK\s*$', log, re.M)
                    and result['exit_code'] == 0 and result['no_skips'] is True
                    and result['differential_1547'] is True and result['exact_coverage'] is True
                    and result['identity'] is True and result['copied_inputs_unchanged'] is True
                    and result['historical_reports_preserved'] is True and result['anchors_unchanged'] is True,
                    'passing regression receipt inconsistent')
        require(result['resources'] == read(Path(result['artifact_directory']) / 'process/resource-report.json'),
                'resource receipt mismatch')
        limits = read(start['config']['path'])['limits']
        require(limits['timeout_seconds'] == (660 if kind == 'single' else 2400)
                and limits['tree_memory_bytes'] == 6 * 1024**3
                and not any('affinity' in k or 'priority' in k for k in limits), 'nonstandard resource profile')
        require(result['resources']['remaining_job_processes'] == 0
                and result['standard_profile_verified'] is True and result['native_lean_verified'] is True,
                'process profile or cleanup not verified')
        control.validate_minute(read(start['minute_observation']['path']))
        require(anchor(start['minute_observation']['path']) == start['minute_observation'], 'minute observation changed')
        new[kind] = result
    require('single' in new, 'fresh standalone test missing')
    return old, reuse, new, code


def candidate():
    old, reuse, new, code = recheck()
    report = deepcopy(old)
    report.update(schema='stage8-evidence-closure-v1', mode='reuse-verified-frozen-evidence-plus-fresh-regression',
        created_utc=datetime.now(timezone.utc).isoformat(), code_and_tests=code,
        evidence_reuse={'baseline': anchor(PROJECT / 'verification/stage8-final-06.json'),
            'review': anchor(PROJECT / 'verification/stage8-reuse-review-09.json'),
            'core_semantic_review': anchor(PROJECT / 'verification/stage8-independent-core-review-06.json'),
            'previous_final_review': anchor(PROJECT / 'verification/stage8-final-review-08.json'),
            'note': 'Six proofs, nine graph variants, indexing, ladder and supervisor integration are reused after exact identity verification; no expensive reruns.'},
        closure_tools={name: anchor(PROJECT / ('verification/' + name)) for name in
                       ('stage8-close-09.py', 'stage8-aggregate-09.py')},
        fresh_test_reports={kind: anchor(PROJECT / ('verification/stage8-' + kind + '-09.json')) for kind in new},
        independent_review={'reviewer_id': '', 'independent': False, 'blocking_findings': ['final review pending']},
        historical_reports_preserved=True, artifacts_complete_after=True,
        code_identity_after=True, config_identity_after=True, manifest_identity_after=True)
    if 'full' in new:
        full = new['full']
        passed = (new['single']['status'] == 'REGRESSION_PASS' and full['status'] == 'REGRESSION_PASS'
            and full['resources']['status'] == 'PROCESS_PASS' and full['resources']['exit_code'] == 0
            and full['resources']['remaining_job_processes'] == 0
            and all(x == 'ok' for x in full['results'].values()) and full['exact_coverage'] is True
            and full['identity'] is True and full['copied_inputs_unchanged'] is True
            and full['anchors_unchanged'] is True and full['historical_reports_preserved'] is True)
        report['regressions'] = {**full, 'exit_code': 0 if passed else 2,
                                 'identity': passed and full['identity'],
                                 'evidence_origin': 'fresh full current suite close-09'}
        log = Path(full['stderr']['path']).read_bytes().decode('utf-8', errors='replace')
        report['negative_tests'] = {k: passed_test(log, v) for k, v in old['negative_test_cases'].items()}
    else:
        require(new['single']['status'] != 'REGRESSION_PASS', 'passing standalone requires full regression')
        report['regressions'] = {'exit_code': None, 'tests': 0, 'no_skips': False,
            'identity': True, 'differential_1547': False,
            'reason': 'Fresh full suite not started because standalone differential did not pass; historical final-06 remains unchanged.'}
    report['independent_parts_pass'] = all(v for k, v in evaluate(report)['components'].items() if k != 'review')
    report['acceptance'] = evaluate(report)
    report['status'] = report['acceptance']['status']
    report['regression_status'] = 'REGRESSION_PASS' if report['acceptance']['components']['regressions'] else 'REGRESSION_NOT_ACCEPTED'
    report['review_state'] = 'AWAITING_FINAL_INDEPENDENT_REVIEW'
    path = PROJECT / 'verification/stage8-candidate-09.json'
    require(not path.exists(), 'candidate already exists; use new evidence name rather than overwrite')
    write(path, report)
    print('CANDIDATE', report['status'], flush=True)


def finalize():
    candidate_path = PROJECT / 'verification/stage8-candidate-09.json'
    report = read(candidate_path)
    _, _, new, code = recheck()
    review_path = PROJECT / 'verification/stage8-final-review-09.json'
    review = read(review_path)
    require(review.get('candidate') == anchor(candidate_path), 'review not bound to exact candidate')
    require(review.get('code_and_tests') == code == report['code_and_tests'], 'review core mismatch')
    require(review.get('independent') is True and bool(review.get('reviewer_id')), 'reviewer missing')
    require(review.get('closure_tools') == report['closure_tools'], 'review tool anchors mismatch')
    for value in report['closure_tools'].values():
        require(anchor(value['path']) == value, 'closure tool changed after candidate')
    for kind, value in report['fresh_test_reports'].items():
        require(kind in new and anchor(value['path']) == value, 'regression report changed after review candidate')
    require(anchor(report['evidence_reuse']['review']['path']) == report['evidence_reuse']['review'], 'reuse review changed')
    report['independent_review'] = review
    report['final_review_receipt'] = anchor(review_path)
    report['reviewed_candidate'] = anchor(candidate_path)
    report['review_state'] = 'FINAL_INDEPENDENT_REVIEW_COMPLETE'
    report['acceptance'] = evaluate(report)
    report['status'] = report['acceptance']['status']
    report['blocking_findings'] = review['blocking_findings']
    path = PROJECT / 'verification/stage8-status-09.json'
    require(not path.exists(), 'final report already exists')
    write(path, report)
    print(report['status'], json.dumps(report['acceptance']['components']), flush=True)
    return 0 if report['status'] == 'STAGE8_PASS' else 2


if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        candidate()
    elif sys.argv[1:] == ['finalize']:
        raise SystemExit(finalize())
    else:
        raise SystemExit('expected prepare or finalize')
