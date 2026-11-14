"""Reuse an accepted source proof under an independently committed identity.

This is an audited IO boundary, not a new source proof.  A cache cannot select
its own expected hashes: they are read from the fixed Stage 5 checkpoint.
Every use checks the complete dependency inventory, original proof bytes and
the complete source-byte export against a fresh caller-owned capture.
"""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import threading

from .extraction import read_json, unique_object
from .stage5_answer_v2 import expected_answer
from .stage5_v2 import canonical, capture, snapshot_payload


BASELINE = "7cbad10af87dc97bae4b23603921441aa899f7b0"
REPORT = "verification/stage5-v2-final-checks.json"
SCHEMA = "repo-proof-prepared-source-v1"
MANIFEST = "prepared-source.json"
MODULES = tuple(sorted((
    "Reachability", "Checker", "ProofTiming", "FastChecker", "ChromiumFast",
    "SourceByteScanner", "SourceGraphBinding", "AnswerBinding", "SourceNames",
    "ProjectionCases", "ChromiumSource",
    *(f"SourceGroup{i:03}" for i in range(30)),
)))
_GIT_ENV_LOCK = threading.RLock()
_ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def file_identity(path):
    """Hash all bytes; callers never substitute mtime/size-only checks."""
    digest = hashlib.sha256()
    length = 0
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
            length += len(chunk)
    return {"bytes": length, "sha256": digest.hexdigest()}


def _bytes_identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _same(left, right):
    # Python's True == 1 must not authorize metadata substitutions.
    return canonical(left) == canonical(right)


@contextmanager
def _git_environment(project):
    """Only child Git processes gain this repository-specific safe.directory.

    Existing environment configuration is retained. No user/system/global Git
    configuration is written. The lock serializes this helper within Python;
    callers must not concurrently mutate process environment themselves.
    """
    with _GIT_ENV_LOCK:
        old_count = os.environ.get("GIT_CONFIG_COUNT")
        count = int(old_count or "0")
        _require(count >= 0, "invalid existing Git environment count")
        key = f"GIT_CONFIG_KEY_{count}"
        value = f"GIT_CONFIG_VALUE_{count}"
        previous = {name: os.environ.get(name) for name in
                    ("GIT_CONFIG_COUNT", key, value, "GIT_NO_REPLACE_OBJECTS")}
        try:
            os.environ["GIT_CONFIG_COUNT"] = str(count + 1)
            os.environ[key] = "safe.directory"
            os.environ[value] = Path(project).resolve().as_posix()
            os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"
            yield
        finally:
            for name, before in previous.items():
                if before is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = before


def anchored_capture(project):
    """Run the preserved full Git/byte/parser capture with scoped Git config."""
    with _git_environment(project):
        return capture(Path(project).resolve())


def _git_blob(project, relative):
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1")
    command = ["git", "-c", f"safe.directory={Path(project).resolve().as_posix()}",
               "show", f"{BASELINE}:{relative}"]
    result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                            check=True)
    return result.stdout


