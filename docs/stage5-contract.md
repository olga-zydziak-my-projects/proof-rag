# Stage 5 frozen execution contract

Frozen before Stage 5 implementation. All normative requirements and gates
are retained verbatim below; there is no reduced PASS definition.

Accepted Stage 4 baseline: e4984110743131d04ad984eaaa48d33d72867336.
Stage 3 ancestor: 3184813. Initial working tree: clean.
Project: C:/Users/User/Documents/Codex/2026-11-08/nie/outputs/repo-proof-lab.
External source storage, not a checkout:
C:/Users/User/Documents/Codex/2026-11-08/nie/outputs/chromium-corpus-27cec857a08a.

Initial pin discrepancy to corroborate (no snapshot selected or switched):
- Supplied inventory claim: 1ab171af2976555a2b12b9bca8b984c204962ba8,
  tree 9e5b002b0ce384a82f6cb836fd3abaebab8a7da6.
- Accepted baseline lock and Stage 2 receipts: 27cec857a08a0ee0e1b41f5eb18c07467a0ce093,
  tree 25131300fa459906dedb84bf592a8537b7848771.
A discrepancy must produce BLOCKED_PIN_CONFLICT, never a silent fallback.
Counts (1864/4419/477, 213 isolated) are regression observations only.

Recovered representation: paths sorted as exact Python strings (the actual
selected paths are ASCII; this is to be checked against captured data), edges
are unique sorted importer/imported pairs. Host path normalization is not used.
Source bytes decode strict UTF-8; invalid encoding or unsupported syntax blocks
source completeness. The detailed accepted scope, import semantics, comments,
escapes, attributes, resolution and unresolved policy are reproduced after the
normative request. Their existing parser implementation is tested, not proved.

## Complete normative Stage 5 request

First, save the completed Stage 4 as a separate local Git commit.
Preserve Stage 3 commit 3184813 and all unrelated user changes.
Do not push. Record the Stage 4 commit SHA as the baseline for Stage 5.
If that checkpoint already exists, verify and reuse it.

Then execute the complete Stage 5 specification below.
Proceed through implementation, proofs, tests, and reporting.
Repair ordinary technical errors internally.
Do not change requirements or success criteria.

# Stage 5 — Bind repository sources to the certified answer

Execution prompt for the local Codex working on repo-proof-lab.
Prepared 2026-11-09. This is a specification for the next stage,
not a report of completed implementation.

## Objective

Implement Stage 5 in the existing local project:

C:/Users/User/Documents/Codex/2026-11-08/nie/outputs/repo-proof-lab

Bind the existing, exact reverse-dependency answer to the source
snapshot and to the machine-readable and human-readable answer
actually released by the program. Preserve the Stage 4
kernel-checked guarantee and all previously accepted requirements.

The target is a source-level statement about the existing Mojom
import relation, under an explicit source-language specification
and explicitly declared I/O and provenance assumptions.
Do not expand the claim to all Chromium dependencies, runtime
behavior, or all files in the corpus.

Complete the authorized implementation, proof work, adversarial
checks, and report. Repair ordinary implementation, syntax, and
test failures internally. Do not stop after producing a plan.
Do not change the goal or acceptance gates to obtain PASS.

No publication, push, PR, messaging, global Git changes,
LLM integration, or new corpus expansion is required.

## 1. Inspect and preserve the accepted baseline

Read applicable AGENTS.md, project README, existing contracts,
reports for Stages 2–4, manifests, parser/extractor code,
serialization checks, tests, and these Lean modules or their
actual equivalents:

- Reachability.lean, Checker.lean, FastChecker.lean;
- Chromium.lean, ChromiumFast.lean;
- Stage 4 export, binding-review, timing, and tampering scripts.

Confirm the actual working directory and source-corpus locations
before executing commands. The path above identifies the project,
not necessarily the Chromium source checkout.

Preserve Stage 3 commit 3184813, Stage 4 code, all historical
reports, and unrelated user changes. Record the current HEAD,
dirty state, relevant file inventory and hashes.

