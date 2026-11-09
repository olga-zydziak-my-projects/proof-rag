# Formalny rdzeń i wykonywalny checker

Lean 4.35.0, `Std`, bez Mathlib.

- `Reachability.lean`: sześć pierwotnych twierdzeń, w tym `exact_dependents`.
- `Checker.lean`: skończony graf `Fin n`, certyfikat jako skończona funkcja, czysty Boolean
  `check`, dowód `check_exact` oraz udowodnione rozbicie `all_split`.
- `ProofTiming.lean`: konstrukcja termu przez `mkDecideProof` i synchroniczne
  `mkAuxLemma`, jak w `decide +kernel`; osobne pomiary konstrukcji i kontroli
  kernela wraz z dodaniem pomocniczego lematu.
- `Chromium.lean`: pełna deterministyczna tabela ścieżek, graf i certyfikat
  etapu 2 oraz cele `Chromium.accepted` i `Chromium.exact`.
- `RunChecker.lean`: osobne wykonanie checkera w VM Lean. Wynik programu
  nie zastępuje dowodu sprawdzanego przez kernel.

Z katalogu projektu:

```powershell
$env:LEAN_PATH = (Resolve-Path formal).Path
& $lean -o formal/Reachability.olean formal/Reachability.lean
& $lean -o formal/Checker.olean formal/Checker.lean
& $lean -o formal/ProofTiming.olean formal/ProofTiming.lean
& $py scripts/export_stage3.py
& $py scripts/review_stage3_binding.py
& $lean -o formal/Chromium.olean formal/Chromium.lean
& $lean --run formal/RunChecker.lean
```

Pełne sprawdzenia, testy, demonstrację źródłową i raport wykonuje
`& $py scripts/check_stage3.py --lean $lean`. `$lean` i `$py` ustaw jak w
[głównym README](../README.md). Stan faktycznego uruchomienia, audyty i pomiary
są opisane w [wynikach etapu 3](../docs/stage3-results.md).

Akceptacja implikuje dokładność względem dostarczonego grafu. Korzeń jest
niezależnym argumentem, krawędź biegnie importer → importowany, a wynik
zawiera korzeń. Rodzice muszą należeć do wyniku, mieć rzeczywistą krawędź
i ściśle mniejszą naturalną rangę. Kontrola domknięcia obejmuje całą listę
krawędzi; kontrola świadków obejmuje wszystkie `Fin n` przez `List.range n`
i sprawdzany warunek `i < n`. Nie wymagamy
najkrótszych ścieżek ani kolejnych rang. Poprawny zbiór z niepoprawnymi
świadkami jest odrzucany.

Certyfikat `Fin n → Option Witness` ma dokładnie jedną pozycję na węzeł. `none` oznacza brak
w wyniku. Korzeń ma świadka `(root, 0)`, co koduje Pythonowe `(null, 0)`.
Lista krawędzi w modelu może powtarzać krawędź; matematyczna relacja jest
przynależnością do listy i dowód nie wymaga jej unikalności. Zewnętrzny
format JSON jest ściślejszy: walidator eksportu odrzuca duplikaty krawędzi,
węzłów i świadków, błędne rekordy i identyfikatory oraz ujemne/bool rangi.
Twierdzenie o danych Lean nie jest dowodem poprawności tego walidatora.

Dowód instancji rozbija listy wierzchołków i krawędzi na części do 64 elementów
przez `all_split`. Kontrole nie są pomijane. Nie ma `native_decide`, własnych
aksjomatów ani nieukończonych dowodów. Sześć pierwotnych twierdzeń ma pusty
audyt aksjomatów. Nowe deklaracje mogą używać standardowych `propext`,
`Classical.choice`, `Quot.sound`; dokładne listy wypisuje Lean.

Nadal nie dowiedziono parsera Mojom, ekstrakcji, serializacji, eksportera,
mapowania ścieżek, Git/manifestu/hashy, zgodności checkera Python z Lean ani
związania wyświetlanej odpowiedzi z twierdzeniem. Niezależne pełne porównanie
literalnych danych Lean z artefaktami pozostaje zewnętrzną kontrolą.
