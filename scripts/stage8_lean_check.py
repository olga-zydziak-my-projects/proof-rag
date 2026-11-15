"""Fresh contextual source proofs, blocked graph ladder and small regressions."""
from hashlib import sha256
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))
from repo_proof.stage8_graph import synthetic, reverse_index, search, reference
from repo_proof.stage8_lean import render, audit, NAMES
from repo_proof.stage8_lean import render_scalable, render_source
from stage8_proof_audit import audit_graph, audit_source
from repo_proof.stage5_v2 import canonical
from stage6_support import audit as audit_axioms
from repo_proof.extraction import read_json
from repo_proof.stage8_store import digest

GRAPH_NAMES = ('Stage8Graph.accepted', 'Stage8Graph.erased_accepted', 'Stage8Graph.exact', 'Stage8Graph.answer_exact')
SOURCE_NAMES = tuple('Stage8Source.' + name for name in
    ('names_injective', 'files_checked', 'graph_checked', 'answer_checked', 'source_to_answer'))


def _audit_module(output, names):
    # The historical strict parser's identifier grammar excludes apostrophes.
    # Rename only exact quoted report labels, retaining its complete-line audit.
    aliases = {name: 'Stage8Axiom.record' + str(i) for i, name in enumerate(names)}
    for name, alias in aliases.items():
        output = output.replace("'" + name + "' ", "'" + alias + "' ")
    parsed = audit_axioms(output, names=tuple(aliases.values()))
    return {name: parsed[alias] for name, alias in aliases.items()}


def _compile(folder, modules, lean, config, name):
    command = [sys.executable, str(PROJECT / 'scripts/stage8_supervise.py'), '--config', str(config),
        '--run-dir', str(folder / ('compile-' + name)), '--artifact-root', str(folder), '--', str(lean),
        '-o', str(modules / (name + '.olean')), '--root=' + str(modules), str(modules / (name + '.lean'))]
    result = subprocess.run(command, capture_output=True, timeout=650)
    receipt = read_json(folder / ('compile-' + name) / 'resource-report.json')
    if result.returncode:
        raise ValueError(name + ' kernel compilation ' + receipt['status'])
    return receipt


