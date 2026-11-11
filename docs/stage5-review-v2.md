# Independent Stage 5 v2 review

Review scope: the byte source relation, source-to-graph proof, answer composition,
complete-corpus export and external byte/answer audit. This review does not itself
grant STAGE5_PASS; the operational gates must pass in the final clean run.

## Formal composition

The reviewed generic composition is sound at its stated scope. `sourceImport`
quantifies a `Trace` from the initial scanner state over the actual byte list;
its definition does not mention exported graph edges, certificates, or Python
extraction results. `checked_sound` composes independently checked byte blocks.
`import_iff_events` establishes equivalence with all emitted events. The file
checker checks complete ordered event coverage, both resolution directions and
both target-list directions. The filename left inverse proves injectivity.
`source_edge_iff` therefore establishes both directions of correspondence with
the graph. `source_exact` reverses the edge relation in the correct argument
order and composes the existing exact reachability theorem. The answer checker
requires every vertex's membership to agree, a duplicate-free ID list and exact
decoding of that list. `source_to_answer` and `answer_nodup` preserve those facts.

No new extraction-correctness premise was found in the generic composition.
The premises are explicit executable checks and must be discharged by the
concrete instance. Standard `propext`, `Classical.choice`, and `Quot.sound`
remain permitted; the result is not axiom-free.

## Scope of source semantics

The formal relation is the explicitly declared byte import projection, not the
full Mojom grammar or type checker. It handles comments, literal boundaries,
escapes, balanced delimiters, header import placement, attributes, strict UTF-8,
canonical paths, repeated declarations and exact selected-path resolution.
Conditional attributes do not filter imports. These choices preserve the frozen
query's import direction, repository-root resolution and root inclusion.

The projection intentionally does not enforce the entire body/module grammar.
Consequently `finish = true` alone must never be reported as a full Mojom parse.
The pinned full parser must remain a mandatory operational rejection layer for
malformed/unsupported files. This restriction is expressly documented; the
concrete corpus also requires full per-file ordered event agreement with the
pinned parser. Such agreement is instance evidence, not a general formal proof
that the full Chromium parser implements the byte projection.

## Complete instance evidence independently inspected

The completed exploratory run records `SOURCE_INSTANCE_KERNEL_PASS`, not a
stage-wide pass. It contains 30 source groups, 1864 file proofs exactly once,
6,946,142 original source bytes and 28,070 blocks. The master and measured group
zero both exited zero, with unchanged source hashes before and after compilation.
The master axiom report contains only the three permitted standard axioms.

The reviewer independently reran the full anchored byte audit, including filename
and file routing and the complete concrete output ID/path sequences. It passed;
the raw result is `local/stage5-v2/full-01/independent-review-byte-audit.json`.
This is an IO/provenance check, not a theorem about Git or SHA implementations.

## Findings and acceptance conditions

1. The earlier snapshot equality check used Python structural equality, which
   identifies booleans with integers. The reviewer requested canonical typed JSON
   comparison. The current implementation uses canonical comparison; a direct
   false-ID substitution was independently checked and rejected after that fix.
   Numeric certificate and other metadata boundaries need the same strictness.
2. The old exploratory finishing script accepts earlier group receipts without
   binding their complete source/dependency identities and does not reread the
   written answer JSON. It must not serve as the final acceptance runner. A clean
   run must compile all instance groups freshly, bind its actual dependencies,
   audit persisted inputs at use, and reread both actual answer artifacts.
3. The byte auditor supports use before master generation, so master audit is
   optional inside that helper. The final gate must separately require the master
   instance, its successful fresh compilation and its axiom audit.
4. A complete A-L attack suite, deterministic full-byte regeneration, final
   regression run and preservation audit remain operational obligations. No
   previous exploratory result or mere `.olean` existence discharges them.

## Clean runner follow-up

The final `check_stage5_v2.py` was reviewed after the exploratory findings. It
copies and freshly compiles all eight project dependency modules, the filename
mapping, all 30 source groups and the master in a run-only Lean search path.
The old finishing script is not its acceptance path. It seals persisted inputs
against a private expected run identity, checks imported compiled objects at
consumption boundaries, requires the master, rereads actual canonical and human
answer files, compares regenerated artifacts by their full bytes, runs all A-L
attacks and the final regression suite, and checks preservation and review hashes
before the mechanical gate assessment. The embedded human binding JSON now
rejects duplicate metadata keys. Actual physical cross-run seal substitution is
included in the attack suite. Source-ID booleans are rejected by strict canonical
comparison.

The independent code review therefore passes. The machine-readable review is
`verification/stage5-v2-review.json`; its file identities describe the reviewed
code, rather than an execution result. It is deliberately not a stage acceptance
receipt. Main proof compilation uses only the precompiled Lean SDK; the preserved
differential regression additionally imports baseline caches and uses VM execution
as test evidence, never as a proof shortcut.

No additional logical flaw was found in the reviewed formal composition. Final
stage acceptance still requires the clean runner to finish successfully and all
original G1-G8 gates to pass without weakening the stated guarantee.

## Final reviewed revision

The initial completed machine review is retained. A second review of the final
revision is recorded in `verification/stage5-v2-review-final.json`. The additions
separate provenance, pinned-parser extraction, and baseline/certificate timings;
those measurements remain outside deterministic payloads. The runner records
project source identities at startup, requires the reviewed identities to match
that startup state, and rechecks every recorded source before acceptance. Its
sealed private run inventory additionally rejects missing or added run inputs.
The new ambiguous human-binding regression passes. No new formal premise or
proof shortcut is introduced by these changes. This revision review remains a
code/specification review; the final execution must independently pass its gates.
