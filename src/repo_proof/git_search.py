"""Build and search a complete, pinned Git snapshot with a byte trigram index."""

import argparse
from collections import defaultdict
from contextlib import closing, contextmanager
from hashlib import sha1
import json
import os
from pathlib import Path
import re
import sqlite3
from struct import iter_unpack, pack
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

from .corpus import encoded, parse_tree


RESULT_FORMAT = "git-literal-search-v1"
PRINTABLE_RUN = re.compile(rb"[ -~]{3,}")


class SnapshotError(ValueError):
    """The source objects do not establish the requested snapshot."""


def snapshot_from(contract):
    snapshot = json.loads(contract.read_bytes())["snapshot"]
    if snapshot["object_format"] != "sha1" or any(
        not re.fullmatch(r"[0-9a-f]{40}", snapshot[key]) for key in ("commit", "root_tree")
    ):
        raise ValueError("the contract must pin a SHA-1 commit and root tree")
    return snapshot


def git_command(store, *args):
    return ["git", "--no-replace-objects", "-C", str(store.resolve()), *args]


def git_env():
    return dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")


def git_read(store, *args):
    result = subprocess.run(git_command(store, *args), env=git_env(), capture_output=True,
                            timeout=120)
    if result.returncode:
        raise SnapshotError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def inventory(store, snapshot, directories=()):
    commit = snapshot["commit"]
    if (git_read(store, "rev-parse", "--show-object-format").strip() != b"sha1"
            or git_read(store, "rev-parse", "--verify", commit + "^{commit}").strip()
            != commit.encode("ascii")
            or git_read(store, "rev-parse", commit + "^{tree}").strip()
            != snapshot["root_tree"].encode("ascii")):
        raise SnapshotError("Git commit, root tree or object format differs from the pin")
    try:
        entries = parse_tree(git_read(store, "ls-tree", "-rz", "--full-tree", commit, "--", *directories))
    except ValueError as exc:
        raise SnapshotError(f"cannot enumerate the pinned Git tree: {exc}") from exc
    regular = [entry for entry in entries if entry["category"] == "regular"]
    symlinks = [entry for entry in entries if entry["category"] == "symlink"]
    counts = {"regular_paths": len(regular), "symlinks": len(symlinks),
              "gitlinks": len(entries) - len(regular) - len(symlinks),
              "blob_paths": len(regular) + len(symlinks)}
    if any(snapshot[key] != count for key, count in counts.items()):
        raise SnapshotError(f"Git tree counts differ from the contract: {counts}")
    return regular, symlinks, counts


