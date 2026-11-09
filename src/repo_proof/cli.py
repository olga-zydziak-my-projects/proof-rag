"""Local CLI; certificate checking is graph-relative, not source verification."""
import argparse
import copy
import json
from pathlib import Path
import sys
from time import perf_counter

from . import ValidationError, generate_certificate, verify_certificate


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError([f"duplicate JSON key: {key!r}"])
        result[key] = value
    return result


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_object)


def _emit(value, path=None):
    encoded = json.dumps(value, indent=2, ensure_ascii=True) + "\n"
    if path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


def demo(graph, root):
    start = perf_counter()
    certificate = generate_certificate(graph, root)
    generated = perf_counter()
    verify_certificate(graph, root, certificate)
    checked = perf_counter()
    included = {item["node"] for item in certificate["candidates"]}
    removable = sorted(included - {root})
    extra = sorted(set(graph["nodes"]) - included)
    if not removable or not extra:
        raise ValidationError(["demo requires a non-root result and an unreachable node"])
    omissions = copy.deepcopy(certificate)
    omissions["candidates"] = [item for item in omissions["candidates"]
                               if item["node"] != removable[0]]
    addition = copy.deepcopy(certificate)
    addition["candidates"].append({"node": extra[0], "parent": root, "rank": 1})
    cases = []
    for name, altered in [("omitted_result", omissions), ("spurious_result", addition)]:
        try:
            verify_certificate(graph, root, altered)
        except ValidationError as exc:
            cases.append({"case": name, "rejected": True, "errors": exc.errors})
        else:
            raise RuntimeError(f"checker accepted tampered certificate: {name}")
    return {
        "scope": "supplied_graph_only",
        "query": certificate["query"],
        "graph_sha256": certificate["graph_sha256"],
        "result": sorted(included),
        "original_certificate_accepted": True,
        "tampering": cases,
        "timings_ms": {"generate": (generated-start)*1000,
                       "verify": (checked-generated)*1000},
        "limitations": ["Python checker is tested, not formally verified.",
                        "No claim about Chromium source extraction or corpus completeness."]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("query", "verify", "demo"):
        sub = commands.add_parser(command)
        sub.add_argument("--graph", required=True)
        sub.add_argument("--root", required=True)
        if command == "verify":
            sub.add_argument("--certificate", required=True)
        else:
            sub.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        graph = _read(args.graph)
        if args.command == "query":
            certificate = generate_certificate(graph, args.root)
            verify_certificate(graph, args.root, certificate)
            _emit(certificate, args.out)
        elif args.command == "verify":
            verify_certificate(graph, args.root, _read(args.certificate))
            _emit({"status": "accepted", "scope": "supplied_graph_only"})
        else:
            _emit(demo(graph, args.root), args.out)
        return 0
    except (ValidationError, OSError, ValueError) as exc:
        print(json.dumps({"status": "rejected", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
