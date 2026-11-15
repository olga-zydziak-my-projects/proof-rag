from copy import deepcopy
from itertools import product
import unittest
from repo_proof.stage8_acceptance import evaluate


def evidence():
    return {'benchmark_variants': [{'nodes': n, 'family': f, 'passed': True}
            for n, f in product((10000, 100000, 1000000), ('chain', 'modular', 'cycles'))],
        'pilot': {'origin': 'real', 'project_count': 3, 'connected_projects': True,
            'version_and_patch_evidence_checked': True, 'manifest_verified': True,
            'queries': [{'root': str(i), 'source_to_answer_lean': True, 'fresh_kernel': True,
                'full_answer_matches_oracle': True, 'artifacts_verified': True,
                'repository_count': 2 if i < 3 else 1} for i in range(6)]},
        'formal_bridge': {'status': 'SOURCE_BRIDGE_PASS'},
        'negative_tests': dict.fromkeys(('sources', 'mapping', 'versions', 'certificates', 'answers', 'proofs'), True),
        'regressions': {'exit_code': 0, 'no_skips': True, 'identity': True, 'differential_1547': True},
        'code_identity_after': True, 'config_identity_after': True, 'manifest_identity_after': True,
        'supervisor_integration_pass': True,
        'lean_ladder': [measurement(n) for n in (256, 1000, 10000)],
        'source_index_measurements': [{'origin': o, 'status': 'SOURCE_INDEX_PASS', 'artifact_verified': True}
            for o in ('real', 'synthetic-fixture')],
        'code_and_tests': {'src/example.py': {'sha256': 'a'*64, 'bytes': 12}},
        'historical_reports_preserved': True,
        'artifacts_complete_after': True,
        'independent_review': {'blocking_findings': [], 'reviewer_id': 'independent-test-reviewer',
            'independent': True, 'code_and_tests': {'src/example.py': {'sha256': 'a'*64, 'bytes': 12}}}}


def measurement(nodes):
    return {'nodes': nodes, 'executed': True, 'status': 'LEAN_GRAPH_PASS',
            'artifact_verified': True, 'edges': nodes - 1,
            'certificate_nodes': nodes, 'answer_nodes': nodes,
            'tools': {'lean_version': 'test-version', 'lean_sha256': 'a'*64},
            'generation_seconds': .1, 'export_seconds': .1,
            'compilation_seconds': 1., 'checking_seconds': .1,
            'peak_memory_bytes': 1000, 'artifact_bytes': 1000,
            'stop_reason': 'kernel accepted complete answer'}


class AcceptanceTests(unittest.TestCase):
    def test_complete_matrix(self):
        self.assertEqual(evaluate(evidence())['status'], 'STAGE8_PASS')

    def test_missing_evidence_fails_closed(self):
        self.assertEqual(evaluate({})['status'], 'STAGE8_INCOMPLETE')
        attacks = []
        bad = evidence(); bad['benchmark_variants'].pop(); attacks.append(bad)
        bad = evidence(); bad['pilot']['queries'].pop(); attacks.append(bad)
        bad = evidence(); bad['pilot']['queries'][2]['repository_count'] = 1; attacks.append(bad)
        bad = evidence(); bad['manifest_identity_after'] = False; attacks.append(bad)
        bad = evidence(); bad['pilot']['queries'][0]['artifacts_verified'] = False; attacks.append(bad)
        bad = evidence(); bad['code_identity_after'] = False; attacks.append(bad)
        bad = evidence(); bad['artifacts_complete_after'] = False; attacks.append(bad)
        bad = evidence(); bad['pilot']['queries'][0]['full_answer_matches_oracle'] = False; attacks.append(bad)
        for bad in attacks:
            with self.subTest(bad=bad):
                self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')

    def test_ladder_requires_measurements_and_explicit_dependencies(self):
        for field in ('edges', 'certificate_nodes', 'answer_nodes', 'tools',
                      'generation_seconds', 'export_seconds', 'compilation_seconds',
                      'checking_seconds', 'peak_memory_bytes', 'artifact_bytes', 'stop_reason'):
            bad = evidence()
            del bad['lean_ladder'][0][field]
            with self.subTest(field=field):
                self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')
        bad = evidence()
        bad['lean_ladder'].pop()
        self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')
        limited = evidence()
        limited['lean_ladder'][0]['status'] = 'TIMEOUT'
        limited['lean_ladder'][0]['stop_reason'] = 'supervisor timeout after 60 seconds'
        limited['lean_ladder'][1:] = [
            {'nodes': n, 'executed': False, 'status': 'SKIPPED',
             'dependency_nodes': previous, 'stop_reason': 'previous planned level did not pass'}
            for n, previous in ((1000, 256), (10000, 1000))]
        self.assertEqual(evaluate(limited)['status'], 'STAGE8_PASS')
        limited['lean_ladder'][0]['status'] = 'LEAN_GRAPH_PASS'
        self.assertEqual(evaluate(limited)['status'], 'STAGE8_INCOMPLETE')

    def test_review_identity_and_history_are_required(self):
        for field in ('reviewer_id', 'independent', 'code_and_tests'):
            bad = evidence()
            del bad['independent_review'][field]
            self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')
        bad = evidence()
        bad['independent_review']['code_and_tests'] = {'other.py': 'wrong'}
        self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')
        bad = evidence()
        bad['historical_reports_preserved'] = False
        self.assertEqual(evaluate(bad)['status'], 'STAGE8_INCOMPLETE')


if __name__ == '__main__':
    unittest.main()
