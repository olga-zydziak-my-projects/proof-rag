"""Cache trust tests use a tiny independent acceptance anchor, no Lean bypass.

The source-byte audit is stubbed only in these IO-boundary unit tests. Actual
source reconstruction and the imported real proof are exercised by Stage 6's
integration run. No fake acceptance receipt is used by the public program.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from repo_proof import stage6_cache as cache
from repo_proof.generator import generate_certificate
from repo_proof.stage5_answer_v2 import expected_answer
from repo_proof.stage5_v2 import Blob, Captured, ROOT, canonical, snapshot_payload


class CacheFixture:
    def __init__(self, project):
        self.project = Path(project)
        self.source = self.project / "accepted-run"
        (self.source / "lean").mkdir(parents=True)
        self.pin = {"repository": "fixture", "commit": "a" * 40,
                    "tree": "b" * 40, "manifest_sha256": "c" * 64}
        graph = {"nodes": [ROOT], "edges": []}
        self.captured = Captured(self.pin, (Blob(ROOT, b"module tiny;", "d" * 40, "100644"),),
                                 graph, generate_certificate(graph, ROOT), {})
        self.nonce = "1" * 32
        artifacts = {}
        checks = [{"name": "lean_version", "passed": True,
                   "stdout": "Lean (version 4.35.0, fixture)"}]
        for name in cache.MODULES:
            for ext in ("lean", "olean"):
                p = self.source / "lean" / f"{name}.{ext}"
                p.write_bytes((name + ":" + ext).encode())
                artifacts[f"lean/{name}.{ext}"] = cache.file_identity(p)
            axioms = {name + ".accepted": []}
            if name == "ChromiumSource":
                axioms = {name + "." + theorem: ["propext"] for theorem in
                          ("source_bound", "paths_unique", "source_to_answer")}
            checks.append({"name": name, "passed": True, "exit_code": 0,
                           "timed_out": False, "run_nonce": self.nonce,
                           "axioms": axioms,
                           "source": artifacts[f"lean/{name}.lean"],
                           "compiled": artifacts[f"lean/{name}.olean"]})
        code = {}
        for rel in ("docs/stage5-contract-v2.md", "docs/stage5-source-spec-v2.md",
                    "src/repo_proof/corpus.py", "scripts/stage5_v2_audit_bytes.py"):
            p = self.project / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(("fixture source " + rel).encode())
            code[rel] = cache.file_identity(p)
        self.report = {"status": "STAGE5_PASS", "stage5_pass": True,
                       "gates": {f"G{i}": "PASS" for i in range(1, 9)},
                       "gate_conditions": {f"G{i}": True for i in range(1, 9)},
                       "run_nonce": self.nonce, "checks": checks,
                       "artifacts": artifacts, "code_at_start": code,
                       "regression": {"pin": deepcopy(self.pin)},
                       "answer": {"canonical": cache._bytes_identity(canonical(expected_answer(self.captured)))}}
        for name, value in (("snapshot", snapshot_payload(self.captured)),
                            ("graph", graph), ("certificate", self.captured.certificate)):
            (self.source / (name + ".json")).write_bytes(canonical(value))
        receipt = {"schema": "stage5-operational-receipt-v2", "run_nonce": self.nonce,
                   "seal": {"nonce": self.nonce},
                   "compiled": {name: artifacts[f"lean/{name}.olean"] for name in cache.MODULES}}
        (self.source / "operational-receipt.json").write_bytes(canonical(receipt))


class PreparedCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = CacheFixture(self.temporary.name)
        self.project = self.fixture.project
        self.prepared = self.project / "prepared"
        self.anchor = patch.object(cache, "_git_blob", side_effect=lambda *_: canonical(self.fixture.report))
        self.anchor.start()
        self.addCleanup(self.anchor.stop)
        self.byte_audit = patch.object(cache, "_byte_audit", return_value={"passed": True})
        self.byte_audit.start()
        self.addCleanup(self.byte_audit.stop)

    def prepare(self, folder=None):
        return cache.prepare_cache(self.project, folder or self.prepared,
                                   self.fixture.source, captured=self.fixture.captured)

    def validate(self):
        return cache.validate_cache(self.project, self.prepared, captured=self.fixture.captured)

    def test_valid_copy_is_deterministic_and_never_overwrites(self):
        first = self.prepare()
        second = self.prepare(self.project / "another-prepared")
        self.assertEqual(first, second)
        self.assertEqual(first, self.validate())
        self.assertTrue(first["source_proof"]["reused"])
        self.assertFalse(first["source_proof"]["fresh_source_compilation"])
        self.assertEqual(len(first["source_proof"]["modules"]), 41)
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.prepare()

    def test_rehashing_modified_dependency_does_not_authorize_it(self):
        manifest = self.prepare()
        changed = self.prepared / "lean/ChromiumSource.olean"
        changed.write_bytes(b"attacker supplied proof")
        manifest["files"]["lean/ChromiumSource.olean"] = cache.file_identity(changed)
        manifest["identity"] = "a" * 64
        (self.prepared / cache.MANIFEST).write_bytes(canonical(manifest))
        with self.assertRaisesRegex(ValueError, "proof bytes changed"):
            self.validate()

    def test_rehashing_source_graph_or_certificate_is_rejected(self):
        original = self.prepare()
        for rel in ("snapshot.json", "graph.json", "certificate.json", "lean/SourceNames.lean"):
            with self.subTest(rel=rel):
                path = self.prepared / rel
                saved = path.read_bytes()
                path.write_bytes(saved + b" ")
                altered = deepcopy(original)
                altered["files"][rel] = cache.file_identity(path)
                (self.prepared / cache.MANIFEST).write_bytes(canonical(altered))
                with self.assertRaisesRegex(ValueError, "proof bytes changed"):
                    self.validate()
                path.write_bytes(saved)
        (self.prepared / cache.MANIFEST).write_bytes(canonical(original))
        self.validate()

    def test_missing_extra_and_shadow_artifacts_are_rejected(self):
        self.prepare()
        for name in ("lean/Injected.olean", "lean/ChromiumSource.ilean", "unexpected.json"):
            with self.subTest(name=name):
                path = self.prepared / name
                path.write_bytes(b"injected")
                with self.assertRaisesRegex(ValueError, "inventory changed"):
                    self.validate()
                path.unlink()
        missing = self.prepared / "lean/SourceNames.olean"
        missing.unlink()
        with self.assertRaisesRegex(ValueError, "inventory changed"):
            self.validate()

    def test_manifest_cannot_choose_other_anchor_nonce_or_bool_encoding(self):
        original = self.prepare()
        for kind in ("anchor", "nonce", "bool"):
            with self.subTest(kind=kind):
                changed = deepcopy(original)
                if kind == "anchor":
                    changed["anchor"]["project_commit"] = "0" * 40
                elif kind == "nonce":
                    changed["source_proof"]["run_nonce"] = "0" * 32
                else:
                    changed["source_proof"]["reused"] = 1
                (self.prepared / cache.MANIFEST).write_bytes(canonical(changed))
                with self.assertRaisesRegex(ValueError, "independent source-proof anchor"):
                    self.validate()

    def test_changed_specification_or_replay_code_invalidates_cache(self):
        self.prepare()
        for rel in ("docs/stage5-source-spec-v2.md", "src/repo_proof/corpus.py"):
            with self.subTest(rel=rel):
                p = self.project / rel
                before = p.read_bytes()
                p.write_bytes(before + b" changed")
                with self.assertRaisesRegex(ValueError, "code/specification changed"):
                    self.validate()
                p.write_bytes(before)

    def test_changed_snapshot_identity_or_graph_is_rejected(self):
        self.prepare()
        self.fixture.captured.pin["commit"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "different source snapshot"):
            self.validate()
        self.fixture.captured.pin["commit"] = "a" * 40
        self.fixture.captured.graph["edges"] = [[ROOT, ROOT]]
        with self.assertRaisesRegex(ValueError, "graph/certificate differs"):
            self.validate()

    def test_source_run_mixing_is_rejected_before_copy(self):
        p = self.fixture.source / "operational-receipt.json"
        receipt = json.loads(p.read_bytes())
        receipt["run_nonce"] = "2" * 32
        p.write_bytes(canonical(receipt))
        with self.assertRaisesRegex(ValueError, "run receipt mismatch"):
            self.prepare()
        self.assertFalse(self.prepared.exists())

    def test_preparation_cannot_write_inside_accepted_run(self):
        target = self.fixture.source / "new-cache"
        with self.assertRaisesRegex(ValueError, "must not modify"):
            self.prepare(target)
        self.assertFalse(target.exists())

    def test_incomplete_or_non_boolean_acceptance_is_rejected(self):
        for field in ("stage5_pass", "condition", "module"):
            with self.subTest(field=field):
                original = deepcopy(self.fixture.report)
                if field == "stage5_pass":
                    self.fixture.report["stage5_pass"] = 1
                elif field == "condition":
                    self.fixture.report["gate_conditions"]["G3"] = 1
                else:
                    self.fixture.report["checks"].pop()
                with self.assertRaises(ValueError):
                    self.prepare()
                self.fixture.report = original

    def test_symbolic_link_cache_is_not_followed(self):
        self.prepare()
        link = self.project / "cache-link"
        try:
            link.symlink_to(self.prepared, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            import _winapi
            try:
                _winapi.CreateJunction(str(self.prepared), str(link))
            except OSError:
                self.skipTest("OS denies symlink and junction creation; reparse metadata checked separately")
        with self.assertRaisesRegex(ValueError, "link or reparse"):
            cache.validate_cache(self.project, link, captured=self.fixture.captured)

    def test_windows_reparse_attribute_is_rejected(self):
        original = Path.lstat
        def metadata(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path == self.project:
                return SimpleNamespace(st_mode=value.st_mode, st_file_attributes=1024)
            return value
        with patch.object(Path, "lstat", metadata):
            with self.assertRaisesRegex(ValueError, "link or reparse"):
                cache._normal_path(self.project, exists=True)

    def test_scoped_git_environment_preserves_and_restores_existing_entries(self):
        env = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.autocrlf",
               "GIT_CONFIG_VALUE_0": "false", "GIT_CONFIG_KEY_1": "old-unused",
               "GIT_CONFIG_VALUE_1": "old-unused-value", "GIT_NO_REPLACE_OBJECTS": "0"}
        with patch.dict(os.environ, env, clear=True):
            before = dict(os.environ)
            with cache._git_environment(self.project):
                self.assertEqual(os.environ["GIT_CONFIG_COUNT"], "2")
                self.assertEqual(os.environ["GIT_CONFIG_KEY_0"], "core.autocrlf")
                self.assertEqual(os.environ["GIT_CONFIG_KEY_1"], "safe.directory")
                self.assertEqual(os.environ["GIT_CONFIG_VALUE_1"], self.project.resolve().as_posix())
                self.assertEqual(os.environ["GIT_NO_REPLACE_OBJECTS"], "1")
            self.assertEqual(dict(os.environ), before)

    def test_git_anchor_read_disables_replace_overlays_and_lazy_fetch(self):
        # Exercise the real helper underneath the fixture's independent anchor.
        self.anchor.stop()
        with patch.object(cache.subprocess, "run", return_value=SimpleNamespace(stdout=b"anchor")) as run:
            self.assertEqual(cache._git_blob(self.project, cache.REPORT), b"anchor")
        command = run.call_args.args[0]
        self.assertIn(cache.BASELINE + ":" + cache.REPORT, command)
        self.assertEqual(run.call_args.kwargs["env"]["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(run.call_args.kwargs["env"]["GIT_NO_LAZY_FETCH"], "1")


if __name__ == "__main__":
    unittest.main()