def check_sources(folder, lean, config, manifest_path, anchor, locations, root_identity):
    """Fresh source and query kernel run, anchored independently by the caller."""
    from repo_proof.stage8_sources import capture, git, identity
    folder, lean, config = Path(folder).resolve(), Path(lean).resolve(), Path(config).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    modules = folder / 'lean'
    modules.mkdir()
    started = time.perf_counter()
    previous = os.environ.get('LEAN_PATH')
    os.environ['LEAN_PATH'] = str(modules)
    report = {'status': 'IN_PROGRESS', 'source_to_answer': False, 'manifest_sha256': anchor,
            'fresh_dependencies': True, 'fresh_source_compilation': True,
            'fresh_query_compilation': True, 'reused_project_oleans': False, 'modules': {}}
    try:
        report['lean_executable_sha256'] = digest(lean)
        report['lean_version'] = subprocess.check_output([str(lean), '--version'], timeout=30).decode().strip()
        files, edges, facts = capture(manifest_path, anchor, locations, spool_dir=folder)
        rows = files.to_pylist()
        identities = [(r['repo_id'], r['commit'], r['path']) for r in rows]
        root = identities.index(tuple(root_identity))
        source_data = [git(locations[k[: 2]], 'cat-file', 'blob', row['blob']) for k, row in zip(identities, rows)]
        ids, parent, rank = search(len(rows), reverse_index(len(rows), edges), root)
        oracle = reference(len(rows), edges, root)
        if not np.array_equal(ids, oracle):
            raise ValueError('complete independent source query answer mismatch')
        graph_text = render_scalable(len(rows), edges, root, ids, parent[ids], rank[ids])
        audit_graph(graph_text, len(rows), edges, root, ids, parent[ids], rank[ids])
        source_text = render_source(identities, source_data, facts['metadata'][0]['manifest']['rules'],
                                  edges, root, ids, parent[ids], rank[ids])
        audit_source(source_text, identities, source_data, facts['metadata'][0]['manifest']['rules'], edges, ids)
        dependencies = ('Reachability', 'Checker', 'FastChecker', 'ProofTiming', 'SourceByteScanner',
                      'SourceGraphBinding', 'ContextualSourceBinding')
        for name in dependencies:
            shutil.copyfile(PROJECT / 'formal' / (name + '.lean'), modules / (name + '.lean'))
        (modules / 'GraphProof.lean').write_text(graph_text, encoding='utf-8', newline='\n')
        (modules / 'SourceProof.lean').write_text(source_text, encoding='utf-8', newline='\n')
        for name in (*dependencies, 'GraphProof', 'SourceProof'):
            receipt = _compile(folder, modules, lean, config, name)
            source = modules / (name + '.lean')
            raw = (folder / ('compile-' + name) / 'stdout.log').read_text(encoding='utf-8')
            theorem_names = {
                'GraphProof': GRAPH_NAMES,
                'SourceProof': SOURCE_NAMES,
            }
            names = theorem_names.get(name)
            if names is None:
                names = tuple(re.findall(
                    r'^#print axioms (\S+)$', source.read_text(encoding='utf-8'), re.M))
            axioms = _audit_module(raw, names) if names else []
            report['modules'][name] = {'source_sha256': digest(source), 'olean_sha256': digest(source.with_suffix('.olean')),
                                     'axioms': axioms, 'resources': receipt}
        # Check every input again after the fresh kernel run.
        audit_graph((modules / 'GraphProof.lean').read_text(encoding='utf-8'), len(rows), edges, root, ids, parent[ids], rank[ids])
        audit_source((modules / 'SourceProof.lean').read_text(encoding='utf-8'), identities, source_data,
                     facts['metadata'][0]['manifest']['rules'], edges, ids)
        files_after, edges_after, facts_after = capture(manifest_path, anchor, locations, spool_dir=folder)
        if not files.equals(files_after) or not np.array_equal(edges, edges_after) or facts != facts_after:
            raise ValueError('source capture changed during proof')
        if digest(lean) != report['lean_executable_sha256']:
            raise ValueError('Lean executable changed')
        answer = [identity(*identities[int(i)]) for i in ids]
        report.update(status='SOURCE_TO_ANSWER_PASS', source_to_answer=True, nodes=len(rows), edges=len(edges),
                      source_bytes=sum(map(len, source_data)), root_identity=list(root_identity),
                      answer_identities=answer, oracle_answer_identities=[identity(*identities[int(i)]) for i in oracle],
                      cross_repository=any(identities[int(i)][0] != root_identity[0] for i in ids),
                      external_events=list(facts['external']), mapping_specification='manually accepted pinned prefix rules')
    except Exception as exc:
        report.update(status='FAILED', error=type(exc).__name__ + ': ' + str(exc))
    finally:
        if previous is None:
            os.environ.pop('LEAN_PATH', None)
        else:
            os.environ['LEAN_PATH'] = previous
        report['elapsed_seconds'] = time.perf_counter() - started
        (folder / 'source-report.json').write_bytes(canonical(report))
    return report


