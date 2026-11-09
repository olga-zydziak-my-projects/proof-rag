"""Run reproducible checks and record the actual boundary of verification."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", default="lean", help="Lean 4.35.0 executable")
    parser.add_argument("--report", default="verification/latest.json")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(project / "src"))
    checks = []
    jobs = [
        ("python_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("lean_version", [args.lean, "--version"]),
        ("lean_theorems", [args.lean, "formal/Reachability.lean"]),
        ("tampering_demo", [sys.executable, "-m", "repo_proof", "demo", "--graph",
                            "examples/graph.json", "--root", "core"]),
    ]
    for name, command in jobs:
        try:
            run = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", timeout=120)
            passed = run.returncode == 0
            if name == "lean_version":
                passed = passed and "version 4.35.0," in run.stdout
            if name == "lean_theorems":
                expected = ("complete", "exact_reachability", "soundness_from_ranked_witnesses",
                            "ranked_exact_reachability", "reachability_has_certificate", "exact_dependents")
                passed = passed and all(
                    f"'RepoProof.{theorem}' does not depend on any axioms" in run.stdout
                    for theorem in expected)
            checks.append({"name": name, "passed": passed, "exit_code": run.returncode,
                           "stdout": run.stdout, "stderr": run.stderr})
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"name": name, "passed": False, "error": str(exc)})
    files = [p for folder in ("src", "tests", "formal", "scripts")
             for p in (project / folder).rglob("*") if p.suffix in (".py", ".lean")]
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "all_checks_passed": all(c["passed"] for c in checks),
        "scope": "Mathematical graph-certificate theorem checked in Lean; Python tested separately.",
        "not_proven": ["Python refinement to Lean theorem", "Mojom extraction correctness",
                       "Formal correctness of Git enumeration and corpus manifest implementation",
                       "large-corpus query performance"],
        "source_sha256": {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(files)},
        "checks": checks,
    }
    destination = project / args.report
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_passed": report["all_checks_passed"],
                      "checks": [{"name": c["name"], "passed": c["passed"]} for c in checks],
                      "report": str(destination)}, indent=2))
    return 0 if report["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