Use additive Stage 5 modules and outputs where practical.
Do not rewrite a completed report or overwrite a previous run.
A local checkpoint may include only identified project-owned
changes; never use an indiscriminate git add .

The Stage 4 report records this fixed regression instance:

- Lean SDK: 4.35.0
- Graph universe: 1864 nodes
- Graph edges: 4419
- Isolated nodes retained: 213
- Query root: mojo/public/mojom/base/time.mojom
- Exact result size: 477, including the root
- Edge direction: importer → imported
- Existing test count: 71

Recover the exact universe-selection rule, path ordering,
edge normalization, import resolution, and query semantics
from accepted local artifacts.

Counts are regression sentinels, not a definition of scope
and not a substitute for full equality.

The earlier corpus inventory records this Chromium source identity:

- repository: chromium/chromium
- commit: 1ab171af2976555a2b12b9bca8b984c204962ba8
- root tree: 9e5b002b0ce384a82f6cb836fd3abaebab8a7da6

Corroborate these values against the actual Stage 2–4 source
provenance before using them. The corpus inventory alone does
not prove which bytes the local experiment used.

A conflicting or unresolvable pin is BLOCKED_PIN_CONFLICT;
do not silently switch snapshots.

Preserve the established selection of files, including files
without imports. Do not infer that 1864 nodes represent the
entire Chromium repository.

Before substantive changes, save docs/stage5-contract.md
containing the objective and all acceptance gates in this prompt,
plus the recovered source scope and semantics.
Record its SHA-256 in subsequent reports.

Routine implementation details may be decided autonomously.
An incompatibility with an existing accepted requirement must
be documented, not resolved by weakening that requirement.

## 2. Keep the trust boundary explicit

Separate these obligations in code and in the report:

1. Snapshot identity and completeness:
   the selected paths, modes, and source bytes belong to the
   expected, externally anchored repository snapshot.

2. Source semantics:
   the graph contains exactly the imports defined by the declared
   Mojom source specification, with the full selected file universe.

3. Graph answer:
   the existing formal checker certifies exactly the
   reverse-reachable vertices, including the root.

4. Answer binding:
   the actual returned paths and query metadata are exactly
   those of this certified instance.

Git object validation, cryptographic collision resistance,
OS/file I/O, the Lean toolchain, and delivery of output bytes
have explicit trust assumptions.

Stage 5 does not require formalizing Git or SHA implementations.
Do not describe these assumptions as Lean theorems.

A self-consistent bundle cannot establish its own expected commit:
the anchor must be compared with the accepted project provenance.

Conversely, parser tests, two extractors agreeing, matching counts,
or matching hashes do not establish a formal source-semantics
theorem. They are supporting checks. Report them as such.

## 3. Establish source identity before certifying any answer

Build one immutable run input from the established pin and scope.
Prefer Git objects at the pin or another existing, equally strong
object-verified snapshot mechanism over mutable working-tree files.

Check the complete selected inventory against the pinned tree.
Verify selected blob contents against the corresponding object
identities, and independently compute content hashes for the receipt.

Account for Git modes, symlinks, and gitlinks under the existing
scope; never follow or expand them silently.

The source stage must distinguish:

- missing files;
- modified bytes;
- wrong revision;
- incomplete inventory;
- duplicate paths;
- invalid paths;
- unsupported input.

Each must prevent a successful source-bound answer.

Check the byte identity of the snapshot exported into Lean against
the verified source bytes. Exporting an unchecked Python
interpretation into Lean is insufficient.

Use repository path semantics rather than host-path normalization.
Preserve case, path boundaries and bytes according to the accepted
specification. Reject traversal, aliasing, duplicate ID mappings,
and lossy conversion.

If the scope permits non-ASCII paths, specify their exact encoding;
otherwise unsupported paths must fail explicitly.

Prevent checking one set of bytes and later using another.
All extraction, proof export, validation, and rendering must consume
the same captured input.

