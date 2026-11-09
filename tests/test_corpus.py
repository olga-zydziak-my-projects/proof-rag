"""Offline integration tests with real synthetic Git objects, including boundaries."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from repo_proof import corpus


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "corpus"
        self.store = self.root / "git"
        self.store.mkdir(parents=True)
        self.call("init", "--bare", str(self.store), bare=False)
        self.source_a = b'module sample;\r\nimport "nested/b.mojom";\r\n'
        self.source_b = b"module sample;\n"
        self.source_weird = b"// original bytes\r\nmodule sample;\n"
        self.a_oid = self.blob(self.source_a)
        self.b_oid = self.blob(self.source_b)
        self.weird_oid = self.blob(self.source_weird)
        empty = self.tree([])
        external_commit = self.call("commit-tree", empty, data=b"external fixture\n").decode().strip()
        nested = self.tree([("100644", "blob", self.b_oid, b"b.mojom")])
        root_tree = self.tree([
            ("100644", "blob", self.a_oid, b"a.mojom"),
            ("100644", "blob", self.weird_oid, b"tab\tand\nnewline.mojom"),
            ("100644", "blob", self.blob(b"not selected"), b"UPPER.MOJOM"),
            ("100755", "blob", self.blob(b"#!/bin/sh\n"), b"runner"),
            ("120000", "blob", self.blob(b"a.mojom"), b"link.mojom"),
            ("160000", "commit", external_commit, b"external"),
            ("040000", "tree", nested, b"nested"),
        ])
        self.commit = self.call("commit-tree", root_tree, data=b"corpus fixture\n").decode().strip()
        self.pinning = patch.object(corpus, "COMMIT", self.commit)
        self.pinning.start()
        self.addCleanup(self.pinning.stop)
        self.references = patch.object(corpus, "REFERENCES", ())
        self.references.start()
        self.addCleanup(self.references.stop)

    def call(self, *args, data=None, bare=True):
        command = ["git"] + (["--git-dir=" + str(self.store)] if bare else []) + list(args)
        env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                   GIT_AUTHOR_DATE="2000-01-01T00:00:00Z", GIT_COMMITTER_DATE="2000-01-01T00:00:00Z",
                   GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
        return subprocess.run(command, input=data, capture_output=True, env=env, check=True).stdout

    def blob(self, data):
        return self.call("hash-object", "-w", "--stdin", data=data).decode().strip()

    def tree(self, entries):
        data = b"".join(f"{mode} {kind} {oid}\t".encode() + name + b"\0"
                        for mode, kind, oid, name in entries)
        return self.call("mktree", "-z", data=data).decode().strip()

    def test_real_git_tree_has_all_categories_and_preserves_special_paths(self):
        tree, raw, entries = corpus.read_tree(self.store)
        self.assertEqual(40, len(tree))
        self.assertTrue(raw.endswith(b"\0"))
        self.assertEqual(8, len(entries))
        self.assertEqual({"regular", "tree", "symlink", "gitlink"},
                         {entry["category"] for entry in entries})
        self.assertEqual(3, sum(map(corpus.selected, entries)))
        self.assertIn("tab\tand\nnewline.mojom", {entry["path"] for entry in entries})
        self.assertFalse(any(corpus.selected(e) for e in entries if e["category"] != "regular"))

    def test_prepare_then_offline_verify_and_rerun_are_byte_deterministic(self):
        first = corpus.run(self.root)
        manifest_bytes = (self.root / "manifest.json").read_bytes()
        offline = corpus.run(self.root, offline=True)
        second = corpus.run(self.root)
        self.assertEqual(manifest_bytes, (self.root / "manifest.json").read_bytes())
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
        self.assertEqual(first["manifest_sha256"], offline["manifest_sha256"])
        self.assertEqual(3, first["new_materialized_blob_objects"])
        self.assertEqual(0, second["new_materialized_blob_objects"])
        self.assertEqual(3, second["reused_blob_objects"])
        self.assertEqual(0, second["requested_missing_git_blob_objects"])
        self.assertEqual(self.source_a, corpus.read_blob(self.root, self.a_oid))
        self.assertEqual(len(self.source_a) + len(self.source_b) + len(self.source_weird),
                         first["mojom_bytes_by_path"])
        manifest = json.loads(manifest_bytes)
        rows = {entry["path"]: entry for entry in manifest["entries"]}
        self.assertEqual("link_not_materialized", rows["link.mojom"]["availability"])
        self.assertEqual("external_not_fetched", rows["external"]["availability"])
        self.assertEqual("not_selected", rows["UPPER.MOJOM"]["availability"])
        self.assertEqual(hashlib.sha256(self.source_a).hexdigest(), rows["a.mojom"]["sha256"])

    def test_interruption_retains_verified_blobs_and_resume_ignores_partial_write(self):
        with self.assertRaisesRegex(corpus.CorpusError, "intentional interruption"):
            corpus.run(self.root, stop_after=1)
        self.assertEqual("interrupted_or_failed", json.loads(
            (self.root / "state.json").read_bytes())["status"])
        self.assertFalse((self.root / "manifest.json").exists())
        with self.assertRaises((corpus.CorpusError, FileNotFoundError)):
            corpus.verify(self.root)
        missing_oid = next(oid for oid in (self.a_oid, self.b_oid, self.weird_oid)
                           if not corpus.blob_path(self.root, oid).exists())
        destination = corpus.blob_path(self.root, missing_oid)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.with_name(destination.name + ".part").write_bytes(b"interrupted bytes")
        resumed = corpus.run(self.root)
        self.assertEqual(1, resumed["reused_blob_objects"])
        self.assertEqual(2, resumed["new_materialized_blob_objects"])
        self.assertFalse(destination.with_name(destination.name + ".part").exists())
        self.assertEqual("complete", json.loads((self.root / "state.json").read_bytes())["status"])
        corpus.verify(self.root)

    def test_modified_blob_is_rejected_offline_then_repaired_from_git(self):
        corpus.run(self.root)
        corpus.blob_path(self.root, self.a_oid).write_bytes(self.source_a.replace(b"\r\n", b"\n"))
        with self.assertRaisesRegex(corpus.CorpusError, "identity mismatch"):
            corpus.verify(self.root)
        repaired = corpus.run(self.root)
        self.assertEqual(1, repaired["new_materialized_blob_objects"])
        self.assertEqual(0, repaired["requested_missing_git_blob_objects"])
        self.assertEqual(self.source_a, corpus.read_blob(self.root, self.a_oid))

    def test_omitted_manifest_row_and_altered_hash_are_rejected(self):
        corpus.run(self.root)
        path = self.root / "manifest.json"
        original = path.read_bytes()
        manifest = json.loads(original)
        manifest["entries"].pop()
        path.write_bytes(corpus.encoded(manifest))
        with self.assertRaisesRegex(corpus.CorpusError, "manifest differs"):
            corpus.verify(self.root)
        manifest = json.loads(original)
        next(row for row in manifest["entries"] if row["path"] == "a.mojom")["sha256"] = "0" * 64
        path.write_bytes(corpus.encoded(manifest))
        with self.assertRaisesRegex(corpus.CorpusError, "manifest differs"):
            corpus.verify(self.root)

    def test_saved_tree_omission_is_rejected(self):
        corpus.run(self.root)
        path = self.root / "tree.entries.z"
        raw = path.read_bytes()
        path.write_bytes(raw[raw.index(b"\0") + 1:])
        with self.assertRaisesRegex(corpus.CorpusError, "saved tree metadata differs"):
            corpus.verify(self.root)

    def test_wrong_pinned_commit_is_rejected_offline(self):
        corpus.run(self.root)
        with patch.object(corpus, "COMMIT", "0" * 40):
            with self.assertRaises(corpus.CorpusError):
                corpus.verify(self.root)

    def test_failed_blob_fetch_leaves_recoverable_metadata_without_manifest(self):
        object_path = self.store / "objects" / self.a_oid[:2] / self.a_oid[2:]
        stored_bytes = object_path.read_bytes()
        object_path.chmod(stat.S_IREAD | stat.S_IWRITE)
        object_path.unlink()
        original_git = corpus.git

        def interrupted_fetch(store, *args, **kwargs):
            if args[0] == "fetch":
                raise corpus.CorpusError("simulated interrupted blob transport")
            return original_git(store, *args, **kwargs)

        with patch.object(corpus, "git", side_effect=interrupted_fetch):
            with self.assertRaisesRegex(corpus.CorpusError, "interrupted blob transport"):
                corpus.run(self.root)
        self.assertTrue((self.root / "tree.entries.z").exists())
        self.assertFalse((self.root / "manifest.json").exists())
        self.assertEqual("interrupted_or_failed", json.loads(
            (self.root / "state.json").read_bytes())["status"])
        object_path.write_bytes(stored_bytes)
        resumed = corpus.run(self.root)
        self.assertTrue(resumed["selected_content_complete"])
        corpus.verify(self.root)

    def test_offline_git_command_disables_lazy_fetch(self):
        completed = subprocess.CompletedProcess([], 0, stdout=b"", stderr=b"")
        with patch.object(corpus.subprocess, "run", return_value=completed) as mocked:
            corpus.git(self.store, "cat-file", "--batch-check")
        self.assertEqual("1", mocked.call_args.kwargs["env"]["GIT_NO_LAZY_FETCH"])
        self.assertIn("protocol.file.allow=never", mocked.call_args.args[0])

    def test_presence_probe_uses_offline_git_wrapper(self):
        real_run = subprocess.run

        def inspect_probe(command, **kwargs):
            if "rev-parse" in command:
                self.assertEqual("1", kwargs["env"]["GIT_NO_LAZY_FETCH"])
                self.assertEqual("0", kwargs["env"]["GIT_TERMINAL_PROMPT"])
            return real_run(command, **kwargs)

        with patch.object(corpus.subprocess, "run", side_effect=inspect_probe):
            corpus.run(self.root)

    def test_nested_nonexistent_root_reaches_fetch_without_disk_usage_failure(self):
        nested = self.root / "new" / "deep" / "corpus"
        original_git = corpus.git

        def reject_network(store, *args, **kwargs):
            if args[0] == "fetch":
                raise corpus.CorpusError("expected fixture fetch failure")
            return original_git(store, *args, **kwargs)

        with patch.object(corpus, "git", side_effect=reject_network):
            with self.assertRaisesRegex(corpus.CorpusError, "expected fixture fetch failure"):
                corpus.run(nested)
        self.assertEqual("interrupted_or_failed", json.loads(
            (nested / "state.json").read_bytes())["status"])


class TreeParserTests(unittest.TestCase):
    def test_truncated_duplicate_or_unknown_mode_fail_closed(self):
        record = b"100644 blob " + b"a" * 40 + b"\ta.mojom\0"
        for raw in (record[:-1], record + record, b"\0" + record, record + b"\0",
                    record.replace(b"100644", b"100600"),
                    record.replace(b"a.mojom", b"../a.mojom")):
            with self.subTest(raw=raw):
                with self.assertRaises(corpus.CorpusError):
                    corpus.parse_tree(raw)

    def test_non_utf8_git_name_is_representable_without_losing_bytes(self):
        raw = b"100644 blob " + b"a" * 40 + b"\tname\xff.mojom\0"
        entries = corpus.parse_tree(raw)
        self.assertEqual(b"name\xff.mojom", entries[0]["path"].encode("utf-8", "surrogateescape"))
        self.assertEqual(entries, json.loads(corpus.encoded(entries)))


if __name__ == "__main__":
    unittest.main()