def check_ladder(folder, lean, config, sizes=(256, 1000, 10000)):
    """Execute increasing blocked graph kernel trials under unchanged limits."""
    folder, lean, config = Path(folder).resolve(), Path(lean).resolve(), Path(config).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    modules = folder / 'lean'
    modules.mkdir()
    previous = os.environ.get('LEAN_PATH')
    os.environ['LEAN_PATH'] = str(modules)
    report = {'status': 'IN_PROGRESS', 'origin': 'synthetic', 'source_to_answer': False,
            'limits': read_json(config)['limits'], 'runs': [],
            'lean_executable_sha256': digest(lean),
            'lean_version': subprocess.check_output([str(lean), '--version'], timeout=30).decode().strip(),
            'fresh_dependencies': {}, 'larger_level_policy': 'skip following levels after a failed previous level'}
    started = time.perf_counter()
    try:
        for name in ('Reachability', 'Checker', 'FastChecker', 'ProofTiming'):
            shutil.copyfile(PROJECT / 'formal' / (name + '.lean'), modules / (name + '.lean'))
            receipt = _compile(folder, modules, lean, config, name)
            source = modules / (name + '.lean')
            names = tuple(re.findall(r'^#print axioms (\S+)$', source.read_text(encoding='utf-8'), re.M))
            raw = (folder / ('compile-' + name) / 'stdout.log').read_text(encoding='utf-8')
            report['fresh_dependencies'][name] = {'source_sha256': digest(source),
                'olean_sha256': digest(source.with_suffix('.olean')), 'resources': receipt,
                'axioms': _audit_module(raw, names) if names else []}
        failed = None
        for n in sizes:
            if failed:
                report['runs'].append({'nodes': n, 'status': 'SKIPPED', 'executed': False,
                    'dependency_nodes': report['runs'][-1]['nodes'],
                    'stop_reason': 'previous measured level ' + str(failed) + ' failed'})
                continue
            run = {'nodes': n, 'family': 'chain', 'root': 0, 'status': 'IN_PROGRESS', 'executed': True,
                 'tools': {'lean_sha256': report['lean_executable_sha256'], 'lean_version': report['lean_version'],
                          'exporter_sha256': digest(PROJECT / 'src/repo_proof/stage8_lean.py'),
                          'auditor_sha256': digest(PROJECT / 'scripts/stage8_proof_audit.py')}}
            report['runs'].append(run)
            phase = time.perf_counter()
            edges = synthetic(n, 'chain')
            ids, p, r = search(n, reverse_index(n, edges), 0)
            oracle = reference(n, edges, 0)
            if not np.array_equal(ids, oracle):
                raise ValueError('ladder complete oracle mismatch')
            run.update(edges=len(edges), certificate_entries=len(ids), answer_entries=len(ids),
                       generation_seconds=time.perf_counter() - phase)
            phase = time.perf_counter()
            text = render_scalable(n, edges, 0, ids, p[ids], r[ids])
            run['export_seconds'] = time.perf_counter() - phase
            phase = time.perf_counter()
            audit_graph(text, n, edges, 0, ids, p[ids], r[ids])
            run['audit_seconds'] = time.perf_counter() - phase
            source = modules / ('Ladder' + str(n) + '.lean')
            source.write_text(text, encoding='utf-8', newline='\n')
            (folder / ('answer-' + str(n) + '.json')).write_bytes(canonical(ids.tolist()))
            (folder / ('oracle-' + str(n) + '.json')).write_bytes(canonical(oracle.tolist()))
            (folder / ('certificate-' + str(n) + '.json')).write_bytes(canonical(
                [[int(v), int(p[v]), int(r[v])] for v in ids]))
            phase = time.perf_counter()
            try:
                receipt = _compile(folder, modules, lean, config, 'Ladder' + str(n))
                raw = (folder / ('compile-Ladder' + str(n)) / 'stdout.log').read_text(encoding='utf-8')
                run['axioms'] = audit_axioms(raw, names=GRAPH_NAMES)
                audit_graph(source.read_text(encoding='utf-8'), n, edges, 0, ids, p[ids], r[ids])
                run.update(status='LEAN_GRAPH_PASS', source_sha256=digest(source),
                    olean_sha256=digest(source.with_suffix('.olean')))
            except Exception as exc:
                run.update(status='FAILED', reason=str(exc))
                failed = n
            run['compile_and_kernel_seconds'] = time.perf_counter() - phase
            run['resources'] = read_json(folder / ('compile-Ladder' + str(n)) / 'resource-report.json')
            if run['status'] == 'FAILED' and run['resources']['status'] in ('TIMEOUT', 'RESOURCE_LIMIT'):
                run['status'] = run['resources']['status']
            raw = (folder / ('compile-Ladder' + str(n)) / 'stdout.log').read_text(encoding='utf-8')
            kernel_ms = re.findall(r'kernel_check_and_insert_ms=([0-9]+)', raw)
            run.update(certificate_nodes=len(ids), answer_nodes=len(ids),
                artifact_verified=True, stop_reason=run.get('reason', 'fresh kernel proof accepted'),
                peak_memory_bytes=max(run['resources']['peak_tree_rss'], run['resources']['peak_tree_private']),
                artifact_bytes=run['resources']['final_artifact_bytes'],
                compilation_seconds=run['compile_and_kernel_seconds'],
                checking_seconds=sum(map(int, kernel_ms)) / 1000,
                timing_note=(
                    'compilation_seconds includes process startup, elaboration and kernel checking; '
                    'checking_seconds is the instrumented kernel subset'))
            run['source_artifact_bytes'] = source.stat().st_size
            run['certificate_artifact_bytes'] = (folder / ('certificate-' + str(n) + '.json')).stat().st_size
            run['answer_artifact_bytes'] = (folder / ('answer-' + str(n) + '.json')).stat().st_size
        report['status'] = 'LEAN_LADDER_MEASURED'
        if digest(lean) != report['lean_executable_sha256']:
            raise ValueError('Lean executable changed')
    except Exception as exc:
        report.update(status='FAILED', error=str(exc))
    finally:
        if previous is None:
            os.environ.pop('LEAN_PATH', None)
        else:
            os.environ['LEAN_PATH'] = previous
        report['elapsed_seconds'] = time.perf_counter() - started
        (folder / 'ladder-report.json').write_bytes(canonical(report))
    return report