Validate persisted artifacts at their consumption boundaries.
If mutable files must be involved, detect changes before
releasing success.

## 4. Add the formal source-to-graph bridge

Choose the smallest complete approach compatible with the existing
code. Suitable designs include a verified import scanner or a source
certificate checker that verifies a complete token/byte partition
and all import declarations.

Optimize representation only after the obligations are explicit.

Write a source-level import specification grounded in the pinned
Mojom language/grammar and the already accepted project semantics.

Specify:

- comments;
- strings and escapes;
- import boundaries;
- encoding;
- attributes or conditional constructs when present;
- malformed input;
- path resolution;
- duplicate imports;
- unresolved targets.

Inspect the full selected corpus for coverage.
A restricted grammar must cover every selected file and must
be named as a restriction; never silently exclude an inconvenient
file or construct.

The specification must describe imports in the source bytes
independently of the exported graph.

Do not define “source imports” as the Python export,
a list of supplied edges, or the fact that the fast checker accepts.

Prove both directions:

- every extracted graph edge corresponds to a source import
  under the declared specification;
- every relevant source import is represented in the graph
  under the unchanged resolution and normalization rules.

Also prove or kernel-check that the path/ID mapping covers
the complete selected universe exactly once.

Preserve files without imports, the 213 isolated vertices,
cycles and all existing graph semantics.

Source spans for present edges help provenance, but alone
do not prove that no import was omitted.

Prove a composition theorem with the following meaning,
adapting names and types to the existing library:

If source binding and the enhanced certificate are accepted
for snapshot S and query root r, then a path occurs in the
decoded answer if and only if it is a selected path with an
import path to r in the declared source relation of S,
including the zero-length path at r.

Compose this through fastCheck_refines, fastCheck_exact
and the existing exactness theorem.

Do not replace the established theorem with a weaker one
or assume source extraction correctness as a newly introduced
unproved premise.

Any necessary well-formedness or coverage premise must itself
be discharged for the complete instance.

The formal claim is relative to the explicitly reviewed source
specification and the exact source bytes supplied to Lean.
External checks connect those bytes to the repository pin.
Describe both parts precisely.

Use kernel-checked proof terms.

Do not use:

- sorry;
- admit;
- native_decide;
- new axioms;
- unchecked FFI/VM results;
- unsafe computation to discharge proof obligations.

Audit the axioms of generic and instantiated theorems.
Preserve the declared Stage 4 allowance for propext,
Classical.choice, and Quot.sound; do not call the result axiom-free.

Named source blocks and per-file proofs may be composed
to control reduction cost.

The composition must cover every required file, byte region,
import and graph edge without omission.

A Python loop that simply asserts that coverage exists
is not the formal bridge.

If the source bridge cannot be completed, retain useful work
and report STAGE5_BLOCKED__SOURCE_PROOF.

Strong external audits alone must not be reported as completion
of this gate.

## 5. Bind the actual answer to the actual proved instance

Produce a typed result envelope with:

- schema version;
- repository identity;
- exact source commit/tree;
- declared scope;
- exact root path and ID;
- edge direction;
- root-inclusion policy;
- full result path list;
- source/graph/result identities;
- a verification receipt.

Record the precise scope of the formal theorem.
A theorem name or verified: true string by itself is not evidence.

Derive the result paths from the same certificate and path table
whose equality to the instantiated Lean data has been checked.

Prove or kernel-check the path decoding and final result sequence
for the full instance, including the absence of omissions,
extra paths and duplicates.

Verify metadata such as root and source identity against
the run inputs; never reuse a proof for another query or dataset
because the output count happens to match.

Use a single deterministic renderer for the canonical answer payload.

Verify that the persisted machine-readable payload decodes to
exactly the certified paths and query metadata.

Generate the human-readable answer from that verified payload
and independently check its complete path list and semantic metadata.

Do not certify only a digest or a hidden list while displaying
a different answer.

