import copy
import unittest
from types import SimpleNamespace

from repo_proof.generator import generate_certificate
from repo_proof.stage5_v2 import canonical
from repo_proof.stage6_answer import expected_answer, check_answer, render_answer, check_human


def fixture():
    return SimpleNamespace(
        graph={'nodes': ['a.mojom', 'b.mojom', 'c.mojom', 'd.mojom', 'z.mojom'],
               'edges': [['a.mojom', 'b.mojom'], ['b.mojom', 'a.mojom'],
                         ['c.mojom', 'd.mojom'], ['d.mojom', 'c.mojom']]},
        pin={'repository': 'fixture', 'commit': 'a'*40, 'tree': 'b'*40,
             'manifest_sha256': 'c'*64})


class Stage6AnswerTests(unittest.TestCase):
    def test_arbitrary_roots_cycles_and_isolated_roundtrip(self):
        c = fixture()
        for root, paths in [('a.mojom', ['a.mojom', 'b.mojom']),
                            ('d.mojom', ['c.mojom', 'd.mojom']), ('z.mojom', ['z.mojom'])]:
            with self.subTest(root=root):
                cert = generate_certificate(c.graph, root)
                value = expected_answer(c, root, cert, 'cache')
                self.assertEqual(value['paths'], paths)
                self.assertEqual(check_human(render_answer(value), c, root, cert, 'cache'), value)
                self.assertEqual(canonical(value), canonical(expected_answer(c, root, cert, 'cache')))

    def test_equal_count_query_and_certificate_swaps_rejected(self):
        c = fixture()
        a, b = 'a.mojom', 'c.mojom'
        ca, cb = (generate_certificate(c.graph, root) for root in (a, b))
        value = expected_answer(c, a, ca, 'cache')
        self.assertEqual(len(ca['candidates']), len(cb['candidates']))
        with self.assertRaises(ValueError):
            check_answer(value, c, b, cb, 'cache')
        with self.assertRaises(ValueError):
            expected_answer(c, b, ca, 'cache')

    def test_all_answer_fields_are_bound_and_typed(self):
        c = fixture(); root = 'a.mojom'; cert = generate_certificate(c.graph, root)
        original = expected_answer(c, root, cert, 'cache')
        changes = [('paths', ['a.mojom', 'c.mojom']), ('paths', ['a.mojom']),
                   ('paths', ['a.mojom', 'b.mojom', 'b.mojom']),
                   ('query', {**original['query'], 'include_root': 1}),
                   ('query', {**original['query'], 'root_id': False}),
                   ('query', {**original['query'], 'root': 'b.mojom'}),
                   ('identities', {**original['identities'], 'source_proof_identity': 'other'}),
                   ('pin', {**original['pin'], 'commit': 'wrong'})]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                changed = copy.deepcopy(original); changed[key] = value
                with self.assertRaises(ValueError):
                    check_answer(changed, c, root, cert, 'cache')
                with self.assertRaises(ValueError):
                    check_human(render_answer(changed), c, root, cert, 'cache')

    def test_duplicate_human_metadata_and_hidden_suffix_rejected(self):
        c = fixture(); root = 'z.mojom'; cert = generate_certificate(c.graph, root)
        text = render_answer(expected_answer(c, root, cert, 'cache'))
        for changed in (text.replace('Metadata: {', 'Metadata: {"pin":{},'),
                        text+'hidden.mojom\n'):
            with self.assertRaises(ValueError):
                check_human(changed, c, root, cert, 'cache')

    def test_output_cannot_mutate_captured_identity(self):
        c = fixture(); cert = generate_certificate(c.graph, 'a.mojom')
        answer = expected_answer(c, 'a.mojom', cert, 'cache')
        answer['pin']['commit'] = 'changed'
        self.assertEqual(c.pin['commit'], 'a'*40)


if __name__ == '__main__':
    unittest.main()
