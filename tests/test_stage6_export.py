import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_stage6_binding import audit_query
from repo_proof.generator import generate_certificate
from repo_proof.stage6_export import render_query


class Stage6QueryExportTests(unittest.TestCase):
    def setUp(self):
        self.graph = {"nodes": ["a", "b", "c", "isolated"], "edges": [["a", "b"], ["b", "a"], ["c", "b"]]}

    def test_every_root_cycle_and_isolate_has_a_different_complete_query(self):
        sizes = []
        for root in self.graph["nodes"]:
            cert = generate_certificate(self.graph, root)
            source = render_query(self.graph, root, cert)
            checked = audit_query(source, self.graph, root, cert)
            self.assertTrue(checked["passed"])
            sizes.append(checked["output_paths_compared"])
            self.assertEqual(source, render_query(self.graph, root, cert))
            self.assertIn("ChromiumSource.source_bound accepted answer_checked p", source)
        self.assertEqual(sizes, [3, 3, 1, 1])

    def test_cross_query_certificate_and_source_rejected(self):
        first = generate_certificate(self.graph, "a")
        second = generate_certificate(self.graph, "b")
        source = render_query(self.graph, "a", first)
        with self.assertRaises(ValueError):
            render_query(self.graph, "a", second)
        with self.assertRaises(ValueError):
            audit_query(source, self.graph, "b", second)

    def test_complete_proof_and_declaration_grammar(self):
        # Cross both independent proof-splitting thresholds and witness blocks.
        for size in (1, 17, 65, 129):
            graph = {"nodes": [f"n{i:03}" for i in range(size)], "edges": []}
            cert = generate_certificate(graph, "n000")
            source = render_query(graph, "n000", cert)
            self.assertTrue(audit_query(source, graph, "n000", cert)["passed"])
            mutations = [
                source.replace("  apply fastCheck_of_parts", "  run_tac pure ()\n  apply fastCheck_of_parts"),
                source.replace("  fastCheck_refines graph root certificate accepted",
                               "  by exact fastCheck_refines graph root certificate accepted"),
                source.replace("  · timed_kernel_decide", "  · decide +kernel", 1),
                source.replace("def root :", "-- injected comment\ndef root :", 1),
                source + "-- trailing content\n",
                source.replace("#print axioms QueryProof.accepted", "#check QueryProof.accepted"),
            ]
            for changed in mutations:
                with self.subTest(size=size, changed=changed[-100:]):
                    self.assertNotEqual(source, changed)
                    with self.assertRaises(ValueError):
                        audit_query(changed, graph, "n000", cert)

    def test_independent_audit_detects_query_data_substitutions(self):
        cert = generate_certificate(self.graph, "a")
        source = render_query(self.graph, "a", cert)
        mutations = [
            source.replace("def root : Fin 4 := ⟨0,", "def root : Fin 4 := ⟨1,", 1),
            source.replace("some (0, 1)", "some (0, 0)", 1),
            source.replace("resultIDs.map SourceNames.names", "resultIDs.map OtherNames.names", 1),
            source.replace("def graph : BlockedGraph 4 := ChromiumFast.graph", "def graph : BlockedGraph 4 := Another.graph", 1),
            source.replace("def resultIDs : List (Fin 4) := [⟨0, by decide +kernel⟩,", "def resultIDs : List (Fin 4) := [", 1),
            source.replace("if v.val < 2 then", "if v.val < 3 then", 1),
            source.replace("some ⟨⟨0, by decide +kernel⟩, 1,", "some ⟨⟨0, by decide +kernel⟩, 2,", 1),
            source.replace("theorem source_to_answer (p : Path) :", "theorem source_to_answer (p : Path) (impossible : False) :", 1),
            source.replace("theorem paths_unique : payloadPaths.Nodup", "theorem paths_unique : False → payloadPaths.Nodup", 1),
            source.replace("namespace QueryProof", "namespace QueryProof\nset_option debug.skipKernelTC true", 1),
            source.replace("def graph :", '  local notation "False" => True\ndef graph :', 1),
            source.replace("def graph :", "open OtherNamespace\ndef graph :", 1),
        ]
        for modified in mutations:
            self.assertNotEqual(source, modified)
            with self.assertRaises(ValueError):
                audit_query(modified, self.graph, "a", cert)

    def test_strict_inputs_reject_missing_root_boolean_rank_and_duplicate_candidate(self):
        cert = generate_certificate(self.graph, "a")
        with self.assertRaises(ValueError):
            render_query(self.graph, "absent", cert)
        bad = copy.deepcopy(cert)
        bad["candidates"][0]["rank"] = False
        with self.assertRaises(ValueError):
            render_query(self.graph, "a", bad)
        with self.assertRaises(ValueError):
            audit_query(render_query(self.graph, "a", cert), self.graph, "a", bad)
        bad = copy.deepcopy(cert)
        bad["candidates"].append(bad["candidates"][0])
        with self.assertRaises(ValueError):
            render_query(self.graph, "a", bad)
        bad = copy.deepcopy(cert)
        bad["graph_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            audit_query(render_query(self.graph, "a", cert), self.graph, "a", bad)


if __name__ == "__main__":
    unittest.main()
