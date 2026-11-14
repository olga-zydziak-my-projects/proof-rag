"""Complete answer binding for an explicitly supplied Stage 6 query.

These IO checks do not establish proof acceptance. The public driver releases
answers only after a fresh kernel check against independently anchored imports.
"""
import json

from .checker import verify_certificate
from .extraction import unique_object
from .stage5_v2 import canonical, sha


def expected_answer(captured, root, certificate, cache_identity):
    verify_certificate(captured.graph, root, certificate)
    names = sorted(captured.graph['nodes'])
    paths = sorted(row['node'] for row in certificate['candidates'])
    return {
        'schema': 'repo-proof-source-answer-v3',
        'pin': dict(captured.pin),
        'scope': 'all selected mojom files in the anchored manifest',
        'query': {'root': root, 'root_id': names.index(root),
                  'edge_direction': 'importer-to-imported',
                  'traversal': 'reverse-reachability', 'include_root': True},
        'paths': paths,
        'identities': {'source_manifest_sha256': captured.pin['manifest_sha256'],
                       'graph_sha256': sha(canonical(captured.graph)),
                       'certificate_sha256': sha(canonical(certificate)),
                       'result_sha256': sha(canonical(paths)),
                       'source_proof_identity': cache_identity},
        'verification_receipt': {'schema': 'stage6-verification-reference-v1',
                                 'relation': 'SourceBytes byte import projection v2',
                                 'theorem': 'QueryProof.source_to_answer',
                                 'operational_evidence': 'query-report.json'},
    }


def check_answer(value, captured, root, certificate, cache_identity):
    expected = expected_answer(captured, root, certificate, cache_identity)
    if canonical(value) != canonical(expected):
        raise ValueError('answer paths, root, source proof or metadata changed')
    return expected


def render_answer(value):
    metadata = {k: v for k, v in value.items() if k != 'paths'}
    return '\n'.join(['Repo Proof Lab source answer v3',
                      'Metadata: ' + canonical(metadata).decode('utf-8').rstrip('\n'),
                      'Paths:', *value['paths'], ''])


def check_human(text, captured, root, certificate, cache_identity):
    lines = text.splitlines()
    if (len(lines) < 4 or lines[0] != 'Repo Proof Lab source answer v3'
            or not lines[1].startswith('Metadata: ') or lines[2] != 'Paths:'):
        raise ValueError('human answer framing changed')
    metadata = json.loads(lines[1][10:], object_pairs_hook=unique_object)
    if not isinstance(metadata, dict) or 'paths' in metadata:
        raise ValueError('human answer metadata changed')
    return check_answer({**metadata, 'paths': lines[3:]}, captured, root,
                        certificate, cache_identity)