Prefer proving the relevant pure decoding/rendering relationship.
Actual filesystem/stdout delivery is an audited I/O boundary
and must remain labeled as such.

Do not claim a proof about arbitrary terminal rendering
or a browser UI that does not exist in this project.

A summary may be displayed, but the complete 477-path answer
must be available and clearly identified.

Displayed claims such as “all dependents” must refer to the exact
established scope and relation.

Do not add natural-language claims beyond those established facts.

Keep timestamps, timings and environment metadata outside
the deterministic canonical answer payload so identical inputs
produce identical payload bytes.

Failure produces a non-success exit status and a diagnostic record,
without leaving a partial or stale artifact marked as a newly
successful answer.

## 6. Use adversarial checks at the right boundary

Retain all existing tests and comparisons.
Add meaningful checks of the public pipeline, not only private helpers.
Run mutations in isolated copies; never corrupt the baseline.

At minimum cover these distinct failure classes:

A. Remove a selected source file, including one with no imports.
   Required: snapshot coverage rejects; the source-bound
   success path cannot continue.

B. Change source bytes and update all attacker-controlled local hashes.
   Required: the fixed expected snapshot identity still rejects.

C. Substitute a wrong commit/tree while leaving internally
   consistent artifacts.
   Required: the external expected anchor rejects.

D. Remove, add or replace an import edge; include a same-count mutation.
   Required: source-to-graph binding rejects even if a graph-only
   certificate is valid.

E. Repeat the Stage 4 edge-deletion/473-result scenario
   with a regenerated certificate.
   Required: graph-only acceptance is distinguished from
   source-bound rejection; record actual observations.

F. Swap two path labels while preserving counts and graph IDs.
   Required: mapping/answer binding rejects.

G. Omit, add, duplicate or replace a final result path;
   include same-count replacement.
   Required: full answer comparison rejects.

H. Change the query root or root-inclusion metadata.
   Required: instance/query binding rejects.

I. Omit or duplicate a source/edge/proof block.
   Required: coverage rejects.

J. Put import-like text in comments/strings;
   exercise legal whitespace and relevant escapes.
   Required: source semantics behave according to
   the frozen specification.

K. Supply malformed or unsupported input.
   Required: explicit rejection; no successful empty graph
   or truncated extraction.

L. Mix artifacts from two runs or change an input between
   validation and use.
   Required: run binding detects the mismatch before
   success is released.

Include at least one test in which hashes and counts match
their attacker-controlled manifest but the expected source anchor
or the semantic contents do not.

The expected manifest must not be regenerated from the attack fixture.

Keep positive cases for cycles, isolated vertices, root inclusion,
existing rank semantics and legal formatting differences.

Record which layer rejects each attack.
Do not claim the Lean kernel rejects a source substitution
if only the provenance audit rejected it.

If a test depends on a cryptographic assumption, state that assumption.

Use separate small source-semantics fixtures for legal formatting
variants. Changing bytes in the fixed real snapshot must still
fail provenance, even if the changed file has equivalent imports.
These are different assertions and must not share an ambiguous
expected outcome.

The existing 1547 Python–Lean comparisons remain tests,
not a proof of Python/Lean equivalence.

Preserve their coverage or explain a genuine infrastructure blocker;
do not silently delete slow or failing checks.

## 7. Reproduce and measure without changing the comparison

Provide one command from the project root that performs:

- snapshot verification;
- source binding;
- graph/certificate checks;
- Lean instance verification;
- answer rendering;
- round-trip/byte audits;
- existing tests;
- Stage 5 attacks.

Produce a new run directory.
Existing output paths must not be silently overwritten.

Run the complete unchanged real instance successfully.
Separately repeat canonical artifact generation from identical
inputs and compare complete bytes.

Measure repetitions within the existing project budget;
distinguish a single observation from a repeated benchmark.
Do not extend the scope into a long campaign.

Report separate timings for:

