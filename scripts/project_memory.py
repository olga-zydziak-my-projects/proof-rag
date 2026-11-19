"""Zapamiętaj preferencję projektu i aktywny wynik Fineract R2 w rozmowie."""

import argparse
from contextlib import ExitStack, closing
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
from time import perf_counter


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from repo_proof.fineract_oracle import strict_json
from repo_proof.git_search import RESULT_FORMAT
from repo_proof.memory_intent import InterpretationError, anthropic_client, interpret_question


DEFAULT_DB = PROJECT / "local/project-memory/preferences.sqlite3"
PREFERENCE = "pokazuj pliki testowe osobno"
TEST_QUESTION = "które z tych plików są testami?"
COMMAND_ERRORS = (OSError, ValueError, TypeError, KeyError, RecursionError, sqlite3.Error)


@dataclass
class VerifiedResult:
    repository: str
    commit: str
    literal: str
    answer_sha256: str
    verification_sha256: str
    paths: list[str]


def project_preference(db_path, project, enabled=None):
    if enabled is True:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    elif not db_path.exists():
        return False

    # A row represents the one supported preference. The key is independent of Git commits.
    with closing(sqlite3.connect(db_path)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS preferences (project TEXT PRIMARY KEY) WITHOUT ROWID")
        if enabled is True:
            db.execute("INSERT INTO preferences (project) VALUES (?) ON CONFLICT DO NOTHING", (project,))
            return True
        if enabled is False:
            db.execute("DELETE FROM preferences WHERE project = ?", (project,))
            return False
        return db.execute("SELECT 1 FROM preferences WHERE project = ?", (project,)).fetchone() is not None


def check_published_directory(folder, output_directory):
    if (not isinstance(output_directory, str) or "\0" in output_directory
            or not Path(output_directory).is_absolute()):
        raise ValueError("pole output_directory w verification.json musi zawierać bezwzględną ścieżkę katalogu")
    target = Path(output_directory)
    try:
        published = folder.samefile(target)
    except (FileNotFoundError, NotADirectoryError):
        published = False
    if not published:
        raise ValueError(f"katalog {folder} nie jest opublikowanym katalogiem R2 z pola output_directory ({target})")


def read_verified_result(folder, *, require_published=False, expected_answer=None, expected_verification=None):
    receipt_bytes = (folder / "verification.json").read_bytes()
    verification_hash = sha256(receipt_bytes).hexdigest()
    if expected_verification is not None and verification_hash != expected_verification:
        raise ValueError("SHA-256 pliku verification.json różni się od zapamiętanego")
    receipt = strict_json(receipt_bytes)
    if receipt["format"] != "fineract-r2-verification-v1":
        raise ValueError("niepoprawny format pliku verification.json")
    if receipt["status"] != "VERIFIED":
        raise ValueError("potwierdzenie R2 musi mieć status VERIFIED")
    if require_published:
        check_published_directory(folder, receipt.get("output_directory"))
    answer = (folder / "answer.jsonl").read_bytes()
    answer_hash = sha256(answer).hexdigest()
    if expected_answer is not None and answer_hash != expected_answer:
        raise ValueError("SHA-256 pliku answer.jsonl różni się od zapamiętanego")
    if answer_hash != receipt["result_sha256"]:
        raise ValueError("SHA-256 pliku answer.jsonl różni się od potwierdzenia R2")

    snapshot = receipt["snapshot"]
    identity = {key: snapshot[key] for key in ("repository", "commit")}
    root_tree, literal = snapshot["root_tree"], receipt["literal"]
    if not all(isinstance(value, str) and value for value in (*identity.values(), root_tree, literal)):
        raise ValueError("niepoprawne dane zapytania w potwierdzeniu R2")
    if not answer.endswith(b"\n"):
        raise ValueError("niekompletny plik answer.jsonl")
    header, *hits, trailer = map(strict_json, answer.splitlines())
    if header != {"type": "result", "format": RESULT_FORMAT, **identity,
                  "root_tree": root_tree, "literal": literal}:
        raise ValueError("nagłówek odpowiedzi R2 różni się od potwierdzonego zapytania")
    paths = []
    hit_fields = {"type", *identity, "path", "blob_id", "byte_offset", "line"}
    for hit in hits:
        if (not isinstance(hit, dict) or set(hit) != hit_fields or hit["type"] != "hit"
                or any(hit[key] != value for key, value in identity.items())
                or not isinstance(hit["path"], str) or not hit["path"]
                or not isinstance(hit["blob_id"], str) or not hit["blob_id"]
                or type(hit["byte_offset"]) is not int or hit["byte_offset"] < 0
                or type(hit["line"]) is not int or hit["line"] < 1):
            raise ValueError("niepoprawny rekord ścieżki w wyniku R2")
        paths.append(hit["path"])
    if (trailer != {"type": "complete", "count": len(paths)}
            or type(trailer["count"]) is not int or type(receipt["count"]) is not int
            or receipt["count"] != len(paths) or len(set(paths)) != len(paths)):
        raise ValueError("niepoprawna liczba lub powtórzone ścieżki w wyniku R2")
    return VerifiedResult(identity["repository"], identity["commit"], literal,
                          answer_hash, verification_hash, paths)


def save_active_result(db_path, conversation, folder, result):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS active_results (
            conversation TEXT PRIMARY KEY, folder TEXT NOT NULL, repository TEXT NOT NULL,
            git_commit TEXT NOT NULL, literal TEXT NOT NULL,
            answer_sha256 TEXT NOT NULL, verification_sha256 TEXT NOT NULL
        ) WITHOUT ROWID""")
        db.execute("""INSERT INTO active_results
            (conversation, folder, repository, git_commit, literal, answer_sha256, verification_sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (conversation) DO UPDATE SET
                folder = excluded.folder, repository = excluded.repository,
                git_commit = excluded.git_commit, literal = excluded.literal,
                answer_sha256 = excluded.answer_sha256, verification_sha256 = excluded.verification_sha256
        """, (conversation, str(folder), result.repository, result.commit, result.literal,
              result.answer_sha256, result.verification_sha256))


def active_result(db_path, conversation):
    if not db_path.exists():
        return None
    with closing(sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        table = db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'active_results'")
        if table.fetchone() is None:
            return None
        return db.execute("""SELECT folder, repository, git_commit, literal, answer_sha256, verification_sha256
            FROM active_results WHERE conversation = ?""", (conversation,)).fetchone()


def resume_result(db_path, conversation):
    active = active_result(db_path, conversation)
    reopen = "Użyj `otwórz-wynik` w tej rozmowie."
    if active is None:
        raise ValueError(f"Rozmowa {conversation!r} nie ma aktywnego wyniku. {reopen}")
    folder, repository, commit, literal, answer_hash, verification_hash = active
    try:
        result = read_verified_result(Path(folder), require_published=True, expected_answer=answer_hash,
                                      expected_verification=verification_hash)
        if (result.repository, result.commit, result.literal) != (repository, commit, literal):
            raise ValueError("repozytorium, commit lub literał różni się od zapamiętanego")
    except FileNotFoundError as exc:
        raise ValueError(f"Brakuje zapamiętanego pliku R2 {exc.filename}. {reopen}") from exc
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise ValueError(f"Nie można odczytać zapamiętanego wyniku R2 z {folder} ({exc}). {reopen}") from exc
    return result


def print_paths(title, paths, *, total=None):
    count = len(paths) if total is None else f"{len(paths)} z {total}"
    print(f"{title} ({count})")
    for path in paths:
        # Escape control characters and surrogateescaped Git paths on a single line.
        display_path = path if path.isprintable() else json.dumps(path)
        print(f"  {display_path}")


def is_test_path(path):
    directories = path.split("/")[:-1]
    return ("src", "test") in zip(directories, directories[1:])


def show_result(paths, split_tests):
    if not split_tests:
        print_paths("Wszystkie pliki", paths)
        return

    tests, others = [], []
    for path in paths:
        group = tests if is_test_path(path) else others
        group.append(path)
    print_paths("Pliki pod src/test/", tests)
    print_paths("Pozostałe pliki", others)


def nonempty_project(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("podaj identyfikator projektu, np. apache/fineract")
    return value


def nonempty_conversation(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("podaj identyfikator rozmowy, np. A")
    return value


def is_known_question(question):
    return question.strip().casefold() in (TEST_QUESTION, f"a {TEST_QUESTION}")


def ask_question(db_path, conversation, question, interpreter, evidence, *, get_client=None):
    if interpreter == "local":
        if not is_known_question(question):
            raise ValueError(f"Obsługiwane pytanie: {TEST_QUESTION}")
        decision = "show_test_paths"
    else:
        decision = interpret_question(interpreter, question, evidence, get_client=get_client)
    evidence["decision"] = decision
    if decision == "clarify":
        print("Czy chodzi o listę plików testowych z aktywnego wyniku rozmowy?")
        evidence["application"] = "asked_for_clarification"
        return
    if decision == "unsupported":
        print("Mogę pokazać listę plików spod src/test/ z aktywnego wyniku rozmowy.")
        evidence["application"] = "explained_scope"
        return

    started = perf_counter()
    evidence["application"] = "active_result_error"
    try:
        result = resume_result(db_path, conversation)
        tests = [path for path in result.paths if is_test_path(path)]
    finally:
        evidence["local_seconds"] = perf_counter() - started
    print(f"Repozytorium: {result.repository}\nCommit: {result.commit}\nLiterał: {result.literal}")
    print_paths("Pliki pod src/test/", tests, total=len(result.paths))
    evidence["application"] = "showed_paths"


def run_session(db_path, conversation, interpreter):
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    with ExitStack() as resources:
        client = None

        def get_client():
            nonlocal client
            if client is None:
                client = resources.enter_context(anthropic_client())
            return client

        while True:
            try:
                question = input(f"{conversation}> " if interactive else "").strip()
            except EOFError:
                return
            if question == "/koniec":
                return
            if not question:
                continue
            if question.startswith("/"):
                command, *identifier = question.split(maxsplit=1)
                if command == "/rozmowa" and identifier:
                    conversation = identifier[0]
                else:
                    print("Błąd: użyj `/rozmowa ID` lub `/koniec`.", file=sys.stderr, flush=True)
                continue

            selected = "local" if is_known_question(question) else interpreter
            try:
                ask_question(db_path, conversation, question, selected, {}, get_client=get_client)
                sys.stdout.flush()
            except COMMAND_ERRORS as exc:
                print(f"Błąd: {exc}", file=sys.stderr, flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help="ścieżka do innej lokalnej bazy SQLite")
    commands = parser.add_subparsers(dest="command", required=True)
    remember = commands.add_parser("zapamiętaj", help="zapisz preferencję projektu")
    show = commands.add_parser("pokaż, co pamiętasz", help="sprawdź preferencję projektu")
    forget = commands.add_parser("zapomnij", help="usuń preferencję projektu")
    for command in (remember, show, forget):
        command.add_argument("--project", type=nonempty_project, required=True)
    remember.add_argument("preferencja", choices=[PREFERENCE])
    result = commands.add_parser("pokaż-wynik", help="wyświetl wcześniej zweryfikowany wynik R2")
    result.add_argument("katalog", type=Path)
    open_result = commands.add_parser("otwórz-wynik", help="ustaw zweryfikowany wynik R2 dla rozmowy")
    ask = commands.add_parser("zapytaj", help="zapytaj o pliki testowe z aktywnego wyniku rozmowy")
    session = commands.add_parser("sesja", help="zadawaj pytania i przełączaj rozmowy w jednym procesie")
    for command in (open_result, ask, session):
        command.add_argument("--rozmowa", type=nonempty_conversation, required=True)
    open_result.add_argument("katalog", type=Path)
    ask.add_argument("pytanie")
    ask.add_argument("--interpreter", choices=("local", "claude", "dspy"), default="local",
                     help="opcjonalny tryb Claude lub DSPy wysyła pytanie do Anthropic API")
    ask.add_argument("--measurement", type=Path, help="nowy plik JSON z pomiarem próby")
    session.add_argument("--interpreter", choices=("local", "claude"), default="local",
                         help="opcjonalny Claude klasyfikuje pytania spoza znanych sformułowań")
    args = parser.parse_args(argv)

    evidence = {}
    measurement = None
    try:
        if args.command == "pokaż-wynik":
            result = read_verified_result(args.katalog)
            show_result(result.paths, project_preference(args.db, result.repository))
        elif args.command == "otwórz-wynik":
            folder = args.katalog.resolve()
            result = read_verified_result(folder, require_published=True)
            save_active_result(args.db, args.rozmowa, folder, result)
            print(f"Otwarto wynik {result.repository} — literał {result.literal!r} — pliki ({len(result.paths)})")
        elif args.command == "zapytaj":
            if args.measurement:
                measurement = args.measurement.open("x", encoding="utf-8")
            ask_question(args.db, args.rozmowa, args.pytanie, args.interpreter, evidence)
        elif args.command == "sesja":
            run_session(args.db, args.rozmowa, args.interpreter)
        else:
            enabled = {"zapamiętaj": True, "zapomnij": False}.get(args.command)
            remembered = project_preference(args.db, args.project, enabled)
            if enabled is not None:
                print("Zapisano preferencję" if enabled else "Usunięto preferencję projektu")
            elif remembered:
                print(f"{args.project} — {PREFERENCE}")
            else:
                print("Brak zapisanych preferencji")
    except InterpretationError as exc:
        evidence["application"] = exc.kind
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    except COMMAND_ERRORS as exc:
        evidence.setdefault("application", "error")
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    finally:
        if measurement is not None:
            with measurement:
                json.dump(evidence, measurement, ensure_ascii=True, indent=2)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