def _identity_schema(value):
    return (isinstance(value, dict) and set(value) == {"bytes", "sha256"}
            and type(value["bytes"]) is int and value["bytes"] > 0
            and isinstance(value["sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", value["sha256"]) is not None)


def _read_anchor(project):
    raw = _git_blob(project, REPORT)
    report = json.loads(raw, object_pairs_hook=unique_object)
    _require(report.get("status") == "STAGE5_PASS" and
             report.get("stage5_pass") is True, "checkpoint has no accepted source proof")
    _require(report.get("gates") == {f"G{i}": "PASS" for i in range(1, 9)},
             "checkpoint acceptance gates are incomplete")
    conditions = report.get("gate_conditions", {})
    _require(set(conditions) == {f"G{i}" for i in range(1, 9)} and
             all(value is True for value in conditions.values()),
             "checkpoint gate conditions are incomplete")
    nonce = report.get("run_nonce")
    _require(isinstance(nonce, str) and re.fullmatch(r"[0-9a-f]{32}", nonce),
             "checkpoint run identity is invalid")
    compiled = {}
    for entry in report["checks"]:
        if "compiled" not in entry:
            continue
        name = entry["name"]
        _require(name in MODULES and name not in compiled, "checkpoint module inventory")
        _require(entry.get("passed") is True and type(entry.get("exit_code")) is int
                 and entry["exit_code"] == 0 and entry.get("timed_out") is False
                 and entry.get("run_nonce") == nonce, "checkpoint module not accepted: " + name)
        _require(_identity_schema(entry.get("source")) and
                 _identity_schema(entry.get("compiled")), "checkpoint identity schema: " + name)
        axioms = entry.get("axioms")
        _require(isinstance(axioms, dict) and
                 all(isinstance(items, list) and set(items) <= _ALLOWED_AXIOMS
                     for items in axioms.values()), "checkpoint axiom audit: " + name)
        for ext, kind in (("lean", "source"), ("olean", "compiled")):
            rel = f"lean/{name}.{ext}"
            _require(_same(report["artifacts"].get(rel), entry[kind]),
                     "checkpoint artifact disagreement: " + rel)
        compiled[name] = entry
    _require(set(compiled) == set(MODULES), "checkpoint proof dependency closure incomplete")
    expected_artifacts = {f"lean/{name}.{ext}" for name in MODULES
                          for ext in ("lean", "olean")}
    _require(set(report["artifacts"]) == expected_artifacts,
             "checkpoint contains an unexpected proof artifact")
    for name in ("ChromiumSource.source_bound", "ChromiumSource.paths_unique",
                 "ChromiumSource.source_to_answer"):
        _require(name in compiled["ChromiumSource"]["axioms"],
                 "checkpoint final theorem audit missing: " + name)
    versions = [entry for entry in report["checks"] if entry["name"] == "lean_version"]
    _require(len(versions) == 1 and versions[0].get("passed") is True and
             "version 4.35.0," in versions[0].get("stdout", ""),
             "checkpoint Lean toolchain mismatch")
    return report, _bytes_identity(raw)


def _check_replay_code(project, report):
    # These are the preserved Python modules actually used to capture/decode
    # sources and the language specification. New stage6 code is a separate IO
    # boundary; a changed old extractor/specification cannot reuse this proof.
    for rel, expected in report["code_at_start"].items():
        if (rel.startswith("src/repo_proof/") or
                rel == "scripts/stage5_v2_audit_bytes.py" or
                rel in ("docs/stage5-contract-v2.md", "docs/stage5-source-spec-v2.md")):
            _require(_same(file_identity(Path(project) / rel), expected),
                     "prepared proof replay code/specification changed: " + rel)


def _expected(project, captured):
    report, report_id = _read_anchor(project)
    _check_replay_code(project, report)
    _require(_same(captured.pin, report["regression"]["pin"]),
             "capture belongs to a different source snapshot")
    # This binds full graph/certificate/result identities to the committed
    # answer without accepting a producer-supplied expected graph hash.
    answer = canonical(expected_answer(captured))
    _require(_same(_bytes_identity(answer), report["answer"]["canonical"]),
             "captured graph/certificate differs from accepted source instance")
    data = {"snapshot.json": canonical(snapshot_payload(captured)),
            "graph.json": canonical(captured.graph),
            "certificate.json": canonical(captured.certificate)}
    files = dict(report["artifacts"])
    files.update({rel: _bytes_identity(raw) for rel, raw in data.items()})
    body = {
        "schema": SCHEMA,
        "anchor": {"project_commit": BASELINE, "report": REPORT,
                   "report_identity": report_id},
        "pin": dict(captured.pin),
        "graph_sha256": files["graph.json"]["sha256"],
        "snapshot_sha256": files["snapshot.json"]["sha256"],
        "source_specification": report["code_at_start"]["docs/stage5-source-spec-v2.md"],
        "source_contract": report["code_at_start"]["docs/stage5-contract-v2.md"],
        "toolchain": "Lean 4.35.0 (Windows x86_64, official pinned SDK)",
        "source_proof": {"reused": True, "fresh_source_compilation": False,
                         "run_nonce": report["run_nonce"],
                         "theorem": "ChromiumSource.source_bound",
                         "modules": list(MODULES),
                         "scope": "SourceBytes byte import projection v2"},
        "files": files,
    }
    body["identity"] = hashlib.sha256(canonical(body)).hexdigest()
    return body, data, report


def _normal_path(path, *, exists):
    """Reject symlinks and Windows reparse points before resolution/IO."""
    path = Path(os.path.abspath(path))
    for item in (path, *path.parents):
        try:
            metadata = item.lstat()
        except FileNotFoundError:
            continue
        reparse = getattr(metadata, "st_file_attributes", 0) & getattr(
            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)
        _require(not stat.S_ISLNK(metadata.st_mode) and not reparse,
                 "proof path uses a link or reparse point: " + str(item))
    if exists:
        _require(path.is_dir(), "proof directory does not exist: " + str(path))
    return path


def _inventory(folder):
    files = set()
    directories = set()
    for current, subdirs, names in os.walk(folder, followlinks=False):
        for name in subdirs + names:
            path = Path(current) / name
            _normal_path(path, exists=False)
            rel = path.relative_to(folder).as_posix()
            if path.is_dir():
                directories.add(rel)
            else:
                _require(path.is_file(), "unexpected non-file proof artifact: " + rel)
                files.add(rel)
    return files, directories


def _verify_files(folder, files, *, manifest):
    actual, directories = _inventory(folder)
    expected = set(files) | ({MANIFEST} if manifest else set())
    _require(actual == expected and directories == {"lean"},
             "prepared proof inventory changed (extra, missing or shadow artifact)")
    for rel, identity in files.items():
        _require(_same(file_identity(folder / rel), identity),
                 "prepared proof bytes changed: " + rel)


def _byte_audit(project, folder, captured):
    script = Path(project) / "scripts/stage5_v2_audit_bytes.py"
    spec = importlib.util.spec_from_file_location("stage6_preserved_byte_audit", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit(folder, captured)


def prepare_cache(project, cache_dir, source_run, *, captured=None):
    """Copy and bind the previously accepted proof; never claim fresh proof.

    A caller-provided capture must be held privately and have been produced by
    anchored_capture; full identities and decoded bytes are checked regardless.
    An incomplete failed preparation has no accepted manifest and is retained
    for diagnosis. Existing paths are never overwritten.
    """
    project = Path(project).resolve()
    folder = _normal_path(cache_dir, exists=False)
    source = _normal_path(source_run, exists=True)
    _require(folder.is_relative_to(project), "prepared directory must be inside project")
    _require(not folder.is_relative_to(source),
             "prepared directory must not modify the accepted source run")
    _require(not folder.exists(), "prepared directory already exists")
    captured = anchored_capture(project) if captured is None else captured
    manifest, data, report = _expected(project, captured)
    source_lean = source / "lean"
    _normal_path(source_lean, exists=True)
    source_files, source_dirs = _inventory(source_lean)
    expected_files = {f"{name}.{ext}" for name in MODULES for ext in ("lean", "olean")}
    _require(source_files == expected_files and not source_dirs,
             "source proof module inventory differs from accepted run")
    for rel, identity in report["artifacts"].items():
        _require(_same(file_identity(source / rel), identity),
                 "source proof differs from committed acceptance: " + rel)
    _normal_path(source / "operational-receipt.json", exists=False)
    receipt = read_json(source / "operational-receipt.json")
    _require(receipt.get("schema") == "stage5-operational-receipt-v2" and
             receipt.get("run_nonce") == report["run_nonce"] and
             receipt.get("seal", {}).get("nonce") == report["run_nonce"],
             "source proof run receipt mismatch")
    expected_compiled = {name: manifest["files"][f"lean/{name}.olean"] for name in MODULES}
    _require(_same(receipt.get("compiled"), expected_compiled),
             "source proof receipt dependencies mismatch")
    # Check original run bytes before copying. Their metadata is not an anchor.
    _byte_audit(project, source, captured)
    folder.mkdir(parents=True)
    (folder / "lean").mkdir()
    for rel in report["artifacts"]:
        with (source / rel).open("rb") as origin, (folder / rel).open("xb") as target:
            shutil.copyfileobj(origin, target)
    for rel, raw in data.items():
        with (folder / rel).open("xb") as target:
            target.write(raw)
    _verify_files(folder, manifest["files"], manifest=False)
    _byte_audit(project, folder, captured)
    with (folder / MANIFEST).open("xb") as target:
        target.write(canonical(manifest))
    return validate_cache(project, folder, captured=captured)


def validate_cache(project, cache_dir, *, captured=None):
    """Revalidate all dependencies against the independent committed anchor.

    Call immediately before and after importing the cache, and before release.
    A stale or attacker-rehashed cache fails. Filesystem/process memory and hash
    collision resistance remain the explicit inherited IO trust assumptions.
    """
    project = Path(project).resolve()
    folder = _normal_path(cache_dir, exists=True)
    captured = anchored_capture(project) if captured is None else captured
    expected, _, _ = _expected(project, captured)
    _verify_files(folder, expected["files"], manifest=True)
    _require((folder / MANIFEST).read_bytes() == canonical(expected),
             "prepared manifest does not match independent source-proof anchor")
    _byte_audit(project, folder, captured)
    return expected
