"""Bounded DuckDB + canonical ordered Parquet fact storage."""
from hashlib import sha256
import json
from pathlib import Path
import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

pa.set_cpu_count(1)
pa.set_io_thread_count(1)


def digest(path):
    h = sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def connect(folder, limits, readonly=False):
    folder = Path(folder)
    con = duckdb.connect(str(folder/'index.duckdb'), read_only=readonly)
    con.execute('SET memory_limit = ?', [limits['duckdb_memory']])
    con.execute('SET threads = ?', [limits['threads']])
    con.execute('SET temp_directory = ?', [str(folder/'duckdb-temp')])
    con.execute('SET max_temp_directory_size = ?', [limits['duckdb_temp']])
    con.execute('SET preserve_insertion_order = false')
    return con


def write_table(folder, name, table):
    pq.write_table(table, Path(folder)/(name+'.parquet'), compression='zstd',
                   use_dictionary=True, row_group_size=65536)


def build(folder, files, edges, facts, limits):
    folder = Path(folder)
    write_table(folder, 'files', files)
    write_table(folder, 'edges', pa.table({'importer': edges[:, 0], 'imported': edges[:, 1]}))
    for name, rows in facts.items():
        # Canonical JSON rows retain all nested provenance without schema inference.
        values = [json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=False) for r in rows]
        write_table(folder, name, pa.table({'ordinal': pa.array(range(len(rows)), type=pa.int64()),
                                         'payload': pa.array(values, type=pa.string())}))
    con = connect(folder, limits)
    try:
        for name in ['files', 'edges', *facts]:
            con.execute('CREATE TABLE '+name+' AS SELECT * FROM read_parquet(?)', [str(folder/(name+'.parquet'))])
        con.execute('CREATE INDEX reverse_edges ON edges(imported)')
        con.execute('CHECKPOINT')
    finally:
        con.close()
    return {f.name: digest(f) for f in sorted(folder.glob('*.parquet'))}


def load(folder, limits):
    con = connect(folder, limits, readonly=True)
    try:
        # Full ordered comparisons: never trust only counts or persisted seal.
        files = con.sql('SELECT * FROM files ORDER BY id').to_arrow_table()
        edge_table = con.sql('SELECT * FROM edges ORDER BY importer, imported').to_arrow_table()
        edges = np.column_stack([edge_table[n].to_numpy() for n in ('importer', 'imported')]).astype(np.int64)
        for name in ('files', 'edges', 'repositories', 'events', 'resolutions', 'external', 'configs', 'metadata'):
            order = 'id' if name == 'files' else 'importer, imported' if name == 'edges' else 'ordinal'
            sql = con.sql('SELECT * FROM '+name+' ORDER BY '+order).to_arrow_table()
            parquet = pq.read_table(Path(folder)/(name+'.parquet'))
            if not sql.equals(parquet):
                raise ValueError('database/parquet mismatch: '+name)
        facts = {name: [json.loads(x) for x in con.execute('SELECT payload FROM '+name+' ORDER BY ordinal').fetchnumpy()['payload']]
                 for name in ('repositories', 'events', 'resolutions', 'external', 'configs', 'metadata')}
        return files, edges, facts
    finally:
        con.close()
