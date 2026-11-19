"""An independently reconciled trigram index with authenticated point reads."""

from collections import defaultdict
from contextlib import closing
from hashlib import sha256
import os
import re
import sqlite3
from struct import iter_unpack, pack

from .fineract_oracle import SourceUnavailable, batch_objects, git_path_inventory, strict_json


FORMAT = "git-checked-trigram-index-v1"
DIGEST_SIZE = 32
EMPTY = bytes(DIGEST_SIZE)
ALPHABET = 95
GRAM_CATALOG_SIZE = ALPHABET ** 2 * DIGEST_SIZE
ASCII_SPANS = re.compile(rb"[\x20-\x7e]{3,}")


def digest(raw):
    return sha256(raw).digest()


def immutable_bytes(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def readonly(path):
    return sqlite3.connect(path.resolve(strict=True).as_uri() + "?mode=ro", uri=True)


def bucket_offset(prefix):
    return ((prefix[0] - 32) * ALPHABET + prefix[1] - 32) * DIGEST_SIZE


def gram_set(raw):
    grams = set()
    for span in ASCII_SPANS.finditer(raw):
        text = span.group()
        grams.update(zip(text, text[1:], text[2:]))
    return grams


def object_seal(oid, raw, paths):
    return digest(bytes.fromhex(oid) + digest(raw) + paths)


def reconcile_shard(repo, store, candidate, target):
    """Re-derive both relations from checked Git bytes and compare every existing index row."""
    name, pin = repo["id"], repo["snapshot"]
    git = ["git", "--no-replace-objects", "-C", str(store)]
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    total = repo["distinct_regular_blobs"]
    paths_by_oid, _, _ = git_path_inventory(git, env, pin, total, repo["directories"], target)
    expected_paths = sorted((path.encode("utf-8", "surrogateescape"), oid)
                            for oid, paths in paths_by_oid.items() for path in paths)
    object_catalog = bytearray()
    postings = defaultdict(bytearray)
    raw_bytes = path_bytes = 0
    with closing(readonly(candidate)) as source, closing(sqlite3.connect(target / f"{name}.sqlite")) as verifier:
        source.execute("BEGIN")
        if list(source.execute("SELECT path, oid FROM paths ORDER BY path")) != expected_paths:
            raise SourceUnavailable(f"{name}: candidate path mapping differs from verified Git trees")
        verifier.executescript("""
            CREATE TABLE objects(id INTEGER PRIMARY KEY, oid TEXT NOT NULL, data BLOB NOT NULL, paths BLOB NOT NULL);
            CREATE TABLE postings(gram BLOB PRIMARY KEY, ids BLOB NOT NULL) WITHOUT ROWID;
            CREATE TABLE proofs(prefix BLOB PRIMARY KEY, members BLOB NOT NULL) WITHOUT ROWID;
        """)
        with verifier:
            indexed = source.execute("SELECT id, oid, data FROM blobs ORDER BY id")
            for number, ((oid, raw), candidate_row) in enumerate(zip(
                    batch_objects(git, env, sorted(paths_by_oid), "blob", target), indexed, strict=True), 1):
                if (number, oid, raw) != candidate_row:
                    raise SourceUnavailable(f"{name}: candidate blob {number} differs from checked Git bytes")
                paths = b"\0".join(sorted(path.encode("utf-8", "surrogateescape") for path in paths_by_oid[oid]))
                object_catalog.extend(object_seal(oid, raw, paths))
                verifier.execute("INSERT INTO objects VALUES (?, ?, ?, ?)", (number, oid, raw, paths))
                raw_bytes += len(raw)
                path_bytes += len(raw) * len(paths_by_oid[oid])
                packed = pack("<I", number)
                for gram in gram_set(raw):
                    postings[bytes(gram)].extend(packed)
            if (raw_bytes, path_bytes) != (repo["distinct_regular_blob_bytes"], repo["regular_path_bytes"]):
                raise SourceUnavailable(f"{name}: blob byte counts differ from the manifest")
            buckets = defaultdict(bytearray)
            expected = sorted(postings.items())
            indexed = source.execute("SELECT gram, blob_ids FROM postings ORDER BY gram")
            for (gram, ids), candidate_row in zip(expected, indexed, strict=True):
                if (gram, ids) != candidate_row:
                    raise SourceUnavailable(f"{name}: incomplete or incorrect postings for {gram!r}")
                verifier.execute("INSERT INTO postings VALUES (?, ?)", (gram, ids))
                buckets[gram[:2]].extend(gram[2:] + digest(ids))
            gram_catalog = bytearray(GRAM_CATALOG_SIZE)
            for prefix, members in buckets.items():
                offset = bucket_offset(prefix)
                gram_catalog[offset:offset + DIGEST_SIZE] = digest(members)
                verifier.execute("INSERT INTO proofs VALUES (?, ?)", (prefix, members))
    immutable_bytes(target / f"{name}.grams", gram_catalog)
    immutable_bytes(target / f"{name}.objects", object_catalog)
    return {"id": name, "paths": len(expected_paths), "objects": total, "blob_bytes": raw_bytes,
            "trigrams": len(postings), "postings_bytes": sum(map(len, postings.values())),
            "grams_sha256": digest(gram_catalog).hex(), "objects_sha256": digest(object_catalog).hex()}


def checked_receipt(directory, expected_sha256):
    raw = (directory / "receipt.json").read_bytes()
    if digest(raw).hex() != expected_sha256:
        raise SourceUnavailable("checked index receipt SHA-256 differs from the configured trust anchor")
    receipt = strict_json(raw)
    if receipt["format"] != FORMAT:
        raise SourceUnavailable("unsupported checked index format")
    return receipt


def authenticate(raw, expected, label):
    if digest(raw) != expected:
        raise SourceUnavailable(f"checked index authentication failed: {label}")
    return raw


def find_verified(directory, stock, literal):
    """Read only authenticated postings, candidate blobs and their complete path sets."""
    needle = literal.encode("ascii")
    if len(needle) < 3:
        raise ValueError("short literals require the full Git verifier")
    name = stock["id"]
    gram_catalog = authenticate((directory / f"{name}.grams").read_bytes(),
                                bytes.fromhex(stock["grams_sha256"]), f"{name} gram catalog")
    objects = authenticate((directory / f"{name}.objects").read_bytes(),
                           bytes.fromhex(stock["objects_sha256"]), f"{name} object catalog")
    if len(gram_catalog) != GRAM_CATALOG_SIZE or len(objects) != stock["objects"] * DIGEST_SIZE:
        raise SourceUnavailable(f"{name}: invalid catalog sizes")
    metrics = {"objects_read": 0, "blob_bytes": 0, "posting_lists_read": 0, "posting_bytes": 0,
               "proof_bytes": len(gram_catalog) + len(objects), "path_bytes": 0}
    with closing(readonly(directory / f"{name}.sqlite")) as db:
        db.execute("BEGIN")
        candidates = None
        proofs = {}
        for gram in dict.fromkeys(needle[i:i + 3] for i in range(len(needle) - 2)):
            prefix = gram[:2]
            if prefix not in proofs:
                offset = bucket_offset(prefix)
                seal = gram_catalog[offset:offset + DIGEST_SIZE]
                if seal == EMPTY:
                    return {}, metrics
                row = db.execute("SELECT members FROM proofs WHERE prefix=?", (prefix,)).fetchone()
                if row is None:
                    raise SourceUnavailable(f"{name}: missing gram authentication proof")
                members = authenticate(row[0], seal, f"{name} proof {prefix!r}")
                metrics["proof_bytes"] += len(members)
                proofs[prefix] = dict(iter_unpack("<B32s", members))
            seal = proofs[prefix].get(gram[2])
            if seal is None:
                return {}, metrics
            row = db.execute("SELECT ids FROM postings WHERE gram=?", (gram,)).fetchone()
            if row is None:
                raise SourceUnavailable(f"{name}: missing certified postings for {gram!r}")
            postings = authenticate(row[0], seal, f"{name} postings {gram!r}")
            metrics["posting_lists_read"] += 1
            metrics["posting_bytes"] += len(postings)
            ids = {number for (number,) in iter_unpack("<I", postings)}
            candidates = ids if candidates is None else candidates & ids
            if not candidates:
                return {}, metrics
        pattern = re.compile(re.escape(needle))
        expected = {}
        for number in sorted(candidates):
            if not 1 <= number <= stock["objects"]:
                raise SourceUnavailable(f"{name}: invalid certified blob ID")
            row = db.execute("SELECT oid, data, paths FROM objects WHERE id=?", (number,)).fetchone()
            if row is None:
                raise SourceUnavailable(f"{name}: missing certified blob {number}")
            oid, raw, paths = row
            offset = (number - 1) * DIGEST_SIZE
            if (len(oid) != 40 or oid != oid.lower()
                    or object_seal(oid, raw, paths) != objects[offset:offset + DIGEST_SIZE]):
                raise SourceUnavailable(f"{name}: changed certified blob or path mapping {number}")
            metrics["objects_read"] += 1
            metrics["blob_bytes"] += len(raw)
            metrics["path_bytes"] += len(paths)
            occurrence = pattern.search(raw)
            if occurrence is not None:
                begin = occurrence.start()
                witness = (oid, begin, raw.count(b"\n", 0, begin) + 1)
                expected.update((path.decode("utf-8", "surrogateescape"), witness) for path in paths.split(b"\0"))
    return expected, metrics
