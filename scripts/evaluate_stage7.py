"""Run the frozen live evaluation (max 40 physical API requests) and 3 proofs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage7 import ClaudeInterpreter, Stage7Error, resolve, run, SYSTEM, SCHEMA
from repo_proof.stage6_cache import anchored_capture, validate_cache
from repo_proof.stage5_v2 import canonical
from stage6 import new_directory
from stage6_select_queries import fixed_point


class RecordedInterpretation:
    """Reuse this evaluation's exact API response, with no second model call."""
    def __init__(self, value, evidence):
        self.value, self.evidence = value, evidence

    def interpret(self, question):
        return self.value, self.evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache-dir', required=True)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--lean', required=True)
    p.add_argument('--model', default='claude-haiku-5-5')
    p.add_argument('--effort', default='medium')
    a = p.parse_args()
    folder = new_directory(PROJECT, a.run_dir)
    frozen = (PROJECT/'verification/stage7-questions.json').read_bytes()
    cases = json.loads(frozen)
    report = {'status': 'IN_PROGRESS', 'set_sha256': sha256(frozen).hexdigest(),
              'prompt_sha256': sha256(SYSTEM.encode()).hexdigest(), 'schema': SCHEMA,
              'model': a.model, 'effort': a.effort, 'request_limit': 40,
              'max_retries': 0, 'cases': [], 'full_runs': []}
    def save():
        (folder/'evaluation.json').write_bytes(canonical(report))
    save()
    try:
        c = anchored_capture(PROJECT)
        validate_cache(PROJECT, Path(a.cache_dir).absolute(), captured=c)
        client = ClaudeInterpreter(a.model, a.effort, limit=40)
        report['sdk_version'] = client.sdk_version
        selected = []
        for case in cases:
            started = time.perf_counter()
            row = {'id': case['id'], 'question': case['question'],
                   'expected_status': case['status'], 'expected_root': case['root']}
            try:
                value, evidence = client.interpret(case['question'])
                plan = resolve(value, case['question'], c.graph['nodes'])
                row.update(interpretation=value, api=evidence, plan=plan,
                           passed=plan['status'] == case['status'] and plan['root'] == case['root'])
                row['safely_stopped'] = plan['status'] != 'ready'
                if row['passed'] and plan['status'] == 'ready' and plan['root'] not in [r[0] for r in selected]:
                    selected.append((plan['root'], case, value, evidence))
            except Stage7Error as exc:
                row.update(passed=False, error=str(exc), safely_stopped=True)
                if exc.evidence is not None:
                    row['api'] = exc.evidence
            row['elapsed_seconds'] = time.perf_counter()-started
            report['cases'].append(row)
            report['requests'] = client.requests
            save()
            print(case['id'], row['passed'], flush=True)
            # An unavailable model or authorization is not repaired by 29 retries.
            if 'error' in row and ('NotFoundError' in row['error'] or
                    'AuthenticationError' in row['error'] or 'PermissionDeniedError' in row['error']):
                report['online_unavailable'] = row['error']
                break
        for i, (root, case, value, evidence) in enumerate(selected[:3]):
            destination = folder/('full-%02d' % (i+1))
            outcome = run(case['question'], RecordedInterpretation(value, evidence),
                          PROJECT, a.cache_dir, destination, a.lean)
            oracle, rounds = fixed_point(root, c.graph['edges'])
            match = False
            if outcome['verified']:
                answer = json.loads((destination/'stage6/answer.json').read_bytes())
                match = answer['paths'] == oracle
            report['full_runs'].append({'case_id': case['id'], 'root': root,
                'directory': str(destination), 'outcome': outcome,
                'independent_full_list_match': match, 'oracle_count': len(oracle)})
            save()
        count = sum(r['passed'] for r in report['cases'])
        report['correct'] = count
        report['total'] = len(cases)
        report['accuracy'] = count/len(cases)
        report['all_unsafe_cases_stopped'] = all(r['passed'] and r['safely_stopped']
            for r in report['cases'] if r['expected_status'] in ('needs_clarification', 'unsupported'))
        report['live_pass'] = (len(report['cases']) == len(cases) and report['accuracy'] >= .9
            and report['all_unsafe_cases_stopped'] and len(report['full_runs']) == 3
            and all(r['independent_full_list_match'] for r in report['full_runs']))
        report['status'] = ('STAGE7_LIVE_PASS' if report['live_pass'] else
            'STAGE7_LIVE_VALIDATION_PENDING' if report.get('online_unavailable') else 'STAGE7_FAILED')
    except Exception as exc:
        report.update(status='STAGE7_LIVE_VALIDATION_PENDING' if isinstance(exc, (Stage7Error, ImportError))
                      else 'STAGE7_FAILED', error=str(exc) if isinstance(exc, Stage7Error) else type(exc).__name__)
    finally:
        save()
    print(report['status'], flush=True)
    return 0 if report.get('live_pass') else 2


if __name__ == '__main__':
    raise SystemExit(main())
