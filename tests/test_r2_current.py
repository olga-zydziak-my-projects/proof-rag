from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT = Path(__file__).resolve().parents[1]
CURRENT = PROJECT / "scripts/fineract_r2_current.py"
R2 = PROJECT / "scripts/fineract_r2_corpus.py"

PAUSE_BEFORE_LATEST = r"""
from pathlib import Path
import sys

sys.argv.pop(0)
sys.path.insert(0, str(Path(sys.argv[0]).parent))
import fineract_r2_current as current

write_json = current.write_json

def pause_after_staging(path, data):
    write_json(path, data)
    if path.parent.name == "latest" and path.suffix == ".tmp":
        print("pending-latest " + data["run"], file=sys.stderr, flush=True)
        if sys.stdin.readline() != "continue\n":
            raise RuntimeError("test did not release publication")

current.write_json = pause_after_staging
raise SystemExit(current.main())
"""


@unittest.skipUnless(sys.platform == "win32", "requires the Windows R2 supervisor")
class R2CurrentTests(unittest.TestCase):
    @contextmanager
    def paused_query(self, env):
        def wait_for_gate(stderr):
            for line in stderr:
                if line.startswith(b"pending-latest "):
                    return line.split()[1].decode("ascii")
            self.fail("query exited before reaching the latest publication gate")

        command = [sys.executable, "-B", "-X", "utf8", "-c", PAUSE_BEFORE_LATEST, str(CURRENT), "query", "needle"]
        with subprocess.Popen(command, env=env, cwd=PROJECT, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            try:
                with ThreadPoolExecutor(max_workers=1) as reader:
                    gate = reader.submit(wait_for_gate, process.stderr)
                    try:
                        run = gate.result(timeout=30)
                    except BaseException:
                        process.kill()
                        raise
                yield process, run
            finally:
                if process.poll() is None:
                    process.kill()

    def concurrent_queries(self, a2_finishes_first):
        with TemporaryDirectory(prefix="rf") as folder:
            root = Path(folder)
            author, server, agent = root / "w", root / "s.git", root / "c"
            config = root / "config.json"
            env = dict(os.environ, GIT_ALLOW_PROTOCOL="file", GIT_NO_LAZY_FETCH="1",
                       REPO_PROOF_CURRENT_CONFIG=str(config))

            def git(store, *args, code=0):
                result = subprocess.run(["git", "-C", str(store), *map(str, args)], env=env, capture_output=True)
                self.assertEqual(result.returncode, code, (args, result.stderr))
                return result.stdout.strip().decode("ascii")

            git(root, "init", "--quiet", "--object-format=sha1", "-b", "main", author)
            git(author, "config", "user.email", "r2@example.invalid")
            git(author, "config", "user.name", "R2 Test")
            git(author, "config", "commit.gpgsign", "false")
            (author / "old.txt").write_bytes(b"needle\n")
            git(author, "add", ".")
            git(author, "commit", "--quiet", "-m", "A2")
            a2 = git(author, "rev-parse", "HEAD")
            git(root, "init", "--quiet", "--bare", "--object-format=sha1", server)
            git(author, "push", server.as_uri(), "main:main")
            config.write_text(json.dumps({"corpora": {"default": {"workspace": "c", "repositories": [{
                "id": "test", "repository": "sample/current", "url": "https://example.invalid/test.git",
                "remote": server.as_uri(), "branch": "main", "directories": [],
            }]}}}))

            def finish(process, run, commit, hits):
                stdout, stderr = process.communicate(b"continue\n", timeout=30)
                self.assertEqual(process.returncode, 0, (stdout, stderr))
                result = json.loads(stdout)
                self.assertEqual(result["status"], "VERIFIED")
                self.assertEqual(result["count"], len(hits))
                self.assertEqual(result["selection"]["repositories"][0]["commit"], commit)
                output = Path(result["output_directory"])
                self.assertEqual(output.parent, agent / "runs" / run)
                answer = (output / "answer.jsonl").read_bytes()
                receipt = json.loads((output / "verification.json").read_bytes())
                self.assertEqual(receipt["status"], "VERIFIED")
                self.assertEqual(sha256(answer).hexdigest(), receipt["result_sha256"])
                self.assertEqual(receipt["result_sha256"], result["result_sha256"])
                self.assertEqual(result["answer"], [json.loads(line) for line in answer.splitlines()])
                self.assertEqual([(r["commit"], r["path"], r["byte_offset"], r["line"])
                                  for r in result["answer"] if r["type"] == "hit"], hits)
                return result

            def assert_latest(result, run, commit):
                [path] = (agent / "latest").glob("*.json")
                pointer = json.loads(path.read_bytes())
                self.assertEqual(pointer["run"], run, f"latest must point to the publication for {commit}")
                selected = agent / "runs" / pointer["run"]
                manifest = (selected / "manifest.json").read_bytes()
                self.assertEqual(json.loads(manifest)["repositories"][0]["snapshot"]["commit"], commit)
                self.assertEqual(sha256(manifest).hexdigest(), pointer["manifest_sha256"])
                self.assertEqual(pointer["manifest_sha256"], result["manifest_sha256"])
                answer = (selected / "answer/answer.jsonl").read_bytes()
                self.assertEqual(sha256(answer).hexdigest(), pointer["result_sha256"])
                self.assertEqual(pointer["result_sha256"], result["result_sha256"])

            with self.paused_query(env) as (old, old_run):
                staged = agent / "runs" / old_run
                receipt = json.loads((staged / "answer/verification.json").read_bytes())
                self.assertEqual(receipt["status"], "VERIFIED")
                self.assertEqual(json.loads((staged / "selection.json").read_bytes())["repositories"][0]["commit"], a2)
                (author / "old.txt").unlink()
                (author / "new.txt").write_bytes(b"first\nneedle\n")
                git(author, "add", "-A")
                git(author, "commit", "--quiet", "-m", "A3")
                a3 = git(author, "rev-parse", "HEAD")
                git(author, "push", server.as_uri(), "main:main")
                self.assertEqual(git(server, "rev-parse", "refs/heads/main"), a3)
                with self.paused_query(env) as (new, new_run):
                    old_hits = [(a2, "old.txt", 0, 1)]
                    new_hits = [(a3, "new.txt", 6, 2)]
                    store = agent / "sources/test.git"
                    self.assertEqual(git(store, "rev-parse", "--is-shallow-repository"), "true")
                    git(store, "merge-base", "--is-ancestor", a2, a3, code=1)
                    if a2_finishes_first:
                        result_a2 = finish(old, old_run, a2, old_hits)
                        assert_latest(result_a2, old_run, a2)
                        result_a3 = finish(new, new_run, a3, new_hits)
                    else:
                        result_a3 = finish(new, new_run, a3, new_hits)
                        assert_latest(result_a3, new_run, a3)
                        result_a2 = finish(old, old_run, a2, old_hits)
                    assert_latest(result_a3, new_run, a3)
                    self.assertTrue(Path(result_a2["output_directory"], "answer.jsonl").is_file())

    def test_latest_keeps_a3_when_a2_finishes_after_a3(self):
        self.concurrent_queries(a2_finishes_first=False)

    def test_latest_advances_to_a3_when_a2_finishes_first(self):
        self.concurrent_queries(a2_finishes_first=True)

    def test_current_query_observes_a_real_push_and_blocks_when_origin_is_unreachable(self):
        with TemporaryDirectory(prefix="rf") as folder:
            root = Path(folder)
            author, server, agent = root / "w", root / "s.git", root / "c"
            env = dict(os.environ, GIT_ALLOW_PROTOCOL="file", GIT_NO_LAZY_FETCH="1")

            def git(store, *args, code=0):
                cmd = ["git", "-C", str(store), *map(str, args)]
                result = subprocess.run(cmd, env=env, capture_output=True)
                self.assertEqual(result.returncode, code, (cmd, result.stderr))
                return result.stdout.strip().decode("ascii")

            def cli(script, *args, code=0):
                cmd = [sys.executable, "-B", "-X", "utf8", str(script), *map(str, args)]
                result = subprocess.run(cmd, env=env, cwd=PROJECT, capture_output=True)
                self.assertEqual(result.returncode, code, (cmd, result.stdout, result.stderr))
                return json.loads(result.stdout)

            git(root, "init", "--quiet", "--object-format=sha1", "-b", "main", author)
            git(author, "config", "user.email", "r2@example.invalid")
            git(author, "config", "user.name", "R2 Test")
            git(author, "config", "commit.gpgsign", "false")
            (author / "base.txt").write_bytes(b"first\nxx needle and needle\n")
            git(author, "add", ".")
            git(author, "commit", "--quiet", "-m", "before")
            old = git(author, "rev-parse", "HEAD")
            git(root, "init", "--bare", "--quiet", "--object-format=sha1", server)
            git(author, "push", server.as_uri(), "main:main")
            config = root / "config.json"
            config.write_text(json.dumps({"corpora": {"default": {"workspace": "c", "repositories": [{
                "id": "test", "repository": "sample/current", "url": "https://example.invalid/test.git",
                "remote": server.as_uri(), "branch": "main", "directories": [],
            }]}}}))
            env["REPO_PROOF_CURRENT_CONFIG"] = str(config)

            def hit_rows(answer):
                return [(row["commit"], row["path"], row["byte_offset"], row["line"])
                        for row in answer["answer"] if row["type"] == "hit"]

            first = cli(CURRENT, "query", "needle")
            self.assertEqual((first["status"], first["operation"], first["count"]),
                             ("VERIFIED", "query-verified", 1))
            self.assertEqual(hit_rows(first), [(old, "base.txt", 9, 2)])
            self.assertEqual(first["selection"]["repositories"][0]["branch"], "main")
            self.assertEqual(first["selection"]["repositories"][0]["commit"], old)
            base = Path(first["output_directory"]) / "answer.jsonl"
            [latest] = (agent / "latest").glob("*.json")
            before = latest.read_bytes()

            (author / "new.txt").write_bytes(b"needle\n")
            git(author, "add", ".")
            git(author, "commit", "--quiet", "-m", "after")
            new = git(author, "rev-parse", "HEAD")
            git(author, "push", server.as_uri(), "main:main")
            client = agent / "sources/test.git"
            self.assertEqual(git(server, "rev-parse", "refs/heads/main"), new)
            git(client, "cat-file", "-e", new + "^{commit}", code=128)
            self.assertEqual(latest.read_bytes(), before)

            second = cli(CURRENT, "query", "needle")
            self.assertEqual((second["status"], second["operation"], second["count"]),
                             ("VERIFIED", "update-verified", 2))
            self.assertEqual(second["selection"]["repositories"][0]["commit"], new)
            self.assertFalse(second["downloads"][0]["commit_present_before_fetch"])
            self.assertEqual(second["downloads"][0]["fetches"], 1)
            self.assertEqual(hit_rows(second), [(new, "base.txt", 9, 2), (new, "new.txt", 0, 1)])
            published = Path(second["output_directory"])
            receipt = json.loads((published / "verification.json").read_text())
            self.assertEqual(receipt["base_result_sha256"], first["result_sha256"])
            self.assertEqual(receipt["result_sha256"], second["result_sha256"])
            self.assertTrue(base.is_file())

            common = ("--sources", agent / "sources", "--manifest", second["manifest"], "--index", root / "i")
            cli(R2, "build", *common, "--log-dir", root / "b")
            control = cli(R2, "query-verified", *common, "--literal=needle",
                          "--output-dir", root / "f", "--log-dir", root / "l")
            self.assertEqual(control["result_sha256"], second["result_sha256"])
            raw = (published / "answer.jsonl").read_bytes()
            self.assertEqual(raw, (root / "f/answer.jsonl").read_bytes())

            renamed = root / "offline"
            server.rename(renamed)
            latest_bytes = latest.read_bytes()
            runs_before = sorted((agent / "runs").iterdir())
            try:
                blocked = cli(CURRENT, "query", "needle", code=3)
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIn("Nie można potwierdzić bieżącej wersji sample/current", blocked["reason"])
                self.assertNotIn("answer", blocked)
                self.assertNotIn("output_directory", blocked)
                self.assertEqual(latest.read_bytes(), latest_bytes)
                self.assertEqual(sorted((agent / "runs").iterdir()), runs_before)
                self.assertEqual((published / "answer.jsonl").read_bytes(), raw)
            finally:
                renamed.rename(server)


if __name__ == "__main__":
    unittest.main()
