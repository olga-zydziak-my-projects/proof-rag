"""Zapisz preferencję projektu i wyświetl opublikowany wynik Fineract R2."""

import argparse
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from repo_proof.fineract_oracle import strict_json


DEFAULT_DB = PROJECT / "local/project-memory/preferences.sqlite3"
PREFERENCE = "pokazuj pliki testowe osobno"


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


def read_verified_paths(folder):
    receipt = strict_json((folder / "verification.json").read_bytes())
    if receipt["status"] != "VERIFIED":
        raise ValueError("potwierdzenie R2 musi mieć status VERIFIED")
    answer = (folder / "answer.jsonl").read_bytes()
    if sha256(answer).hexdigest() != receipt["result_sha256"]:
        raise ValueError("SHA-256 pliku answer.jsonl różni się od potwierdzenia R2")

    project = receipt["snapshot"]["repository"]
    header, *hits, trailer = map(strict_json, answer.splitlines())
    if (not isinstance(project, str) or not project.strip()
            or header["type"] != "result" or header["repository"] != project):
        raise ValueError("wynik R2 i potwierdzenie muszą wskazywać ten sam projekt")
    paths = []
    for hit in hits:
        if hit["type"] != "hit" or not isinstance(hit["path"], str):
            raise ValueError("niepoprawny rekord ścieżki w wyniku R2")
        paths.append(hit["path"])
    if (trailer != {"type": "complete", "count": len(paths)}
            or receipt["count"] != len(paths) or len(set(paths)) != len(paths)):
        raise ValueError("niepoprawna liczba lub powtórzone ścieżki w wyniku R2")
    return project, paths


def print_paths(title, paths):
    print(f"{title} ({len(paths)})")
    for path in paths:
        # Escape control characters and surrogateescaped Git paths on a single line.
        display_path = path if path.isprintable() else json.dumps(path)
        print(f"  {display_path}")


def show_result(paths, split_tests):
    if not split_tests:
        print_paths("Wszystkie pliki", paths)
        return

    tests, others = [], []
    for path in paths:
        directories = path.split("/")[:-1]
        group = tests if ("src", "test") in zip(directories, directories[1:]) else others
        group.append(path)
    print_paths("Pliki pod src/test/", tests)
    print_paths("Pozostałe pliki", others)


def nonempty_project(value):
    if not value.strip():
        raise argparse.ArgumentTypeError("podaj identyfikator projektu, np. apache/fineract")
    return value


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
    args = parser.parse_args(argv)

    try:
        if args.command == "pokaż-wynik":
            project, paths = read_verified_paths(args.katalog)
            show_result(paths, project_preference(args.db, project))
        else:
            enabled = {"zapamiętaj": True, "zapomnij": False}.get(args.command)
            remembered = project_preference(args.db, args.project, enabled)
            if enabled is not None:
                print("Zapisano preferencję" if enabled else "Usunięto preferencję projektu")
            elif remembered:
                print(f"{args.project} — {PREFERENCE}")
            else:
                print("Brak zapisanych preferencji")
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        print(f"Błąd: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
