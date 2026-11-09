"""Adversarial source/certificate binding checks against fresh reconstruction."""
import copy
from dataclasses import replace
import unittest
from unittest.mock import patch

from repo_proof import generate_certificate, verify_certificate
from repo_proof.extraction import SourceBindingError
from repo_proof.graph import ValidationError, graph_sha256
from repo_proof.instance import verify_instance

from test_extraction import SyntheticCorpus


class InstanceTests(unittest.TestCase):
    def test_explicit_null_graph_or_result_is_not_an_omitted_optional_input(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            for field in ("graph", "result"):
                with self.subTest(field=field):
                    with self.assertRaises(SourceBindingError):
                        verify_instance(fixture.root, fixture.expected, extraction, certificate, **{field: None})

    def test_full_verifier_reconstructs_sources_without_calling_generator(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            with patch("repo_proof.generator.generate_certificate", side_effect=AssertionError("search called")):
                result, times = verify_instance(fixture.root, fixture.expected, extraction, certificate,
                                               graph=extraction["graph"])
            self.assertEqual("complete_for_declared_scope", result["status"])
            self.assertTrue(result["source_complete"])
            self.assertEqual(["a.mojom", "b.mojom", "r.mojom"], result["result"])
            self.assertGreaterEqual(times["full_instance_verification_seconds"],
                                    times["repeated_certificate_verification_seconds"])
            repeated, _ = verify_instance(fixture.root, fixture.expected, extraction, certificate, result=result)
            self.assertEqual(result, repeated)

    def test_unresolved_unrelated_file_never_becomes_complete_source_answer(self):
        with SyntheticCorpus({"r.mojom": b"module target;", "a.mojom": b'import "r.mojom";',
                              "broken.mojom": b"struct Bad { !!! };"}) as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            result, _ = verify_instance(fixture.root, fixture.expected, extraction, certificate)
            self.assertEqual("accepted_for_reconstructed_graph", result["graph_certificate_status"])
            self.assertEqual("unresolved", result["status"])
            self.assertFalse(result["source_complete"])
            self.assertEqual(["a.mojom", "r.mojom"], result["result"])

    def test_edge_deleted_before_generation_passes_graph_checker_but_fails_source_binding(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            tampered = copy.deepcopy(extraction)
            tampered["graph"]["edges"].remove(["a.mojom", "r.mojom"])
            tampered["graph_sha256"] = graph_sha256(tampered["graph"])
            certificate = generate_certificate(tampered["graph"], fixture.expected.root)
            self.assertTrue(verify_certificate(tampered["graph"], fixture.expected.root, certificate))
            self.assertEqual(["r.mojom"], [r["node"] for r in certificate["candidates"]])
            with self.assertRaisesRegex(SourceBindingError, "reconstructed from verified source"):
                verify_instance(fixture.root, fixture.expected, tampered, certificate)

    def test_standalone_graph_provenance_and_bool_type_substitution_are_rejected(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            standalone = copy.deepcopy(extraction["graph"])
            standalone["edges"].pop()
            with self.assertRaisesRegex(SourceBindingError, "standalone graph"):
                verify_instance(fixture.root, fixture.expected, extraction, certificate, graph=standalone)
            for field in ("provenance", "bool"):
                modified = copy.deepcopy(extraction)
                if field == "provenance":
                    modified["files"][0]["imports"][0]["original_literal"] = '"forged.mojom"'
                else:
                    modified["coverage"]["all_S_have_terminal_status"] = 1
                with self.subTest(field=field):
                    with self.assertRaisesRegex(SourceBindingError, "provenance/diagnostics"):
                        verify_instance(fixture.root, fixture.expected, modified, certificate)

    def test_expected_root_and_certificate_result_omission_or_addition_are_rejected(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            with self.assertRaises(ValidationError):
                verify_instance(fixture.root, replace(fixture.expected, root="a.mojom"), extraction, certificate)
            with self.assertRaisesRegex(SourceBindingError, "out_of_scope"):
                verify_instance(fixture.root, replace(fixture.expected, root="R.mojom"), extraction, certificate)
            omitted = copy.deepcopy(certificate)
            omitted["candidates"] = [r for r in omitted["candidates"] if r["node"] != "b.mojom"]
            extra = copy.deepcopy(certificate)
            extra["candidates"].append({"node": "x.mojom", "parent": "r.mojom", "rank": 1})
            for altered in (omitted, extra):
                with self.subTest(altered=altered):
                    with self.assertRaises(ValidationError):
                        verify_instance(fixture.root, fixture.expected, extraction, altered)

    def test_displayed_result_substitution_is_checked_against_certificate_and_sources(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            result, _ = verify_instance(fixture.root, fixture.expected, extraction, certificate)
            result["result"].remove("b.mojom")
            result["result_count"] -= 1
            with self.assertRaisesRegex(SourceBindingError, "query result differs"):
                verify_instance(fixture.root, fixture.expected, extraction, certificate, result=result)

    def test_full_verification_rechecks_source_bytes_and_refuses_stale_complete_artifact(self):
        with SyntheticCorpus() as fixture:
            extraction = fixture.extract()
            certificate = generate_certificate(extraction["graph"], fixture.expected.root)
            fixture.blob_path("x.mojom").unlink()  # Outside the root's dependency component.
            with self.assertRaisesRegex(SourceBindingError, "provenance/diagnostics"):
                verify_instance(fixture.root, fixture.expected, extraction, certificate)
            partial = fixture.extract()
            self.assertEqual(extraction["graph"], partial["graph"])
            result, _ = verify_instance(fixture.root, fixture.expected, partial, certificate)
            self.assertEqual("unresolved", result["status"])
            self.assertFalse(result["source_complete"])
            self.assertEqual("accepted_for_reconstructed_graph", result["graph_certificate_status"])


if __name__ == "__main__":
    unittest.main()
