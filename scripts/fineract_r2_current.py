"""Resolve configured Git branches and publish a full R2 answer for the selected commits."""

from contextlib import closing, contextmanager, redirect_stdout
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
from time import perf_counter, time_ns
from urllib.parse import urlsplit
from uuid import uuid4

from fineract_r2 import PROJECT, STATUS, StatusParser, sha256_file, strict_json, write_json
from fineract_r2_corpus import parse_manifest, read_manifest, read_verified_base
from prepare_r2_corpus import prepare
from repo_proof.checked_index import checked_receipt, immutable_bytes
from repo_proof.fineract_oracle import ResultMismatch, SourceUnavailable
from repo_proof.git_search import git_command, git_env, git_read


R2 = PROJECT / "scripts/fineract_r2_corpus.py"
OID = re.compile(r"[0-9a-f]{40}")
DEFAULT_CONFIG = PROJECT / "local/r2-current/config.json"


class FreshnessError(ValueError):
    """The selected branch or its Git objects could not be confirmed."""


class R2Error(Exception):
    def __init__(self, result):
        self.result = result


def git(store, *args, data=None):
    command = git_command(store, *args) if store is not None else ["git", *args]
    result = subprocess.run(command, input=data, capture_output=True, timeout=120, env=git_env())
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip() or "Git nie zwrócił wskazanej gałęzi")
    return result.stdout


def corpus_entry(path, corpus):
    path = path.resolve(strict=True)
    return path, strict_json(path.read_bytes())["corpora"][corpus]


def validate_pr_number(number):
    if type(number) is not int or number < 1:
        raise ValueError("PR number must be a positive integer")


def pr_directory(path, entry):
    return (path.parent / entry["pr_directory"]).resolve()


def pr_room(path, entry, corpus, repository, number):
    validate_pr_number(number)
    identity = json.dumps([corpus, repository, number], ensure_ascii=True).encode("ascii")
    return pr_directory(path, entry) / f"p-{sha256(identity).hexdigest()[:32]}"


def pr_registry_transaction(path, entry, corpus, number):
    validate_pr_number(number)
    directory = pr_directory(path, entry)
    directory.mkdir(parents=True, exist_ok=True)
    identity = json.dumps([corpus, number], ensure_ascii=True).encode("ascii")
    return latest_transaction(directory / f"registry-{sha256(identity).hexdigest()[:32]}.json")


def registered_pr(path, entry, corpus, number, repository=None):
    with pr_registry_transaction(path, entry, corpus, number):
        return _find_registered_pr(path, entry, corpus, number, repository)


def _find_registered_pr(path, entry, corpus, number, repository, *, opening=False):
    # The caller holds the registry transaction across the entire scan.
    repositories = sorted({repo["id"] for repo in entry["repositories"]})
    if repository is not None:
        if repository not in repositories:
            raise ValueError(f"Repozytorium {repository!r} nie należy do korpusu {corpus!r}")
        repositories = [repository]
    legacy = pr_directory(path, entry) / f"pr-{number}"
    matches = []
    for name in repositories:
        room = pr_room(path, entry, corpus, name, number)
        try:
            view = strict_json((room / "view.json").read_bytes())
        except FileNotFoundError:
            continue
        if (view["corpus"], view["repository"], view["number"]) != (corpus, name, number):
            raise ValueError("Zapisana tożsamość PR-a nie zgadza się z katalogiem")
        matches.append((room, view))
    try:
        old = strict_json((legacy / "view.json").read_bytes())
    except FileNotFoundError:
        old = None
    if (old is not None and old["corpus"] == corpus and old["number"] == number
            and old["repository"] in repositories and all(view["repository"] != old["repository"] for _, view in matches)):
        matches.append((legacy, old))
    if len(matches) > 1:
        names = sorted(view["repository"] for _, view in matches)
        raise ValueError(f"PR #{number} jest niejednoznaczny: {', '.join(names)}. "
                         f"Użyj --repo {names[0]} --pr {number} lub podaj pole repository w zdarzeniu synchronize.")
    if matches:
        return matches[0]
    if opening:
        return pr_room(path, entry, corpus, repository, number), None
    raise ValueError(f"PR #{number} nie jest zarejestrowany dla {', '.join(repositories)} w korpusie {corpus!r}")


