"""Final Stage 7 validation: replay authentic responses, 8 holdouts, 3 fresh proofs, regressions.

The original 32-call evaluation remains immutable. Replay is explicitly post-hoc.
This command makes at most 8 NEW requests; do not rerun it within the same
40-request experiment. For a new experiment freeze a new set and budget first.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage7 import ClaudeInterpreter, Stage7Error, SYSTEM, parse_response, resolve, run
from repo_proof.stage6_cache import anchored_capture, validate_cache
from repo_proof.stage5_v2 import canonical
from evaluate_stage7 import RecordedInterpretation
from stage6 import new_directory
from stage6_regressions import code_inventory, prepare_regression_view, verify_regression_view
from stage6_select_queries import fixed_point


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evaluation', required=True)
    p.add_argument('--cache-dir', required=True)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--lean', required=True)
    p.add_argument('--report', required=True)
    a = p.parse_args()
    folder = new_directory(PROJECT, a.run_dir)
    output = Path(a.report)
    if output.exists():
        raise ValueError('report must be new')
    before = code_inventory(PROJECT)
    report = {'status': 'IN_PROGRESS', 'passed': False,
              'replay_is_post_hoc': True, 'code_and_tests': before,
              'holdout': [], 'replay': [], 'full_runs': []}
    def save():
        output.write_bytes(canonical(report))
    save()
    regression = None
    try:
        original_raw = Path(a.evaluation).read_bytes()
        original = json.loads(original_raw)
        frozen_raw = (PROJECT/'verification/stage7-questions.json').read_bytes()
        cases = json.loads(frozen_raw)
        holdout_raw = (PROJECT/'verification/stage7-holdout.json').read_bytes()
        holdouts = json.loads(holdout_raw)
        if (original['set_sha256'] != sha256(frozen_raw).hexdigest()
                or original['prompt_sha256'] != sha256(SYSTEM.encode()).hexdigest()
                or original['requests'] != 32 or len(original['cases']) != len(cases)
                or len(holdouts) != 8):
            raise ValueError('frozen experiment identity or request budget mismatch')
        (folder/'original-evaluation.json').write_bytes(original_raw)
        report.update(original_evaluation_sha256=sha256(original_raw).hexdigest(),
                      original_claude_correct=original['correct'], original_total=original['total'],
                      original_status=original['status'], holdout_sha256=sha256(holdout_raw).hexdigest(),
                      prompt_sha256=original['prompt_sha256'], model=original['model'],
                      effort=original['effort'], sdk_version=original['sdk_version'])
        c = anchored_capture(PROJECT)
        validate_cache(PROJECT, Path(a.cache_dir).absolute(), captured=c)
        selected = []
        for case, row in zip(cases, original['cases']):
            if row['id'] != case['id'] or row['question'] != case['question']:
                raise ValueError('question/response linkage changed')
            raw = row['api']['response']
            response = SimpleNamespace(stop_reason=raw['stop_reason'],
                content=[SimpleNamespace(**b) for b in raw['content']])
            value = parse_response(response, case['question'])
            if value != row['interpretation']:
                raise ValueError('persisted interpretation differs from API response')
            plan = resolve(value, case['question'], c.graph['nodes'])
            passed = plan['status'] == case['status'] and plan['root'] == case['root']
            report['replay'].append({'id': case['id'], 'interpretation': value,
                                     'plan': plan, 'passed': passed})
            if passed and plan['status'] == 'ready' and plan['root'] not in [s[0] for s in selected]:
                selected.append((plan['root'], case, value, row['api']))
        save()
        # Eight fresh questions frozen before the local fix; prompt unchanged.
        client = ClaudeInterpreter(original['model'], original['effort'], limit=8)
        if client.sdk_version != original['sdk_version']:
            raise ValueError('SDK changed within experiment')
        for case in holdouts:
            row = dict(case)
            try:
                value, evidence = client.interpret(case['question'])
                plan = resolve(value, case['question'], c.graph['nodes'])
                row.update(interpretation=value, api=evidence, plan=plan,
                           passed=plan['status'] == case['status'] and plan['root'] == case['root'])
            except Stage7Error as exc:
                row.update(passed=False, error=str(exc))
                if exc.evidence is not None:
                    row['api'] = exc.evidence
            report['holdout'].append(row)
            report['total_physical_requests'] = original['requests']+client.requests
            save()
            print(case['id'], row['passed'], flush=True)
        # Run unchanged historical regressions against final current code/tests.
        view = prepare_regression_view(PROJECT, folder/'regression-view')
        env = dict(os.environ, PYTHONPATH=str(Path(view['directory'])/'src'), REPO_PROOF_LEAN=a.lean)
        env.pop('ANTHROPIC_API_KEY', None)
        with (folder/'regressions.stdout').open('wb') as out, (folder/'regressions.stderr').open('wb') as err:
            regression = subprocess.Popen([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                cwd=view['directory'], env=env, stdout=out, stderr=err)
        for i, (root, case, value, evidence) in enumerate(selected[:3]):
            destination = folder/('full-%02d' % (i+1))
            outcome = run(case['question'], RecordedInterpretation(value, evidence),
                          PROJECT, a.cache_dir, destination, a.lean)
            oracle, _ = fixed_point(root, c.graph['edges'])
            actual = json.loads((destination/'stage6/answer.json').read_bytes()) if outcome['verified'] else None
            report['full_runs'].append({'case_id': case['id'], 'root': root,
                'outcome': outcome, 'independent_full_list_match': actual is not None and actual['paths'] == oracle,
                'oracle_paths': oracle, 'directory': str(destination)})
            save()
            print('full', i+1, outcome['status'], flush=True)
        exit_code = regression.wait(timeout=2400)
        log = (folder/'regressions.stderr').read_text(encoding='utf-8')
        count = re.search(r'^Ran (\d+) tests? in ', log, re.M)
        report['regressions'] = {'exit_code': exit_code, 'view': view,
            'identity_verified': verify_regression_view(PROJECT, view),
            'count': int(count.group(1)) if count else None,
            'no_skips': 'skipped=' not in log and '... skipped ' not in log,
            'differential_1547': 'test_differential (test_lean_export.LeanExportTests.test_differential) ... ok' in log}
        # Only the authorized main README may differ from the accepted Stage 6 tree.
        changed = subprocess.check_output(['git', 'diff', '--no-renames',
            '--diff-filter=CDMRTUXB', '--name-only',
            '683ec76b021349cf5b911aabf77f01e07fc6828f', '--'], cwd=PROJECT).decode().splitlines()
        report['historical_changes'] = changed
        report['historical_files_preserved'] = changed == ['README.md']
        report['code_unchanged_during_checks'] = before == code_inventory(PROJECT)
        report['gates'] = {
            'original_claude_accuracy_90_percent': original['accuracy'] >= .9,
            'final_replay_32_correct': len(report['replay']) == 32 and all(r['passed'] for r in report['replay']),
            'fresh_holdout_8_correct': len(report['holdout']) == 8 and all(r['passed'] for r in report['holdout']),
            'request_budget': report['total_physical_requests'] <= 40,
            'three_complete_proofs': len(report['full_runs']) == 3 and all(
                r['outcome']['verified'] and r['independent_full_list_match'] for r in report['full_runs']),
            'regressions': exit_code == 0 and report['regressions']['no_skips']
                and report['regressions']['differential_1547'] and count is not None,
            'preservation': report['historical_files_preserved'],
            'current_code_identity': report['code_unchanged_during_checks']}
        report['passed'] = all(report['gates'].values())
        report['status'] = 'STAGE7_PASS' if report['passed'] else 'STAGE7_FAILED'
    except Exception as exc:
        report.update(status='STAGE7_FAILED', error=str(exc) if isinstance(exc, Stage7Error) else type(exc).__name__)
    finally:
        if regression is not None and regression.poll() is None:
            regression.wait(timeout=2400)
        save()
    print(report['status'], flush=True)
    return 0 if report['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
