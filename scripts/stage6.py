"""Prepare an anchored source proof and answer any root in its Mojom universe."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import stat
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))

from repo_proof.checker import verify_certificate
from repo_proof.extraction import read_json
from repo_proof.generator import generate_certificate
from repo_proof.stage5_v2 import canonical
from repo_proof.stage6_answer import expected_answer, check_answer, render_answer, check_human
from repo_proof.stage6_cache import anchored_capture, prepare_cache, validate_cache
from repo_proof.stage6_export import render_query
from review_stage6_binding import audit_query
from stage4_support import file_info
from stage6_support import audit
from stage5_support import run_process


def write_new(path, value):
    with Path(path).open('xb') as target:
        target.write(canonical(value))


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def new_directory(project, folder):
    project, folder = Path(project).resolve(), Path(folder).absolute()
    if not folder.resolve().is_relative_to(project) or folder.resolve() == project:
        raise ValueError('output directory must be below the project')
    for part in (folder, *folder.parents):
        if part == project:
            break
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0)
                & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)):
            raise ValueError('output path must not use links or junctions')
    folder.mkdir(parents=True, exist_ok=False)
    return folder.resolve()


def project_code(project):
    """Detect code changes during this run; review remains a separate gate."""
    return {p.relative_to(project).as_posix(): file_info(p)
            for base in ('src', 'scripts', 'formal')
            for p in (project / base).rglob('*') if p.suffix in ('.py', '.lean')}


def validate_artifacts(folder, captured, root, certificate, cache_info, frozen):
    folder = Path(folder)
    for rel, expected in frozen.items():
        if file_info(folder / rel) != expected:
            raise ValueError('query input changed: ' + rel)
    saved_cert = read_json(folder / 'certificate.json')
    if canonical(saved_cert) != canonical(certificate):
        raise ValueError('query certificate was substituted')
    verify_certificate(captured.graph, root, saved_cert)
    comparison = audit_query((folder / 'lean/QueryProof.lean').read_text(encoding='utf-8'),
                             captured.graph, root, saved_cert)
    check_answer(read_json(folder / 'expected-answer.json'), captured, root,
                 saved_cert, cache_info['identity'])
    return comparison


def execute_query(project, cache_dir, root, folder, lean):
    project, lean = (Path(p).resolve() for p in (project, lean))
    # Keep link/reparse evidence until the cache validator checks the path.
    cache_dir = Path(cache_dir).absolute()
    folder = new_directory(project, folder)
    (folder / 'lean').mkdir()
    # The preserved timing tactic writes local/stage3-proof-progress.txt.
    # Give it a private working directory, separate from all import paths.
    (folder / 'process-cwd/local').mkdir(parents=True)
    started = time.perf_counter()
    report = {'schema': 'stage6-query-report-v1', 'status': 'IN_PROGRESS',
              'passed': False, 'answer_released': False, 'root': root,
              'phases_seconds': {}, 'checks': [],
              'proof_mode': 'Reuse the independently anchored Stage5 source/graph proof; freshly kernel-check this root, certificate and complete answer.'}
    report_path = folder / 'query-report.json'
    def save():
        report_path.write_bytes(canonical(report))
    def measure(name, fn):
        begin = time.perf_counter()
        value = fn()
        report['phases_seconds'][name] = time.perf_counter() - begin
        save()
        return value
    try:
        code_before = project_code(project)
        report['code_at_start'] = code_before
        report['lean_executable'] = file_info(lean)
        save()
        c = measure('snapshot_and_full_parser', lambda: anchored_capture(project))
        report['source_component_timings_seconds'] = c.timings
        if not isinstance(root, str) or root not in c.graph['nodes']:
            raise ValueError('root must exactly name a selected Mojom file')
        cache = measure('validate_prepared_proof', lambda: validate_cache(project, cache_dir, captured=c))
        report['source_proof'] = cache['source_proof']
        report['cache_identity'] = cache['identity']
        env = dict(os.environ, LEAN_PATH=os.pathsep.join((str(cache_dir / 'lean'),
                                                        str(folder / 'lean'))))
        def check_process_directory():
            cwd = folder / 'process-cwd'
            allowed = {'local', 'local/stage3-proof-progress.txt'}
            for path in cwd.rglob('*'):
                metadata = path.lstat()
                if (path.relative_to(cwd).as_posix() not in allowed
                        or stat.S_ISLNK(metadata.st_mode)
                        or getattr(metadata, 'st_file_attributes', 0)
                        & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)):
                    raise ValueError('unexpected process working-directory artifact')
        def process(name, command):
            # Prevent unrelated cwd modules from shadowing the sealed imports.
            check_process_directory()
            with working_directory(folder / 'process-cwd'):
                result = run_process(name, command, env, folder, timeout=1800)
            check_process_directory()
            report['checks'].append(result)
            if not result['passed']:
                raise ValueError(name + ' failed; see process logs')
            return result
        version = process('lean_version', [str(lean), '--version'])
        if 'version 4.35.0,' not in version['stdout']:
            raise ValueError('Lean 4.35.0 required for the prepared proof')
        def generate():
            cert = generate_certificate(c.graph, root)
            verify_certificate(c.graph, root, cert)
            source = render_query(c.graph, root, cert)
            value = expected_answer(c, root, cert, cache['identity'])
            write_new(folder / 'certificate.json', cert)
            write_new(folder / 'expected-answer.json', value)
            with (folder / 'lean/QueryProof.lean').open('xb') as target:
                target.write(source.encode('utf-8'))
            # Recompute full canonical bytes, independent of filesystem copies.
            if (source != render_query(c.graph, root, generate_certificate(c.graph, root))
                    or canonical(value) != canonical(expected_answer(c, root, cert, cache['identity']))):
                raise ValueError('query generation is not deterministic')
            return cert
        cert = measure('generation_and_repeat', generate)
        frozen = {rel: file_info(folder / rel) for rel in
                  ('certificate.json', 'expected-answer.json', 'lean/QueryProof.lean')}
        report['input_files'] = frozen
        report['literal_audit'] = measure('query_literal_audit', lambda:
            validate_artifacts(folder, c, root, cert, cache, frozen))
        source = folder / 'lean/QueryProof.lean'
        proof = measure('fresh_query_kernel_process', lambda:
            process('QueryProof', [str(lean), '-o', str(source.with_suffix('.olean')),
                                   '--root='+str(folder / 'lean'), str(source)]))
        proof['axioms'] = audit(proof['stdout'])
        proof['compiled'] = file_info(source.with_suffix('.olean'))
        report['query_proof'] = proof['compiled']
        # Validate all imported bytes again after compiler use. A hash-only manifest
        # from the producer is never the expected anchor for this check.
        measure('recheck_prepared_proof', lambda: validate_cache(project, cache_dir, captured=c))
        validate_artifacts(folder, c, root, cert, cache, frozen)
        expected_lean_files = {'QueryProof.lean', 'QueryProof.olean'}
        if {p.name for p in (folder / 'lean').iterdir()} != expected_lean_files:
            raise ValueError('unexpected query-local import or output')
        if project_code(project) != code_before or file_info(lean) != report['lean_executable']:
            raise ValueError('project code or Lean executable changed during query')
        def release():
            value = read_json(folder / 'expected-answer.json')
            check_answer(value, c, root, cert, cache['identity'])
            write_new(folder / 'answer.pending.json', value)
            text = render_answer(value)
            with (folder / 'answer.pending.txt').open('xb') as target:
                target.write(text.encode('utf-8'))
            saved = read_json(folder / 'answer.pending.json')
            check_answer(saved, c, root, cert, cache['identity'])
            check_human((folder / 'answer.pending.txt').read_text(encoding='utf-8'),
                        c, root, cert, cache['identity'])
            if (folder / 'answer.pending.json').read_bytes() != canonical(value):
                raise ValueError('noncanonical persisted answer')
            if (folder / 'answer.pending.txt').read_bytes() != text.encode('utf-8'):
                raise ValueError('human output bytes changed')
            for suffix in ('json', 'txt'):
                (folder / ('answer.pending.' + suffix)).rename(folder / ('answer.' + suffix))
            if (folder / 'answer.json').read_bytes() != canonical(value):
                raise ValueError('promoted JSON bytes changed')
            if (folder / 'answer.txt').read_bytes() != text.encode('utf-8'):
                raise ValueError('promoted human answer bytes changed')
            check_answer(read_json(folder / 'answer.json'), c, root, cert, cache['identity'])
            check_human((folder / 'answer.txt').read_text(encoding='utf-8'),
                        c, root, cert, cache['identity'])
            return {'paths': len(value['paths']), 'json': file_info(folder / 'answer.json'),
                    'text': file_info(folder / 'answer.txt')}
        report['answer'] = measure('answer_persisted_roundtrip', release)
        report.update(status='STAGE6_QUERY_PASS', passed=True, answer_released=True)
        report['total_elapsed_seconds'] = time.perf_counter() - started
        save()
    except Exception as error:
        report.update(status='QUERY_REJECTED', passed=False, answer_released=False,
                      error=type(error).__name__ + ': ' + str(error))
        for name in ('answer.json', 'answer.txt', 'answer.pending.json', 'answer.pending.txt'):
            path = folder / name
            if path.exists():
                try:
                    path.rename(folder / (name + '.failed'))
                except OSError as cleanup_error:
                    report.setdefault('cleanup_errors', []).append(str(cleanup_error))
        report['total_elapsed_seconds'] = time.perf_counter() - started
        try:
            save()
        except OSError as report_error:
            report['diagnostic_write_error'] = str(report_error)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='copy and verify the accepted source-proof dependency closure')
    prep.add_argument('--cache-dir', required=True)
    prep.add_argument('--source-run', default='local/stage5-v2/full-03')
    query = commands.add_parser('query', help='freshly prove one explicit root on the prepared corpus')
    query.add_argument('--cache-dir', required=True)
    query.add_argument('--root', required=True)
    query.add_argument('--run-dir', required=True)
    query.add_argument('--lean', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'prepare':
            start = time.perf_counter()
            cache = prepare_cache(PROJECT, Path(args.cache_dir).absolute(), Path(args.source_run).absolute())
            print(json.dumps({'status': 'SOURCE_PROOF_PREPARED', 'identity': cache['identity'],
                              'seconds': time.perf_counter() - start, 'source_proof': cache['source_proof']}))
            return 0
        result = execute_query(PROJECT, args.cache_dir, args.root, args.run_dir, args.lean)
        print(json.dumps({'status': result['status'], 'root': args.root,
                          'paths': result.get('answer', {}).get('paths'),
                          'seconds': result['total_elapsed_seconds'],
                          'error': result.get('error')}))
        return 0 if result['passed'] else 2
    except (ValueError, OSError) as error:
        print('STAGE6_REJECTED: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