- provenance checks;
- extraction/source validation;
- generation;
- compilation of generic modules;
- fresh instance checking;
- answer validation;
- the whole operational pipeline.

State which libraries and generic proofs were precompiled.
A cached proof import must not be described as fresh
instance verification.

Report source and artifact sizes and process memory with
the same precise Windows definitions as Stage 4 where comparable.
Use machine-readable raw measurements.

Preserve these historical facts:

- 749.257 s → 1.550 s was the sum of kernel checks plus
  leaf-lemma insertion, not total program time;
- 9.992150 s was the fresh Stage 4 instance process,
  after generic-module compilation;
- the complete Stage 3 process time and baseline memory peak
  are unknown;
- Stage 4's full-run speed was one observation,
  and its artifacts grew.

Do not rerun the expensive historical Stage 3 proof merely
to fill a missing number.

Do not claim a new speedup unless the measurement boundaries
and baselines support it.

This stage's primary success criterion is source-to-answer binding;
do not invent a performance improvement requirement.

## 8. Deliver evidence and assign the result mechanically

Use project conventions; the following are suggested new outputs:

- docs/stage5-contract.md:
  frozen objective, scope, semantics and gates;

- docs/stage5-trust-boundary.md:
  proved properties, external audits, assumptions
  and unsupported claims;

- additive Lean modules for the source specification/checker,
  path/answer binding and full instance;

- source snapshot receipt and canonical machine-readable answer;

- human-readable answer containing or linking
  the complete verified list;

- one orchestrating script and necessary focused test scripts;

- verification/stage5-checks.json;

- verification/stage5-tampering.json;

- docs/stage5-results.md:
  reproduction command, measurements and limitations.

Include enough data and provenance to reproduce the run.

If the corpus is external rather than bundled, list its exact
required location/identity or retrieval procedure;
do not call the bundle self-contained.

Record changes and baseline-preservation checks before
and after execution.

STAGE5_PASS requires every gate below:

G1 — Preservation
Existing accepted requirements, Stage 3/4 artifacts and unrelated
changes are preserved; the full regression instance is unchanged.

G2 — Snapshot
Complete selected paths and actual bytes are checked against
the established, externally anchored pin, with no silent omissions.

G3 — Source theorem
A kernel-checked, sound and complete source-to-graph bridge exists
under the explicit source specification and is instantiated
for all selected files.

G4 — Exactness
The existing exactness guarantee composes with that bridge
and full path mapping for the unchanged query and result.

G5 — Answer binding
The actual released canonical and human-readable answers are checked
against that exact instance, with deterministic canonical bytes.

G6 — Attacks and regressions
Existing checks pass, the required positive cases pass,
and each attack is rejected by the stated layer.

G7 — Reproduction
A clean operational run and deterministic regeneration
are demonstrated, with raw evidence and declared
environment dependencies.

G8 — Claim accuracy
The report clearly separates formal results, operational checks
and assumptions; no new trusted proof shortcut or unsupported
end-to-end guarantee is introduced.

Assign FAIL when a completed check contradicts a gate.
Assign BLOCKED when an essential input or proof is unavailable,
with the exact reason.

An implemented external provenance audit with G3 unresolved
is partial progress, not STAGE5_PASS.

Preserve negative results and useful partial artifacts.

Finish in Polish, briefly reporting:

- status and G1–G8 results;
- the exact guarantee now obtained and its assumptions;
- source pin and scope, full graph/result counts;
- kernel-checked theorem names and axiom audit;
- source-tampering and answer-tampering outcomes;
- measured full-pipeline and instance times with their boundaries;
- test results, remaining limits and concrete artifact paths.

Do not publish or send the results anywhere.
Do not modify acceptance gates after observing outcomes.

## Accepted local source semantics, recovered without alteration

# Pierwsze zapytanie: zależności przez deklaracje importów Mojom