def publish_pr(path, entry, view):
    corpus, repository, number = view["corpus"], view["repository"], view["number"]
    with pr_registry_transaction(path, entry, corpus, number):
        room, known = _find_registered_pr(path, entry, corpus, number, repository, opening=True)
        if known is None:
            room.mkdir(parents=True, exist_ok=True)
            temporary = room / f"{uuid4().hex}.tmp"
            try:
                write_json(temporary, view)
                os.replace(temporary, room / "view.json")
            finally:
                temporary.unlink(missing_ok=True)
        elif known != view:
            raise ValueError("PR was already registered with different branches")
    return room, view


def settings(path, entry, corpus, *, selected_pr=None):
    repositories = entry["repositories"]
    if (not repositories or len({r["id"] for r in repositories}) != len(repositories)
            or len({r["repository"] for r in repositories}) != len(repositories)):
        raise ValueError("Korpus musi zawierać unikalne repozytoria")
    workspace = (path.parent / entry["workspace"]).resolve()
    if selected_pr is not None:
        room, view = selected_pr
        base = next((repo for repo in repositories if repo["id"] == view["repository"]), None)
        if base is None or view["corpus"] != corpus or view["base"] != base["branch"]:
            raise ValueError("registered PR does not match the configured base")
        repositories = [{**repo, "branch": view["head"]} if repo is base else repo for repo in repositories]
        workspace = room / "agent"
    for repo in repositories:
        directories = repo["directories"]
        if (not re.fullmatch(r"[a-z0-9-]+", repo["id"])
                or not repo["repository"] or not repo["url"]
                or not repo["branch"] or repo["branch"].startswith("refs/")
                or urlsplit(repo["remote"]).scheme not in ("file", "https")
                or type(directories) is not list or len(set(directories)) != len(directories)
                or any(not re.fullmatch(r"[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*", directory)
                       or set(directory.split("/")) & {".", ".."} for directory in directories)):
            raise ValueError("Nieprawidłowa konfiguracja repozytorium lub zakresu")
        git(None, "check-ref-format", "refs/heads/" + repo["branch"])
    index = (path.parent / entry["seed_index"]).resolve() if "seed_index" in entry else None
    checked = None
    if "checked_index" in entry:
        spec = entry["checked_index"]
        if index is None or not re.fullmatch(r"[0-9a-f]{64}", spec["receipt_sha256"]):
            raise ValueError("checked_index requires a seed_index and a trusted receipt SHA-256")
        checked = (path.parent / spec["directory"]).resolve(), spec["receipt_sha256"]
    return workspace, repositories, index, checked


def selected_heads(repositories):
    heads = []
    for repo in repositories:
        ref = "refs/heads/" + repo["branch"]
        try:
            raw = git(None, "ls-remote", "--exit-code", "--refs", repo["remote"], ref)
            commit, separator, actual_ref = raw.rstrip(b"\r\n").decode("ascii").partition("\t")
            if not separator or actual_ref != ref or not OID.fullmatch(commit):
                raise ValueError("Źródło nie zwróciło dokładnie jednego identyfikatora gałęzi")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raise FreshnessError(f"Nie można potwierdzić bieżącej wersji {repo['repository']} "
                                 f"({repo['branch']}): {exc}") from exc
        heads.append({**{key: repo[key] for key in ("id", "repository", "remote", "branch")},
                      "commit": commit, "resolved_unix_ns": time_ns()})
    return heads


def local_commit(store, commit):
    if not store.is_dir():
        return False
    try:
        return git_read(store, "rev-parse", "--verify", commit + "^{commit}").strip() == commit.encode("ascii")
    except ValueError:
        return False


