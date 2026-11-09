"""Verify/restore the exact small upstream Mojom parser + PLY dependency set.

Normal use is offline --check. --payload accepts a GitHub contents-API base64
response bundle; --download restores the same pinned files from raw GitHub.
No Chromium checkout, hooks, DEPS or build are involved.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
DESTINATION = PROJECT / "vendor" / "chromium"
LOCK = PROJECT / "vendor" / "mojom-parser.lock.json"
COMMIT = "27cec857a08a0ee0e1b41f5eb18c07467a0ce093"
REPOSITORY = "https://github.com/chromium/chromium"
LOCK_SHA256 = "fa01aa9d679d877088dc66865c02ff45eea62fcaf940aa254949cd3e3cee8e54"


def identity(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def checked_lock(raw):
    """Authenticate the original checked-in lock before trusting its entries."""
    if hashlib.sha256(raw).hexdigest() != LOCK_SHA256:
        raise ValueError("vendored parser lock identity mismatch")
    lock = json.loads(raw)
    if lock["commit"] != COMMIT or lock["repository"] != REPOSITORY:
        raise ValueError("vendor source pin mismatch")
    return lock


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--payload", type=Path, help="Developer bootstrap from an exact GitHub API bundle")
    mode.add_argument("--download", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.payload:
            corpus_root = Path(json.loads((PROJECT / "local" / "corpus.json").read_text())["data_dir"])
            metadata = {e["path"]: e for e in json.loads((corpus_root / "manifest.json").read_bytes())["entries"]}
            entries = []
            contents = {}
            for item in json.loads(args.payload.read_bytes()):
                path = item["path"]
                data = base64.b64decode(item["content"], validate=False)
                if item["sha"] != metadata[path]["object_id"] or identity(data) != item["sha"]:
                    raise ValueError("upstream blob identity mismatch: " + path)
                contents[path] = data
                entries.append({"path": path, "object_id": item["sha"], "size_bytes": len(data),
                                "sha256": hashlib.sha256(data).hexdigest(),
                                "source_url": REPOSITORY + "/blob/" + COMMIT + "/" + path})
            lock = {"format": "repo-proof-vendored-mojom-v1", "repository": REPOSITORY,
                    "commit": COMMIT, "parser": "Chromium Mojom Parse (unmodified)",
                    "ply_version": "3.11", "license_files": ["LICENSE", "mojo/public/LICENSE", "third_party/ply/LICENSE"],
                    "entries": sorted(entries, key=lambda item: item["path"])}
            lock_bytes = encoded(lock)
            checked_lock(lock_bytes)
            for path, data in contents.items():
                target = DESTINATION / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            LOCK.parent.mkdir(parents=True, exist_ok=True)
            LOCK.write_bytes(lock_bytes)
        lock = checked_lock(LOCK.read_bytes())
        for entry in lock["entries"]:
            path = DESTINATION / entry["path"]
            if args.download:
                url = "https://raw.githubusercontent.com/chromium/chromium/" + COMMIT + "/" + entry["path"]
                with urllib.request.urlopen(url, timeout=90) as stream:
                    data = stream.read()
                if identity(data) != entry["object_id"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise ValueError("downloaded source hash mismatch: " + entry["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            data = path.read_bytes()
            if len(data) != entry["size_bytes"] or identity(data) != entry["object_id"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError("vendored source mismatch: " + entry["path"])
        print(json.dumps({"status": "verified", "commit": COMMIT, "files": len(lock["entries"]),
                          "bytes": sum(e["size_bytes"] for e in lock["entries"]), "ply_version": lock["ply_version"]}))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "unresolved", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
