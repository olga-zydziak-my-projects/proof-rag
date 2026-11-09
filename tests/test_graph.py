import copy
import itertools
import unittest

from repo_proof import ValidationError, generate_certificate, graph_sha256, verify_certificate


def brute_dependents(graph, root):
    """Independent fixed-point reference; no use of certificate producer."""
    answer = {root}
    while True:
        expanded = answer | {a for a, b in graph["edges"] if b in answer}
        if expanded == answer:
            return answer
        answer = expanded


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "nodes": ["r", "a", "b", "isolated", "x", "y"],
            "edges": [["a", "r"], ["b", "a"], ["a", "b"],
                      ["x", "y"], ["y", "x"]],
        }
        self.cert = generate_certificate(self.graph, "r")

    def rejected(self, cert, graph=None, root="r"):
        with self.assertRaises(ValidationError) as context:
            verify_certificate(self.graph if graph is None else graph, root, cert)
        self.assertTrue(context.exception.errors)
        return context.exception.errors

    def test_all_three_node_directed_graphs_match_independent_reference(self):
        nodes = ["0", "1", "2"]
        possible = list(itertools.product(nodes, repeat=2))
        for bits in range(1 << len(possible)):
            graph = {"nodes": nodes, "edges": [list(edge) for i, edge in enumerate(possible)
                                               if bits & (1 << i)]}
            for root in nodes:
                certificate = generate_certificate(graph, root)
                actual = {item["node"] for item in certificate["candidates"]}
                self.assertEqual(brute_dependents(graph, root), actual)
                self.assertTrue(verify_certificate(graph, root, certificate))

    def test_direction_is_reverse_and_root_is_included(self):
        graph = {"nodes": ["r", "a"], "edges": [["r", "a"]]}
        cert = generate_certificate(graph, "r")
        self.assertEqual(["r"], [item["node"] for item in cert["candidates"]])
        self.assertTrue(verify_certificate(graph, "r", cert))

    def test_reachable_cycle_and_rank_gaps_are_valid(self):
        for item in self.cert["candidates"]:
            item["rank"] *= 10
        self.assertTrue(verify_certificate(self.graph, "r", self.cert))

    def test_omitted_reachable_leaf_is_rejected_by_closure(self):
        self.cert["candidates"] = [i for i in self.cert["candidates"] if i["node"] != "b"]
        self.assertTrue(any("closure" in e for e in self.rejected(self.cert)))

    def test_missing_root_is_rejected(self):
        self.cert["candidates"] = []
        self.rejected(self.cert)

    def test_extra_disconnected_node_is_rejected(self):
        self.cert["candidates"].append({"node": "isolated", "parent": "r", "rank": 1})
        self.assertTrue(any("parent edge" in e for e in self.rejected(self.cert)))

    def test_disconnected_cycle_cannot_prove_itself(self):
        self.cert["candidates"].extend([
            {"node": "x", "parent": "y", "rank": 2},
            {"node": "y", "parent": "x", "rank": 1},
        ])
        self.assertTrue(any("rank must decrease" in e for e in self.rejected(self.cert)))

    def test_wrong_expected_root_and_modified_query_rejected(self):
        self.rejected(self.cert, root="a")
        self.cert["query"]["root"] = "a"
        self.rejected(self.cert)

    def test_wrong_graph_hash_rejected_even_if_reachability_unchanged(self):
        graph = copy.deepcopy(self.graph)
        graph["nodes"].append("another_isolated_node")
        self.assertTrue(any("hash" in e for e in self.rejected(self.cert, graph=graph)))

    def test_graph_order_does_not_change_hash(self):
        graph = {"nodes": self.graph["nodes"][::-1], "edges": self.graph["edges"][::-1]}
        self.assertEqual(graph_sha256(self.graph), graph_sha256(graph))
        self.assertTrue(verify_certificate(graph, "r", self.cert))

    def test_malformed_ranks_fail_closed(self):
        for rank in [True, False, -1, 1.0, "1", None, [], {}]:
            with self.subTest(rank=rank):
                cert = copy.deepcopy(self.cert)
                cert["candidates"][0]["rank"] = rank
                self.rejected(cert)

    def test_bad_parent_types_duplicates_unknown_nodes_fail_closed(self):
        for parent in [[], {}, 1, True, "unknown", None]:
            cert = copy.deepcopy(self.cert)
            next(item for item in cert["candidates"] if item["node"] == "a")["parent"] = parent
            self.rejected(cert)
        cert = copy.deepcopy(self.cert)
        cert["candidates"].append(copy.deepcopy(cert["candidates"][0]))
        self.rejected(cert)
        cert = copy.deepcopy(self.cert)
        cert["candidates"].append({"node": "unknown", "parent": "r", "rank": 1})
        self.rejected(cert)

    def test_malformed_graphs_and_certificates(self):
        graphs = [None, {}, {"nodes": ["r", "r"], "edges": []},
                  {"nodes": ["r"], "edges": [["r", "x"]]},
                  {"nodes": ["r"], "edges": [["r", "r"], ["r", "r"]]},
                  {"nodes": ["r", []], "edges": [None]}]
        for graph in graphs:
            with self.subTest(graph=graph):
                with self.assertRaises(ValidationError):
                    verify_certificate(graph, "r", self.cert)
                with self.assertRaises(ValidationError):
                    generate_certificate(graph, "r")
        for cert in [None, [], {}, {**self.cert, "candidates": {}},
                     {**self.cert, "candidates": [None]},
                     {**self.cert, "extra": True}]:
            self.rejected(cert)

    def test_multiple_independent_errors_are_reported(self):
        self.cert["format"] = "wrong"
        self.cert["graph_sha256"] = "wrong"
        self.cert["query"] = {}
        self.assertGreaterEqual(len(self.rejected(self.cert)), 3)

    def test_nonstring_root_is_validation_error(self):
        self.rejected(self.cert, root=[])
        with self.assertRaises(ValidationError):
            generate_certificate(self.graph, [])


if __name__ == "__main__":
    unittest.main()
