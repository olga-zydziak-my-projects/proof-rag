"""Full-file pinned Chromium parser, with original UTF-8 source coordinates.

The upstream grammar is unmodified. Its Import AST normalizes paths, so its
import_filename is deliberately NOT used for resolution. We retain and decode
the original STRING_LITERAL token. This adapter and upstream parser are tested,
not formally verified. PLY's shared parser is serialized by a process lock.
"""
import ast as python_ast
from functools import lru_cache
import hashlib
import importlib
import json
from pathlib import Path
import sys
import threading

PROJECT = Path(__file__).resolve().parents[2]
VENDOR = PROJECT / "vendor" / "chromium"
LOCK_PATH = PROJECT / "vendor" / "mojom-parser.lock.json"
UPSTREAM_COMMIT = "27cec857a08a0ee0e1b41f5eb18c07467a0ce093"
LOCK_SHA256 = "fa01aa9d679d877088dc66865c02ff45eea62fcaf940aa254949cd3e3cee8e54"
ADAPTER_VERSION = "repo-proof-mojom-adapter-v1"
_PARSER_LOCK = threading.RLock()


class ParserRuntimeError(ValueError):
    """The expected checked-in parser runtime cannot be used."""


def _vendor_lock():
    raw = LOCK_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LOCK_SHA256:
        raise ParserRuntimeError("vendored parser lock identity mismatch")
    lock = json.loads(raw)
    if lock["commit"] != UPSTREAM_COMMIT or lock["ply_version"] != "3.11":
        raise ParserRuntimeError("vendored parser version mismatch")
    for item in lock["entries"]:
        data = (VENDOR / item["path"]).read_bytes()
        oid = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if len(data) != item["size_bytes"] or oid != item["object_id"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ParserRuntimeError("vendored parser content mismatch: " + item["path"])
    return lock


def parser_identity():
    """Validate upstream sources and identify the adapter actually used."""
    lock = _vendor_lock()
    return {"name": "Chromium Mojom Parse", "upstream_commit": UPSTREAM_COMMIT,
            "ply_version": lock["ply_version"], "adapter_version": ADAPTER_VERSION,
            "vendor_lock_sha256": LOCK_SHA256,
            "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "upstream_files": len(lock["entries"])}


def _check_module_origins():
    for name, module in tuple(sys.modules.items()):
        if name == "mojom" or name.startswith("mojom.") or name == "ply" or name.startswith("ply."):
            origin = getattr(module, "__file__", None)
            if origin is None or VENDOR.resolve() not in Path(origin).resolve().parents:
                raise ParserRuntimeError("foreign module shadows pinned runtime: " + name)


@lru_cache(maxsize=1)
def _runtime():
    _vendor_lock()
    _check_module_origins()
    location = str(VENDOR / "mojo" / "public" / "tools" / "mojom")
    if location not in sys.path:
        sys.path.insert(0, location)
    upstream = importlib.import_module("mojom.parse.parser")
    _check_module_origins()
    return upstream


def _byte_span(data, start, end):
    if not (0 <= start <= end <= len(data)):
        raise ParserRuntimeError("source span outside original bytes")
    previous_newline = data.rfind(b"\n", 0, start)
    return {"byte_start": start, "byte_end": end,
            "line": data.count(b"\n", 0, start) + 1,
            "byte_column": start - previous_newline}


def _offsets(source):
    result = [0]
    for char in source:
        result.append(result[-1] + len(char.encode("utf-8")))
    return result


def _diagnostic(exc, code):
    diagnostic = {"code": code, "message": str(exc)}
    if getattr(exc, "lineno", None) is not None:
        diagnostic["line"] = exc.lineno
    return diagnostic


def _header_imports(tokens):
    """Complete lexical header imports only; not a replacement for Parse."""
    imports = []
    depth = 0
    header_open = True
    attribute_start = None
    attribute_end = None
    for index, token in enumerate(tokens):
        if depth == 0 and token.type in ("STRUCT", "UNION", "INTERFACE", "ENUM", "CONST", "FEATURE"):
            header_open = False
        if token.type == "LBRACKET" and depth == 0:
            attribute_start = token.lexpos
        if token.type in ("LBRACKET", "LBRACE", "LPAREN"):
            depth += 1
        elif token.type in ("RBRACKET", "RBRACE", "RPAREN"):
            depth -= 1
            if depth == 0 and token.type == "RBRACKET":
                attribute_end = token.lexpos + len(token.value)
        if token.type == "IMPORT" and depth == 0 and header_open and index + 2 < len(tokens):
            literal, semicolon = tokens[index + 1:index + 3]
            if literal.type == "STRING_LITERAL" and semicolon.type == "SEMI":
                imports.append((token, literal, semicolon, attribute_start, attribute_end))
        if token.type == "SEMI" and depth == 0:
            attribute_start = None
            attribute_end = None
    return imports


def _record_import(data, source, offsets, item, status):
    keyword, literal, semicolon, attr_start, attr_end = item
    statement_start = keyword.lexpos
    statement_end = semicolon.lexpos + len(semicolon.value)
    declaration_start = attr_start if attr_start is not None else statement_start
    literal_end = literal.lexpos + len(literal.value)
    decoded = python_ast.literal_eval(literal.value)
    if not isinstance(decoded, str):
        raise ParserRuntimeError("import token did not decode to a string")
    record = {
        "original_literal": literal.value, "decoded_path": decoded,
        "declaration_span": _byte_span(data, offsets[declaration_start], offsets[statement_end]),
        "keyword_span": _byte_span(data, offsets[statement_start], offsets[statement_start + len(keyword.value)]),
        "literal_span": _byte_span(data, offsets[literal.lexpos], offsets[literal_end]),
        "attributes_literal": source[attr_start:attr_end] if attr_start is not None else None,
        "source_status": status,
        "declaration_validation": "whole_file_parser" if status == "parsed" else "lexical_prefix_only",
    }
    span = record["literal_span"]
    if data[span["byte_start"]:span["byte_end"]] != literal.value.encode("utf-8"):
        raise ParserRuntimeError("original literal span does not match source bytes")
    return record


def parse_source(data, filename):
    """Return status/imports/diagnostics after lexing and parsing the whole file.

    Parsed files carry exact upstream import grammar and byte spans. Failed
    files may retain complete lexical header imports marked lexical_prefix_only;
    their presence never establishes source completeness. No conditions are
    evaluated and no import paths are normalized by this adapter.
    """
    diagnostics = []
    if not isinstance(data, bytes):
        raise TypeError("parse_source requires original bytes")
    try:
        source = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return {"status": "unresolved", "imports": [], "diagnostics": [
            {"code": "invalid_utf8", "message": str(exc),
             "span": _byte_span(data, exc.start, exc.end)}]}
    if source.startswith("\ufeff"):
        return {"status": "unresolved", "imports": [], "diagnostics": [
            {"code": "unsupported_bom", "message": "UTF-8 BOM is outside the contract",
             "span": _byte_span(data, 0, 3)}]}
    offsets = _offsets(source)
    try:
        with _PARSER_LOCK:
            upstream = _runtime()
            _check_module_origins()
            lexer, lex_obj, _, _ = upstream._GetCachedParser()
            lexer.filename = filename
            lexer.line_comments = []
            lexer.suffix_comments = []
            lex_obj.lineno = 1
            lex_obj.begin("INITIAL")
            lex_obj.lexstatestack = []
            lex_obj.input(source)
            tokens = []
            try:
                while True:
                    token = lex_obj.token()
                    if token is None:
                        break
                    tokens.append(token)
            except Exception as exc:
                diagnostics.append(_diagnostic(exc, "lexical_error"))
            tree = None
            try:
                tree = upstream.Parse(source, filename)
            except Exception as exc:
                diagnostic = _diagnostic(exc, "whole_file_parse_error")
                if not any(d["message"] == diagnostic["message"] for d in diagnostics):
                    diagnostics.append(diagnostic)
            status = "unresolved" if diagnostics else "parsed"
            lexical_imports = _header_imports(tokens)
            if status == "parsed":
                parsed_positions = [node.start.lexpos for node in tree.import_list]
                lexical_positions = [item[0].lexpos for item in lexical_imports]
                if parsed_positions != lexical_positions:
                    raise ParserRuntimeError("AST import positions disagree with original tokens")
            imports = []
            for item in lexical_imports:
                try:
                    imports.append(_record_import(data, source, offsets, item, status))
                except (SyntaxError, ValueError) as exc:
                    diagnostics.append(_diagnostic(exc, "import_literal_or_location_error"))
            if diagnostics:
                status = "unresolved"
                for item in imports:
                    item["source_status"] = "unresolved"
                    item["declaration_validation"] = "lexical_prefix_only"
            return {"status": status, "imports": imports, "diagnostics": diagnostics}
    except (OSError, ValueError, ImportError) as exc:
        return {"status": "unresolved", "imports": [], "diagnostics": [
            _diagnostic(exc, "parser_runtime_error")]}
