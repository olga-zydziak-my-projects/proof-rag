"""Whole-corpus Mojom extraction, source provenance, and explicit coverage.

This is tested implementation, not a verified parser or source-to-graph proof.
All paths are Git identities. No checkout, Windows normalization, or DEPS lookup.
"""
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from time import perf_counter

from . import corpus
from .graph import graph_sha256

CONTRACT = "mojom-import-dependents-v1"
EXTRACTOR_VERSION = "repo-proof-mojom-extractor-v1"


class SourceBindingError(ValueError):
    """An independently expected corpus identity or its metadata did not match."""


@dataclass(frozen=True)
class ExpectedInputs:
    commit: str
    manifest_sha256: str
    root: str
    contract_version: str = CONTRACT

    def validate(self):
        if self.commit != corpus.COMMIT:
            raise SourceBindingError("expected commit differs from the pinned Chromium commit")
        if not isinstance(self.manifest_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", self.manifest_sha256):
            raise SourceBindingError("expected manifest SHA-256 must be 64 lowercase hex digits")
        if self.contract_version != CONTRACT:
            raise SourceBindingError("unsupported independently expected query contract")
        if not isinstance(self.root, str) or not self.root:
            raise SourceBindingError("expected query root must be a nonempty Git path")


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise SourceBindingError(f"duplicate JSON key: {key!r}")
        value[key] = item
    return value


def read_json(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique_object)


def artifact_sha256(value):
    return hashlib.sha256(corpus.encoded(value)).hexdigest()


@dataclass
class Snapshot:
    manifest: dict
    source_entries: list
    metadata_by_path: dict
    source_bytes: dict
    diagnostics: list


def load_snapshot(data_dir, expected):
    """Verify expected identity + full Git metadata, then check EVERY content blob.

Invalid identity/metadata rejects the input. Missing/corrupt content is collected
per file, permitting an honest unresolved artifact with one record for every S.
"""
    expected.validate()
    data_dir = Path(data_dir)
    raw_manifest = (data_dir / "manifest.json").read_bytes()
    if hashlib.sha256(raw_manifest).hexdigest() != expected.manifest_sha256:
        raise SourceBindingError("manifest differs from independently expected SHA-256")
    manifest = json.loads(raw_manifest, object_pairs_hook=unique_object)
    if (manifest.get("format") != "repo-proof-corpus-v1"
            or manifest.get("repository") != corpus.REPOSITORY
            or manifest.get("commit") != expected.commit
            or manifest.get("metadata_complete") is not True
            or manifest.get("selected_content_complete") is not True
            or manifest.get("full_chromium_content_complete") is not False
            or manifest.get("git_object_format") != "sha1"
            or manifest.get("selection") != {"regular_suffix": ".mojom", "references": list(corpus.REFERENCES)}):
        raise SourceBindingError("manifest header/scope differs from pinned corpus contract")
    tree, raw_tree, entries = corpus.read_tree(data_dir / "git")
    if manifest.get("root_tree_object_id") != tree:
        raise SourceBindingError("manifest root tree differs from independently enumerated Git tree")
    if (data_dir / "tree.entries.z").read_bytes() != raw_tree:
        raise SourceBindingError("saved tree listing differs from pinned Git tree")
    rows = manifest.get("entries")
    if not isinstance(rows, list) or len(rows) != len(entries):
        raise SourceBindingError("manifest omits/adds Git tree entries")
    source_entries, by_path, content, diagnostics = [], {}, {}, []
    for entry, row in zip(entries, rows):
        if not isinstance(row, dict) or any(row.get(key) != value for key, value in entry.items()):
            raise SourceBindingError("manifest metadata differs from complete Git enumeration")
        keys = set(entry) | {"availability"}
        if corpus.wanted(entry):
            keys |= {"content_role", "size_bytes", "sha256"}
            role = "mojom" if corpus.selected(entry) else "parser_reference"
            if (row.get("availability") != "materialized" or row.get("content_role") != role
                    or type(row.get("size_bytes")) is not int or row["size_bytes"] < 0
                    or not isinstance(row.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
                raise SourceBindingError("invalid selected content metadata")
            try:
                data = corpus.read_blob(data_dir, row["object_id"])
                if len(data) != row["size_bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                    raise corpus.CorpusError("materialized content size/SHA-256 mismatch")
                if role == "mojom":
                    content[row["path"]] = data
            except (corpus.CorpusError, OSError) as exc:
                diagnostics.append({"path": row["path"], "code": "content_unavailable_or_corrupt",
                                    "message": str(exc).replace(str(data_dir), "<corpus>")})
            if role == "mojom":
                source_entries.append(row)
        else:
            status = {"tree": "metadata_only", "regular": "not_selected",
                      "symlink": "link_not_materialized", "gitlink": "external_not_fetched"}[entry["category"]]
            if row.get("availability") != status:
                raise SourceBindingError("manifest availability differs from declared selection")
        if set(row) != keys:
            raise SourceBindingError("unexpected/missing manifest entry fields")
        by_path[row["path"]] = entry
    if len(source_entries) != sum(map(corpus.selected, entries)):
        raise SourceBindingError("selected source count differs from complete Git enumeration")
    return Snapshot(manifest, source_entries, by_path, content, diagnostics)


def canonical_import_path(literal, decoded):
    """Return (canonical path, reason), preserving case and refusing escapes."""
    if not isinstance(literal, str) or len(literal) < 2 or literal[0] != '"' or literal[-1] != '"':
        return None, "unsupported_import_literal"
    value = literal[1:-1]
    if (not value or "\\" in value or '"' in value or value.startswith("/")
            or any(ord(c) < 32 or ord(c) == 127 for c in value)
            or any(p in ("", ".", "..") for p in value.split("/"))
            or ":" in value.split("/", 1)[0]):
        return None, "noncanonical_or_escaped_import_path"
    if value != decoded:
        return None, "literal_decoding_does_not_preserve_canonical_path"
    return value, None


def outside_reason(path, metadata):
    exact = metadata.get(path)
    if exact:
        return {"gitlink": "gitlink_not_in_scope", "symlink": "symlink_not_in_scope",
                "tree": "directory_not_in_scope", "regular": "regular_file_not_mojom"}[exact["category"]]
    parts = path.split("/")
    for end in range(1, len(parts)):
        ancestor = metadata.get("/".join(parts[:end]))
        if ancestor and ancestor["category"] in ("gitlink", "symlink"):
            return "below_" + ancestor["category"] + "_not_in_scope"
    return "no_tracked_entry_at_exact_case_sensitive_path"


def check_span(data, span):
    if not isinstance(span, dict):
        return False
    start, end = span.get("byte_start"), span.get("byte_end")
    return (type(start) is int and type(end) is int and 0 <= start < end <= len(data)
            and type(span.get("line")) is int and type(span.get("byte_column")) is int
            and span.get("line") == data.count(b"\n", 0, start) + 1
            and span.get("byte_column") == start - data.rfind(b"\n", 0, start))


def valid_import_location(data, item):
    declaration, literal = item.get("declaration_span"), item.get("literal_span")
    keyword = item.get("keyword_span")
    if not all(check_span(data, span) for span in (declaration, keyword, literal)):
        return False
    if not (declaration["byte_start"] <= keyword["byte_start"] < keyword["byte_end"] <= literal["byte_start"]
            < literal["byte_end"] <= declaration["byte_end"]):
        return False
    try:
        if (data[keyword["byte_start"]:keyword["byte_end"]] != b"import"
                or data[literal["byte_start"]:literal["byte_end"]].decode("utf-8") != item["original_literal"]
                or data[declaration["byte_end"] - 1:declaration["byte_end"]] != b";"):
            return False
        attributes = item.get("attributes_literal")
        if attributes is None:
            return declaration["byte_start"] == keyword["byte_start"]
        if not isinstance(attributes, str):
            return False
        attr_bytes = attributes.encode("utf-8")
        attr_end = declaration["byte_start"] + len(attr_bytes)
        return (attr_bytes.startswith(b"[") and attr_bytes.endswith(b"]")
                and attr_end <= keyword["byte_start"]
                and data[declaration["byte_start"]:attr_end] == attr_bytes)
    except (KeyError, UnicodeError):
        return False


def extractor_identity():
    folder = Path(__file__).resolve().parent
    return {"version": EXTRACTOR_VERSION, "source_sha256": {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in ("extraction.py", "corpus.py", "graph.py")}}


def build_extraction(snapshot, expected):
    from .mojom_parser import parse_source, parser_identity

    expected.validate()
    parser = parser_identity()  # validates the pinned runtime before use
    nodes = sorted(e["path"] for e in snapshot.source_entries)
    node_set, edges, records = set(nodes), set(), []
    data_diagnostics = {}
    for item in snapshot.diagnostics:
        data_diagnostics.setdefault(item["path"], []).append(item)
    for entry in snapshot.source_entries:
        path = entry["path"]
        record = {"path": path, "blob_object_id": entry["object_id"],
                  "source_sha256": entry["sha256"], "size_bytes": entry["size_bytes"],
                  "status": "unresolved", "parse_status": "not_parsed", "imports": [],
                  "diagnostics": list(data_diagnostics.get(path, []))}
        data = snapshot.source_bytes.get(path)
        if data is not None:
            parsed = parse_source(data, path)
            record["parse_status"] = parsed["status"]
            record["diagnostics"].extend(parsed["diagnostics"])
            for original in parsed["imports"]:
                item = dict(original, importer=path, importer_blob_object_id=entry["object_id"])
                resolved, reason = canonical_import_path(item.get("original_literal"), item.get("decoded_path"))
                item["resolved_path"] = resolved
                if not valid_import_location(data, item):
                    item.update(status="unresolved", reason="invalid_original_byte_location")
                elif parsed["status"] != "parsed":
                    item.update(status="unresolved", reason="enclosing_source_not_fully_validated")
                elif reason:
                    item.update(status="unresolved", reason=reason)
                elif resolved in node_set:
                    item.update(status="internal", reason="exact_tracked_regular_mojom_path")
                    edges.add((path, resolved))
                else:
                    item.update(status="outside_scope", reason=outside_reason(resolved, snapshot.metadata_by_path))
                if item["status"] == "unresolved":
                    record["diagnostics"].append({"code": item["reason"],
                                                 "literal_span": item.get("literal_span")})
                record["imports"].append(item)
            if parsed["status"] == "parsed" and not record["diagnostics"]:
                record["status"] = "resolved"
        records.append(record)
    records.sort(key=lambda r: r["path"])
    graph = {"nodes": nodes, "edges": [list(e) for e in sorted(edges)]}
    statuses = Counter(i["status"] for r in records for i in r["imports"])
    file_statuses = Counter(r["status"] for r in records)
    complete = not snapshot.diagnostics and file_statuses.get("unresolved", 0) == 0
    return {
        "format": "repo-proof-mojom-extraction-v1",
        "binding": {"repository": corpus.REPOSITORY, "commit": expected.commit,
                    "manifest_sha256": expected.manifest_sha256,
                    "root_tree_object_id": snapshot.manifest["root_tree_object_id"],
                    "contract_version": expected.contract_version,
                    "extractor": extractor_identity(), "parser": parser},
        "extraction_status": "complete" if complete else "unresolved",
        "corpus_status": "verified" if not snapshot.diagnostics else "unresolved",
        "graph_scope": "all_S_nodes; internal declarations from fully parsed sources only",
        "graph_sha256": graph_sha256(graph), "graph": graph, "files": records,
        "corpus_diagnostics": snapshot.diagnostics,
        "coverage": {
            "source_files": len(nodes), "verified_source_files": len(snapshot.source_bytes),
            "fully_parsed_files": sum(r["parse_status"] == "parsed" for r in records),
            "file_statuses": {s: file_statuses.get(s, 0) for s in ("resolved", "unresolved")},
            "declarations": sum(statuses.values()),
            "declaration_statuses": {s: statuses.get(s, 0) for s in ("internal", "outside_scope", "unresolved")},
            "unique_edges": len(edges),
            "duplicate_internal_declarations": statuses.get("internal", 0) - len(edges),
            "diagnostics": sum(len(r["diagnostics"]) for r in records) + sum(
                item["path"] not in node_set for item in snapshot.diagnostics),
            "all_S_have_terminal_status": len(records) == len(nodes),
            "source_complete": complete,
        },
    }


def extract_corpus(data_dir, expected):
    start = perf_counter()
    snapshot = load_snapshot(data_dir, expected)
    checked = perf_counter()
    artifact = build_extraction(snapshot, expected)
    finished = perf_counter()
    return artifact, {"corpus_verification_seconds": checked - start,
                      "parse_and_graph_seconds": finished - checked}
