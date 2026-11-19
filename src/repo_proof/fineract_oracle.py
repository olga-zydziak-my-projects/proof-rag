"""Independent Git object scan and strict JSONL comparison for Fineract R2."""

from collections import defaultdict
from hashlib import sha1, sha256
import json
import os
import re
import subprocess
from tempfile import TemporaryFile


class SourceUnavailable(ValueError):
    """The pinned Git objects do not establish a complete snapshot."""


class ResultMismatch(ValueError):
    """The candidate answer differs from the exact Git answer or its format."""


def strict_json(raw):
    def unique(pairs):
        values = {}
        for key, value in pairs:
            if key in values:
                raise ValueError(f"duplicate JSON key: {key!r}")
            values[key] = value
        return values

    def reject_constant(value):
        raise ValueError(f"invalid JSON constant: {value}")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=reject_constant)


def check_object(oid, kind, raw):
    digest = sha1(f"{kind} {len(raw)}\0".encode("ascii"))
    digest.update(raw)
    if digest.hexdigest() != oid:
        raise SourceUnavailable(f"Git {kind} hash differs for {oid}")


def batch_objects(git, environment, object_ids, kind, temp_dir):
    with TemporaryFile(dir=temp_dir) as requests:
        for oid in object_ids:
            requests.write(oid.encode("ascii") + b"\n")
        requests.seek(0)
        with subprocess.Popen(git + ["cat-file", "--batch"], env=environment,
                              stdin=requests, stdout=subprocess.PIPE) as process:
            try:
                for oid in object_ids:
                    fields = process.stdout.readline().split()
                    if len(fields) != 3 or fields[:2] != [oid.encode("ascii"), kind.encode("ascii")]:
                        raise SourceUnavailable(f"missing or invalid Git {kind} {oid}")
                    size = int(fields[2])
                    if size < 0:
                        raise SourceUnavailable(f"invalid Git object length for {oid}")
                    raw = process.stdout.read(size)
                    if len(raw) != size or process.stdout.read(1) != b"\n":
                        raise SourceUnavailable(f"truncated Git object {oid}")
                    check_object(oid, kind, raw)
                    yield oid, raw
                if process.stdout.read(1) or process.wait(timeout=15):
                    raise SourceUnavailable("Git object stream did not end successfully")
            finally:
                if process.poll() is None:
                    process.kill()


def tree_entries(raw):
    cursor = 0
    seen = set()
    while cursor < len(raw):
        end = raw.index(b"\0", cursor)
        mode, name = raw[cursor:end].split(b" ", 1)
        oid = raw[end + 1:end + 21]
        if (len(oid) != 20 or not name or b"/" in name or name in (b".", b"..")
                or name in seen or mode not in
                (b"40000", b"100644", b"100755", b"120000", b"160000")):
            raise SourceUnavailable("malformed entry in Git tree object")
        seen.add(name)
        yield mode, name, oid.hex()
        cursor = end + 21


def git_path_inventory(git, env, pin, distinct_blobs, directories, temp_dir):
    """Derive the complete regular path mapping from hash-checked Git trees."""
    root = pin["root_tree"]
    commit = pin["commit"]
    prefixes = tuple(path.encode("utf-8") + b"/" for path in directories)

    def covers_tree(path):
        return not prefixes or path.startswith(prefixes) or any(prefix.startswith(path) for prefix in prefixes)

    def read(*args):
        return subprocess.check_output(git + list(args), env=env,
                                       stderr=subprocess.PIPE, timeout=55)

    raw_commit = read("cat-file", "commit", commit)
    check_object(commit, "commit", raw_commit)
    if raw_commit.partition(b"\n")[0] != b"tree " + root.encode("ascii"):
        raise SourceUnavailable("pinned Git commit does not identify the pinned root tree")

    # Use ls-tree only to schedule object reads. Derive actual path mappings
    # from the bytes and SHA-1 IDs of the root and every reachable subtree.
    tree_ids = {root}
    listing = read("ls-tree", "-r", "-t", "-z", "--full-tree", root).split(b"\0")
    if listing.pop():
        raise SourceUnavailable("unterminated Git tree listing")
    for row in listing:
        fields, path = row.split(b"\t", 1)
        mode, kind, oid = fields.split()
        if mode == b"040000" and kind == b"tree" and covers_tree(path + b"/"):
            if not re.fullmatch(rb"[a-f0-9]{40}", oid):
                raise SourceUnavailable("invalid Git subtree ID")
            tree_ids.add(oid.decode("ascii"))
    trees = {oid: list(tree_entries(raw))
             for oid, raw in batch_objects(git, env, sorted(tree_ids), "tree", temp_dir)}
    pending = [(b"", root)]
    visited_prefixes = set()
    paths_by_blob = defaultdict(list)
    symlinks = []
    gitlinks = 0
    while pending:
        prefix, tree = pending.pop()
        if prefix in prefixes:
            visited_prefixes.add(prefix)
        for mode, name, oid in trees[tree]:
            path = prefix + name
            if mode == b"40000":
                if covers_tree(path + b"/"):
                    pending.append((path + b"/", oid))
            elif prefixes and not path.startswith(prefixes):
                continue
            elif mode == b"160000":
                gitlinks += 1
            elif mode == b"120000":
                symlinks.append({"path": path.decode("utf-8", "surrogateescape"),
                                 "blob_id": oid})
            else:
                paths_by_blob[oid].append(path.decode("utf-8", "surrogateescape"))
    regular = sum(map(len, paths_by_blob.values()))
    counts = {"regular_paths": regular, "blob_paths": regular + len(symlinks),
              "symlinks": len(symlinks), "gitlinks": gitlinks}
    if (visited_prefixes != set(prefixes) or any(pin[key] != count for key, count in counts.items())
            or len(paths_by_blob) != distinct_blobs):
        raise SourceUnavailable("verified Git inventory differs from the contracted scope")

    return paths_by_blob, counts, symlinks


