"""Reproduce Stage 6: authenticated preparation, twelve fresh answers and tests."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.extraction import read_json
from repo_proof.generator import generate_certificate
from repo_proof.stage5_v2 import canonical
from repo_proof.stage6_answer import expected_answer, check_answer, render_answer, check_human
from repo_proof.stage6_cache import BASELINE, anchored_capture, prepare_cache, validate_cache
from review_stage6_binding import audit_query
from stage4_support import file_info
from stage5_support import run_process
from stage6 import execute_query, new_directory, project_code, working_directory
from stage6_regressions import prepare_regression_view, verify_regression_view
from stage6_select_queries import build_selection


def regression_summary(tests):
    """Recognize unittest's actual result, including the preserved named test.

    That test captures Lean stdout internally; it does not print its case count.
    Its unchanged source covers 512*3 graph/root pairs, nine witness cases and
    two substitutions. Baseline preservation separately binds that source.
    """
    stderr = tests.get('stderr', '')
    count = re.search(r'^Ran (\d+) tests? in ', stderr, re.M)
    if (tests.get('passed') is not True or tests.get('exit_code') != 0
            or not count or int(count.group(1)) < 111
            or not re.search(r'^OK(?: \(skipped=\d+\))?$', stderr, re.M)):
        raise ValueError('complete regression suite failed')
    name = 'test_differential (test_lean_export.LeanExportTests.test_differential) ... ok'
    if name not in stderr.splitlines():
        raise ValueError('preserved Python/Lean differential test did not pass')
    skipped = re.search(r'^OK \(skipped=(\d+)\)$', stderr, re.M)
    return {'test_count': int(count.group(1)),
            'test_skipped': int(skipped.group(1)) if skipped else 0,
            'differential_cases': 512*3+9+2,
            'differential_evidence': 'Named unittest passed; case count from preserved test source, not a stdout claim.'}


def preservation():
    baseline = read_json(PROJECT/'verification/stage6-baseline.json')
    # The final Stage 6 audit explicitly updates the main usage document.
    # Keep the historical baseline intact and expose both identities.
    documentation_update = {'README.md': {
        'historical': baseline['preserved_files']['README.md'],
        'current': file_info(PROJECT/'README.md'),
        'reason': 'User-requested Stage 6 README update'}}
    changed = [rel for rel, expected in baseline['preserved_files'].items()
               if rel not in documentation_update
               and (not (PROJECT/rel).is_file() or file_info(PROJECT/rel) != expected)]
    if changed:
        raise ValueError('preserved baseline files changed: ' + str(changed))
    command = ['git', '-c', 'safe.directory='+PROJECT.as_posix()]
    head = subprocess.check_output(command+['rev-parse', 'HEAD'], cwd=PROJECT, text=True).strip()
    subprocess.run(command+['merge-base', '--is-ancestor', BASELINE, 'HEAD'], cwd=PROJECT, check=True)
    return {'passed': True, 'files': len(baseline['preserved_files']) - len(documentation_update),
            'documentation_update': documentation_update, 'head': head,
            'stage5_checkpoint_is_ancestor': True}


def actual_attacks(c, cache_dir, cache, folder, selection, queries):
    """Mutate private copies only; this is IO/checker evidence, not kernel rejection."""
    folder.mkdir()
    rows = []
    def reject(label, layer, fn):
        try:
            fn()
        except (ValueError, OSError) as error:
            rows.append({'attack': label, 'layer': layer, 'rejected': True, 'reason': str(error)})
        else:
            raise ValueError('attack accepted: '+label)
    # The pair has equal counts but different certified paths.
    labels = {q['label']: q for q in selection['queries']}
    a, b = labels['same_count_a']['root'], labels['same_count_b']['root']
    ca, cb = generate_certificate(c.graph, a), generate_certificate(c.graph, b)
    va = expected_answer(c, a, ca, cache['identity'])
    reject('same_count_answer_swap', 'full answer metadata and paths',
           lambda: check_answer(va, c, b, cb, cache['identity']))
    reject('same_count_certificate_swap', 'independent expected root',
           lambda: expected_answer(c, b, ca, cache['identity']))
    query_a = next(Path(q['directory']) for q in queries if q['root'] == a)
    text = (query_a/'lean/QueryProof.lean').read_text(encoding='utf-8')
    reject('same_count_proof_swap', 'independent Lean literal audit',
           lambda: audit_query(text, c.graph, b, cb))
    changes = [
        ('omit_path', 'paths', va['paths'][:-1]),
        ('add_path', 'paths', va['paths']+['not-selected.mojom']),
        ('duplicate_path', 'paths', [va['paths'][0]]*len(va['paths'])),
        ('same_count_replace_path', 'paths', labels['same_count_b']['paths']),
        ('root', 'query', {**va['query'], 'root': b}),
        ('root_id_bool', 'query', {**va['query'], 'root_id': False}),
        ('root_policy', 'query', {**va['query'], 'include_root': False}),
        ('root_policy_type', 'query', {**va['query'], 'include_root': 1}),
        ('commit', 'pin', {**va['pin'], 'commit': '0'*40}),
        ('proof_identity', 'identities', {**va['identities'], 'source_proof_identity': '0'*64}),
    ]
    for label, field, value in changes:
        changed = copy.deepcopy(va); changed[field] = value
        reject(label+'_json', 'JSON answer binding',
               lambda changed=changed: check_answer(changed, c, a, ca, cache['identity']))
        reject(label+'_text', 'parsed human answer binding',
               lambda changed=changed: check_human(render_answer(changed), c, a, ca, cache['identity']))
    # Copy every dependency; never mutate baseline/cache files via hard links.
    attack_cache = folder/'altered-cache'
    shutil.copytree(cache_dir, attack_cache)
    manifest_path = attack_cache/'prepared-source.json'
    original_manifest = manifest_path.read_bytes()
    for rel in ('lean/SourceNames.lean', 'lean/ChromiumSource.olean', 'graph.json'):
        path = attack_cache/rel
        original = path.read_bytes()
        mutated = bytearray(original); mutated[len(mutated)//2] ^= 1
        path.write_bytes(mutated)
        manifest = json.loads(original_manifest)
        manifest['files'][rel] = file_info(path)  # attacker rehashes own manifest
        manifest_path.write_bytes(canonical(manifest))
        reject('rehash_modified_'+rel, 'committed source-proof anchor',
               lambda: validate_cache(PROJECT, attack_cache, captured=c))
        path.write_bytes(original); manifest_path.write_bytes(original_manifest)
    shadow = attack_cache/'lean/QueryProof.olean'; shadow.write_bytes(b'shadow')
    reject('extra_shadow_module', 'complete imported artifact inventory',
           lambda: validate_cache(PROJECT, attack_cache, captured=c))
    shadow.unlink()
    changed = json.loads(original_manifest); changed['source_proof']['run_nonce'] = '0'*32
    manifest_path.write_bytes(canonical(changed))
    reject('mixed_source_run', 'independently reconstructed manifest',
           lambda: validate_cache(PROJECT, attack_cache, captured=c))
    manifest_path.write_bytes(original_manifest)
    validate_cache(PROJECT, attack_cache, captured=c)
    return {'passed': True, 'checks': rows, 'count': len(rows),
            'boundary': 'Actual-data IO/checker rejections; no claim that the kernel rejected these mutations.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean', required=True)
    p.add_argument('--run-dir', required=True)
    p.add_argument('--report', required=True)
    p.add_argument('--source-run', default='local/stage5-v2/full-03')
    a = p.parse_args()
    os.chdir(PROJECT)
    report_path = Path(a.report).absolute()
    if (report_path.exists() or not report_path.resolve().is_relative_to(PROJECT)
            or report_path.resolve().is_relative_to(Path(a.run_dir).resolve())):
        p.error('choose a new report below the project and outside the run directory')
    folder = new_directory(PROJECT, a.run_dir)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    report = {'schema': 'stage6-checks-v1', 'status': 'IN_PROGRESS', 'stage6_pass': False,
              'run_dir': str(folder), 'stage5_checkpoint': BASELINE, 'queries': [],
              'phases_seconds': {}, 'proof_mode': 'Committed Stage5 source proof reused; each query proof freshly kernel-checked.'}
    def save(): report_path.write_bytes(canonical(report))
    def measure(name, fn):
        begin = time.perf_counter(); value = fn()
        report['phases_seconds'][name] = time.perf_counter()-begin; save()
        return value
    try:
        report['preservation_before'] = preservation()
        report['code_at_start'] = project_code(PROJECT)
        c = measure('preparation_snapshot_capture', lambda: anchored_capture(PROJECT))
        report['preparation_source_component_timings_seconds'] = c.timings
        cache_dir = folder/'prepared'
        cache = measure('prepare_reused_source_proof', lambda:
            prepare_cache(PROJECT, cache_dir, Path(a.source_run).absolute(), captured=c))
        report['prepared_identity'] = cache['identity']
        report['prepared_bytes'] = sum(v['bytes'] for v in cache['files'].values())
        selection = measure('independent_query_oracle', lambda:
            build_selection(canonical(c.graph)))
        if canonical(selection) != (PROJECT/'verification/stage6-query-selection.json').read_bytes():
            raise ValueError('independent query selection changed')
        if len(selection['queries']) < 10:
            raise ValueError('insufficient representative queries')
        for index, case in enumerate(selection['queries']):
            print('QUERY', index+1, case['label'], case['root'], flush=True)
            query_dir = folder/('query-'+case['label'])
            result = execute_query(PROJECT, cache_dir, case['root'], query_dir, a.lean)
            if not result['passed']:
                raise ValueError('query failed: '+case['root']+' '+result.get('error', ''))
            answer = read_json(query_dir/'answer.json')
            if answer['paths'] != case['paths']:
                raise ValueError('full independent query result mismatch: '+case['root'])
            row = {'label': case['label'], 'root': case['root'], 'paths': len(answer['paths']),
                   'directory': str(query_dir), 'full_oracle_match': True,
                   'elapsed_seconds': result['total_elapsed_seconds'],
                   'phases_seconds': result['phases_seconds'],
                   'answer': result['answer'], 'query_proof': result['query_proof'],
                   'report_identity': file_info(query_dir/'query-report.json')}
            report['queries'].append(row); save()
            print('PASS', case['label'], row['paths'], round(row['elapsed_seconds'], 3), flush=True)
        # A new process and fresh proof for the same input; complete deterministic
        # source/certificate/JSON/text bytes are compared, not just their hashes.
        repeated = selection['queries'][3]
        repeat_dir = folder/'query-repeat'
        repeat = measure('repeat_query', lambda:
            execute_query(PROJECT, cache_dir, repeated['root'], repeat_dir, a.lean))
        if not repeat['passed']: raise ValueError('repeated query failed')
        first_dir = folder/('query-'+repeated['label'])
        deterministic = ('certificate.json', 'lean/QueryProof.lean', 'answer.json', 'answer.txt')
        if not all((first_dir/rel).read_bytes() == (repeat_dir/rel).read_bytes() for rel in deterministic):
            raise ValueError('repeated query canonical bytes differ')
        report['determinism'] = {'passed': True, 'root': repeated['root'], 'full_byte_files': list(deterministic)}
        report['attacks'] = measure('actual_data_attacks', lambda:
            actual_attacks(c, cache_dir, cache, folder/'attacks', selection, report['queries']))
        # Exercise the actual public command's non-success code and output absence.
        env = dict(os.environ, PYTHONPATH=str(PROJECT/'src'), REPO_PROOF_LEAN=str(Path(a.lean).resolve()))
        invalid = run_process('invalid_root_cli', [sys.executable, str(PROJECT/'scripts/stage6.py'),
            'query', '--cache-dir', str(cache_dir), '--root', 'not/a/selected/file.mojom',
            '--run-dir', str(folder/'invalid-root'), '--lean', str(Path(a.lean).resolve())], env, folder)
        if invalid['exit_code'] != 2 or (folder/'invalid-root/answer.json').exists():
            raise ValueError('public invalid-root rejection failed')
        report['public_cli_invalid_root'] = invalid
        view = prepare_regression_view(PROJECT, folder/'regression-view')
        report['regression_view'] = view
        regression_env = dict(env, PYTHONPATH=str(Path(view['directory'])/'src'))
        with working_directory(view['directory']):
            tests = measure('all_regressions', lambda: run_process('all_tests',
                [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                regression_env, folder, timeout=1800))
        report['regression_view_unchanged'] = verify_regression_view(PROJECT, view)
        report['tests'] = tests
        report.update(regression_summary(tests))
        report['preservation_after'] = preservation()
        if project_code(PROJECT) != report['code_at_start']:
            raise ValueError('project source changed during acceptance run')
        report['query_elapsed_summary_seconds'] = {
            'min': min(q['elapsed_seconds'] for q in report['queries']),
            'median': statistics.median(q['elapsed_seconds'] for q in report['queries']),
            'max': max(q['elapsed_seconds'] for q in report['queries'])}
        report['gates'] = {
            'preservation': True, 'independent_cache_anchor': True,
            'arbitrary_roots_fresh_source_answer_proofs': len(report['queries']) >= 10,
            'full_independent_answers': all(q['full_oracle_match'] for q in report['queries']),
            'determinism': report['determinism']['passed'],
            'attacks': report['attacks']['passed'], 'regressions': tests['passed']}
        report.update(status='STAGE6_CHECKS_PASS', checks_pass=True)
        # Independent final review is deliberately a separate required gate.
    except Exception as error:
        report.update(status='STAGE6_CHECKS_FAILED', checks_pass=False,
                      error=type(error).__name__+': '+str(error))
    report['total_elapsed_seconds'] = time.perf_counter()-start
    save()
    print(json.dumps({'status': report['status'], 'queries': len(report['queries']),
                      'seconds': report['total_elapsed_seconds'], 'report': str(report_path),
                      'error': report.get('error')}), flush=True)
    return 0 if report.get('checks_pass') else 2


if __name__ == '__main__':
    raise SystemExit(main())