@contextmanager
def git_blobs(store):
    """Keep one Git subprocess and at most one active blob response."""
    command = git_command(store, "cat-file", "--batch")
    with subprocess.Popen(command, env=git_env(), stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE) as process:
        def read(oid):
            process.stdin.write(oid.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[:2] != [oid.encode("ascii"), b"blob"]:
                raise SnapshotError(f"missing or invalid Git blob: {oid}")
            size = int(header[2])
            raw = process.stdout.read(size)
            digest = sha1(b"blob " + str(size).encode("ascii") + b"\0")
            digest.update(raw)
            if (len(raw) != size or process.stdout.read(1) != b"\n"
                    or digest.hexdigest() != oid):
                raise SnapshotError(f"truncated or corrupt Git blob: {oid}")
            return raw

        try:
            yield read
            process.stdin.close()
            if process.wait(timeout=30):
                raise SnapshotError("git cat-file failed")
        finally:
            if process.poll() is None:
                process.kill()


def trigrams(raw):
    return (raw[i:i + 3] for i in range(len(raw) - 2))


def unused_part(path):
    return path.with_name(f".r2-{uuid4().hex[:16]}.part")


def build(store, snapshot, index, *, directories=()):
    start = perf_counter()
    regular, symlinks, counts = inventory(store, snapshot, directories)
    paths = [(e["path"].encode("utf-8", "surrogateescape"), e["mode"], e["object_id"])
             for e in regular]
    object_ids = sorted({oid for _, _, oid in paths})
    index.parent.mkdir(parents=True, exist_ok=True)
    part = unused_part(index)
    try:
        with closing(sqlite3.connect(part)) as db:
            db.executescript("""
                CREATE TABLE blobs(id INTEGER PRIMARY KEY, oid TEXT UNIQUE, data BLOB NOT NULL);
                CREATE TABLE paths(path BLOB PRIMARY KEY, mode TEXT NOT NULL, oid TEXT NOT NULL)
                    WITHOUT ROWID;
                CREATE TABLE postings(gram BLOB PRIMARY KEY, blob_ids BLOB NOT NULL)
                    WITHOUT ROWID;
                CREATE TABLE metadata(receipt BLOB NOT NULL);
            """)
            postings = defaultdict(bytearray)
            raw_bytes = 0
            with db, git_blobs(store) as read:
                for blob_id, oid in enumerate(object_ids, 1):
                    raw = read(oid)
                    raw_bytes += len(raw)
                    db.execute("INSERT INTO blobs VALUES (?, ?, ?)", (blob_id, oid, raw))
                    grams = {gram for run in PRINTABLE_RUN.finditer(raw)
                             for gram in trigrams(run[0])}
                    packed_id = pack("<I", blob_id)
                    for gram in grams:
                        postings[gram].extend(packed_id)
                db.executemany("INSERT INTO postings VALUES (?, ?)", sorted(postings.items()))
                db.executemany("INSERT INTO paths VALUES (?, ?, ?)", paths)
                if (set(db.execute("SELECT path, mode, oid FROM paths")) != set(paths)
                        or {oid for (oid,) in db.execute("SELECT oid FROM blobs")}
                        != set(object_ids)):
                    raise ValueError("index paths or blob IDs differ from the Git inventory")
                receipt = {"complete": True, "schema": 1, "snapshot": snapshot, **counts,
                           "distinct_regular_blobs": len(object_ids), "raw_blob_bytes": raw_bytes,
                           "distinct_trigrams": len(postings), "excluded_symlinks": symlinks,
                           "path_and_blob_sets_reconciled": True}
                if directories:
                    receipt["directories"] = list(directories)
                db.execute("INSERT INTO metadata VALUES (?)", (encoded(receipt),))
        os.replace(part, index)
    finally:
        part.unlink(missing_ok=True)
    return {**receipt, "build_seconds": perf_counter() - start, "index_bytes": index.stat().st_size,
            "peak_rss_bytes": peak_rss()}


def peak_rss():
    """Peak resident/working-set size of this process, in bytes."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("page_faults", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in
                ("peak_working_set", "working_set", "peak_paged_pool", "paged_pool",
                 "peak_nonpaged_pool", "nonpaged_pool", "pagefile", "peak_pagefile")
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        if ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.c_void_p(-1), ctypes.byref(counters), counters.cb
        ):
            return counters.peak_working_set
    if sys.platform in ("linux", "darwin"):
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value * 1024 if sys.platform == "linux" else value
    return None


def candidate_ids(db, needle):
    candidates = None
    for gram in dict.fromkeys(trigrams(needle)):
        row = db.execute("SELECT blob_ids FROM postings WHERE gram = ?", (gram,)).fetchone()
        if row is None:
            return set()
        ids = {blob_id for (blob_id,) in iter_unpack("<I", row[0])}
        candidates = ids if candidates is None else candidates & ids
        if not candidates:
            break
    return candidates


def match(db, needle, *, read_bytes=None):
    ids = candidate_ids(db, needle)
    if ids is None:
        rows = db.execute("SELECT oid, data FROM blobs")
    else:
        sql = "SELECT oid, data FROM blobs WHERE id = ?"
        rows = (db.execute(sql, (blob_id,)).fetchone() for blob_id in sorted(ids))
    matches = {}
    candidates = 0
    for oid, raw in rows:
        candidates += 1
        if read_bytes is not None:
            read_bytes[0] += len(raw)
        offset = raw.find(needle)
        if offset >= 0:
            matches[oid] = (offset, 1 + raw.count(b"\n", 0, offset))
    return matches, candidates


def query(index, snapshot, literal, output, preview_limit, *, directories=()):
    if not re.fullmatch(r"[ -~]+", literal):
        raise ValueError("literal must be nonempty printable ASCII on one line")
    if output.resolve() == index.resolve():
        raise ValueError("query output must differ from the index")
    start = perf_counter()
    with closing(sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("BEGIN")
        metadata = list(db.execute("SELECT receipt FROM metadata"))
        if len(metadata) != 1:
            raise ValueError("index has no unique completion receipt")
        receipt = json.loads(metadata[0][0])
        if (receipt.get("complete") is not True or receipt.get("schema") != 1
                or receipt.get("snapshot") != snapshot or receipt.get("directories", []) != list(directories)):
            raise ValueError("index is incomplete or differs from the pinned snapshot")
        if (db.execute("SELECT count(*) FROM paths").fetchone()[0] != snapshot["regular_paths"]
                or db.execute("SELECT count(*) FROM blobs").fetchone()[0]
                != receipt["distinct_regular_blobs"]):
            raise ValueError("index inventory differs from its completion receipt")

        read_bytes = [0]
        matches, candidates = match(db, literal.encode("ascii"), read_bytes=read_bytes)
        match_seconds = perf_counter() - start
        provenance = {"repository": snapshot["repository"], "commit": snapshot["commit"]}
        header = {"type": "result", "format": RESULT_FORMAT, **provenance,
                  "root_tree": snapshot["root_tree"], "literal": literal}
        count = 0
        preview = []
        output.parent.mkdir(parents=True, exist_ok=True)
        part = unused_part(output)
        try:
            with part.open("xb") as stream:
                stream.write(encoded(header))
                for path, oid in db.execute("SELECT path, oid FROM paths ORDER BY path"):
                    if oid in matches:
                        offset, line = matches[oid]
                        hit = {"type": "hit", **provenance, "blob_id": oid,
                               "path": path.decode("utf-8", "surrogateescape"),
                               "byte_offset": offset, "line": line}
                        stream.write(encoded(hit))
                        count += 1
                        if len(preview) < preview_limit:
                            preview.append(hit)
                stream.write(encoded({"type": "complete", "count": count}))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(part, output)
        finally:
            part.unlink(missing_ok=True)
    total = perf_counter() - start
    return {"literal": literal, "count": count, "preview": preview,
            "method": "full_scan" if len(literal) < 3 else "trigram_candidates",
            "candidate_blobs": candidates, "candidate_blob_bytes": read_bytes[0], "match_seconds": match_seconds,
            "output_seconds": total - match_seconds, "total_seconds": total,
            "peak_rss_bytes": peak_rss()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("--git-dir", required=True, type=Path)
    search = commands.add_parser("query")
    search.add_argument("--literal", required=True)
    search.add_argument("--output", required=True, type=Path)
    search.add_argument("--preview", type=int, default=5, metavar="0..50")
    for command in (builder, search):
        command.add_argument("--contract", required=True, type=Path)
        command.add_argument("--index", required=True, type=Path)
    args = parser.parse_args()
    try:
        snapshot = snapshot_from(args.contract)
        if args.command == "build":
            if args.index.resolve() == args.contract.resolve():
                raise ValueError("index must differ from the contract")
            result = build(args.git_dir, snapshot, args.index)
        else:
            if not 0 <= args.preview <= 50:
                parser.error("--preview must be between 0 and 50")
            if args.output.resolve() == args.contract.resolve():
                raise ValueError("query output must differ from the contract")
            result = query(args.index, snapshot, args.literal, args.output, args.preview)
    except (SnapshotError, subprocess.TimeoutExpired, BrokenPipeError) as exc:
        print(f"Snapshot unavailable or incomplete: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        print(f"Git search failed: {exc}", file=sys.stderr)
        return 1
    print(encoded(result).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
