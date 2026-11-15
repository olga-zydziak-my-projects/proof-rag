"""Fail-closed aggregation of evidence produced by the Stage 8 runner."""
from itertools import product
import math


def nonnegative_number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def formal_ladder_complete(rows):
    """Every planned level is measured, or explicitly depends on a stopped level."""
    levels = (256, 1000, 10000)
    if [row.get('nodes') for row in rows] != list(levels):
        return False
    previous = None
    for row in rows:
        if row.get('executed') is False:
            if (previous is None or row.get('status') != 'SKIPPED'
                    or previous.get('status') == 'LEAN_GRAPH_PASS'
                    or row.get('dependency_nodes') != previous['nodes']
                    or not isinstance(row.get('stop_reason'), str) or not row['stop_reason'].strip()):
                return False
        elif row.get('executed') is True:
            if (row.get('status') not in ('LEAN_GRAPH_PASS', 'TIMEOUT', 'RESOURCE_LIMIT', 'FAILED')
                    or row.get('artifact_verified') is not True
                    or not isinstance(row.get('tools'), dict) or not row['tools']
                    or not isinstance(row.get('stop_reason'), str) or not row['stop_reason'].strip()
                    or any(type(row.get(key)) is not int or row[key] < 0 for key in
                           ('edges', 'certificate_nodes', 'answer_nodes', 'peak_memory_bytes', 'artifact_bytes'))
                    or any(not nonnegative_number(row.get(key)) for key in
                           ('generation_seconds', 'export_seconds', 'compilation_seconds', 'checking_seconds'))
                    or row['certificate_nodes'] > row['nodes'] or row['answer_nodes'] > row['nodes']):
                return False
        else:
            return False
        previous = row
    return True


def evaluate(report):
    required = set(product((10000, 100000, 1000000), ('chain', 'modular', 'cycles')))
    variants = report.get('benchmark_variants', [])
    matrix = [(v.get('nodes'), v.get('family')) for v in variants]
    scaling = (len(matrix) == len(required) and set(matrix) == required
               and all(v.get('passed') is True for v in variants))
    pilot = report.get('pilot', {})
    queries = pilot.get('queries', [])
    roots = [q.get('root') for q in queries]
    six = (len(queries) >= 6 and len(set(roots)) == len(roots)
           and all(q.get('source_to_answer_lean') is True
                   and q.get('fresh_kernel') is True
                   and q.get('full_answer_matches_oracle') is True
                   and q.get('artifacts_verified') is True for q in queries))
    corpus = (pilot.get('origin') == 'real' and pilot.get('project_count', 0) >= 3
              and pilot.get('connected_projects') is True
              and pilot.get('version_and_patch_evidence_checked') is True
              and pilot.get('manifest_verified') is True)
    bridge = report.get('formal_bridge', {}).get('status') == 'SOURCE_BRIDGE_PASS'
    cross = sum(q.get('repository_count', 0) > 1 for q in queries) >= 3
    negative = report.get('negative_tests', {})
    rejections = all(negative.get(k) is True for k in
                     ('sources', 'mapping', 'versions', 'certificates', 'answers', 'proofs'))
    regression = report.get('regressions', {})
    regressions = (regression.get('exit_code') == 0 and regression.get('no_skips') is True
                   and regression.get('identity') is True and regression.get('differential_1547') is True)
    identity = all(report.get(k) is True for k in
                   ('code_identity_after', 'config_identity_after', 'manifest_identity_after'))
    supervisor = report.get('supervisor_integration_pass') is True
    ladder = report.get('lean_ladder', [])
    formal_scale = formal_ladder_complete(ladder)
    indexing = report.get('source_index_measurements', [])
    source_scale = all(any(r.get('origin') == origin and r.get('status') == 'SOURCE_INDEX_PASS'
                              and r.get('artifact_verified') is True for r in indexing)
                       for origin in ('real', 'synthetic-fixture'))
    reviewed = report.get('independent_review', {})
    review = (reviewed.get('blocking_findings') == []
              and isinstance(reviewed.get('reviewer_id'), str) and bool(reviewed['reviewer_id'].strip())
              and reviewed.get('independent') is True
              and bool(report.get('code_and_tests'))
              and reviewed.get('code_and_tests') == report['code_and_tests'])
    preserved = report.get('historical_reports_preserved') is True
    artifacts = report.get('artifacts_complete_after') is True
    pilot_pass = corpus and bridge and six and cross and rejections
    components = {'corpus': corpus, 'formal_bridge': bridge, 'pilot': pilot_pass,
                  'scaling': scaling, 'regressions': regressions, 'supervisor': supervisor,
                  'formal_scaling': formal_scale, 'source_indexing': source_scale,
                  'code_identity': identity, 'review': review, 'historical_reports': preserved,
                  'artifacts': artifacts}
    return {'status': 'STAGE8_PASS' if all(components.values()) else 'STAGE8_INCOMPLETE',
            'components': components}
