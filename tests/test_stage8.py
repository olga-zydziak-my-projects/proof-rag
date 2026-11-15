"""Offline tests. All Git repositories below are explicitly synthetic fixtures."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from repo_proof.stage5_v2 import canonical
from repo_proof.stage8_fixture import create
from repo_proof.stage8_sources import capture, resolve_event, identity
from repo_proof.stage8_graph import synthetic, validate_graph, reverse_index, search, traverse, reference, check_certificate, fixed_point
from repo_proof.stage8_store import build, load
from repo_proof.stage8_lean import render, audit

LIMITS = {'duckdb_memory': '256MB', 'duckdb_temp': '1GB', 'threads': 1}


class Stage8Tests(unittest.TestCase):
    def test_three_graph_families_full_reference_and_certificate(self):
        for family in ('chain', 'modular', 'cycles'):
            edges = validate_graph(64, synthetic(64, family))
            for root in (0, 32, 63):
                with self.subTest(family=family, root=root):
                    ids, parent, rank = search(64, reverse_index(64, edges), root)
                    self.assertTrue(check_certificate(64, edges, root, ids, parent[ids], rank[ids]))
                    np.testing.assert_array_equal(ids, reference(64, edges, root))
                    np.testing.assert_array_equal(ids, traverse(64, reverse_index(64, edges), root))
                    np.testing.assert_array_equal(ids, fixed_point(64, edges, root))

    def test_rejects_incomplete_or_substituted_certificates(self):
        edges = synthetic(12, 'chain')
        ids, p, r = search(12, reverse_index(12, edges), 0)
        attacks = [(ids[:-1], p[ids[:-1]], r[ids[:-1]]),
                   (ids, p[ids], np.zeros(len(ids), dtype=np.int64)),
                   (ids, np.full(len(ids), -1, dtype=np.int64), r[ids])]
        for i, ps, rs in attacks:
            with self.assertRaises(ValueError):
                check_certificate(12, edges, 0, i, ps, rs)
        with self.assertRaises(ValueError):
            check_certificate(12, edges, 5, ids, p[ids], r[ids])

    def test_collision_versions_and_missing_resolution(self):
        a, b, c = ('a', '1'*40, 'same.mojom'), ('b', '2'*40, 'same.mojom'), ('b', '3'*40, 'same.mojom')
        self.assertEqual(len({identity(*a), identity(*b), identity(*c)}), 3)
        rules = [{'id': 'r', 'from': list(a[:2]), 'prefix': '', 'to': list(b[:2]), 'target_prefix': ''}]
        self.assertEqual(resolve_event(a, 'same.mojom', rules, {a, b, c})[0], b)
        for bad in ([], rules+rules):
            with self.assertRaises(ValueError):
                resolve_event(a, 'same.mojom', bad, {a, b, c})
        with self.assertRaises(ValueError):
            resolve_event(a, 'same.mojom', rules, {a, c})
        with self.assertRaises(ValueError):
            resolve_event(a, '../same.mojom', rules, {a, b})

    def test_manifest_complete_source_fixture_and_external(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            m, anchor, locations = create(folder)
            files, edges, facts = capture(folder/'manifest.json', anchor, locations)
            self.assertEqual((len(files), len(edges), len(facts['events']), len(facts['external'])), (4, 3, 4, 1))
            self.assertEqual(facts['metadata'][0]['manifest']['origin'], 'synthetic-fixture')
            ids, p, r = search(4, reverse_index(4, edges), 0)
            self.assertEqual(len(ids), 3)
            check_certificate(4, edges, 0, ids, p[ids], r[ids])
            cache = Path(temp)/'cache'
            cache.mkdir()
            build(cache, files, edges, facts, LIMITS)
            f, e, data = load(cache, LIMITS)
            self.assertTrue(files.equals(f))
            np.testing.assert_array_equal(e, edges)
            self.assertEqual(data, facts)
            # Physical database edge substitution conflicts with full Parquet facts.
            import duckdb
            con = duckdb.connect(str(cache/'index.duckdb'))
            con.execute('DELETE FROM edges WHERE importer=0')
            con.close()
            with self.assertRaises(ValueError):
                load(cache, LIMITS)

    def test_missing_repo_and_blob(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            m, anchor, locations = create(folder)
            with self.assertRaises(ValueError):
                capture(folder/'manifest.json', anchor, {})
            broken = deepcopy(m)
            broken['repositories'][0]['files'][0]['blob'] = '0'*40
            raw = canonical(broken)
            (folder/'bad.json').write_bytes(raw)
            with self.assertRaises(ValueError):
                capture(folder/'bad.json', sha256(raw).hexdigest(), locations)

    def test_all_manifest_mutations_fail_independent_anchor(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            m, anchor, locations = create(folder)
            attacks = []
            for name in ('commit', 'tree'):
                bad = deepcopy(m)
                bad['repositories'][0][name] = '0'*40
                attacks.append(bad)
            bad = deepcopy(m); bad['repositories'].pop(); attacks.append(bad)
            bad = deepcopy(m); bad['repositories'][0]['files'].pop(); attacks.append(bad)
            bad = deepcopy(m); bad['repositories'][0]['files'][0]['sha256'] = '0'*64; attacks.append(bad)
            bad = deepcopy(m); bad['rules'][0]['to'][1] = '0'*40; attacks.append(bad)
            bad = deepcopy(m); bad['rules'][0]['target_prefix'] = 'wrong/'; attacks.append(bad)
            for i, bad in enumerate(attacks):
                with self.subTest(i=i):
                    (folder/'bad.json').write_bytes(canonical(bad))
                    with self.assertRaises(ValueError):
                        capture(folder/'bad.json', anchor, locations)

    def test_bad_semantics_even_with_new_manifest_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'fixture'
            m, _, locations = create(folder)
            attacks = []
            bad = deepcopy(m); bad['repositories'][0]['files'].pop(); attacks.append(bad)
            bad = deepcopy(m); bad['rules'].append(bad['rules'][0]); attacks.append(bad)
            bad = deepcopy(m); bad['rules'][0]['to'][1] = '0'*40; attacks.append(bad)
            bad = deepcopy(m); bad['configs'][0]['sha256'] = '0'*64; attacks.append(bad)
            for bad in attacks:
                raw = canonical(bad)
                (folder/'bad.json').write_bytes(raw)
                with self.assertRaises(ValueError):
                    capture(folder/'bad.json', sha256(raw).hexdigest(), locations)

    def test_complete_lean_grammar_and_mutations(self):
        edges = synthetic(8, 'cycles')
        ids, p, r = search(8, reverse_index(8, edges), 0)
        text = render(8, edges, 0, ids, p[ids], r[ids])
        self.assertTrue(audit(text, 8, edges, 0, ids, p[ids], r[ids]))
        for bad in (text+'\nrun_tac pure ()\n', text.replace('by decide +kernel', 'by sorry', 1),
                    text.replace('#print axioms Stage8Graph.exact\n', ''),
                    text.replace('def root : Fin 8 := ⟨0', 'def root : Fin 8 := ⟨1')):
            with self.assertRaises(ValueError):
                audit(bad, 8, edges, 0, ids, p[ids], r[ids])

    def test_strict_axiom_reports(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
        from stage6_support import audit as axioms
        from repo_proof.stage8_lean import NAMES
        good = '\n'.join("'"+name+"' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in NAMES)
        self.assertEqual(len(axioms(good, names=NAMES)), 3)
        for bad in (good+'\n'+good, good.splitlines()[0], good.replace('Quot.sound', 'sorryAx')):
            with self.assertRaises(ValueError):
                axioms(bad, names=NAMES)

    def test_monitor_tolerates_disappearing_temp_file(self):
        import sys
        from unittest.mock import Mock, patch
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
        from stage8_supervise import directory_bytes
        vanished = Mock()
        vanished.is_file.return_value = True
        vanished.stat.side_effect = FileNotFoundError('DuckDB removed temp file')
        with patch('stage8_supervise.Path') as constructor:
            constructor.return_value.rglob.return_value = [vanished]
            self.assertEqual(directory_bytes('fake'), 0)


if __name__ == '__main__':
    unittest.main()
