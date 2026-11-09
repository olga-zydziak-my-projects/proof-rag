"""Exercise saved-artifact replay, deterministic CLI output, and exit statuses."""
import contextlib
import io
import json
from pathlib import Path
import unittest

from repo_proof import corpus
from repo_proof.experiment import main
from test_extraction import SyntheticCorpus


class ExperimentTests(unittest.TestCase):
    def test_explicit_json_null_in_required_bundle_files_is_rejected(self):
        with SyntheticCorpus() as fixture:
            common = self.inputs(fixture)
            directory = fixture.root.parent / "bundle"
            self.assertEqual(0, self.quiet(["run", *common, "--artifact-dir", str(directory)])[0])
            for filename in ("graph.json", "query.json"):
                path = directory / filename
                original = path.read_bytes()
                path.write_bytes(b"null\n")
                status, _, _ = self.quiet(["verify", *common, "--artifact-dir", str(directory)])
                self.assertEqual(2, status, filename)
                path.write_bytes(original)

    def inputs(self, fixture):
        base = fixture.root.parent
        config, lock = base / "local-config.json", base / "source-lock.json"
        config.write_bytes(corpus.encoded({"repository": corpus.REPOSITORY,
                                          "commit": fixture.commit, "data_dir": str(fixture.root)}))
        lock.write_bytes(corpus.encoded({"repository": corpus.REPOSITORY, "commit": fixture.commit,
                                        "manifest_sha256": fixture.expected.manifest_sha256}))
        return ["--config", str(config), "--lock", str(lock), "--root", fixture.expected.root]

    def quiet(self, args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = main(args)
        return status, output.getvalue(), error.getvalue()

    def test_run_replay_repeat_compare_and_tampering_are_offline(self):
        with SyntheticCorpus() as fixture:
            common = self.inputs(fixture)
            first, second = fixture.root.parent / "first", fixture.root.parent / "second"
            for directory in (first, second):
                status, _, error = self.quiet(["run", *common, "--artifact-dir", str(directory)])
                self.assertEqual(0, status, error)
            self.assertEqual(0, self.quiet(["verify", *common, "--artifact-dir", str(first)])[0])
            self.assertEqual(0, self.quiet(["compare", "--first", str(first), "--second", str(second)])[0])
            status, output, error = self.quiet(["tamper", *common, "--artifact-dir", str(first)])
            self.assertEqual(0, status, error)
            report = json.loads(output)
            self.assertTrue(report["all_tampering_rejected"])
            dropped = report["cases"][-1]
            self.assertTrue(dropped["graph_checker_accepted_modified_graph"])
            self.assertTrue(dropped["source_binding_rejected"])

    def test_displayed_result_mutation_is_rejected_by_cli_replay(self):
        with SyntheticCorpus() as fixture:
            common = self.inputs(fixture)
            directory = fixture.root.parent / "bundle"
            self.assertEqual(0, self.quiet(["run", *common, "--artifact-dir", str(directory)])[0])
            path = directory / "query.json"
            result = json.loads(path.read_bytes())
            result["result"].remove("b.mojom")
            path.write_bytes(corpus.encoded(result))
            status, _, error = self.quiet(["verify", *common, "--artifact-dir", str(directory)])
            self.assertEqual(2, status)
            self.assertIn("query result differs", error)

    def test_unresolved_source_has_distinct_exit_code_and_terminal_file_record(self):
        with SyntheticCorpus({"r.mojom": b"module target;", "bad.mojom": b"struct Bad { !!! };"}) as fixture:
            common = self.inputs(fixture)
            directory = fixture.root.parent / "bundle"
            status, output, error = self.quiet(["run", *common, "--artifact-dir", str(directory)])
            self.assertEqual(3, status, error)
            report = json.loads(output)
            self.assertEqual("unresolved", report["status"])
            self.assertEqual(2, report["coverage"]["source_files"])
            self.assertEqual(1, report["coverage"]["file_statuses"]["unresolved"])
            self.assertEqual(3, self.quiet(["verify", *common, "--artifact-dir", str(directory)])[0])


if __name__ == "__main__":
    unittest.main()
