from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT / "scripts"

PAUSE_AFTER_MISSING_BRAVE = r"""
import io
import os
from pathlib import Path
import runpy
import sys

sys.argv.pop(0)
sys.path.insert(0, str(Path(sys.argv[0]).parent))
import fineract_r2_current as current

control = sys.stdin
sys.stdin = io.TextIOWrapper(io.BytesIO(control.readline().encode("ascii")), encoding="ascii")
config, entry = current.corpus_entry(Path(os.environ["REPO_PROOF_CURRENT_CONFIG"]), "default")
brave = current.pr_room(config, entry, "default", "brave", 1) / "view.json"
read_bytes = Path.read_bytes

def pause_after_missing_brave(path):
    try:
        return read_bytes(path)
    except FileNotFoundError:
        if path == brave:
            print("brave-missing", file=sys.stderr, flush=True)
            if control.readline() != "continue\n":
                raise RuntimeError("test did not release the PR scan")
        raise

Path.read_bytes = pause_after_missing_brave
runpy.run_path(sys.argv[0], run_name="__main__")
"""


class CheckedR2Fixture(unittest.TestCase):
    repository_id = "demo"

    def setUp(self):
        directory = TemporaryDirectory(prefix="rc")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.author, self.sources, self.agent = (self.root / name for name in ("w", "s", "a"))
        self.server = self.sources / f"{self.repository_id}.git"
        self.index, self.manifest, self.config = (self.root / name for name in ("i", "m.json", "c.json"))
        self.env = dict(os.environ, GIT_ALLOW_PROTOCOL="file", GIT_NO_LAZY_FETCH="1",
                        REPO_PROOF_CURRENT_CONFIG=str(self.config))
        self.git(self.root, "init", "--quiet", "--object-format=sha1", "-b", "main", self.author)
        self.git(self.author, "config", "user.name", "R2 Test")
        self.git(self.author, "config", "user.email", "r2@example.invalid")
        self.git(self.author, "config", "commit.gpgsign", "false")
        self.git(self.author, "config", "core.autocrlf", "false")
        (self.author / "src").mkdir()
        files = {"a": b"!\nneedle needle\n", "b": b"!\nneedle needle\n",
                 "c": b"nee eed edl dle\n", "d": b"unrelated\n"}
        for name, data in files.items():
            (self.author / "src" / name).write_bytes(data)
        (self.author / "outside").write_bytes(b"needle")
        self.git(self.author, "add", ".")
        self.git(self.author, "commit", "--quiet", "-m", "A")
        self.old = self.git(self.author, "rev-parse", "HEAD")
        tree = self.git(self.author, "rev-parse", "HEAD^{tree}")
        self.sources.mkdir()
        self.git(self.root, "init", "--bare", "--quiet", "--object-format=sha1", self.server)
        self.git(self.author, "push", self.server.as_uri(), "main:main")
        self.repo = self.repository(self.repository_id, self.server)
        pin = {k: self.repo[k] for k in ("repository", "url")}
        pin.update(commit=self.old, root_tree=tree, object_format="sha1", regular_paths=4, blob_paths=4,
                   symlinks=0, gitlinks=0)
        entry = {"id": self.repository_id, "directories": ["src"], "snapshot": pin,
                 "distinct_regular_blobs": 3, "distinct_regular_blob_bytes": sum(map(len, set(files.values()))),
                 "regular_path_bytes": sum(map(len, files.values()))}
        self.write(self.manifest, {"format": "git-literal-corpus-manifest-v1", "repositories": [entry]})
        self.cli("fineract_r2_corpus.py", "build", "--sources", self.sources, "--manifest", self.manifest,
                 "--index", self.index, "--log-dir", self.root / "bl")

    def repository(self, name, server):
        return {"id": name, "repository": f"example/{name}", "url": f"https://example.invalid/{name}.git",
                "directories": ["src"], "remote": server.as_uri(), "branch": "main"}

    def write(self, path, data):
        path.write_bytes(json.dumps(data).encode("ascii"))

    def git(self, directory, *args):
        proc = subprocess.run(["git", "-C", str(directory), *map(str, args)], env=self.env, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip().decode("ascii")

    def cli(self, script, *args, code=0, data=None):
        proc = subprocess.run([sys.executable, "-B", "-X", "utf8", str(SCRIPTS / script), *map(str, args)],
                              env=self.env, cwd=PROJECT, input=data, capture_output=True, timeout=60)
        self.assertEqual(proc.returncode, code, (proc.stdout, proc.stderr))
        return json.loads(proc.stdout)

    def prepare(self, index, output, code=0):
        return self.cli("prepare_checked_r2_index.py", "--sources", self.sources, "--manifest", self.manifest,
                        "--index", index, "--output", output, code=code)

    def configure(self, checked, receipt, index):
        self.write(self.config, {"corpora": {"default": {"workspace": str(self.agent),
                   "repositories": [self.repo], "seed_index": str(index),
                   "checked_index": {"directory": str(checked), "receipt_sha256": receipt["receipt_sha256"]}}}})

    def query(self, literal="needle", code=0):
        return self.cli("fineract_r2_current.py", "query", literal, code=code)

    def hits(self, result):
        return [(r["path"], r["byte_offset"], r["line"]) for r in result["answer"] if r["type"] == "hit"]

    def answer(self, result):
        return Path(result["output_directory"], "answer.jsonl").read_bytes()

    def configure_two_prs(self, name):
        server = self.sources / f"{name}.git"
        other = self.repository(name, server)
        self.git(self.root, "init", "--bare", "--quiet", "--object-format=sha1", server)
        self.git(self.author, "push", server.as_uri(), "main:main")
        manifest = json.loads(self.manifest.read_bytes())
        [initial] = manifest["repositories"]
        manifest["repositories"].append({**initial, "id": name, "snapshot": {
            **initial["snapshot"], "repository": other["repository"], "url": other["url"],
        }})
        self.write(self.manifest, manifest)
        index = self.root / "two"
        self.cli("fineract_r2_corpus.py", "build", "--sources", self.sources, "--manifest", self.manifest,
                 "--index", index, "--log-dir", self.root / "two-log")
        checked = self.root / "two-checked"
        receipt = self.prepare(index, checked)
        self.configure(checked, receipt, index)
        config = json.loads(self.config.read_bytes())
        config["corpora"]["default"].update(pr_directory="pr", repositories=[self.repo, other])
        self.write(self.config, config)
        return server

    def push_feature(self, name, server, literal):
        self.git(self.author, "checkout", "--quiet", "-b", name, self.old)
        (self.author / "src" / name).write_bytes(literal.encode("ascii"))
        self.git(self.author, "add", ".")
        self.git(self.author, "commit", "--quiet", "-m", f"Add {name} path")
        commit = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", server.as_uri(), f"{name}:feature")
        return commit


@unittest.skipUnless(sys.platform == "win32", "requires the Windows R2 supervisor")
class CheckedR2Tests(CheckedR2Fixture):
    def test_prepare_publishes_the_manifest_bytes_read_before_source_changes(self):
        with patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
            from prepare_checked_r2_index import prepare

        self.git(self.author, "commit", "--quiet", "--allow-empty", "-m", "B")
        b = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", self.server.as_uri(), "main:main")
        original = self.manifest.read_bytes()
        changed = json.loads(original)
        changed["repositories"][0]["snapshot"]["commit"] = b
        checked = self.root / "race"
        read_bytes = Path.read_bytes
        reads = []

        def replace_after_read(path):
            data = read_bytes(path)
            if path == self.manifest:
                reads.append(data)
                self.write(path, changed)
            return data

        with patch.object(Path, "read_bytes", replace_after_read):
            result = prepare(self.sources, self.manifest, self.index, checked)

        self.assertEqual(reads, [original])
        self.assertEqual(json.loads(self.manifest.read_bytes()), changed)
        self.assertEqual((checked / "manifest.json").read_bytes(), original)
        self.assertEqual(result["manifest_sha256"], sha256(original).hexdigest())
        receipt = json.loads((checked / "receipt.json").read_bytes())
        self.assertEqual(receipt["manifest_sha256"], sha256(original).hexdigest())

    def configure_pr(self):
        checked = self.root / "checked"
        receipt = self.prepare(self.index, checked)
        self.configure(checked, receipt, self.index)
        config = json.loads(self.config.read_bytes())
        config["corpora"]["default"]["pr_directory"] = "pr"
        self.write(self.config, config)

    def test_opened_pr_with_existing_changes_publishes_checked_index(self):
        self.configure_pr()
        self.git(self.author, "checkout", "--quiet", "-b", "feature")
        literal = "already-in-pr"
        (self.author / "src/new").write_bytes(literal.encode("ascii"))
        self.git(self.author, "add", "src/new")
        self.git(self.author, "commit", "--quiet", "-m", "Add file before opening PR")
        commit = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", self.server.as_uri(), "feature:feature")

        event = {"action": "opened", "number": 1, "repository": "demo", "base": "main", "head": "feature"}
        payload = json.dumps(event).encode("ascii")
        opened = self.cli("fineract_r2_pr.py", "event", data=payload)
        self.assertEqual(opened["status"], "REGISTERED")
        self.assertEqual((opened["base_head"]["commit"], opened["pr_head"]["commit"]), (self.old, commit))
        ready_path = Path(opened["view_directory"]) / "ready.json"
        self.assertTrue(ready_path.is_file(), "opened must activate the index before any synchronize event or query")
        ready = json.loads(ready_path.read_bytes())
        releases = set((ready_path.parent / "r").iterdir())

        result = self.cli("fineract_r2_current.py", "query", "--pr", 1, literal)
        self.assertEqual((result["status"], result["operation"], result["full_git_scans"]),
                         ("VERIFIED", "query-checked", 0))
        self.assertEqual(result["checked_index_sha256"], ready["receipt_sha256"])
        self.assertEqual(result["selection"]["repositories"][0]["commit"], commit)
        self.assertEqual(self.hits(result), [("src/new", 0, 1)])
        base = self.query(literal)
        self.assertEqual((base["status"], base["selection"]["repositories"][0]["commit"], self.hits(base)),
                         ("VERIFIED", self.old, []))

        repeated = self.cli("fineract_r2_pr.py", "event", data=payload)
        self.assertEqual(repeated["status"], "REGISTERED")
        self.assertEqual(json.loads(ready_path.read_bytes()), ready)
        self.assertEqual(set((ready_path.parent / "r").iterdir()), releases)

    def test_pull_request_event_registers_a_view_and_activates_the_new_checked_index(self):
        self.configure_pr()
        self.git(self.author, "checkout", "--quiet", "-b", "feature")
        self.git(self.author, "push", self.server.as_uri(), "feature:feature")

        def event(action, **fields):
            data = json.dumps({"action": action, "number": 1, **fields}).encode("ascii")
            return self.cli("fineract_r2_pr.py", "event", data=data)

        def search(literal, pr=True):
            view = ("--pr", 1) if pr else ()
            return self.cli("fineract_r2_current.py", "query", *view, literal)

        self.assertFalse(list(self.root.glob("pr/*/view.json")))
        opened = event("opened", repository="demo", base="main", head="feature")
        room = Path(opened["view_directory"])
        self.assertEqual(opened["status"], "REGISTERED")
        self.assertEqual(opened["pr_head"]["commit"], self.old)
        self.assertEqual(search("needle")["operation"], "query-checked")

        (self.author / "src/new").write_bytes(b"one-unique-result\n")
        self.git(self.author, "add", "src/new")
        self.git(self.author, "commit", "--quiet", "-m", "B")
        b = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", self.server.as_uri(), "feature:feature")
        first = search("one-unique-result")
        self.assertEqual((first["operation"], first["checked_fallback"]), ("query-verified", "snapshot_changed"))
        self.assertEqual(first["selection"]["repositories"][0]["commit"], b)
        self.assertEqual(self.hits(first), [("src/new", 0, 1)])
        base = search("one-unique-result", pr=False)
        self.assertEqual((base["count"], base["selection"]["repositories"][0]["commit"]), (0, self.old))
        self.assertFalse((room / "ready.json").exists())

        refreshed = event("synchronize")
        self.assertEqual(refreshed["status"], "READY")
        self.assertEqual(refreshed["candidate_rebuilt"], ["demo"])
        self.assertEqual(refreshed["selection"][0]["commit"], b)
        self.assertEqual(refreshed["verification"]["reconciled_repositories"], ["demo"])
        second = search("one-unique-result")
        self.assertEqual(second["operation"], "query-checked")
        self.assertEqual(second["checked_index_sha256"], refreshed["receipt_sha256"])
        self.assertEqual(self.answer(first), self.answer(second))
        old_path = search("needle")
        self.assertEqual(old_path["selection"]["repositories"][0]["commit"], b)
        self.assertEqual(self.hits(old_path), [("src/a", 2, 2), ("src/b", 2, 2)])
        self.assertTrue(event("synchronize")["already_ready"])

    def test_legacy_pr_remains_selectable_without_leaking_to_another_corpus(self):
        self.configure_pr()
        config = json.loads(self.config.read_bytes())
        config["corpora"]["other"] = config["corpora"]["default"]
        self.write(self.config, config)
        self.git(self.author, "checkout", "--quiet", "-b", "feature")
        self.git(self.author, "push", self.server.as_uri(), "feature:feature")
        legacy = self.root / "pr/pr-1"
        legacy.mkdir(parents=True)
        old = {"number": 1, "corpus": "default", "repository": "demo", "base": "main", "head": "feature"}
        self.write(legacy / "view.json", old)

        implicit = self.cli("fineract_r2_current.py", "query", "--pr", 1, "needle")
        explicit = self.cli("fineract_r2_current.py", "query", "--repo", "demo", "--pr", 1, "needle")
        self.assertTrue(Path(implicit["output_directory"]).is_relative_to(legacy))
        self.assertEqual(self.answer(implicit), self.answer(explicit))
        missing = self.cli("fineract_r2_current.py", "query", "--corpus", "other", "--pr", 1, "needle", code=4)
        self.assertIn("nie jest zarejestrowany", missing["reason"])

        sync = b'{"action":"synchronize","number":1}'
        self.assertTrue(self.cli("fineract_r2_pr.py", "event", data=sync)["already_ready"])
        opened = self.cli("fineract_r2_pr.py", "event", "--corpus", "other",
                          data=b'{"action":"opened","repository":"demo","number":1,"base":"main","head":"feature"}')
        other = self.cli("fineract_r2_current.py", "query", "--corpus", "other", "--pr", 1, "needle")
        self.assertTrue(Path(other["output_directory"]).is_relative_to(Path(opened["view_directory"])))
        self.assertFalse(Path(other["output_directory"]).is_relative_to(legacy))
        self.assertEqual(self.answer(implicit), self.answer(other))
        self.assertEqual(json.loads((legacy / "view.json").read_bytes()), old)

    def test_same_number_in_two_repositories_is_isolated_and_unqualified_operations_do_not_write(self):
        other_server = self.configure_two_prs("mirror")
        literal = "r2-twin-pr"
        commits, rooms = {}, {}

        def event(action, code=0, **fields):
            return self.cli("fineract_r2_pr.py", "event", code=code,
                            data=json.dumps({"action": action, "number": 1, **fields}).encode("ascii"))

        def search(name=None, code=0):
            args = ("--repo", name) if name else ()
            return self.cli("fineract_r2_current.py", "query", *args, "--pr", 1, literal, code=code)

        for name, server in (("demo", self.server), ("mirror", other_server)):
            commits[name] = self.push_feature(name, server, literal)
            opened = event("opened", repository=name, base="main", head="feature")
            self.assertEqual(opened["refresh"]["status"], "READY")
            rooms[name] = Path(opened["view_directory"])

        with ThreadPoolExecutor(max_workers=2) as queries:
            before = dict(zip(rooms, queries.map(search, rooms), strict=True))
        for name, result in before.items():
            self.assertEqual((result["status"], result["operation"]), ("VERIFIED", "query-checked"))
            self.assertEqual(result["selection"]["pull_request_repository"], name)
            self.assertEqual(self.hits(result), [(f"src/{name}", 0, 1)])
            self.assertEqual({row["id"]: row["commit"] for row in result["selection"]["repositories"]},
                             {repo: commits[repo] if name == repo else self.old for repo in rooms})

        def state(name):
            room = rooms[name]
            return {str(path.relative_to(room)): path.read_bytes()
                    for path in [room / "ready.json", *list((room / "agent/latest").glob("*.json"))]}

        def files():
            return {path for room in rooms.values() for path in room.rglob("*")}

        saved = {name: state(name) for name in rooms}
        saved_files = files()
        for run in (lambda: search(code=4), lambda: event("synchronize", code=4)):
            rejected = run()
            self.assertEqual(set(rejected), {"status", "reason"})
            self.assertEqual(rejected["status"], "ERROR")
            self.assertIn("niejednoznaczny", rejected["reason"])
            self.assertIn("demo, mirror", rejected["reason"])
            self.assertIn("--repo demo --pr 1", rejected["reason"])
            self.assertIn("repository", rejected["reason"])
            self.assertEqual({name: state(name) for name in rooms}, saved)
            self.assertEqual(files(), saved_files)

        self.git(self.author, "checkout", "--quiet", "demo")
        (self.author / "src/second").write_bytes(literal.encode("ascii"))
        self.git(self.author, "add", ".")
        self.git(self.author, "commit", "--quiet", "-m", "Update only demo")
        self.git(self.author, "push", self.server.as_uri(), "demo:feature")
        updated = event("synchronize", repository="demo")
        self.assertEqual(updated["status"], "READY")
        self.assertEqual(state("mirror"), saved["mirror"])
        demo = search("demo")
        mirror = search("mirror")
        self.assertEqual(self.hits(demo), [("src/demo", 0, 1), ("src/second", 0, 1)])
        self.assertNotEqual(demo["checked_index_sha256"], before["demo"]["checked_index_sha256"])
        self.assertEqual(mirror["checked_index_sha256"], before["mirror"]["checked_index_sha256"])
        self.assertEqual(self.answer(mirror), self.answer(before["mirror"]))

    def test_shared_index_is_complete_and_falls_back_for_short_literals_and_new_commits(self):
        checked = self.root / "checked"
        receipt = self.prepare(self.index, checked)
        self.configure(checked, receipt, self.index)
        result = self.query()
        self.assertEqual((result["status"], result["operation"], result["full_git_scans"]),
                         ("VERIFIED", "query-checked", 0))
        self.assertEqual(self.hits(result), [("src/a", 2, 2), ("src/b", 2, 2)])
        self.assertEqual(result["verifier_reads"][0]["objects_read"], 2)
        control = self.cli("fineract_r2_corpus.py", "query-verified", "--sources", self.sources,
                           "--manifest", self.manifest, "--index", self.index, "--literal=needle",
                           "--output-dir", self.root / "full", "--log-dir", self.root / "fl")
        self.assertEqual(self.answer(result), self.answer(control))
        empty = self.query("needle__missing")
        self.assertEqual((empty["count"], empty["full_git_scans"]), (0, 0))
        short = self.query("ee")
        self.assertEqual((short["operation"], short["checked_fallback"], short["full_git_scans"]),
                         ("query-verified", "short_literal", 1))
        self.assertEqual(self.hits(short), [("src/a", 3, 2), ("src/b", 3, 2), ("src/c", 1, 1)])
        (self.author / "src/new").write_bytes(b"needle")
        self.git(self.author, "add", "src/new")
        self.git(self.author, "commit", "--quiet", "-m", "B")
        new = self.git(self.author, "rev-parse", "HEAD")
        self.git(self.author, "push", self.server.as_uri(), "main:main")
        updated = self.query()
        self.assertEqual((updated["operation"], updated["checked_fallback"]), ("update-verified", "snapshot_changed"))
        self.assertEqual(updated["selection"]["repositories"][0]["commit"], new)
        self.assertEqual(self.hits(updated), [("src/a", 2, 2), ("src/b", 2, 2), ("src/new", 0, 1)])

    def test_preparation_rejects_a_wrong_path_mapping_and_an_incomplete_posting(self):
        changes = (
            ("path", "UPDATE paths SET oid=(SELECT oid FROM paths WHERE path=X'7372632F63') WHERE path=X'7372632F62'",
             "candidate path mapping"),
            ("posting", "UPDATE postings SET blob_ids=substr(blob_ids,5) WHERE gram=X'6E6565'", "postings"),
        )
        for label, sql, message in changes:
            with self.subTest(label=label):
                index = self.root / label
                shutil.copytree(self.index, index)
                with closing(sqlite3.connect(index / "demo.sqlite")) as db, db:
                    self.assertEqual(db.execute(sql).rowcount, 1)
                target = self.root / f"proof-{label}"
                result = self.prepare(index, target, code=3)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn(message, result["reason"])
                self.assertFalse(target.exists())

    def test_changed_verifier_posting_or_path_set_fails_closed(self):
        checked = self.root / "checked"
        receipt = self.prepare(self.index, checked)
        self.configure(checked, receipt, self.index)
        good = self.query()
        [latest] = (self.agent / "latest").glob("*.json")
        original = latest.read_bytes()
        evidence = checked / "demo.sqlite"
        with closing(sqlite3.connect(evidence)) as db, db:
            (ids,) = db.execute("SELECT ids FROM postings WHERE gram=?", (b"nee",)).fetchone()
            db.execute("UPDATE postings SET ids=? WHERE gram=?", (ids[4:], b"nee"))
        damaged = self.query(code=3)
        self.assertIn("authentication failed", damaged["reason"])
        with closing(sqlite3.connect(evidence)) as db, db:
            db.execute("UPDATE postings SET ids=? WHERE gram=?", (ids, b"nee"))
            db.execute("UPDATE objects SET paths=? WHERE paths=?", (b"src/a", b"src/a\0src/b"))
        damaged = self.query(code=3)
        self.assertIn("changed certified blob or path mapping", damaged["reason"])
        self.assertEqual(latest.read_bytes(), original)
        self.assertEqual(sha256(self.answer(good)).hexdigest(), good["result_sha256"])
        self.assertEqual(len(list((self.agent / "runs").glob("*/answer"))), 1)

    def test_omitting_one_candidate_alias_reaches_comparison_and_preserves_latest(self):
        checked = self.root / "checked"
        receipt = self.prepare(self.index, checked)
        self.configure(checked, receipt, self.index)
        good = self.query()
        [latest] = (self.agent / "latest").glob("*.json")
        original = latest.read_bytes()
        copy = self.root / "bad"
        shutil.copytree(self.index, copy)
        self.assertFalse((copy / "demo.sqlite").samefile(self.index / "demo.sqlite"))
        self.assertFalse((copy / "demo.sqlite").samefile(checked / "demo.sqlite"))
        with closing(sqlite3.connect(copy / "demo.sqlite")) as db, db:
            (oid,) = db.execute("SELECT oid FROM paths WHERE path=?", (b"src/c",)).fetchone()
            self.assertEqual(db.execute("UPDATE paths SET oid=? WHERE path=?", (oid, b"src/b")).rowcount, 1)
        self.configure(checked, receipt, copy)
        rejected = self.query(code=2)
        self.assertEqual(rejected["status"], "MISMATCH")
        self.assertIn("omits 1 Git path", rejected["reason"])
        self.assertEqual([r["count"] for r in rejected["candidate_counts"]], [1])
        self.assertEqual([r["count"] for r in rejected["git_counts"]], [2])
        self.assertEqual(latest.read_bytes(), original)
        self.assertEqual(len(list((self.agent / "runs").glob("*/answer"))), 1)
        self.configure(checked, receipt, self.index)
        self.assertEqual(self.answer(self.query()), self.answer(good))


@unittest.skipUnless(sys.platform == "win32", "requires the Windows R2 supervisor")
class PrRegistryRaceTests(CheckedR2Fixture):
    repository_id = "brave"

    def registry_is_locked(self):
        # Probe the writer's lock without waiting. The old code has no registry
        # database, so both publications can finish with the reader at the gate.
        for lock in (self.root / "pr").glob("registry-*.sqlite3"):
            with closing(sqlite3.connect(lock, timeout=0)) as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as exc:
                    if str(exc) == "database is locked":
                        return True
                    raise
        return False

    def race_registration(self, script, *args, event=None):
        electron = self.configure_two_prs("electron")
        for name, server in (("brave", self.server), ("electron", electron)):
            self.push_feature(name, server, "r2-pr-race")

        def open_both():
            for name in ("brave", "electron"):
                data = json.dumps({"action": "opened", "number": 1, "repository": name,
                                   "base": "main", "head": "feature"}).encode("ascii")
                opened = self.cli("fineract_r2_pr.py", "event", data=data)
                self.assertEqual((opened["status"], opened["refresh"]["status"]), ("REGISTERED", "READY"))

        def wait_for_gate(stderr):
            for line in stderr:
                if line.rstrip() == b"brave-missing":
                    return True
            return False

        command = [sys.executable, "-B", "-X", "utf8", "-c", PAUSE_AFTER_MISSING_BRAVE,
                   str(SCRIPTS / script), *map(str, args)]
        with (
            subprocess.Popen(command, env=self.env, cwd=PROJECT, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE) as reader,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            try:
                reader.stdin.write(json.dumps(event).encode("ascii") + b"\n")
                reader.stdin.flush()
                self.assertTrue(pool.submit(wait_for_gate, reader.stderr).result(timeout=30),
                                "CLI exited before the missing Brave view was read")
                registry_is_locked = self.registry_is_locked()
                registrations = pool.submit(open_both)
                if not registry_is_locked:
                    registrations.result(timeout=120)
                stdout, stderr = reader.communicate(b"continue\n", timeout=60)
                registrations.result(timeout=120)
            finally:
                if reader.poll() is None:
                    reader.kill()
        self.assertIn(reader.returncode, (0, 4), (stdout, stderr))
        return reader.returncode, json.loads(stdout)

    def assert_consistent_selection(self, code, result, *, success):
        if code == 4:
            self.assertEqual(result["status"], "ERROR")
            reason = result["reason"]
            if "niejednoznaczny" in reason:
                self.assertIn("brave, electron", reason)
                self.assertIn("--repo brave --pr 1", reason)
                self.assertIn("repository", reason)
            else:
                self.assertIn("nie jest zarejestrowany", reason)
            return
        self.assertEqual(result["status"], success)
        selection = result["selection"]
        heads = selection["repositories"] if success == "VERIFIED" else selection
        self.assertEqual([row["id"] for row in heads if row["branch"] == "feature"], ["brave"],
                         "only Brave could have been unique when registrations publish Brave then Electron")
        if success == "VERIFIED":
            self.assertEqual(selection["pull_request_repository"], "brave")

    def test_number_only_query_uses_a_consistent_registry_view(self):
        self.assert_consistent_selection(*self.race_registration(
            "fineract_r2_current.py", "query", "--pr", 1, "r2-pr-race"), success="VERIFIED")

    def test_synchronize_without_repository_uses_a_consistent_registry_view(self):
        self.assert_consistent_selection(*self.race_registration(
            "fineract_r2_pr.py", "event", event={"action": "synchronize", "number": 1}), success="READY")
