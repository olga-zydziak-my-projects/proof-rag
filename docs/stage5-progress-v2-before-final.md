# Stage 5 v2 — work in progress

Status: **IN_PROGRESS**, not `STAGE5_PASS`. This is the corrected-pin run.
The original `stage5-results.md` is the preserved historical pin-conflict report.
This file is not a final acceptance report.

Stage 4 checkpoint: `e4984110743131d04ad984eaaa48d33d72867336`.
Authoritative Chromium commit: `27cec857a08a0ee0e1b41f5eb18c07467a0ce093`.
Root tree: `25131300fa459906dedb84bf592a8537b7848771`.
The user-authorized correction is recorded in `stage5-pin-correction-v2.md` and
`stage5-contract-v2.md`. The old contract, blocked report and corpus are retained.

## Evidence obtained so far

- A fresh capture verifies the anchored snapshot and rebuilds the complete
  pinned-parser extraction from those captured bytes. Its complete extraction
  and regenerated certificate equal the accepted baseline, not just its counts.
- All 1864 selected files, 6,946,142 bytes and 28,070 packed proof blocks were
  independently decoded from the generated Lean source and compared byte for
  byte with the anchored capture. Filename and file routing, the complete output
  ID sequence and all 477 output paths were also compared.
- `SourceNames.mapping_checked` has passed kernel checking for every filename.
- The generic source scanner, source/graph correspondence and answer composition
  modules compile. They use only `propext`, `Classical.choice` and `Quot.sound` in
  the recorded axiom audits. This is not an axiom-free result.
- Concrete source groups are being compiled, with independent logs and receipts
  under `local/stage5-v2/full-01`. A completed group does not establish the
  complete corpus theorem. The master instance must also compile successfully.
- Seventeen lexical acceptance/rejection fixtures pass kernel checking, including
  comments, ordinary strings, attributes, duplicate imports, invalid UTF-8,
  unsupported BOM and incomplete delimiters/imports.
- The regression run completed: 81 tests passed. A subsequent metadata alias
  protection change passed the four targeted answer tests, including its new
  regression case. The earlier 81-test run predates that additional case.
- Twenty-three actual-data substitution checks rejected altered inputs or
  answers. This remains partial A–L evidence; these are operational rejections,
  not claims that the kernel verified Git provenance or rejected those attacks.

## Gates still to close

| Gate | Current evidence |
| --- | --- |
| G1 preservation | Baselines retained; final full preservation audit pending. |
| G2 snapshot | Full anchored capture and independent full proof-byte comparison pass. |
| G3 source theorem | Generic theorem and partial concrete groups pass; all groups/master pending. |
| G4 exactness | Generic composition exists; concrete master theorem pending. |
| G5 answer binding | Complete comparison/round-trip implementation and tests exist; release pending proof. |
| G6 attacks/regressions | Regressions pass; A–L operational evidence incomplete. |
| G7 reproduction | Clean complete operational reproduction and deterministic regeneration pending. |
| G8 claim accuracy | No stage success or full-grammar theorem is claimed. Final audit pending. |

The precise formal relation is the byte import projection specified in
`stage5-source-spec-v2.md`, independent of the supplied graph. The full pinned
Mojom parser additionally rejects malformed bodies operationally; its complete
grammar is not proved in Lean. This distinction must remain in the final report.

The measured group runner records process wall time and Windows native peak
working set/process commit separately. Parallel group wall times must not be
added and presented as elapsed whole-pipeline time. No final performance claim
is available yet. No push has been performed.
