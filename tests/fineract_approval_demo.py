"""Run and grade the same live Claude question across an isolated local Fineract push."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from fineract_r2 import PROJECT, strict_json, write_json
from fineract_r2_current import R2, git, manifest_for
from prepare_r2_corpus import prepare
from run_r2_freshness_experiment import bare
from test_fineract_r2_ask import check_version, overlap_push, run_scripted


QUESTION = "Klient złożył wniosek 12 maja. Czy według reguły daty można go zatwierdzić również 12 maja?"
REPO = "fineract"
BASE = "main"
PR = "local-approval-after"
LOANS = "fineract-provider/src/main/java/org/apache/fineract/portfolio/loanaccount/"
VALIDATOR = LOANS + "serialization/LoanApplicationValidator.java"
SERVICE = LOANS + "service/LoanApplicationWritePlatformServiceJpaRepositoryImpl.java"
DATE_UTILS = "fineract-core/src/main/java/org/apache/fineract/infrastructure/core/service/DateUtils.java"
BEFORE = "DateUtils.isBefore(approvedOnDate, loan.getSubmittedOnDate())"
AFTER = "!DateUtils.isAfter(approvedOnDate, loan.getSubmittedOnDate())"
CALL = "loanApplicationValidator.validateApproval(command, loanId);"
MUTATION = "loanScheduleAssembler.assembleLoanApproval("
THROW = 'throw new InvalidLoanStateTransitionException("approval"'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def lines_at(store, commit, path):
    return git(store, "show", f"{commit}:{path}").decode("utf-8").splitlines()


def at_line(lines, marker):
    matches = [number for number, line in enumerate(lines, 1) if marker in line]
    require(len(matches) == 1, f"Missing or non-unique Git marker: {marker}")
    return matches[0]


def oracle(store, commit, *, local_change):
    validator = lines_at(store, commit, VALIDATOR)
    service = lines_at(store, commit, SERVICE)
    date_utils = lines_at(store, commit, DATE_UTILS)
    for method in ("Before", "After"):
        definition = at_line(date_utils, f"boolean is{method}(LocalDate first, LocalDate second)")
        require(f"first.is{method}(second)" in date_utils[definition],
                "DateUtils LocalDate comparison changed")
    condition = at_line(validator, AFTER if local_change else BEFORE)
    require(not any((BEFORE if local_change else AFTER) in line for line in validator), "Unexpected second date rule")
    exception = next(number for number in range(condition + 1, condition + 8) if THROW in validator[number - 1])
    call, mutation = at_line(service, CALL), at_line(service, MUTATION)
    require(call < mutation, "Validation must precede approval")
    return {"commit": commit, "local_test_change": local_change, "verdict": "no" if local_change else "yes",
            "rule": {"path": VALIDATOR, "start": condition, "end": exception,
                     "source": validator[condition - 1:exception]},
            "call": {"path": SERVICE, "start": call, "end": mutation, "source": service[call - 1:mutation]}}


def grade(store, report, expected):
    response = report.get("stdout_json") or {}
    checks = {"citations": "REJECTED", "business_conclusion": "NOT_CHECKED", "status": "FAIL"}
    try:
        require(report["exit_code"] == 0 and response["status"] == "VERIFIED", "CLI did not verify an answer")
        [repo] = response["view"]["repositories"]
        commit = expected["commit"]
        require(repo["commit"] == commit and repo["branch"] == expected["branch"]
                and response["view"]["kind"] == expected["view"], "Unexpected version")
        require(response["checks"]["citations"] == "VERIFIED", "CLI did not verify citations")
        checks["citations"] = "VERIFIED"
        correct = response["verdict"] == expected["verdict"]
        checks["business_conclusion"] = "CORRECT" if correct else "INCORRECT"
        require(correct, "Claude's business verdict differs from Git")
        independent = []
        for cite in response["citations"]:
            require(cite["commit"] == commit and cite["manifest_sha256"] == response["manifest_sha256"],
                    "Citation version differs")
            path, start, end = (cite[field] for field in ("path", "start", "end"))
            lines = lines_at(store, commit, path)
            require(1 <= start <= end <= len(lines) and cite["quote"].strip() in "\n".join(lines[start - 1:end]),
                    "Citation text differs in independent Git read")
            independent.append((path, start, end))
        for label in ("rule", "call"):
            proof = expected[label]
            for line, source_line in enumerate(proof["source"], proof["start"]):
                if not source_line.strip():
                    continue
                require(any(path == proof["path"] and start <= line <= end for path, start, end in independent),
                        f"Missing {label} evidence for line {line}")
        require(len(response["searches"]) >= 2 and len(response["reads"]) >= 2, "Incomplete code discovery")
        run = Path(response["run_directory"])
        require(sha256((run / "manifest.json").read_bytes()).hexdigest() == response["manifest_sha256"],
                "Saved manifest digest differs")
        for search in response["searches"]:
            require(search["status"] == "VERIFIED" and search["manifest_sha256"] == response["manifest_sha256"],
                    "Search verification differs")
            answer = Path(search["output_directory"]) / "answer.jsonl"
            require(sha256(answer.read_bytes()).hexdigest() == search["result_sha256"], "R2 result digest differs")
            require(all(row["commit"] == commit for line in answer.read_bytes().splitlines()
                        if (row := strict_json(line))["type"] in ("result", "hit")), "R2 search mixed commits")
        require(all(read["commit"] == commit and read["manifest_sha256"] == response["manifest_sha256"]
                    for read in response["reads"]), "Git reads mixed commits")
        return {**checks, "status": "PASS", "prose_review_required": True}
    except (KeyError, OSError, ValueError) as exc:
        return {**checks, "reason": str(exc)}


def measure(root, raw, source):
    os.environ["GIT_ALLOW_PROTOCOL"] = "file"
    os.environ["GIT_NO_LAZY_FETCH"] = "1"
    git_config = int(os.environ.get("GIT_CONFIG_COUNT", 0))
    os.environ[f"GIT_CONFIG_KEY_{git_config}"] = "safe.directory"
    os.environ[f"GIT_CONFIG_VALUE_{git_config}"] = source.as_posix()
    os.environ["GIT_CONFIG_COUNT"] = str(git_config + 1)
    os.environ.pop("REPO_PROOF_CURRENT_CONFIG", None)
    report = {"question": QUESTION, "work_directory": str(root), "attempts": [], "git_checks": {}}
    root.mkdir(parents=True)

    def save():
        temporary = raw.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(raw)

    def run(label, script, *args, data=None):
        command = [sys.executable, "-B", "-X", "utf8", str(script), *map(str, args)]
        started = perf_counter()
        try:
            proc = subprocess.run(command, input=data, capture_output=True, cwd=PROJECT, timeout=600)
        except (OSError, subprocess.SubprocessError) as exc:
            report["attempts"].append({"id": label, "argv": command, "wall_seconds": perf_counter() - started,
                                       "execution_error": type(exc).__name__})
            save()
            raise
        record = {"id": label, "argv": command, "exit_code": proc.returncode,
                  "wall_seconds": perf_counter() - started,
                  "stdout": proc.stdout.decode("utf-8", "replace"), "stderr": proc.stderr.decode("utf-8", "replace")}
        try:
            record["stdout_json"] = strict_json(proc.stdout)
            del record["stdout"]
        except ValueError:
            pass
        report["attempts"].append(record)
        save()
        return record

    try:
        a = git(source, "rev-parse", "refs/fineract-r1/pin^{commit}").decode("ascii").strip()
        server = root / "s" / f"{REPO}.git"
        bare(server)
        git(server, "fetch", "--quiet", "--depth=1", "--no-tags", source.as_uri(), f"{a}:refs/heads/{BASE}")
        git(server, "update-ref", f"refs/heads/{PR}", a)
        git(server, "config", "receive.denyNonFastForwards", "true")
        snapshot_a = oracle(server, a, local_change=False)
        report["git_checks"]["A"] = snapshot_a

        spec = {"id": REPO, "repository": "apache/fineract", "url": "https://github.com/apache/fineract.git",
                "remote": server.as_uri(), "branch": BASE, "directories": []}
        tree = git(server, "rev-parse", a + "^{tree}").decode("ascii").strip()
        entry, _ = prepare({**spec, "commit": a, "root_tree": tree}, server.parent, False)
        manifest, index, checked = (root / name for name in ("base.json", "i", "checked"))
        write_json(manifest, manifest_for([entry]))
        build = run("build-baseline", R2, "build", "--sources", server.parent, "--manifest", manifest,
                    "--index", index, "--log-dir", root / "build-log")
        require(build["exit_code"] == 0, "Baseline path index failed")
        verified = run("check-baseline", PROJECT / "scripts/prepare_checked_r2_index.py",
                       "--sources", server.parent, "--manifest", manifest, "--index", index, "--output", checked)
        require(verified["exit_code"] == 0, "Checked baseline failed")
        config = root / "config.json"
        write_json(config, {"corpora": {"default": {
            "repositories": [spec], "workspace": "base", "pr_directory": "pr", "seed_index": "i",
            "checked_index": {"directory": "checked", "receipt_sha256": verified["stdout_json"]["receipt_sha256"]},
        }}})
        event = PROJECT / "scripts/fineract_r2_pr.py"
        ask = PROJECT / "scripts/fineract_r2_ask.py"
        opened = {"action": "opened", "number": 1, "repository": REPO, "base": BASE, "head": PR}
        registration = run("opened", event, "event", "--config", config, data=json.dumps(opened).encode("ascii"))
        require(registration["exit_code"] == 0 and registration["stdout_json"]["refresh"]["status"] == "READY",
                "Opened PR did not prepare its index")

        def question(label, expected, *, pr=False):
            args = ("--repo", REPO, "--pr", "1") if pr else ()
            attempt = run(label, ask, "ask", "--config", config, *args, QUESTION)
            attempt["grade"] = grade(server, attempt, {**expected, "branch": PR if pr else BASE,
                                                       "view": "pull_request" if pr else "branch"})
            save()
            print(label, attempt["exit_code"], attempt["grade"], flush=True)
            return attempt["grade"]["status"] == "PASS"

        before = question("pr-before-push", snapshot_a, pr=True)
        author = root / "w.git"
        bare(author)
        git(author, "fetch", "--quiet", "--depth=1", "--no-tags", server.as_uri(), f"refs/heads/{PR}")
        git(author, "read-tree", a)
        original = git(author, "show", f"{a}:{VALIDATOR}")
        require(original.count(BEFORE.encode()) == 1, "Cannot edit the rule safely")
        changed = original.replace(BEFORE.encode(), AFTER.encode())
        changed = changed.replace(b" can not be before its submittal date: ", b" must be after its submittal date: ")
        changed = changed.replace(b"cannot.be.before.submittal.date", b"must.be.after.submittal.date")
        anchor = b"            if (approvedOnDate != null && " + AFTER.encode()
        changed = changed.replace(anchor, b"            // Local test rule: require a later approval date.\n\n" + anchor)
        oid = git(author, "hash-object", "-w", "--stdin", data=changed).decode("ascii").strip()
        git(author, "update-index", "--cacheinfo", "100644", oid, VALIDATOR)
        tree = git(author, "write-tree").decode("ascii").strip()
        b = git(author, "-c", "user.name=Repo Proof Lab", "-c", "user.email=lab@example.invalid",
                "commit-tree", tree, "-p", a, "-m", "Local QA only: require approval after submission"
                ).decode("ascii").strip()
        git(author, "update-ref", f"refs/heads/{PR}", b)

        def push_local_change():
            git(author, "push", server.as_uri(), f"refs/heads/{PR}:refs/heads/{PR}")

        controlled_a = overlap_push(config, os.environ, push_local_change)
        report["controlled_race"] = {"paused_question": controlled_a}
        save()
        check_version(controlled_a, a, "yes")
        require(git(server, "rev-parse", f"refs/heads/{PR}").strip() == b.encode()
                and git(server, "rev-parse", f"refs/heads/{BASE}").strip() == a.encode(), "Wrong branches after local push")
        changed_paths = git(server, "diff", "--name-only", a, b).decode("utf-8").splitlines()
        require(changed_paths == [VALIDATOR], "Unexpected changes in the local experiment")
        snapshot_b = oracle(server, b, local_change=True)
        require(snapshot_b["rule"]["start"] != snapshot_a["rule"]["start"], "Rule lines did not move")
        report["git_checks"]["B"] = snapshot_b
        report["git_checks"]["changed_paths"] = changed_paths
        save()

        after = question("pr-after-push-before-synchronize", snapshot_b, pr=True)
        controlled_b = run_scripted(config, os.environ)
        report["controlled_race"]["next_question"] = controlled_b
        save()
        check_version(controlled_b, b, "no")
        report["controlled_race"]["status"] = "PASS"
        sync = {"action": "synchronize", "number": 1}
        refreshed = run("synchronize", event, "event", "--config", config, data=json.dumps(sync).encode("ascii"))
        require(refreshed["exit_code"] == 0 and refreshed["stdout_json"]["status"] == "READY",
                "Synchronize did not publish the PR index")
        base = question("base-after-push", snapshot_a)
        [fallback] = [row for row in report["attempts"] if row["id"] == "pr-after-push-before-synchronize"]
        searches = fallback.get("stdout_json", {}).get("searches") or []
        report["fallback_exercised"] = bool(searches) and all(row["operation"] == "query-verified" for row in searches)
        report["status"] = "PASS" if before and after and base and report["fallback_exercised"] else "FAIL"
    except Exception as exc:
        report["status"] = "FAIL"
        report["execution_error"] = {"kind": type(exc).__name__, "detail": str(exc)}
    finally:
        save()
    return report["status"] == "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=PROJECT / "local/fineract-r1/source.git")
    args = parser.parse_args()
    if args.measurements.exists():
        parser.error("use a new measurements file for each attempt")
    return 0 if measure(args.work_dir.resolve(), args.measurements.resolve(), args.source.resolve(strict=True)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
