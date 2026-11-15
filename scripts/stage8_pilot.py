"""Execute six complete source queries against a frozen real Mojom scope."""
from pathlib import Path
import sys
import time
import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT/'src'))
from repo_proof.extraction import read_json
from repo_proof.stage5_v2 import canonical
from repo_proof.stage8_sources import capture, identity
from repo_proof.stage8_graph import reference
from repo_proof.stage8_artifacts import inventory, verify


def connected_projects(files, edges):
    projects = {r['repo_id'] for r in files}
    adjacency = {p: set() for p in projects}
    for a, b in edges:
        x, y = files[int(a)]['repo_id'], files[int(b)]['repo_id']
        adjacency[x].add(y)
        adjacency[y].add(x)
    seen, todo = set(), [next(iter(projects))]
    while todo:
        p = todo.pop()
        if p not in seen:
            seen.add(p)
            todo.extend(adjacency[p]-seen)
    return seen == projects


def run(folder, lean, config, manifest_path, anchor, locations):
    from stage8_lean_check import check_sources
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    files, edges, facts = capture(manifest_path, anchor, locations, spool_dir=folder)
    rows = files.to_pylist()
    names = [identity(r['repo_id'], r['commit'], r['path']) for r in rows]
    manifest = facts['metadata'][0]['manifest']
    # Freeze the complete universe before selecting roots. Prioritize roots
    # whose independently computed answers cross project boundaries.
    answers = {i: reference(len(rows), edges, i).tolist() for i in range(len(rows))}
    roots = sorted(answers, key=lambda i: (-len({rows[j]['repo_id'] for j in answers[i]}), names[i]))[:6]
    selection = {'manifest_sha256': anchor, 'universe': names, 'roots': [names[i] for i in roots],
                 'selection': 'descending number of projects in independent answer, then identity'}
    (folder/'selection.json').write_bytes(canonical(selection))
    report = {'origin': manifest['origin'], 'project_count': len({r['repo_id'] for r in rows}),
        'connected_projects': connected_projects(rows, edges), 'manifest_verified': True,
        'manifest_sha256': anchor, 'files': len(rows), 'edges': len(edges), 'queries': []}
    for index, root in enumerate(roots):
        outcome = check_sources(folder/('query-'+str(index)), lean, config,
                                manifest_path, anchor, locations,
                                (rows[root]['repo_id'], rows[root]['commit'], rows[root]['path']))
        expected = [names[i] for i in answers[root]]
        actual = outcome.get('answer_identities')
        accepted = outcome.get('status') == 'SOURCE_TO_ANSWER_PASS'
        report['queries'].append({'root': names[root], 'answer': actual,
            'oracle_answer': expected, 'full_answer_matches_oracle': actual == expected,
            'repository_count': len({rows[j]['repo_id'] for j in answers[root]}),
            'source_to_answer_lean': accepted,
            'fresh_kernel': accepted and outcome.get('fresh_query_compilation') is True,
            'artifacts_verified': accepted and outcome.get('fresh_source_compilation') is True,
            'artifact_directory': str((folder/('query-'+str(index))).resolve()),
            'artifact_inventory': inventory(folder/('query-'+str(index))),
            'proof': outcome})
        (folder/'pilot-report.json').write_bytes(canonical(report))
    for query in report['queries']:
        verify(query['artifact_directory'], query['artifact_inventory'])
    return report