Wersja kontraktu: `mojom-import-dependents-v1`. Repozytorium źródłowe to
`https://github.com/chromium/chromium`, commit
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`. Kontrakt określa przyszłą
ekstrakcję i znaczenie wyniku; etap 1 nie zawiera formalnie zweryfikowanego
parsera ani dowodu zgodności ekstraktora z kodem Chromium.

## Zakres i wynik

Niech `S` oznacza wszystkie zwykłe, śledzone pliki o ścieżkach kończących się
dokładnie na `.mojom` w drzewie wskazanego commitu głównego repozytorium.
Tryby `100644` i `100755` oznaczają zwykłe pliki. Dowiązania `120000`, gitlinki
`160000` oraz zawartość zewnętrznych repozytoriów DEPS nie należą do `S`.
Ścieżki są identyfikatorami z drzewa Git, z ukośnikiem `/` i rozróżnieniem
wielkości liter. Zawartość pliku oznacza oryginalne bajty obiektu Git.

Dla `r ∈ S` wynik to zbiór:

```text
R(r) = {v ∈ S | istnieje ścieżka importów v → … → r,
                 której wszystkie wierzchołki należą do S}
```

Ścieżka długości zero jest dozwolona: wynik zawsze zawiera wskazany plik `r`.
To celowy wybór zgodny z istniejącym certyfikatem
`reverse_reachability_including_root`. Cykle i pętle są dozwolone. Duplikaty
deklaracji dają jedną krawędź grafu, z zachowaniem wszystkich lokalizacji
deklaracji jako danych pochodzenia. Kolejność listy wynikowej nie ma znaczenia
matematycznego; zapis wyników powinien sortować ścieżki.

## Co tworzy krawędź

Krawędź `Import(a, b)` biegnie od importera do importowanego pliku. Powstaje
z poprawnej, kompletnej deklaracji importu na poziomie pliku, zakończonej
średnikiem, której literał ścieżki rozwiązuje się jednoznacznie do `b ∈ S`.
Deklaracje poprzedzają definicje; opcjonalna deklaracja modułu poprzedza
importy. Składnia importu w przypiętym parserze to
`attribute_section IMPORT STRING_LITERAL SEMI`, gdzie sekcja atrybutów może
być pusta. Źródła dekodujemy jako UTF-8 w trybie ścisłym; błąd dekodowania
lub nieobsługiwany BOM daje `unresolved`. Nie normalizujemy tekstu ani
końców linii. Są to reguły kontraktu oparte na
[przypiętym parserze Chromium](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/mojom/mojom/parse/parser.py).
Ekstraktor musi rozpoznawać tokeny języka, komentarze, literały i zagnieżdżenia;
samo wyszukanie napisu `import` lub wyrażenie regularne na liniach nie jest
specyfikacją parsera. Napis przypominający import w komentarzu albo innym
literale nie tworzy krawędzi.

Importy z atrybutami warunkowymi wchodzą do relacji bez oceny warunków.
Relacja oznacza obecność deklaracji w zamrożonym tekście, niezależnie od
ustawień GN, systemu operacyjnego i wybranego wariantu kompilacji. Nie jest
to graf importów konkretnego zbudowanego programu. Komentarze liniowe
`// …` i blokowe `/* … */` są pomijane zgodnie z regułami leksykalnymi;
niedomknięty komentarz lub literał jest błędem ekstrakcji.
Przypięty [lexer Chromium](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/mojom/mojom/parse/lexer.py)
oddziela tokeny komentarzy od tokenów literałów. Jego pełne reguły literałów
dopuszczają więcej zapisów niż przyjęty niżej podzbiór ścieżek.

## Rozwiązywanie ścieżek

Kontrakt używa jawnie ustalonego pojedynczego korzenia: katalogu głównego
zamrożonego repozytorium. Import `"mojo/public/mojom/base/string16.mojom"`
wskazuje tę samą ścieżkę w drzewie Git, niezależnie od katalogu importera.
Nie przeszukujemy systemu plików komputera, bieżącego katalogu, katalogów
wyników kompilacji ani repozytoriów DEPS. Nie stosujemy niejawnego fallbacku
do ścieżki względnej wobec importera.
To jawny wybór eksperymentu: narzędzia budowania Chromium mają również
konfigurowalne katalogi importów i katalog wynikowy, co widać w
[generatorze wiązań](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/bindings/mojom_bindings_generator.py).