def scan_git(store, pin, distinct_blobs, literal, temp_dir=None, *, directories=(), include_sizes=False):
    """Reconstruct paths from verified raw tree objects, then scan all regular blobs."""
    git = ["git", "--no-replace-objects", "-C", str(store)]
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    pattern = re.compile(re.escape(literal.encode("ascii")))
    try:
        paths_by_blob, counts, symlinks = git_path_inventory(git, env, pin, distinct_blobs, directories, temp_dir)
        expected = {}
        blob_bytes = path_bytes = 0
        for oid, raw in batch_objects(git, env, list(paths_by_blob), "blob", temp_dir):
            blob_bytes += len(raw)
            path_bytes += len(raw) * len(paths_by_blob[oid])
            occurrence = pattern.search(raw)
            if occurrence is not None:
                offset = occurrence.start()
                witness = (oid, offset, raw.count(b"\n", 0, offset) + 1)
                expected.update((path, witness) for path in paths_by_blob[oid])
        inventory = {**counts, "distinct_regular_blobs": distinct_blobs,
                     "excluded_symlinks": sorted(symlinks, key=lambda entry: entry["path"])}
        if include_sizes:
            inventory.update(distinct_regular_blob_bytes=blob_bytes, regular_path_bytes=path_bytes)
        return expected, inventory
    except SourceUnavailable:
        raise
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        raise SourceUnavailable(f"unable to read the complete pinned Git snapshot: {exc}") from exc


def compare(file, pin, literal, expected):
    with file.open("rb") as stream:
        return compare_section(stream, pin, literal, expected, require_eof=True)


def compare_section(stream, pin, literal, expected, *, require_eof=False, strict_order=False):
    """Compare a complete R2 section against Git and hash the exact bytes read."""
    identity = {"repository": pin["repository"], "commit": pin["commit"]}
    header = {"type": "result", "format": "git-literal-search-v1", **identity,
              "root_tree": pin["root_tree"], "literal": literal}
    fields = {"type", "repository", "commit", "path", "blob_id", "byte_offset", "line"}
    digest = sha256()
    seen = set()
    last_path = None

    def record(raw):
        if not raw.endswith(b"\n") or raw.endswith(b"\r\n"):
            raise ResultMismatch("missing complete LF-delimited result record")
        digest.update(raw)
        try:
            value = strict_json(raw)
        except (ValueError, RecursionError) as exc:
            raise ResultMismatch("invalid result JSON") from exc
        if type(value) is not dict:
            raise ResultMismatch("result record must be a JSON object")
        return value

    if record(stream.readline()) != header:
        raise ResultMismatch("result header differs from the pinned query")
    for raw in stream:
        row = record(raw)
        if row.get("type") == "complete":
            if set(row) != {"type", "count"} or type(row["count"]) is not int \
                    or row["count"] != len(seen):
                raise ResultMismatch("invalid completion marker or path count")
            if require_eof and stream.read(1):
                raise ResultMismatch("data follows the completion marker")
            if len(seen) != len(expected):
                raise ResultMismatch(f"result omits {len(expected) - len(seen)} Git path(s)")
            return {"result_sha256": digest.hexdigest(), "count": len(seen)}
        if (set(row) != fields or row["type"] != "hit"
                or any(row[key] != value for key, value in identity.items())
                or type(row["path"]) is not str or type(row["blob_id"]) is not str
                or type(row["byte_offset"]) is not int or type(row["line"]) is not int):
            raise ResultMismatch("invalid witness fields, types or provenance")
        path = row["path"]
        if path in seen:
            raise ResultMismatch("duplicate result path")
        actual = (row["blob_id"], row["byte_offset"], row["line"])
        if expected.get(path) != actual:
            raise ResultMismatch("result contains an extra path or an incorrect Git witness")
        if strict_order:
            path_bytes = path.encode("utf-8", "surrogateescape")
            if last_path is not None and path_bytes <= last_path:
                raise ResultMismatch("result paths are out of canonical byte order")
            last_path = path_bytes
        seen.add(path)
    raise ResultMismatch("missing completion marker")
