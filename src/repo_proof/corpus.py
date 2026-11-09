"""Reproducible partial corpus. Git and this implementation are trusted inputs.

Never checks out sources or follows Git symlinks/submodules. Content-addressed
files contain original blob bytes. Operational reports are separate from the
deterministic manifest. No claim of formal source extraction correctness.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from time import perf_counter

REPOSITORY = "https://github.com/chromium/chromium"
COMMIT = "27cec857a08a0ee0e1b41f5eb18c07467a0ce093"
PROJECT = Path(__file__).resolve().parents[2]
REFERENCES = (
    "mojo/public/tools/mojom/mojom/parse/lexer.py",
    "mojo/public/tools/mojom/mojom/parse/parser.py",
    "mojo/public/tools/bindings/mojom_bindings_generator.py",
)


class CorpusError(ValueError):
    pass


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def git(store, *args, data=None, network=False, allow_missing=False):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    # Disabling automatic lazy fetch makes offline verification actually offline.
    command = ["git", "-c", "core.hooksPath=" + str(store / "disabled-hooks"),
               "-c", "protocol.file.allow=never", "--git-dir=" + str(store), *args]
    run = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, timeout=1800 if network else 120)
    if run.returncode and allow_missing:
        return None
    if run.returncode:
        raise CorpusError(f"git {' '.join(args)} exited {run.returncode}: "
                          + run.stderr.decode("utf-8", "replace").strip())
    return run.stdout


def parse_tree(raw):
    if raw and not raw.endswith(b"\0"):
        raise CorpusError("truncated ls-tree output (missing final NUL)")
    entries = []
    seen = set()
    modes = {"040000": "tree", "100644": "blob", "100755": "blob",
             "120000": "blob", "160000": "commit"}
    for record in raw.split(b"\0")[:-1]:
        if not record:
            raise CorpusError("empty internal ls-tree record")
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split(" ")
            path = raw_path.decode("utf-8", "surrogateescape")
        except (ValueError, UnicodeError) as exc:
            raise CorpusError("invalid ls-tree record") from exc
        if modes.get(mode) != kind or not re.fullmatch(r"[0-9a-f]{40}", oid):
            raise CorpusError(f"unsupported Git tree entry: {metadata!r}")
        if not path or path in seen or path.startswith("/") or any(
                part in ("", ".", "..") for part in path.split("/")):
            raise CorpusError(f"invalid/duplicate Git path: {path!r}")
        seen.add(path)
        category = ("tree" if kind == "tree" else "gitlink" if mode == "160000"
                    else "symlink" if mode == "120000" else "regular")
        entries.append({"path": path, "mode": mode, "type": kind,
                        "object_id": oid, "category": category})
    return sorted(entries, key=lambda item: item["path"].encode("utf-8", "surrogateescape"))


def selected(entry):
    return entry["category"] == "regular" and entry["path"].endswith(".mojom")


def wanted(entry):
    return selected(entry) or (entry["category"] == "regular" and entry["path"] in REFERENCES)


def blob_path(root, oid):
    return root / "blobs" / oid[:2] / oid[2:]


def blob_identity(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def read_blob(root, oid):
    path = blob_path(root, oid)
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise CorpusError(f"missing materialized blob: {oid}") from exc
    if blob_identity(data) != oid:
        raise CorpusError(f"blob Git identity mismatch: {oid}")
    return data


def read_tree(store):
    actual = git(store, "rev-parse", "--verify", COMMIT + "^{commit}").decode().strip()
    if actual != COMMIT:
        raise CorpusError(f"commit mismatch: {actual}")
    tree = git(store, "rev-parse", COMMIT + "^{tree}").decode().strip()
    raw = git(store, "ls-tree", "-r", "-t", "-z", "--full-tree", COMMIT)
    entries = parse_tree(raw)
    # Independent Git leaf listing guards accidental omission of a category/tree.
    leaves = parse_tree(git(store, "ls-tree", "-r", "-z", "--full-tree", COMMIT))
    if [e for e in entries if e["category"] != "tree"] != leaves:
        raise CorpusError("recursive tree and leaf enumeration disagree")
    if sum(map(selected, entries)) != sum(map(selected, leaves)):
        raise CorpusError("selected .mojom count differs from Git leaf enumeration")
    return tree, raw, entries


def build_manifest(root, tree, entries):
    rows = []
    for entry in entries:
        row = dict(entry)
        if wanted(entry):
            data = read_blob(root, entry["object_id"])
            row.update(availability="materialized", size_bytes=len(data),
                       sha256=hashlib.sha256(data).hexdigest(),
                       content_role="mojom" if selected(entry) else "parser_reference")
        else:
            row["availability"] = {
                "tree": "metadata_only", "regular": "not_selected",
                "symlink": "link_not_materialized", "gitlink": "external_not_fetched",
            }[entry["category"]]
        rows.append(row)
    return {
        "format": "repo-proof-corpus-v1", "repository": REPOSITORY, "commit": COMMIT,
        "root_tree_object_id": tree, "git_object_format": "sha1",
        "scope": "All recursive main-repository entries including trees; regular case-sensitive .mojom blobs plus listed parser references; no submodule traversal",
        "selection": {"regular_suffix": ".mojom", "references": list(REFERENCES)},
        "metadata_complete": True, "selected_content_complete": True,
        "full_chromium_content_complete": False, "entries": rows,
    }


def initialize(root):
    store = root / "git"
    if not (store / "config").exists():
        root.mkdir(parents=True, exist_ok=True)
        run = subprocess.run(["git", "init", "--bare", str(store)], capture_output=True)
        if run.returncode:
            raise CorpusError(run.stderr.decode("utf-8", "replace"))
    for key, value in (("remote.origin.url", REPOSITORY),
                       ("remote.origin.promisor", "true"),
                       ("remote.origin.partialclonefilter", "blob:none"),
                       ("core.autocrlf", "false"), ("gc.auto", "0")):
        git(store, "config", "--local", key, value)
    return store


def materialize(root, store, entries, stop_after=None):
    wanted_ids = sorted({e["object_id"] for e in entries if wanted(e)})
    needed = []
    reused = 0
    for oid in wanted_ids:
        try:
            read_blob(root, oid)
            reused += 1
        except CorpusError:
            needed.append(oid)
    local = git(store, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                data=("\n".join(needed) + "\n").encode() if needed else b"")
    lines = local.decode("ascii").splitlines()
    if len(lines) != len(needed):
        raise CorpusError("cat-file local inventory length mismatch")
    missing = []
    for oid, line in zip(needed, lines):
        if line == oid + " missing":
            missing.append(oid)
        elif line != oid + " blob":
            raise CorpusError(f"unexpected local object: {line}")
    if missing:
        print(f"Fetching {len(missing)} selected/reference blob objects", file=sys.stderr, flush=True)
        git(store, "fetch", "--no-tags", "--no-recurse-submodules", "--no-auto-maintenance",
            "--no-write-fetch-head", "--filter=blob:none", "--stdin", "origin",
            data=("\n".join(missing) + "\n").encode(), network=True)
    written = 0
    written_bytes = 0
    # Batches bound Python memory while amortizing subprocess costs.
    for start in range(0, len(needed), 64):
        batch = needed[start:start + 64]
        output = git(store, "cat-file", "--batch", data=("\n".join(batch) + "\n").encode())
        offset = 0
        for oid in batch:
            end = output.index(b"\n", offset)
            header = output[offset:end].decode("ascii").split()
            if len(header) != 3 or header[:2] != [oid, "blob"]:
                raise CorpusError(f"unexpected batch object header: {header}")
            size = int(header[2])
            data = output[end + 1:end + 1 + size]
            offset = end + size + 2
            if len(data) != size or output[offset - 1:offset] != b"\n" or blob_identity(data) != oid:
                raise CorpusError(f"truncated/corrupt Git blob: {oid}")
            atomic_write(blob_path(root, oid), data)
            written += 1
            written_bytes += len(data)
            if stop_after is not None and written >= stop_after:
                raise CorpusError(f"intentional interruption after {written} materialized blobs")
        if offset != len(output):
            raise CorpusError("extra bytes in cat-file batch response")
    return {"reused_blob_objects": reused, "new_materialized_blob_objects": written,
            "new_materialized_bytes": written_bytes,
            "requested_missing_git_blob_objects": len(missing)}


def disk_bytes(root):
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def allocated_bytes(root):
    """Actual allocation where available; never substitute logical size."""
    paths = (p for p in root.rglob("*") if p.is_file())
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class FileStandardInfo(ctypes.Structure):
            _fields_ = [("AllocationSize", ctypes.c_longlong), ("EndOfFile", ctypes.c_longlong),
                        ("NumberOfLinks", wintypes.DWORD), ("DeletePending", ctypes.c_ubyte),
                        ("Directory", ctypes.c_ubyte)]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                           wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create.restype = wintypes.HANDLE
        info = kernel.GetFileInformationByHandleEx
        info.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
        info.restype = wintypes.BOOL
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close.restype = wintypes.BOOL
        total = 0
        for path in paths:
            handle = create(str(path), 0x80, 7, None, 3, 0, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                standard = FileStandardInfo()
                if not info(handle, 1, ctypes.byref(standard), ctypes.sizeof(standard)):
                    raise ctypes.WinError(ctypes.get_last_error())
                total += standard.AllocationSize
            finally:
                close(handle)
        return total
    sizes = [p.stat() for p in paths]
    return sum(s.st_blocks * 512 for s in sizes) if all(hasattr(s, "st_blocks") for s in sizes) else None


def verify(root):
    tree, raw, entries = read_tree(root / "git")
    if (root / "tree.entries.z").read_bytes() != raw:
        raise CorpusError("saved tree metadata differs from pinned Git tree")
    expected = encoded(build_manifest(root, tree, entries))
    if (root / "manifest.json").read_bytes() != expected:
        raise CorpusError("manifest differs from complete tree/current blob bytes")
    return json.loads(expected)


def run(root, *, offline=False, stop_after=None):
    start = perf_counter()
    existing_parent = root
    while not existing_parent.exists():
        existing_parent = existing_parent.parent
    before_free = shutil.disk_usage(existing_parent).free
    materialized = {}
    if offline:
        manifest = verify(root)
    else:
        atomic_write(root / "state.json", encoded({"status": "in_progress", "commit": COMMIT}))
        try:
            store = initialize(root)
            present = git(store, "rev-parse", "--verify", COMMIT + "^{commit}", allow_missing=True) is not None
            if not present:
                print("Fetching pinned commit and complete tree metadata (blob:none)",
                      file=sys.stderr, flush=True)
                git(store, "fetch", "--depth=1", "--filter=blob:none", "--no-tags",
                    "--no-recurse-submodules", "--no-auto-maintenance", "origin", COMMIT,
                    network=True)
            tree, raw, entries = read_tree(store)
            atomic_write(root / "tree.entries.z", raw)
            materialized = materialize(root, store, entries, stop_after=stop_after)
            atomic_write(root / "manifest.json", encoded(build_manifest(root, tree, entries)))
            manifest = verify(root)
            atomic_write(root / "state.json", encoded({"status": "complete", "commit": COMMIT}))
        except BaseException as exc:
            atomic_write(root / "state.json", encoded({"status": "interrupted_or_failed",
                         "commit": COMMIT, "error": str(exc)}))
            raise
    rows = manifest["entries"]
    sources = [e for e in rows if e.get("content_role") == "mojom"]
    content = [e for e in rows if e["availability"] == "materialized"]
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(), "data_dir": str(root),
        "repository": REPOSITORY, "commit": COMMIT, "offline_verification": offline,
        "metadata_complete": True, "selected_content_complete": True,
        "full_chromium_content_complete": False, "tree_entries": len(rows),
        "entry_categories": dict(sorted(Counter(e["category"] for e in rows).items())),
        "mojom_files": len(sources), "mojom_bytes_by_path": sum(e["size_bytes"] for e in sources),
        "materialized_bytes_by_path": sum(e["size_bytes"] for e in content),
        "unique_materialized_blob_bytes": sum(len(read_blob(root, oid)) for oid in
                                               {e["object_id"] for e in content}),
        "manifest_sha256": hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest(),
        "manifest_bytes": (root / "manifest.json").stat().st_size,
        "tree_listing_bytes": (root / "tree.entries.z").stat().st_size,
        "git_store_logical_bytes": disk_bytes(root / "git"),
        "corpus_logical_bytes": disk_bytes(root),
        "corpus_allocated_file_bytes": allocated_bytes(root), "free_bytes_before": before_free,
        "allocation_method": ("GetFileInformationByHandleEx.FileStandardInfo.AllocationSize"
                              if os.name == "nt" else "stat.st_blocks * 512 (when available)"),
        "free_bytes_after": shutil.disk_usage(root).free,
        "elapsed_seconds": perf_counter() - start, **materialized,
        "measurement_notes": ["File sizes are logical lengths, not filesystem allocation.",
                              "Allocated file bytes exclude directory entries and filesystem metadata.",
                              "Git pack transfer bytes not measured; blob bytes are uncompressed original content.",
                              "DEPS and submodules excluded; full Chromium source size not measured."],
    }
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--config", default=str(PROJECT / "local" / "corpus.json"))
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--stop-after-blobs", type=int, help="Deliberately interrupt for recovery testing")
    args = parser.parse_args(argv)
    try:
        config = Path(args.config)
        if args.data_dir is not None:
            root = args.data_dir.resolve()
        else:
            root = Path(json.loads(config.read_text(encoding="utf-8"))["data_dir"]).resolve()
        if root == PROJECT or PROJECT in root.parents:
            raise CorpusError("corpus data must be outside the tool repository")
        if args.command == "prepare":
            atomic_write(config, encoded({"data_dir": str(root), "repository": REPOSITORY, "commit": COMMIT}))
        report = run(root, offline=args.command == "verify", stop_after=args.stop_after_blobs)
        if args.report:
            atomic_write(args.report, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (CorpusError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "unresolved", "commit": COMMIT, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