Obsługiwany literał ścieżki zawiera kanoniczną ścieżkę repozytoryjną:
niepuste segmenty rozdzielone `/`, bez początkowego `/`, segmentów `.` lub
`..`, odwrotnych ukośników, sekwencji ucieczki, bajtów NUL oraz prefiksów
dysku lub schematu URL. Inny zapis wymaga rozszerzenia kontraktu albo daje
status `unresolved`; nie jest automatycznie normalizowany regułami Windows.
Nieprawidłowa lub niejednoznaczna ścieżka nie znika z raportu.

## Przykład z przypiętych źródeł

Pierwszy proponowany korzeń to `mojo/public/mojom/base/time.mojom`.
Rzeczywisty plik
[`mojo/public/mojom/base/file_info.mojom`](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/mojom/base/file_info.mojom)
importuje ten korzeń bezpośrednio w linii 7. Należy więc do wyniku wraz
z samym korzeniem. Obiekt Git pliku ma identyfikator
`c10e953809bee580680b84839ed02274d76b2de7`.

Istnieje też ścieżka o dwóch krawędziach:

```text
services/network/public/mojom/url_loader.mojom
  → services/network/public/mojom/url_response_head.mojom
  → mojo/public/mojom/base/time.mojom
```

Pierwszą deklarację zawiera
[`url_loader.mojom`, linia 12](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/services/network/public/mojom/url_loader.mojom#L12)
(obiekt `47daa39be77716831401f3205b804352714a5ce7`), a drugą
[`url_response_head.mojom`, linia 7](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/services/network/public/mojom/url_response_head.mojom#L7)
(obiekt `2551c74d161edc11e3d4e95c858c144a063ae80a`). To przykładowi
bezpośredni i pośredni importerzy, a nie wyliczenie pełnego wyniku.

Rzeczywisty import warunkowy znajduje się w
[`chrome/common/renderer_configuration.mojom`, linie 12–13](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/chrome/common/renderer_configuration.mojom#L12):
atrybut `EnableIf=enable_request_header_integrity` poprzedza import
`services/network/public/mojom/http_request_headers.mojom`. Kontrakt zachowuje
tę krawędź bez oceny warunku. Obiekt pliku to
`b5631d2a8d915c9209ee9499cedad28b0b43e79a`.
Przykłady oraz referencyjne pliki parsera sprawdzono także w lokalnym
magazynie korpusu: identyfikatory Git i SHA-256 oryginalnych bajtów zgadzają
się z manifestem. Nie jest to walidacja składni całego korpusu ani pełne
wyliczenie grafu importów.

## Granice korpusu i niepełne dane

Każda rozpoznana deklaracja musi otrzymać jawny status rozstrzygnięcia:

- `internal`: kanoniczny cel należy do `S`; tworzy krawędź `Import`.
- `outside_scope`: kanoniczny cel nie należy do `S`, co potwierdza kompletne
  drzewo Git. Raport zachowuje importera, literał i przyczynę, np. gitlink,
  dowiązanie, brak śledzonego wpisu lub inny typ pliku. Cel nie jest dopisywany
  do `S`, a ścieżka zapytania nie może przechodzić przez taki cel.
- `unresolved`: nie można rozstrzygnąć ścieżki, składni albo przynależności
  do zakresu, lub nie można odczytać zweryfikowanej treści wymaganego pliku.

Znany import poza zakresem sam w sobie nie uniemożliwia dokładnej odpowiedzi
na powyższe zapytanie o graf indukowany przez `S`. Taka odpowiedź nie obejmuje
ścieżek wychodzących z `S` i powracających przez zewnętrzne repozytoria.
Jeżeli użytkownik oczekuje również takich ścieżek, potrzebny jest inny zakres
i nowe pobranie; obecny wynik nie jest odpowiedzią na rozszerzone zapytanie.

Brakujące bajty dla dowolnego pliku z `S`, niepełny manifest, błędny skrót,
nieobsługiwana składnia lub nierozstrzygnięta deklaracja powodują
`unresolved` dla zapytania o cały `S`. Błąd w pozornie niepowiązanym pliku
może ukryć import do korzenia. Nie wolno zawęzić kontroli do plików
odwiedzonych przez wyszukiwarkę. Można zachować wynik cząstkowy i przyczyny
błędu, ale nie przedstawiać go jako kompletnego. Korzeń spoza `S` jest
odrzucany jako `out_of_scope`; nie jest zastępowany podobną ścieżką.

Śledzone pliki wygenerowane, jeśli mają zwykły tryb Git i rozszerzenie
`.mojom`, należą do `S` tak samo jak inne pliki. Nieśledzone wyniki generatorów,
hooki, budowanie Chromium i pobieranie DEPS nie są częścią eksperymentu.
Błędna składnia nie oznacza pliku bez importów: musi być zgłoszona. Pełny
parser albo jawnie określony, odrzucający nieobsługiwane konstrukcje podzbiór
gramatyki musi poprzedzić deklarację dokładności ekstrakcji.

## Znaczenie statusu i granica formalnej gwarancji

Docelowy status `complete_for_declared_scope` wymaga kompletnego manifestu,
zgodności commitu i treści wszystkich plików `S`, zakończonej ekstrakcji bez
nierozstrzygnięć oraz przyjęcia certyfikatu przez niezależny checker.
Pozostaje on stwierdzeniem implementacji z udokumentowanymi założeniami
dotyczącymi ekstraktora. Nie jest dowodem formalnym parsera.

`RepoProof.exact_dependents` dowodzi dokładności względem dostarczonego
grafu przy trzech obowiązkach: korzeń należy do wyniku; każdy inny wynik
ma rodzica z oryginalną krawędzią `Import(v, parent)` i ściśle mniejszą rangą;
wynik jest domknięty po wszystkich odwróconych krawędziach. Dowód nie
ustanawia, że manifest albo graf wiernie opisują źródła. Checker Python nie
wywołuje wyszukiwania generatora, ale jego zgodność z Lean jest testowana,
a nie formalnie udowodniona.

Aby połączyć źródła z twierdzeniem o grafie, pozostają obowiązki:

1. Wykazać kompletność enumeracji drzewa wskazanego commitu, jednoznaczność
   ścieżek, klasyfikacji trybów i wyboru `S`, w tym wykluczenie gitlinków
   oraz dowiązań bez podążania za nimi.
2. Związać każde źródło z obiektem Git, oryginalnymi bajtami i manifestem;
   jawnie określić założenia kryptograficzne hashy oraz model zaufania do Git.
3. Określić gramatykę, leksykę, dekodowanie i rozwiązywanie ścieżek, a potem
   wykazać poprawność i kompletność ekstrakcji każdej deklaracji w każdym
   pliku `S`, włącznie z komentarzami i atrybutami.
4. Wykazać, że serializacja grafu zachowuje dokładnie relację `Import`,
   kierunek krawędzi i zbiór `S`, bez pominięć lub dodatkowych krawędzi.
5. Wykazać zgodność walidacji wejścia i checkera Python z obowiązkami
   `exact_dependents`, w tym naturalność rang i kontrolę wszystkich krawędzi.
6. Związać oczekiwany korzeń, wersję kontraktu, manifest, graf i certyfikat
   z jedną instancją zapytania; nie polegać wyłącznie na deklaracjach generatora.

Wynik opisuje zależność tekstowych deklaracji importów. Nie dowodzi, że zmiana
pliku wpłynie na zachowanie programu, że dany kod jest wykonywany ani że
konkretna konfiguracja kompilacji używa wszystkich znalezionych deklaracji.
