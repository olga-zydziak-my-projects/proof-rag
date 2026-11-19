"""Fineract R2 fixtures exercise the public command and exact response format."""

from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
import fineract_r2 as cli
import fineract_r2_corpus as corpus_cli
import stage8_supervise
from repo_proof import git_search
from repo_proof.corpus import encoded
from repo_proof.fineract_oracle import ResultMismatch, SourceUnavailable, compare, scan_git


@unittest.skipUnless(sys.platform == "win32", "requires the Windows R2 supervisor")
class FineractR2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("FINERACT_R2_TEST_ROOT")
        if root:
            cls.folder = Path(root).resolve()
            cls.folder.mkdir()
        else:
            temporary = TemporaryDirectory()
            cls.addClassCleanup(temporary.cleanup)
            cls.folder = Path(temporary.name)
        cls.git_store = cls.folder / "fixture.git"
        subprocess.run(["git", "init", "--bare", "--object-format=sha1", cls.git_store],
                       check=True, capture_output=True)
        environment = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                           GIT_AUTHOR_EMAIL="fixture@example.invalid",
                           GIT_COMMITTER_EMAIL="fixture@example.invalid",
                           GIT_AUTHOR_DATE="2000-01-01T00:00:00Z",
                           GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")

        def git(*args, data=None):
            return subprocess.run(["git", "-C", cls.git_store, *args], input=data, check=True,
                                  capture_output=True, env=environment).stdout.strip()

        binary = git("hash-object", "-w", "--stdin", data=b"Needle\r\n\x00Needle.")
        final = git("hash-object", "-w", "--stdin", data=b"row\r\nNeedle")
        empty = git("hash-object", "-w", "--stdin", data=b"")
        link = git("hash-object", "-w", "--stdin", data=b"Needle")
        nested = git("mktree", "-z", data=b"100644 blob " + final + b"\tend-\xff.txt\0")
        tree = git("mktree", "-z", data=b"".join([
            b"100644 blob " + binary + b"\tbinary.bin\0",
            b"100755 blob " + binary + b"\tcopy & [x].bin\0",
            b"040000 tree " + nested + b"\tnested\0",
            b"100644 blob " + empty + b"\tempty\0",
            b"120000 blob " + link + b"\tlink\0",
        ]))
        commit = git("commit-tree", tree.decode("ascii"), "-m", "R2 fixture")
        cls.pin = {"repository": "local/fineract-r2-fixture", "url": cls.git_store.as_uri(),
                   "object_format": "sha1", "commit": commit.decode("ascii"),
                   "root_tree": tree.decode("ascii"), "blob_paths": 5, "regular_paths": 4,
                   "symlinks": 1, "gitlinks": 0}
        cls.spec = {"contract_version": 2, "snapshot": cls.pin, "distinct_regular_blobs": 3}
        cls.contract = cls.folder / "contract.json"
        cls.contract.write_text(json.dumps(cls.spec), encoding="ascii")
        cls.index = cls.folder / "fixture.sqlite"
        cls.binary, cls.final, cls.empty = map(bytes.decode, (binary, final, empty))
        cls.expected = {
            "binary.bin": (cls.binary, 0, 1),
            "copy & [x].bin": (cls.binary, 0, 1),
            "nested/end-\udcff.txt": (cls.final, 5, 2),
        }
        build = cls.execute("build", "--git-dir", cls.git_store, "--contract", cls.contract,
                            "--index", cls.index, "--log-dir", cls.folder / "build-log")
        if build[0] != 0 or build[1]["status"] != "BUILT":
            raise AssertionError(build)
        cls.canonical = cls.folder / "canonical"
        verified = cls.execute("query-verified", "--git-dir", cls.git_store,
                               "--contract", cls.contract, "--index", cls.index,
                               "--literal=Needle", "--output-dir", cls.canonical,
                               "--log-dir", cls.folder / "canonical-log")
        if verified[0] != 0 or verified[1]["status"] != "VERIFIED":
            raise AssertionError(verified)
        cls.rows = [json.loads(line) for line in (cls.canonical / "answer.jsonl").read_bytes().splitlines()]

    @staticmethod
    def execute(*args):
        cmd = [sys.executable, "-B", str(PROJECT / "scripts/fineract_r2.py"), *map(str, args)]
        run = subprocess.run(cmd, cwd=PROJECT, capture_output=True, timeout=30)
        return run.returncode, json.loads(run.stdout), run.stderr.decode("utf-8", "replace")

    def search_arguments(self, out, *, index=None, store=None, contract=None, literal="Needle"):
        return ["query-verified", "--git-dir", str(store or self.git_store),
                "--contract", str(contract or self.contract), "--index", str(index or self.index),
                f"--literal={literal}", "--output-dir", str(out), "--log-dir", str(out) + "-log"]

    def reject(self, name, code, status, **kwargs):
        out = self.folder / name
        actual_code, result, stderr = self.execute(*self.search_arguments(out, **kwargs))
        self.assertEqual((actual_code, result["status"]), (code, status), (result, stderr))
        self.assertFalse(out.exists())
        self.assertNotIn("count", result)
        return result

    def changed_index(self, name, statement, parameters=()):
        copy = self.folder / (name + ".sqlite")
        shutil.copyfile(self.index, copy)
        with sqlite3.connect(copy) as db:
            self.assertEqual(db.execute(statement, parameters).rowcount, 1)
        return copy

    def assert_bad_format(self, name, rows, trailer=b""):
        file = self.folder / f"{name}.jsonl"
        file.write_bytes(b"".join(line if isinstance(line, bytes) else
                                 (json.dumps(line) + "\n").encode("ascii") for line in rows) + trailer)
        with self.assertRaises(ResultMismatch):
            compare(file, self.pin, "Needle", self.expected)

    def test_known_witnesses_and_raw_names(self):
        answer = self.canonical / "answer.jsonl"
        by_path = {row["path"]: (row["blob_id"], row["byte_offset"], row["line"])
                   for row in self.rows[1:-1]}
        receipt = json.loads((self.canonical / "verification.json").read_bytes())
        self.assertEqual(by_path, self.expected)
        self.assertEqual(receipt["status"], "VERIFIED")
        self.assertEqual(receipt["result_sha256"], sha256(answer.read_bytes()).hexdigest())
        self.assertEqual(receipt["inventory"]["excluded_symlinks"][0]["path"], "link")
        self.assertEqual(receipt["inventory"]["regular_paths"], 4)
        self.assertEqual(receipt["inventory"]["distinct_regular_blobs"], 3)
        self.assertEqual(scan_git(self.git_store, self.pin, 3, "Needle")[0], self.expected)

    def test_verified_empty(self):
        out = self.folder / "empty-answer"
        code, report, _ = self.execute(*self.search_arguments(out, literal="NEEDLE"))
        self.assertEqual((code, report["status"], report["count"]), (0, "VERIFIED", 0))
        self.assertEqual(len((out / "answer.jsonl").read_bytes().splitlines()), 2)

    def test_scoped_index_and_raw_git_exclude_other_paths(self):
        scope = ["nested"]
        pin = {**self.pin, "regular_paths": 1, "blob_paths": 1, "symlinks": 0}
        index = self.folder / "scoped.sqlite"
        search = self.folder / "scoped.jsonl"
        git_search.build(self.git_store, pin, index, directories=scope)
        git_search.query(index, pin, "Needle", search, 0, directories=scope)
        expected, inventory = scan_git(self.git_store, pin, 1, "Needle", directories=scope, include_sizes=True)
        self.assertEqual(expected, {"nested/end-\udcff.txt": (self.final, 5, 2)})
        self.assertEqual(inventory["distinct_regular_blob_bytes"], len(b"row\r\nNeedle"))
        self.assertEqual(compare(search, pin, "Needle", expected)["count"], 1)
        with self.assertRaises(ValueError):
            git_search.query(index, pin, "Needle", search, 0)

    def test_corpus_requires_the_complete_zero_hit_section(self):
        pin2 = {**self.pin, "repository": "local/empty"}
        repos = [{"snapshot": self.pin}, {"snapshot": pin2}]
        digest = "1" * 64
        answer = self.folder / "corpus-answer.jsonl"
        prefix = encoded(corpus_cli.header(repos, "Needle", digest)) + (self.canonical / "answer.jsonl").read_bytes()
        empty_header = {**self.rows[0], "repository": pin2["repository"]}
        empty_section = encoded(empty_header) + encoded({"type": "complete", "count": 0})
        footer = encoded(corpus_cli.trailer(repos, [{"count": 3}, {"count": 0}]))
        answer.write_bytes(prefix + empty_section + footer)
        count, per_repo = corpus_cli.compare_corpus(answer, repos, "Needle", digest, [self.expected, {}])
        self.assertEqual((count, [row["count"] for row in per_repo]), (3, [3, 0]))
        answer.write_bytes(prefix + footer)
        with self.assertRaises(ResultMismatch):
            corpus_cli.compare_corpus(answer, repos, "Needle", digest, [self.expected, {}])

    def test_corpus_cleanup_error_preserves_verified_publication(self):
        folder = self.folder / "cln"
        folder.mkdir()
        out = folder / "answer"
        manifest = folder / "manifest.json"
        binary_bytes = len(b"Needle\r\n\x00Needle.")
        nested_bytes = len(b"row\r\nNeedle")
        manifest.write_bytes(encoded({
            "format": "git-literal-corpus-manifest-v1",
            "repositories": [{"id": "fixture", "snapshot": self.pin, "directories": [],
                              "distinct_regular_blobs": 3, "distinct_regular_blob_bytes": binary_bytes + nested_bytes,
                              "regular_path_bytes": 2 * binary_bytes + nested_bytes}],
        }))
        manifest_hash = sha256(manifest.read_bytes()).hexdigest()
        repo = self.pin["repository"]
        expected = (encoded({"type": "corpus-result", "format": "git-literal-corpus-v1", "literal": "Needle",
                             "manifest_sha256": manifest_hash, "repositories": [repo]})
                    + (self.canonical / "answer.jsonl").read_bytes()
                    + encoded({"type": "corpus-complete", "count": 3,
                               "repositories": [{"repository": repo, "count": 3}]}))

        stdout, stderr = io.StringIO(), io.StringIO()
        cleanup_attempts = []
        rmtree = shutil.rmtree

        def deny_scratch_cleanup(path, *args, **kwargs):
            scratch = Path(path)
            if scratch.parent == folder and scratch.name.startswith(".r2-corpus-stage-"):
                self.assertTrue(out.is_dir())
                self.assertTrue((out / "answer.jsonl").is_file())
                self.assertTrue((out / "verification.json").is_file())
                cleanup_attempts.append(scratch)
                raise PermissionError("fixture scratch cleanup denied")
            return rmtree(path, *args, **kwargs)

        args = ["query-verified", "--literal", "Needle", "--manifest", str(manifest),
                "--sources", str(self.folder), "--index", str(self.folder),
                "--output-dir", str(out), "--log-dir", str(folder / "log")]
        with patch.object(corpus_cli.shutil, "rmtree", side_effect=deny_scratch_cleanup), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = corpus_cli.main(args)

        self.assertEqual(len(cleanup_attempts), 1)
        self.assertTrue(cleanup_attempts[0].is_dir())
        report = json.loads(stdout.getvalue())
        self.assertEqual((code, report["status"]), (0, "VERIFIED"), report)
        self.assertIn("fixture scratch cleanup denied", stderr.getvalue())
        receipt = json.loads((out / "verification.json").read_bytes())
        self.assertEqual(receipt["status"], "VERIFIED")
        answer = (out / "answer.jsonl").read_bytes()
        self.assertEqual(answer, expected)
        self.assertEqual(receipt["result_sha256"], sha256(answer).hexdigest())
        self.assertEqual(report["result_sha256"], receipt["result_sha256"])

    def test_corpus_update_matches_full_query_with_same_hit_count(self):
        folder = self.folder / "upd"
        folder.mkdir()
        environment = dict(os.environ, GIT_INDEX_FILE=str(folder / "git.index"),
                           GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                           GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")

        def git(*args, data=None):
            return subprocess.run(["git", "-C", self.git_store, *args], input=data, check=True,
                                  capture_output=True, env=environment).stdout.strip().decode("ascii")

        git("read-tree", self.pin["commit"])
        git("update-index", "-z", "--index-info", data=f"0 {'0' * 40}\tcopy & [x].bin\0".encode("ascii"))
        newly_matching, no_match = b"prefix Needle\n", b"different bytes\n"
        new_oid = git("hash-object", "-w", "--stdin", data=newly_matching)
        no_match_oid = git("hash-object", "-w", "--stdin", data=no_match)
        for mode, oid, path in [("100644", new_oid, "empty"), ("100644", no_match_oid, "binary.bin"),
                                ("100755", self.binary, "renamed.bin")]:
            git("update-index", "--add", "--cacheinfo", f"{mode},{oid},{path}")
        tree_b = git("write-tree")
        commit_b = git("commit-tree", tree_b, "-p", self.pin["commit"], "-m", "Update, remove and rename hits")
        pin_b = {**self.pin, "commit": commit_b, "root_tree": tree_b}

        def manifest(path, pin, distinct, blob_bytes, path_bytes):
            path.write_bytes(encoded({"format": "git-literal-corpus-manifest-v1", "repositories": [{
                "id": "fixture", "snapshot": pin, "directories": [], "distinct_regular_blobs": distinct,
                "distinct_regular_blob_bytes": blob_bytes, "regular_path_bytes": path_bytes,
            }]}))
            return path

        binary, nested = len(b"Needle\r\n\x00Needle."), len(b"row\r\nNeedle")
        manifest_a = manifest(folder / "a.json", self.pin, 3, binary + nested, 2 * binary + nested)
        bytes_b = binary + nested + len(newly_matching) + len(no_match)
        manifest_b = manifest(folder / "b.json", pin_b, 4, bytes_b, bytes_b)

        def run(operation, manifest_file, label, *args, code=0):
            command = [sys.executable, "-B", str(PROJECT / "scripts/fineract_r2_corpus.py"), operation,
                       "--sources", str(self.folder), "--manifest", str(manifest_file),
                       "--log-dir", str(folder / f"{label}-log"), *map(str, args)]
            result = subprocess.run(command, cwd=PROJECT, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, code, (result.stdout, result.stderr))
            return json.loads(result.stdout)

        a, updated, full = (folder / name for name in ("a", "updated", "full"))
        a_receipt = run("query-verified", manifest_a, "a", "--index", self.folder,
                        "--output-dir", a, "--literal=Needle")
        base_args = ("--base-manifest", manifest_a, "--base-answer", a, "--literal=Needle")
        delta = run("update-verified", manifest_b, "updated", *base_args, "--output-dir", updated)
        index_b = folder / "index-b"
        run("build", manifest_b, "build-b", "--index", index_b)
        oracle = run("query-verified", manifest_b, "full", "--index", index_b,
                     "--output-dir", full, "--literal=Needle")
        self.assertEqual([row["count"] for row in (a_receipt, delta, oracle)], [3, 3, 3])
        self.assertEqual(delta["result_sha256"], oracle["result_sha256"])
        self.assertEqual(delta["delta"][0]["changed_regular_paths"], 4)
        self.assertEqual(delta["delta"][0]["git_objects_read"]["blob"]["count"], 3)
        answer = (updated / "answer.jsonl").read_bytes()
        self.assertEqual(answer, (full / "answer.jsonl").read_bytes())
        hits = [row for row in map(json.loads, answer.splitlines()) if row["type"] == "hit"]
        self.assertEqual([(row["path"], row["byte_offset"], row["line"], row["commit"]) for row in hits], [
            ("empty", 7, 1, commit_b), ("nested/end-\udcff.txt", 5, 2, commit_b), ("renamed.bin", 0, 1, commit_b),
        ])

        base_answer = a / "answer.jsonl"
        base_answer.write_bytes(base_answer.read_bytes() + b"\n")
        rejected = folder / "rejected"
        failure = run("update-verified", manifest_b, "rejected", *base_args, "--output-dir", rejected, code=2)
        self.assertEqual(failure["status"], "MISMATCH")
        self.assertFalse(rejected.exists())

    def test_deleted_trigram_reproduces_false_empty_then_rejects(self):
        copy = self.changed_index("deleted-posting", "DELETE FROM postings WHERE gram=?", (b"Nee",))
        candidate = self.folder / "r1-false-empty.jsonl"
        cmd = [sys.executable, "-B", "-m", "repo_proof.git_search", "query",
               "--contract", str(self.contract), "--index", str(copy), "--literal=Needle",
               "--output", str(candidate), "--preview", "0"]
        run = subprocess.run(cmd, cwd=PROJECT, capture_output=True, timeout=30,
                             env=dict(os.environ, PYTHONPATH=str(PROJECT / "src")))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["count"], 0)
        r2 = self.reject("deleted-posting-answer", 2, "MISMATCH", index=copy)
        self.assertEqual(r2["reason"], "result omits 3 Git path(s)")
        (self.folder / "deleted-posting-evidence.json").write_text(json.dumps({
            "removed_postings": 1, "r1_command": cmd, "r1_exit_code": run.returncode,
            "r1_count": 0, "git_count": len(self.expected), "r2_exit_code": 2,
            "r2_status": r2["status"], "r2_published": False,
        }), encoding="ascii")

    def test_changed_blob_bytes(self):
        copy = self.changed_index("changed-bytes", "UPDATE blobs SET data=? WHERE oid=?",
                                  (b"prefix Needle", self.binary))
        self.reject("wrong-blob-bytes", 2, "MISMATCH", index=copy)

    def test_changed_path_mapping(self):
        copy = self.changed_index("changed-mapping", "UPDATE paths SET oid=? WHERE path=?",
                                  (self.empty, b"binary.bin"))
        self.reject("wrong-path-mapping", 2, "MISMATCH", index=copy)

    def test_missing_git_blob(self):
        copy = self.folder / "missing-objects.git"
        parent = self.git_store / "objects" / self.final[:2]
        shutil.copytree(self.git_store, copy, ignore=lambda folder, names:
                        [self.final[2:]] if Path(folder) == parent else [])
        self.reject("missing-blob", 3, "BLOCKED", store=copy)

    def test_wrong_contract_pins(self):
        for field in ("commit", "root_tree"):
            with self.subTest(field=field):
                contract = self.folder / f"wrong-{field}.json"
                contract.write_text(json.dumps({**self.spec, "snapshot":
                                               {**self.pin, field: "0" * 40}}), encoding="ascii")
                code, result, _ = self.execute("build", "--git-dir", self.git_store, "--contract",
                                               contract, "--index", self.folder / f"wrong-{field}.sqlite")
                self.assertEqual((code, result["status"]), (3, "BLOCKED"))
                self.assertFalse((self.folder / f"wrong-{field}.sqlite").exists())
                with self.assertRaises(SourceUnavailable):
                    scan_git(self.git_store, {**self.pin, field: "0" * 40}, 3, "Needle")

    def test_invalid_literals(self):
        for number, literal in enumerate(("", "a\nb", "é", "\x7f")):
            with self.subTest(literal=literal):
                self.reject(f"invalid-literal-{number}", 4, "ERROR", literal=literal)

    def test_existing_output(self):
        out = self.folder / "existing"
        out.mkdir()
        marker = out / "keep"
        marker.write_bytes(b"keep")
        code, result, _ = self.execute(*self.search_arguments(out))
        self.assertEqual((code, result["status"]), (4, "ERROR"))
        self.assertEqual(list(out.iterdir()), [marker])
        self.assertEqual(marker.read_bytes(), b"keep")

    def test_timeout_does_not_publish(self):
        out = self.folder / "timeout"
        code, report, _ = self.execute(*self.search_arguments(out), "--timeout", "0.001")
        self.assertEqual((code, report["status"]), (4, "ERROR"))
        self.assertFalse(out.exists())
        monitor = json.loads((self.folder / "timeout-log/resource-report.json").read_bytes())
        self.assertEqual((monitor["status"], monitor["remaining_job_processes"]), ("TIMEOUT", 0))

    def test_supervised_interrupt_does_not_publish(self):
        out = self.folder / "interrupt"
        stdout = io.StringIO()
        sleep = time.sleep

        def interrupt(delay):
            if delay == 0.02:
                raise KeyboardInterrupt()
            return sleep(delay)

        with patch.object(stage8_supervise.time, "sleep", side_effect=interrupt), redirect_stdout(stdout):
            code = cli.main(self.search_arguments(out))
        self.assertEqual((code, json.loads(stdout.getvalue())["status"]), (4, "ERROR"))
        self.assertFalse(out.exists())
        monitor = json.loads((self.folder / "interrupt-log/resource-report.json").read_bytes())
        self.assertEqual((monitor["status"], monitor["remaining_job_processes"]), ("INTERRUPTED", 0))

    def test_interrupt_mask_at_publication_commit(self):
        out = self.folder / "commit-interrupt"
        stdout = io.StringIO()
        rename = os.rename
        previous = signal.getsignal(signal.SIGINT)

        def interrupt_after_rename(source, destination):
            rename(source, destination)
            if Path(destination) == out:
                self.assertEqual(signal.getsignal(signal.SIGINT), signal.SIG_IGN)
                signal.raise_signal(signal.SIGINT)

        with patch.object(cli.os, "rename", side_effect=interrupt_after_rename), redirect_stdout(stdout):
            code = cli.main(self.search_arguments(out))
        self.assertEqual((code, json.loads(stdout.getvalue())["status"]), (0, "VERIFIED"))
        self.assertEqual(signal.getsignal(signal.SIGINT), previous)
        self.assertTrue((out / "verification.json").exists())

    def test_omitted_and_additional_path(self):
        self.assert_bad_format("omission", [self.rows[0], *self.rows[2:-1],
                                           {"type": "complete", "count": 2}])
        self.assert_bad_format("addition", [*self.rows[:-1], {**self.rows[1], "path": "extra"},
                                           {"type": "complete", "count": 4}])

    def test_second_occurrence_and_wrong_line(self):
        self.assert_bad_format("second-offset",
                               [self.rows[0], {**self.rows[1], "byte_offset": 9, "line": 2},
                                *self.rows[2:]])
        self.assert_bad_format("wrong-line", [self.rows[0], {**self.rows[1], "line": 2}, *self.rows[2:]])

    def test_wrong_result_provenance(self):
        for key in ("commit", "root_tree", "literal", "repository"):
            with self.subTest(key=key):
                self.assert_bad_format("header-" + key, [{**self.rows[0], key: "changed"}, *self.rows[1:]])
        self.assert_bad_format("witness-commit",
                               [self.rows[0], {**self.rows[1], "commit": "0" * 40}, *self.rows[2:]])

    def test_incomplete_and_invalid_jsonl(self):
        self.assert_bad_format("no-footer", self.rows[:-1])
        self.assert_bad_format("invalid-json", [self.rows[0], b'{"bad":\n', *self.rows[2:]])
        self.assert_bad_format("invalid-utf8", [self.rows[0], b'{"path":"\xff"}\n', *self.rows[2:]])
        self.assert_bad_format("trailing-data", self.rows, trailer=b"\n")
        self.assert_bad_format("truncated-footer", [*self.rows[:-1], b'{"count":3,"type":"complete"}'])
        self.assert_bad_format("incorrect-count", [*self.rows[:-1], {"type": "complete", "count": 4}])

    def test_duplicate_keys_paths_and_wrong_types(self):
        repeated_key = json.dumps(self.rows[1])[:-1] + ', "line": 1}\n'
        self.assert_bad_format("duplicate-key", [self.rows[0], repeated_key.encode("ascii"), *self.rows[2:]])
        self.assert_bad_format("duplicate-path", [*self.rows[:-1], self.rows[1], self.rows[-1]])
        self.assert_bad_format("boolean-offset", [self.rows[0], {**self.rows[1], "byte_offset": False},
                                                  *self.rows[2:]])
        self.assert_bad_format("floating-line", [self.rows[0], {**self.rows[1], "line": 1.0}, *self.rows[2:]])
        self.assert_bad_format("incomplete-witness", [self.rows[0], {"type": "hit"}, *self.rows[2:]])
        self.assert_bad_format("wrong-footer-type", [*self.rows[:-1], {"type": "complete", "count": 3.0}])


if __name__ == "__main__":
    unittest.main()
