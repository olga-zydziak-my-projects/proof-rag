"""Deterministic Stage 8 prepare/query/benchmark CLI. No LLM integration."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.stage5_v2 import canonical
from repo_proof.extraction import read_json
from repo_proof.stage8_sources import capture, identity
from repo_proof.stage8_graph import reverse_index, search, reference, check_certificate, validate_graph
from repo_proof.stage8_store import build, load, write_table
from repo_proof.stage8_benchmark import bench
from stage6 import new_directory


def source_inputs(a):
    rows = read_json(a.locations)
    locations = {(r['repo_id'], r['commit']): r['directory'] for r in rows}
    if len(locations) != len(rows):
        raise ValueError('duplicate locations')
    return capture(a.manifest, a.manifest_sha256, locations, spool_dir=a.run_dir)


def prepare(a):
    folder = new_directory(PROJECT, a.run_dir)
    files, edges, facts = source_inputs(a)
    hashes = build(folder, files, edges, facts, read_json(a.config)['limits'])
    saved_files, saved_edges, saved_facts = load(folder, read_json(a.config)['limits'])
    if not files.equals(saved_files) or not np.array_equal(edges, saved_edges) or facts != saved_facts:
        raise ValueError('persisted source index mismatch')
    report = {'status': 'INDEX_IO_CHECKED', 'verification_level': 'PYTHON_SOURCE_IO_ONLY',
              'source_to_answer_lean': False, 'manifest_sha256': a.manifest_sha256,
              'files': len(files), 'edges': len(edges), 'fact_hashes': hashes}
    (folder/'prepare-report.json').write_bytes(canonical(report))
    return report


def query(a):
    folder = new_directory(PROJECT, a.run_dir)
    report = {'status': 'IN_PROGRESS', 'formally_verified': False}
    try:
        expected_files, expected_edges, expected_facts = source_inputs(a)
        files, edges, facts = load(a.index_dir, read_json(a.config)['limits'])
        if not expected_files.equals(files) or not np.array_equal(expected_edges, edges) or facts != expected_facts:
            raise ValueError('index no longer matches anchored sources/config/tools')
        requested = identity(a.repo_id, a.commit, a.path)
        rows = files.to_pylist()
        names = [identity(r['repo_id'], r['commit'], r['path']) for r in rows]
        if requested not in names:
            raise ValueError('unknown exact root identity')
        root = names.index(requested)
        ids, parents, ranks = search(len(files), reverse_index(len(files), edges), root)
        check_certificate(len(files), edges, root, ids, parents[ids], ranks[ids])
        expected = reference(len(files), edges, root)
        if not np.array_equal(ids, expected):
            raise ValueError('full reference mismatch')
        write_table(folder, 'certificate', pa.table({'id': ids, 'parent': parents[ids], 'rank': ranks[ids]}))
        cert = pq.read_table(folder/'certificate.parquet')
        check_certificate(len(files), edges, root, *[cert[k].to_numpy().astype(np.int64) for k in ('id', 'parent', 'rank')])
        answer = {'schema': 'stage8-answer-v1', 'operation': 'reverse_importers', 'root': requested,
            'manifest_sha256': a.manifest_sha256, 'scope': expected_facts['metadata'][0]['manifest'],
            'files': [names[i] for i in ids], 'count': len(ids),
            'repository_count': len({rows[i]['repo_id'] for i in ids}),
            'repository_version_count': len({(rows[i]['repo_id'], rows[i]['commit']) for i in ids}),
            'certificate': 'certificate.parquet', 'report': 'query-report.json',
            'verification_level': 'GRAPH_PASS_WITH_PYTHON_SOURCE_IO', 'source_to_answer_lean': False,
            'external_events': list(facts['external']),
            'limitation': 'No multi-repository source-to-answer Lean bridge has been accepted.'}
        payload = canonical(answer)
        (folder/'answer.pending.json').write_bytes(payload)
        if read_json(folder/'answer.pending.json') != answer or (folder/'answer.pending.json').read_bytes() != payload:
            raise ValueError('persisted complete answer mismatch')
        # Recheck all externally anchored inputs at consumption boundary.
        final_files, final_edges, final_facts = source_inputs(a)
        if not files.equals(final_files) or not np.array_equal(edges, final_edges) or facts != final_facts:
            raise ValueError('sources changed during query')
        report.update(status='GRAPH_PASS_WITH_PYTHON_SOURCE_IO', formally_verified=False,
                      root=requested, count=len(ids), result_sha256=sha256(payload).hexdigest())
        (folder/'query-report.json').write_bytes(canonical(report))
        if read_json(folder/'query-report.json') != report:
            raise ValueError('report changed')
        (folder/'answer.pending.json').rename(folder/'answer.json')
    except Exception as exc:
        report.update(status='QUERY_REJECTED', error=type(exc).__name__+': '+str(exc))
        for name in ('answer.json', 'answer.pending.json'):
            if (folder/name).exists():
                (folder/name).rename(folder/(name+'.failed'))
        (folder/'query-report.json').write_bytes(canonical(report))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='command', required=True)
    for command in ('prepare', 'query'):
        c = commands.add_parser(command)
        c.add_argument('--manifest', required=True)
        c.add_argument('--manifest-sha256', required=True)
        c.add_argument('--locations', required=True)
        c.add_argument('--config', default='verification/stage8-benchmark-config.json')
        c.add_argument('--run-dir', required=True)
        if command == 'query':
            c.add_argument('--index-dir', required=True)
            c.add_argument('--repo-id', required=True)
            c.add_argument('--commit', required=True)
            c.add_argument('--path', required=True)
    b = commands.add_parser('benchmark')
    b.add_argument('--nodes', type=int, required=True)
    b.add_argument('--family', choices=['chain', 'modular', 'cycles'], required=True)
    b.add_argument('--config', default='verification/stage8-benchmark-config.json')
    b.add_argument('--run-dir', required=True)
    a = p.parse_args()
    try:
        if a.command == 'benchmark':
            config = read_json(a.config)
            # Production measurements are always launched by the supervisor.
            result = bench(a.run_dir, a.nodes, a.family, config)
        else:
            result = prepare(a) if a.command == 'prepare' else query(a)
        print(json.dumps(result, ensure_ascii=True))
        return 0 if result['status'] in ('GRAPH_PASS', 'INDEX_IO_CHECKED', 'GRAPH_PASS_WITH_PYTHON_SOURCE_IO') else 2
    except Exception as exc:
        print(json.dumps({'status': 'STAGE8_REJECTED', 'error': type(exc).__name__+': '+str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
