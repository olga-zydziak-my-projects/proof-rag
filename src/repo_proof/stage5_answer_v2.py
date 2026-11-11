"""Typed output envelope and complete round-trip checks for Stage 5.

The caller may release output only after successful compilation of the concrete
source-to-answer theorem and its axiom audit. These functions alone prove nothing.
"""
import json
from .stage5_v2 import ROOT, canonical, sha
from .extraction import unique_object


def expected_answer(captured):
    paths = [row['node'] for row in captured.certificate['candidates']]
    names = [blob.path for blob in captured.blobs]
    return {'schema': 'repo-proof-source-answer-v2', 'pin': dict(captured.pin),
            'scope': 'all selected mojom files in the anchored manifest',
            'query': {'root': ROOT, 'root_id': names.index(ROOT),
                      'edge_direction': 'importer-to-imported',
                      'traversal': 'reverse-reachability', 'include_root': True},
            'paths': paths,
            'identities': {'source_manifest_sha256':captured.pin['manifest_sha256'],
                           'graph_sha256':sha(canonical(captured.graph)),
                           'certificate_sha256':sha(canonical(captured.certificate)),
                           'result_sha256':sha(canonical(paths))},
            'verification_receipt': {'schema':'stage5-verification-reference-v2',
                'theorem':'ChromiumSource.source_to_answer',
                'relation':'SourceBytes byte import projection v2',
                'operational_evidence':'operational-receipt.json'}}


def check_answer(value, captured):
    expected = expected_answer(captured)
    # Equality includes the full ordered path list and every metadata field.
    # Bool is not interchangeable with integer values in this typed envelope.
    if canonical(value) != canonical(expected):
        raise ValueError('answer paths, query or snapshot identity changed')
    return expected


def render_answer(value):
    q = value['query']
    return '\n'.join([
        'Repo Proof Lab source answer v2',
        'Repository: '+value['pin']['repository'],
        'Commit: '+value['pin']['commit'],
        'Tree: '+value['pin']['tree'],
        'Manifest SHA256: '+value['pin']['manifest_sha256'],
        'Scope: '+value['scope'],
        'Root: '+q['root'],
        'Root ID: '+str(q['root_id']),
        'Edges: '+q['edge_direction'],
        'Traversal: '+q['traversal'],
        'Include root: '+str(q['include_root']).lower(),
        'Binding: '+json.dumps({'identities':value['identities'],
                               'verification_receipt':value['verification_receipt']},sort_keys=True,separators=(',',':')),
        'Paths:', *value['paths'], ''])


def check_human(text, captured):
    # Independent parsing, not a comparison of a renderer's digest.
    lines = text.splitlines()
    labels = ['Repository', 'Commit', 'Tree', 'Manifest SHA256', 'Scope',
              'Root', 'Root ID', 'Edges', 'Traversal', 'Include root']
    if len(lines) < 13 or lines[0] != 'Repo Proof Lab source answer v2' or lines[12] != 'Paths:':
        raise ValueError('human answer framing')
    fields = {}
    for line, label in zip(lines[1:11], labels):
        prefix = label+': '
        if not line.startswith(prefix):
            raise ValueError('human answer metadata')
        fields[label] = line[len(prefix):]
    if fields['Include root'] not in ('true', 'false'):
        raise ValueError('human root policy')
    if not lines[11].startswith('Binding: '): raise ValueError('human binding metadata')
    binding=json.loads(lines[11][9:],object_pairs_hook=unique_object)
    if set(binding)!= {'identities','verification_receipt'}: raise ValueError('human binding fields')
    value = {'schema': 'repo-proof-source-answer-v2',
             'pin': {'repository': fields['Repository'], 'commit': fields['Commit'],
                     'tree': fields['Tree'], 'manifest_sha256': fields['Manifest SHA256']},
             'scope': fields['Scope'],
             'query': {'root': fields['Root'], 'root_id': int(fields['Root ID']),
                       'edge_direction': fields['Edges'], 'traversal': fields['Traversal'],
                       'include_root': fields['Include root'] == 'true'},
             'paths': lines[13:], **binding}
    return check_answer(value, captured)
