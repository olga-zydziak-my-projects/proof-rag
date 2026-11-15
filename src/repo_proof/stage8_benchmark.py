"""Synthetic graph measurements, explicitly without source-to-answer claims."""
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
import time
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from .stage5_v2 import canonical
from .stage8_graph import synthetic, validate_graph, reverse_index, search, traverse, reference, check_certificate, fixed_point
from .stage8_sources import tool_identity
from .stage8_store import build, load, write_table, digest


def bench(folder, n, family, config):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    phases = {}
    report = {'status': 'IN_PROGRESS', 'origin': 'synthetic', 'family': family, 'nodes': n,
              'seed': config['seed'], 'levels': {'graph_certificate': False, 'lean_graph': False,
              'source_to_answer': False}, 'lean_status': 'NOT_RUN_SIZE_BOUND_64', 'phases_seconds': phases,
              'tools': tool_identity(), 'roots': []}
    def measured(name, fn):
        begin = time.perf_counter()
        value = fn()
        phases[name] = time.perf_counter()-begin
        return value
    def save():
        (folder/'benchmark.json').write_bytes(canonical(report))
    save()
    try:
        edges = measured('prepare_graph', lambda: validate_graph(n, synthetic(n, family, config['seed'])))
        report['edges'] = len(edges)
        repo_ids = (np.arange(n)//100 if family == 'modular' else np.arange(n)) % 3
        report['logical_repo_counts'] = np.bincount(repo_ids, minlength=3).tolist()
        report['cross_logical_repo_edges'] = int(np.sum(repo_ids[edges[:, 0]] != repo_ids[edges[:, 1]]))
        names = pa.table({'id': np.arange(n, dtype=np.int64),
            'repo_id': pa.array(['logical-'+str(int(i)) for i in repo_ids]),
            'commit': pa.array(['synthetic-seed-'+str(config['seed'])]*n),
            'path': pa.array(['node/%07d.mojom' % i for i in range(n)])})
        facts = {name: [] for name in ('repositories', 'events', 'resolutions', 'external', 'configs')}
        facts['repositories'] = [{'repo_id': 'logical-'+str(i), 'real_repository': False} for i in range(3)]
        facts['metadata'] = [{'config': config, 'family': family, 'nodes': n, 'tools': tool_identity()}]
        hashes = measured('build_database_parquet', lambda: build(folder, names, edges, facts, config['limits']))
        files, saved_edges, saved_facts = measured('read_and_validate_full_index', lambda: load(folder, config['limits']))
        if not files.equals(names) or not np.array_equal(edges, saved_edges) or saved_facts != facts:
            raise ValueError('full snapshot differs')
        report['deterministic_fact_identity'] = sha256(canonical(hashes)).hexdigest()
        index = measured('build_reverse_CSR', lambda: reverse_index(n, saved_edges))
        # root 0 large, midpoint medium, last tiny/isolated; unique ordered roots.
        for root in sorted({0, n//2, n-1}):
            samples = []
            produced = None
            for repeat in range(config['query_repeats']):
                begin = time.perf_counter()
                ids = traverse(n, index, root)
                elapsed = time.perf_counter()-begin
                if produced is not None and not np.array_equal(produced, ids):
                    raise ValueError('nondeterministic repeated search')
                produced = ids
                samples.append(elapsed)
            row = {'root_id': root, 'result_count': len(ids), 'search_samples_seconds': samples,
                   'search_median_seconds': median(samples), 'search_range_seconds': [min(samples), max(samples)]}
            begin = time.perf_counter()
            cert_ids, parents, ranks = search(n, index, root)
            if not np.array_equal(ids, cert_ids):
                raise ValueError('query and certificate generation mismatch')
            cert = pa.table({'id': ids, 'parent': parents[ids], 'rank': ranks[ids]})
            row['certificate_generation_seconds'] = time.perf_counter()-begin
            begin = time.perf_counter()
            check_certificate(n, edges, root, ids, parents[ids], ranks[ids])
            row['independent_certificate_check_seconds'] = time.perf_counter()-begin
            begin = time.perf_counter()
            expected = reference(n, edges, root)
            row['independent_DFS_seconds'] = time.perf_counter()-begin
            if not np.array_equal(ids, expected):
                raise ValueError('full reference mismatch')
            row['full_reference_match'] = True
            # Quadratic fixed point deliberately restricted to a small induced prefix.
            small_n = min(n, 64)
            small_edges = edges[np.all(edges < small_n, axis=1)]
            small_root = root if root < small_n else small_n-1
            small_ids = search(small_n, reverse_index(small_n, small_edges), small_root)[0]
            if not np.array_equal(small_ids, fixed_point(small_n, small_edges, small_root)):
                raise ValueError('small fixed point mismatch')
            row['fixed_point_induced_prefix_nodes'] = small_n
            begin = time.perf_counter()
            destination = folder/('root-'+str(root))
            destination.mkdir()
            write_table(destination, 'certificate', cert)
            write_table(destination, 'answer', files.take(pa.array(ids)))
            saved = pq.read_table(destination/'certificate.parquet')
            arrays = [saved[k].to_numpy().astype(np.int64) for k in ('id', 'parent', 'rank')]
            check_certificate(n, edges, root, *arrays)
            if not np.array_equal(arrays[0], ids) or not pq.read_table(destination/'answer.parquet').equals(files.take(pa.array(expected))):
                raise ValueError('persisted complete answer mismatch')
            row['write_full_answer_roundtrip_seconds'] = time.perf_counter()-begin
            row['result_sha256'] = digest(destination/'answer.parquet')
            row['certificate_sha256'] = digest(destination/'certificate.parquet')
            row['verification_level'] = 'GRAPH_PASS_PYTHON_CERTIFICATE'
            report['roots'].append(row)
            save()
        # Repeat deterministic Parquet fact export; database binary need not repeat.
        repeat = folder/'repeat'
        repeat.mkdir()
        write_table(repeat, 'files', names)
        write_table(repeat, 'edges', pa.table({'importer': edges[:, 0], 'imported': edges[:, 1]}))
        if any(digest(repeat/(name+'.parquet')) != hashes[name+'.parquet'] for name in ('files', 'edges')):
            raise ValueError('nondeterministic fact export')
        report.update(status='GRAPH_PASS', deterministic_fact_export=True)
        report['levels']['graph_certificate'] = True
        report['index_bytes'] = (folder/'index.duckdb').stat().st_size
        report['temporary_bytes_at_end'] = sum(p.stat().st_size for p in (folder/'duckdb-temp').rglob('*') if p.is_file()) if (folder/'duckdb-temp').exists() else 0
    except Exception as exc:
        report.update(status='FAILED', error=type(exc).__name__+': '+str(exc))
    report['total_seconds'] = time.perf_counter()-started
    report['artifact_bytes'] = sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
    save()
    return report
