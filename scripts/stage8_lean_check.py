"""Fresh bounded GRAPH-ONLY kernel runs; never a source-to-answer receipt."""
from hashlib import sha256
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage8_graph import synthetic, reverse_index, search, reference
from repo_proof.stage8_lean import render, audit, NAMES
from repo_proof.stage5_v2 import canonical
from stage6_support import audit as audit_axioms
from repo_proof.extraction import read_json
from repo_proof.stage8_store import digest


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
