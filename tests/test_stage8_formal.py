"""Complete-export regression checks for the contextual stage 8 source bridge."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from repo_proof.stage8_graph import synthetic, reverse_index, search
from repo_proof.stage8_lean import render_scalable, render_source
from stage8_proof_audit import audit_graph, audit_source


class Stage8FormalTests(unittest.TestCase):
    def test_blocked_export_above_previous_limit_and_complete_audit(self):
        n = 256
        edges = synthetic(n, 'chain')
        ids, p, r = search(n, reverse_index(n, edges), 0)
        text = render_scalable(n, edges, 0, ids, p[ids], r[ids])
        self.assertTrue(audit_graph(text, n, edges, 0, ids, p[ids], r[ids]))
        for bad in (text + 'axiom extra : False\n', text.replace('by decide +kernel', 'by sorry', 1),
                    text.replace('witnessBlock0 v', 'witnessBlock1 v', 1),
                    text.replace('some (0, 0)', 'some (0, 1)', 1)):
            with self.subTest(attack=bad[-80: ]):
                with self.assertRaises(ValueError):
                    audit_graph(bad, n, edges, 0, ids, p[ids], r[ids])

    def test_contextual_source_export_bytes_rules_universe_and_answer(self):
        identities = [('a', '1' * 40, 'a.mojom'), ('b', '2' * 40, 'b.mojom'), ('c', '3' * 40, 'c.mojom')]
        sources = [b'module a; import "dep/b.mojom";', b'module b; import "dep/c.mojom";',
                 b'module c; import "dep/a.mojom"; import "external/other.mojom";']
        rules = [{'id': str(i), 'from': list(identities[i][: 2]), 'prefix': 'dep/',
                'to': list(identities[(i + 1) % 3][: 2]), 'target_prefix': '', 'evidence': 'config'} for i in range(3)]
        rules.append({'id': 'external', 'from': list(identities[2][: 2]), 'prefix': 'external/',
                      'to': None, 'target_prefix': '', 'evidence': 'config'})
        edges = np.array([[0, 1], [1, 2], [2, 0]], dtype=np.int64)
        ids, p, r = search(3, reverse_index(3, edges), 0)
        text = render_source(identities, sources, rules, edges, 0, ids, p[ids], r[ids])
        self.assertTrue(audit_source(text, identities, sources, rules, edges, ids))
        for bad in (text + 'run_tac pure ()\n', text.replace('by decide +kernel', 'by native_decide', 1),
                    text.replace('identity0\n', 'identity1\n', 1),
                    text.replace('def answer : List (Fin 3) := [⟨0', 'def answer : List (Fin 3) := [⟨1', 1),
                    text.replace('0x', '0x1', 1)):
            with self.assertRaises(ValueError):
                audit_source(bad, identities, sources, rules, edges, ids)
        wrong = list(sources)
        wrong[0] += b'\n'
        with self.assertRaises(ValueError):
            audit_source(text, identities, wrong, rules, edges, ids)
        with self.assertRaises(ValueError):
            render_source(identities, sources, rules, edges[: -1], 0, ids, p[ids], r[ids])


if __name__ == '__main__':
    unittest.main()