@contextmanager
def latest_transaction(latest):
    with closing(sqlite3.connect(latest.with_suffix(".sqlite3"), timeout=120)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        yield db


def read_latest(latest):
    try:
        pointer = strict_json(latest.read_bytes())
    except (FileNotFoundError, ValueError):
        return {}
    return pointer if isinstance(pointer, dict) else {}


def observe_heads(latest, repositories):
    latest.parent.mkdir(parents=True, exist_ok=True)
    with latest_transaction(latest) as db:
        # Serialize the remote observations themselves so the counter orders the selected heads.
        heads = selected_heads(repositories)
        previous = read_latest(latest)
        db.execute("CREATE TABLE IF NOT EXISTS observation (id INTEGER PRIMARY KEY, number INTEGER NOT NULL)")
        (number,) = db.execute(
            """INSERT INTO observation VALUES (1, ?)
               ON CONFLICT(id) DO UPDATE SET number = MAX(observation.number + 1, excluded.number)
               RETURNING number""",
            (previous.get("observation", 0) + 1,),
        ).fetchone()
    return heads, number, previous


def load_base(pointer, runs, literal):
    try:
        token = pointer["run"]
        if not re.fullmatch(r"[0-9a-f]{32}", token):
            return None
        folder = runs / token
        manifest = folder / "manifest.json"
        repositories = read_manifest(manifest)
        manifest_hash = sha256_file(manifest)
        _, answer_hash = read_verified_base(folder / "answer", repositories, literal, manifest_hash)
        if pointer["manifest_sha256"] != manifest_hash or pointer["result_sha256"] != answer_hash:
            return None
        return folder, {repo["id"]: repo for repo in repositories}
    except (OSError, ResultMismatch, ValueError, TypeError, KeyError):
        return None


def collect_repositories(sources, repositories, heads, previous):
    sources.mkdir(parents=True, exist_ok=True)
    prepared, downloads = [], []
    for repo, head in zip(repositories, heads, strict=True):
        started = perf_counter()
        store = sources / (repo["id"] + ".git")
        commit = head["commit"]
        had_commit = local_commit(store, commit)
        fetches = 0
        fetch_seconds = 0.0

        def fetch(*args, data=None):
            nonlocal fetches, fetch_seconds
            before = perf_counter()
            git(store, "fetch", "--no-tags", "--no-recurse-submodules", "--no-auto-maintenance",
                "--no-write-fetch-head", *args, data=data)
            fetches += 1
            fetch_seconds += perf_counter() - before

        try:
            if not store.is_dir():
                git(None, "init", "--quiet", "--bare", "--object-format=sha1", str(store))
            if not had_commit:
                fetch("--depth=1", repo["remote"], f"{commit}:refs/r2-current/{commit}")
            root_tree = git_read(store, "rev-parse", "--verify", commit + "^{tree}").strip().decode("ascii")
            old = previous.get(repo["id"])
            if old is not None and (old["snapshot"]["commit"], old["snapshot"]["root_tree"]) == (commit, root_tree):
                entry = old
            else:
                def fetch_blobs(batch):
                    fetch("--stdin", repo["remote"], data=("\n".join(batch) + "\n").encode("ascii"))

                source = {**repo, "commit": commit, "root_tree": root_tree}
                with redirect_stdout(sys.stderr):
                    entry, _ = prepare(source, sources, False, fetch_missing=fetch_blobs)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raise FreshnessError(f"Nie można pobrać lub sprawdzić wersji {repo['repository']} "
                                 f"({repo['branch']} @ {commit}): {exc}") from exc
        prepared.append(entry)
        downloads.append({"repository": repo["repository"], "commit_present_before_fetch": had_commit,
                          "fetches": fetches, "fetch_seconds": fetch_seconds,
                          "local_preparation_seconds": perf_counter() - started - fetch_seconds})
    return prepared, downloads


def manifest_for(repositories):
    return {"format": "git-literal-corpus-manifest-v1", "repositories": repositories,
            "totals": {
                "regular_paths": sum(repo["snapshot"]["regular_paths"] for repo in repositories),
                "regular_path_bytes": sum(repo["regular_path_bytes"] for repo in repositories),
            }}


def invoke_r2(operation, sources, manifest, log, *args):
    command = [sys.executable, "-B", "-X", "utf8", str(R2), operation, "--sources", str(sources),
               "--manifest", str(manifest), "--log-dir", str(log), *map(str, args)]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    response = strict_json(result.stdout)
    if result.returncode or response.get("status") != ("BUILT" if operation == "build" else "VERIFIED"):
        if response.get("status") not in ("MISMATCH", "ERROR", "BLOCKED"):
            raise ValueError("Proces R2 nie zwrócił prawidłowego statusu")
        raise R2Error(response)
    return response


def compatible_shard(path, repo):
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
            [(row,)] = db.execute("SELECT receipt FROM metadata").fetchall()
            receipt = strict_json(row)
            return (receipt["complete"] is True and receipt["schema"] == 1
                    and receipt["snapshot"] == repo["snapshot"]
                    and receipt.get("directories", []) == repo["directories"])
    except (sqlite3.Error, OSError, ValueError, TypeError, KeyError):
        return False


def index_for(run, sources, repositories, seed_index):
    index = run / "index"
    reusable, missing = [], []
    for repo in repositories:
        name = repo["id"] + ".sqlite"
        if seed_index is not None and compatible_shard(seed_index / name, repo):
            reusable.append(name)
        else:
            missing.append(repo)
    if missing:
        subset = run / "index-manifest.json"
        write_json(subset, manifest_for(missing))
        invoke_r2("build", sources, subset, run / "build-log", "--index", index)
    else:
        index.mkdir()
    for name in reusable:
        try:
            os.link(seed_index / name, index / name)
        except OSError:
            shutil.copyfile(seed_index / name, index / name)
    return index


def matching_checked_manifest(checked, repositories, heads):
    directory, anchor = checked
    receipt = checked_receipt(directory, anchor)
    raw = (directory / "manifest.json").read_bytes()
    if sha256(raw).hexdigest() != receipt["manifest_sha256"]:
        raise SourceUnavailable("checked index manifest SHA-256 differs from the receipt")
    pinned = [(repo["id"], repo["directories"], repo["snapshot"]["repository"], repo["snapshot"]["url"],
               repo["snapshot"]["commit"]) for repo in parse_manifest(raw)]
    current = [(repo["id"], repo["directories"], repo["repository"], repo["url"], head["commit"])
               for repo, head in zip(repositories, heads, strict=True)]
    return raw if pinned == current else None


def select_view(config, corpus, pr, repository):
    if repository is not None and pr is None:
        raise ValueError("--repo wymaga --pr")
    path, entry = corpus_entry(config, corpus)
    selected_pr = registered_pr(path, entry, corpus, pr, repository) if pr is not None else None
    return selected_pr, settings(path, entry, corpus, selected_pr=selected_pr)


def checked_for_heads(selected_pr, seed_index, checked, repositories, heads):
    prepared_manifest = None
    if selected_pr is not None:
        room, _ = selected_pr
        ready_path = room / "ready.json"
        with latest_transaction(ready_path):
            ready = read_latest(ready_path)
        if ready:
            if not re.fullmatch(r"[0-9a-f]{32}", ready["release"]):
                raise SourceUnavailable("invalid PR index publication")
            release = room / "r" / ready["release"]
            ready_checked = (release / "checked", ready["receipt_sha256"])
            prepared_manifest = matching_checked_manifest(ready_checked, repositories, heads)
            if prepared_manifest is not None:
                return release / "index", ready_checked, prepared_manifest
    if checked is not None:
        prepared_manifest = matching_checked_manifest(checked, repositories, heads)
    return seed_index, checked, prepared_manifest


def query(config, corpus, literal, *, pr=None, repository=None):
    if not re.fullmatch(r"[ -~]+", literal):
        raise ValueError("Literał musi zawierać niepuste, drukowalne znaki ASCII")
    selected_pr, (workspace, repositories, seed_index, checked) = select_view(config, corpus, pr, repository)
    identity = [{key: repo[key] for key in ("id", "repository", "url", "directories", "remote", "branch")}
                for repo in repositories]
    key = sha256(json.dumps([identity, literal], sort_keys=True, ensure_ascii=True).encode("ascii")).hexdigest()
    runs = workspace / "runs"
    latest = workspace / "latest" / f"{key}.json"
    started = perf_counter()
    heads, observation, previous = observe_heads(latest, repositories)
    resolution = perf_counter() - started
    started = perf_counter()
    seed_index, checked, prepared_manifest = checked_for_heads(
        selected_pr, seed_index, checked, repositories, heads)
    checked_seconds = perf_counter() - started
    fast = prepared_manifest is not None and len(literal) >= 3
    base = None if prepared_manifest is not None else load_base(previous, runs, literal)
    run = runs / uuid4().hex
    run.mkdir(parents=True)
    selection = {"corpus": corpus, "literal": literal, "repositories": heads, "observation": observation}
    if selected_pr is not None:
        _, view = selected_pr
        selection["pull_request"] = view["number"]
        selection["pull_request_repository"] = view["repository"]
    write_json(run / "selection.json", selection)

    sources = workspace / "sources"
    manifest = run / "manifest.json"
    started = perf_counter()
    if fast:
        immutable_bytes(manifest, prepared_manifest)
        downloads = []
    else:
        prepared, downloads = collect_repositories(sources, repositories, heads, base[1] if base else {})
        write_json(manifest, manifest_for(prepared))
    fetch_seconds = sum(repo["fetch_seconds"] for repo in downloads)
    manifest_seconds = perf_counter() - started - fetch_seconds + checked_seconds

    started = perf_counter()
    if fast:
        operation = "query-checked"
        options = ("--index", seed_index, "--checked-directory", checked[0], "--checked-sha256", checked[1])
    elif base:
        operation = "update-verified"
        options = ("--base-manifest", base[0] / "manifest.json", "--base-answer", base[0] / "answer")
    else:
        operation = "query-verified"
        options = ("--index", index_for(run, sources, prepared, seed_index))
    index_seconds = perf_counter() - started if not base else 0.0

    answer = run / "answer"
    started = perf_counter()
    result = invoke_r2(operation, sources, manifest, run / "query-log",
                       f"--literal={literal}", "--output-dir", answer, *options)
    query_seconds = perf_counter() - started
    data = (answer / "answer.jsonl").read_bytes()
    if sha256(data).hexdigest() != result["result_sha256"]:
        raise ValueError("Opublikowana odpowiedź zmieniła się po weryfikacji")
    rows = [strict_json(line) for line in data.splitlines()]
    temporary = latest.with_name(run.name + ".tmp")
    try:
        write_json(temporary, {"run": run.name, "observation": observation,
                               "manifest_sha256": result["manifest_sha256"],
                               "result_sha256": result["result_sha256"]})
        with latest_transaction(latest):
            if observation > read_latest(latest).get("observation", 0):
                os.replace(temporary, latest)
    finally:
        temporary.unlink(missing_ok=True)
    fallback = ({"checked_fallback": "short_literal" if prepared_manifest is not None else "snapshot_changed"}
                if checked and not fast else {})
    return {**result, **fallback, "operation": operation, "manifest": str(manifest), "selection": selection,
            "downloads": downloads, "answer": rows,
            "current_seconds": {"resolve_branches": resolution, "fetch": fetch_seconds,
                                "prepare_manifest": manifest_seconds, "prepare_index": index_seconds,
                                "query_and_publication": query_seconds}}


def main(argv=None):
    parser = StatusParser(description=__doc__)
    parser.add_argument("operation", choices=["query"])
    parser.add_argument("--config", type=Path,
                        default=Path(os.environ.get("REPO_PROOF_CURRENT_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--corpus", default="default")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--repo")
    parser.add_argument("literal")
    try:
        args = parser.parse_args(argv)
        result = query(args.config, args.corpus, args.literal, pr=args.pr, repository=args.repo)
    except R2Error as exc:
        result = exc.result
    except (FreshnessError, SourceUnavailable) as exc:
        result = {"status": "BLOCKED", "reason": str(exc)}
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        result = {"status": "ERROR", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return STATUS[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