def check(folder, lean, config):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    modules = folder/'lean'
    modules.mkdir()
    previous = os.environ.get('LEAN_PATH')
    os.environ['LEAN_PATH'] = str(modules.resolve())
    report = {'origin': 'synthetic', 'source_to_answer': False, 'status': 'IN_PROGRESS',
              'fresh_dependencies': True, 'reused_project_oleans': False, 'runs': []}
    started = time.perf_counter()
    try:
        report['lean_executable_sha256'] = digest(lean)
        version = subprocess.run([str(lean), '--version'], capture_output=True, timeout=30, check=True)
        report['lean_version'] = version.stdout.decode('utf-8').strip()
        report['dependency_sources'] = {}
        for name in ('Reachability', 'Checker'):
            source = modules/(name+'.lean')
            shutil.copyfile(PROJECT/'formal'/(name+'.lean'), source)
            command = [sys.executable, str(PROJECT/'scripts/stage8_supervise.py'), '--config', str(config),
                       '--run-dir', str(folder/('compile-'+name)), '--artifact-root', str(folder), '--', str(lean),
                       '-o', str(source.with_suffix('.olean')), '--root='+str(modules), str(source)]
            result = subprocess.run(command, capture_output=True, timeout=650)
            if result.returncode:
                raise ValueError('fresh dependency failed: '+name)
            report['dependency_sources'][name] = {'source_sha256': digest(source),
                'olean_sha256': digest(source.with_suffix('.olean'))}
        for family in ('chain', 'modular', 'cycles'):
            edges = synthetic(64, family)
            ids, parent, rank = search(64, reverse_index(64, edges), 0)
            if not np.array_equal(ids, reference(64, edges, 0)):
                raise ValueError('reference mismatch')
            text = render(64, edges, 0, ids, parent[ids], rank[ids])
            audit(text, 64, edges, 0, ids, parent[ids], rank[ids])
            source = modules/('Proof_'+family+'.lean')
            source.write_text(text, encoding='utf-8', newline='\n')
            if source.read_bytes() != text.encode():
                raise ValueError('Lean source roundtrip')
            command = [sys.executable, str(PROJECT/'scripts/stage8_supervise.py'), '--config', str(config),
                       '--run-dir', str(folder/family), '--artifact-root', str(folder), '--', str(lean),
                       '-o', str(source.with_suffix('.olean')), '--root='+str(modules), str(source)]
            result = subprocess.run(command, capture_output=True, timeout=650)
            if result.returncode:
                raise ValueError('graph-only kernel failed: '+family)
            raw = (folder/family/'stdout.log').read_text(encoding='utf-8')
            axioms = audit_axioms(raw, names=NAMES)
            audit(source.read_text(encoding='utf-8'), 64, edges, 0, ids, parent[ids], rank[ids])
            report['runs'].append({'family': family, 'nodes': 64, 'edges': len(edges),
                'root': 0, 'answer_ids': ids.tolist(), 'axioms': axioms,
                'source_sha256': digest(source), 'olean_sha256': digest(source.with_suffix('.olean')),
                'resource_report': read_json(folder/family/'resource-report.json')})
        if digest(lean) != report['lean_executable_sha256']:
            raise ValueError('Lean executable changed')
        report['status'] = 'LEAN_GRAPH_PASS'
    except Exception as exc:
        report.update(status='FAILED', error=str(exc))
    finally:
        if previous is None:
            os.environ.pop('LEAN_PATH', None)
        else:
            os.environ['LEAN_PATH'] = previous
        report['elapsed_seconds'] = time.perf_counter()-started
        (folder/'lean-report.json').write_bytes(canonical(report))
    return report


if __name__ == '__main__':
    result = check(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve())
    print(result['status'], result.get('error', ''))
    raise SystemExit(0 if result['status'] == 'LEAN_GRAPH_PASS' else 2)
