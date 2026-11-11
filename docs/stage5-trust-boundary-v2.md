# Stage 5 v2 — current trust boundary

The corrected source identity is Chromium commit
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`, tree
`25131300fa459906dedb84bf592a8537b7848771`, anchored in `corpus.lock.json`
from project checkpoint `e4984110743131d04ad984eaaa48d33d72867336`.
The historical v1 conflict report and its boundary document remain unchanged.
The final acceptance state is recorded in `stage5-results-v2.md` and the linked
machine-readable final checks, not inferred merely from this description.

## Formal statement

`RepoProof.SourceBytes.sourceImport` is defined by a trace over complete raw
byte sequences. It does not refer to a Python extraction, graph edge list,
certificate acceptance or result list. Its explicit language is the Mojom byte
import projection described in `stage5-source-spec-v2.md`.

The checked source witnesses establish canonical unpacking of every byte block,
every transition, acceptance at EOF and the complete emitted import sequence.
`import_iff_events` relates those witnesses to the independent trace definition.
`file_target_iff` checks both directions of exact internal path resolution.
`source_edge_iff` consequently states both soundness and completeness of the
source/graph relation. Files with no imports are still checked and remain in the
complete universe. Duplicate declarations retain their trace events but create
one graph edge. Imports outside the selected universe create no internal edge.

The concrete `ChromiumSource.source_bound` discharges this bridge for the entire
selected corpus. `ChromiumSource.source_to_answer` states that a byte path occurs
in the full decoded output list exactly when it names a selected vertex with a
reverse-reachability path from the fixed query root in the source import
relation. Equivalently, the selected file has a chain of imports to the root.
`ChromiumSource.paths_unique` establishes absence of duplicate output paths.
The proof checks the complete 477-element sequence, not only its count/digest.

Composition uses the existing `fastCheck_exact`, including its refinement to the
old checker and the previously proved exactness theorem. The root is included
by the zero-length reachability path. The source relation and graph retain the
direction importer to imported. Conditional import attributes are not evaluated.

The generic and concrete audits permit only `propext`, `Classical.choice` and
`Quot.sound`. These are not axiom-free results. No new axiom, `sorry`, `admit`,
`native_decide` or unchecked VM/FFI computation closes a proof obligation.
The timing tactic constructs a term and asks the kernel to check and insert it.
VM runs in the preserved differential suite are tests, not proof acceptance.

## Operational source identity and input binding

The IO layer verifies the externally anchored Git snapshot, complete selected
inventory, modes and actual blob bytes. Selection remains ordinary tracked
`.mojom` files of the main repository; symlinks, gitlinks and DEPS are not
expanded. The expected identity is not regenerated from attacker data.

One caller-owned capture supplies extraction, witness export, audits and output.
Source contents are immutable Python bytes held in frozen blob records. The full
pinned parser additionally checks complete Mojom files; its grammar and type
analysis are not formally verified here. The Lean theorem is about the explicit
byte import projection, not all Mojom grammar or arbitrary Chromium semantics.

An independent auditor decodes all packed Lean bytes and compares full contents,
path/ID routing, file routing and complete output paths with that same capture.
It does not rely only on matching counts or producer-supplied hashes. The
provenance audit is an external check, not a Lean theorem about Git or SHA.

The clean proof run has its own source directory and module search path. Only
the Lean SDK is precompiled in the main proof pipeline; all project modules,
filename mapping, 30 source groups and master instance are freshly compiled.
Previously accepted `.olean` files are hashed at subsequent consumption
boundaries. A caller-retained input seal and run nonce reject persisted input
changes and cross-run receipt substitution. Run input additions are checked;
startup hashes also check that each recorded project source file remains
unchanged. Independent review hashes must match both startup and final files.

These checks assume honest OS/process/file APIs and collision-resistant hashes.
They detect the tested changes between validation and use; they do not defeat an
adversarial kernel or an attacker controlling the verifier's private memory,
expected anchor, executable and filesystem while invisibly restoring all reads.

## Released answer

The deterministic JSON contains the pin, scope, root path/ID, direction,
root-inclusion policy, complete ordered paths, content identities and a reference
to operational verification evidence. Times, dates, environment details and run
nonce remain outside this payload. Complete repeated generation is compared
byte for byte. Numeric IDs are not interchangeable with booleans.

The persisted JSON is read again with duplicate-key rejection. The single human
renderer consumes that checked value; an independent parser checks all displayed
metadata and every displayed path. Kernel checking covers the typed Lean path
sequence; JSON parsing, canonical serialization, rendering and delivery remain
audited IO boundaries. No theorem about arbitrary terminal or browser rendering
is claimed.

Output promotion follows proofs, attacks, regressions, review and preservation
checks. A failure returns nonzero, records diagnostics and retains failed output
under a failure name, rather than releasing a new successful answer. Operational
receipts are valid only with their linked final report marked `STAGE5_PASS`.

This result concerns textual imports in the selected snapshot. It does not prove
runtime impact, build dependencies, correctness of Chromium, all external
repositories, equivalence of the Python checker with Lean, or cryptographic
implementations. The source/graph theorem and external identity checks are
separate parts of the guarantee.
