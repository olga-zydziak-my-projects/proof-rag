# Etap 5 v2 — STAGE5_PASS

Etap ukończony 10 listopada 2026. Pełny przebieg zakończył się kodem **0**,
statusem **STAGE5_PASS** i wynikiem **PASS dla G1–G8**. Kernel przyjął konkretny
most źródło–graf–dokładna osiągalność–pełna lista ścieżek. Przeszło **85 testów**,
w tym zachowane **1547 porównań Python–Lean**, oraz **46 kontroli A–L**.
Nie wykonano push ani publikacji.

## Odpowiedź i dowody wykonania

- [Pełna odpowiedź JSON — 477 ścieżek](../local/stage5-v2/full-03/answer.json).
- [Pełna odpowiedź czytelna dla człowieka](../local/stage5-v2/full-03/answer.txt).
- [Końcowy przebieg, bramy, czasy, pamięć, audyty i logi](../verification/stage5-v2-final-checks.json).
- [Wyniki A–L](../local/stage5-v2/full-03/evidence/attacks.json).
- [Rachunek pochodzenia dowodów i odpowiedzi](../local/stage5-v2/full-03/operational-receipt.json).
- [Dodatkowy audyt wydanych artefaktów i zachowania bazy](../verification/stage5-v2-post-audit.json).
- [Niezależny przegląd](stage5-review-v2.md) i [tożsamości przejrzanego kodu](../verification/stage5-v2-review-final.json).
- [Aktualna granica zaufania](stage5-trust-boundary-v2.md) oraz [specyfikacja bajtowa](stage5-source-spec-v2.md).

## Jedno polecenie odtworzenia

Z katalogu projektu, Windows, Python 3.10+, Git i Lean 4.35.0:

```powershell
& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/check_stage5_v2.py --lean 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe' --run-dir local/stage5-v2/reproduce-01 --report verification/stage5-v2-reproduce-01.json
```

Wybierz nieistniejące ścieżki przy każdym powtórzeniu. Potrzebne są istniejące
`local/corpus.json`, obiektowo zweryfikowany korpus i artefakty etapu 2. Nie
potrzeba dodatkowych pakietów Pythona ani nowego pobierania Chromium. Raport
musi być poza zapieczętowanym katalogiem przebiegu. Zmiana przejrzanego kodu
wymaga nowego przeglądu, nie zachowania starego napisu PASS.

Polecenie obejmuje snapshot, pełne parsowanie, eksport i powtórną generację,
świeże dowody, audyty bajtów, A–L, cały zestaw testów, zapis i ponowny odczyt
odpowiedzi oraz ocenę bram. Niepowodzenie daje kod niezerowy i diagnostykę;
nieudane odpowiedzi zachowują nazwę wskazującą porażkę.

## Zachowana kotwica i zakres

Commit etapu 4: **`e4984110743131d04ad984eaaa48d33d72867336`**. Zachowano jego
historię i przodka etapu 3 `3184813`. HEAD nadal wskazuje checkpoint etapu 4;
nie tworzono nowego commita etapu 5.

| Własność | Potwierdzona wartość |
| --- | --- |
| Repozytorium | `https://github.com/chromium/chromium` |
| Commit Chromium | `27cec857a08a0ee0e1b41f5eb18c07467a0ce093` |
| Root tree | `25131300fa459906dedb84bf592a8537b7848771` |
| SHA-256 manifestu | `1e6fe63490e2007c56b088194f0c2acb61abc834aeefb4edb2bbfe6399bc2e4a` |
| Wybrane pliki / węzły | 1864, w tym 213 izolowanych |
| Bajty źródeł / bloki dowodu | 6 946 142 / 28 070 |
| Deklaracje importów | 4428: 4424 wewnętrzne, w tym 5 powtórzeń; 4 poza zakresem |
| Unikalne krawędzie | 4419, importer → importowany |
| Korzeń / ID | `mojo/public/mojom/base/time.mojom` / 995 |
| Wynik | 477 ścieżek, z korzeniem |

Liczby są wyłącznie kontrolą regresji. Akceptacja wymaga pełnej zgodności
inwentarza, trybów, bajtów, mapowania, grafu, certyfikatu i wyniku. Zakres to
zwykłe śledzone `.mojom` głównego repozytorium; symlinki, gitlinki i DEPS nie
są rozwijane. Nie jest to całe Chromium. Nie ma `unresolved` w zaakceptowanej
instancji. Ścieżki zachowują tożsamość Git i UTF-8; rzeczywiste wybrane nazwy
są ASCII. Atrybuty warunkowe nie usuwają deklarowanych importów.

Kotwicę odczytuje się z `git show e498411...:corpus.lock.json`, niezależnie od
pakietu producenta; sprawdzane są rzeczywiste obiekty i bajty snapshotu.
[Aneks](stage5-pin-correction-v2.md) i [kontrakt v2](stage5-contract-v2.md)
zachowują wszystkie wymagania. SHA-256 kontraktu v2:
`fcd136117c0a699a5b31b2553f5940ac95c2b4ffaecf187b7fa5d05ae93e8690`.

Historyczne kontrakty, [raport v1](stage5-results.md), raporty blokady i korpus
pozostały niezmienione. Dawna para `1ab171af...` / `9e5b002...` jest wycofaną
referencją. Kontrola v1 nie jest bramą snapshotu v2; zachowano jej testy jako
regresje. Poprzedni tekst postępu v2 jest w [osobnym archiwum](stage5-progress-v2-before-final.md).

## Dokładna gwarancja i twierdzenia

`RepoProof.SourceBytes.sourceImport` jest zdefiniowane przez ślad przejść po
całych surowych bajtach, akceptację na końcu i zdarzenie importu. Nie używa
dostarczonego grafu, listy eksportera ani przyjęcia certyfikatu. Jawna
specyfikacja obejmuje komentarze, napisy i ucieczki, granice importów, UTF-8,
atrybuty, ścieżki, duplikaty i odrzucenia.

Kernel sprawdza kanoniczne rozpakowanie bloków, każde przejście i pełne zdarzenia
każdego pliku. `source_edge_iff` dowodzi obu kierunków zgodności z grafem.
Sprawdzono pełne i różnowartościowe mapowanie ścieżek/ID, wszystkie 1864 dowody
plików, w tym bez importów, i równość całego grafu z instancją etapu 4. Osobny
audyt dekoduje wszystkie bajty Lean i porównuje pełną treść z tym samym wejściem.

Główne twierdzenia ogólne przyjęte przez kernel:

- `RepoProof.SourceBytes.trace_iff_run`, `run_append`, `checked_sound`, `import_iff_events`;
- `RepoProof.SourceBinding.mapping_injective`, `file_target_iff`, `source_edge_iff`, `source_exact`;
- `RepoProof.AnswerBinding.answer_mem`, `answer_nodup`, `source_to_answer`.

Konkretnie przyjęto `SourceNames.mapping_checked`, wszystkie 1864
`SourceGroupNNN.fID_ok`, `ChromiumSource.source_bound`, `paths_unique`,
`source_to_answer` oraz świeżo `ChromiumFast.accepted`, `erased_accepted`, `exact`.

Końcowe twierdzenie mówi: ścieżka występuje w dokładnie tej liście odpowiedzi
wtedy i tylko wtedy, gdy nazywa wybrany plik z łańcuchem importów do korzenia
w zadeklarowanej relacji źródłowej. Zerowa długość ścieżki włącza korzeń.
Kompozycja używa `fastCheck_exact`, jego mostu do starego checkera i zachowanej
dokładności. Sprawdzono pełną sekwencję oraz brak duplikatów, bez założenia
poprawności ekstraktora jako nowej nieudowodnionej przesłanki.

Audyty dopuszczają wyłącznie standardowe **`propext`, `Classical.choice`,
`Quot.sound`**; końcowe trzy twierdzenia konkretne mają dokładnie te zależności.
Wynik nie jest wolny od aksjomatów. Nie użyto `sorry`, `admit`, `native_decide`,
nowych aksjomatów ani niezweryfikowanego VM/FFI do zamknięcia dowodu.

To dowód **byte import projection**, nie pełnej gramatyki ani systemu typów
Mojom. Pełny przypięty parser osobno operacyjnie odrzuca wadliwe ciała plików;
formalna relacja nie zakłada jego poprawności. Git, hashe, Python, serializacja,
renderer i dostarczenie bajtów pozostają audytowaną granicą IO. Nie jest to
dowód wpływu zmian na zachowanie Chromium.

## Faktycznie wydana odpowiedź

Koperta zawiera pin, zakres, korzeń/ID, kierunek, politykę korzenia, pełne
uporządkowane ścieżki, tożsamości źródła/grafu/certyfikatu/wyniku i odwołanie do
rachunku weryfikacji. Czasy i nonce pozostają poza deterministycznym payloadem.

Osobno powtórzono 37 kanonicznych artefaktów z tego samego wejścia i porównano
pełne bajty. Wydany JSON jest bajtowo równy powtórnie wygenerowanej kopercie.
Zapisany JSON ponownie odczytano ze ścisłą kontrolą kluczy. Niezależny parser
tekstu porównał całe metadane i wszystkie ścieżki. Po wydaniu ponownie sprawdzono
także pełne bajty obu odpowiedzi.

| Artefakt | Bajty | SHA-256 |
| --- | ---: | --- |
| JSON | 29 998 | `9137860015d720b500f5c65c3dd02597ef529a6c3befce8133ccf92a2f092eb8` |
| Tekst | 28 990 | `5fbef7ef17ad7a68256c052699356d5cfa603f4b5a44bdaf162b101234a8f897` |

Prywatnie zachowany seal i nonce wiążą persisted wejścia z przebiegiem. Przy
użyciu ponownie kontroluje się wejścia i skompilowane zależności. Tożsamości
przejrzanego kodu muszą zgadzać się ze stanem początkowym i końcowym. Hashe
chronią tę granicę IO; nie zastępują pełnego porównania semantyki ani dowodu.

## Testy, ataki i przegląd

Końcowy pełny zestaw: **85 testów OK**, 181,223 s według `unittest`. Zachowano
1547 porównań Python–Lean, cykle, izolowane wierzchołki, korzeń i rangi z przerwami.
Testy zgodności programów nie są formalnym dowodem ich równoważności.

| Klasa | Rzeczywisty rezultat / warstwa |
| --- | --- |
| A | Brak pliku, także bez importów: odrzucenie pełnego inwentarza. |
| B | Zmienione bajty z przeliczonymi lokalnymi hashami/OID: odrzucenie względem stałej kotwicy. |
| C | Zły commit/tree: odrzucenie tożsamości wejścia. |
| D | Usunięcie, dodanie i zamiana krawędzi przy tej samej liczbie: odrzucenie pełnej zgodności źródło–graf; nowe certyfikaty grafowe sprawdzono osobno. |
| E | Usunięcie `file_info.mojom → time.mojom`: rzeczywiście 473 wyniki i akceptacja grafowego certyfikatu; kontrola źródłowa odrzuca graf. |
| F | Zamiana etykiet, także zapakowanych nazw Lean bez zmiany ID/liczb: odrzucenie mapowania/bajtów. |
| G | Brak, dodanie, duplikat i zamiana ścieżki: odrzucenie pełnej koperty i tekstu. |
| H | Zmieniony korzeń/polityka włączenia: odrzucenie metadanych instancji. |
| I | Brak/powtórzenie bloków źródła, pliku, dowodu i krawędzi: odrzucenie pokrycia/schematu. |
| J | Komentarze, napisy, ucieczki, atrybuty, duplikaty i legalne formatowanie: właściwe importy bez fałszywych deklaracji. |
| K | Wadliwe ciało, niedomknięte komentarze/napisy, UTF-8, BOM i nieobsługiwana ucieczka ścieżki: jawne odrzucenia parsera/specyfikacji. |
| L | Fizyczna podmiana zapisanego seala między przebiegami oraz zmiana źródła/dowodu po kontroli: odrzucenie przy użyciu. |

Łącznie **46 kontroli A–L**. Osobno kernel sprawdził 17 przypadków leksykalnych.
Testy publicznego preflightu potwierdzają kod niezerowy i brak wydania odpowiedzi
po podmianie. Poprawiono rozróżnianie `false`/`0`, aliasowanie metadanych i
odrzucanie powtórzonych kluczy odpowiedzi tekstowej.

Nie przypisujemy kernelowi odrzuceń wykonanych przez Python/parser/audyt.
Niezależny przegląd objął kompozycję, specyfikację, wszystkie bajty, 1864 dowody,
odpowiedź i driver. Problemy rozwiązano; końcowy przegląd wiąże 21 konkretnych
plików ze stanem rzeczywiście uruchomionego programu.

## Pomiary pojedynczego pełnego przebiegu

`full-03` używa prekompilowanego SDK Lean/Std, ale świeżo kompiluje wszystkie
moduły projektu, mapowanie, 30 grup i master. Nie importuje dowodu z wcześniejszych
przebiegów ani starego `Chromium.olean`. Zachowany test różnicowy dodatkowo
importuje bazowe cache `formal/` i wykonuje VM — jest regresją, nie dowodem.

| Faza | Czas rzeczywisty |
| --- | ---: |
| Pochodzenie/snapshot | 5,886606 s |
| Pełne parsowanie/ekstrakcja | 8,005241 s |
| Porównanie bazy i certyfikat | 0,100951 s |
| Cały capture z pozostałym narzutem | 14,129037 s |
| Generowanie / osobne powtórzenie | 1,713324 / 1,642097 s |
| Świeże zależności, w tym `ChromiumFast` | 20,744432 s |
| Mapowanie ścieżek | 129,647250 s |
| Kernelowe przypadki leksykalne | 2,031399 s |
| Wszystkie grupy, elapsed przy dwóch procesach | 1126,947431 s |
| Zbiorcza instancja z audytem drivera | 116,395925 s |
| Sam proces Lean zbiorczej instancji | 115,960089 s |
| Pełny audyt bajtów/ścieżek | 0,725168 s |
| A–L | 3,730429 s |
| Pełny proces regresji | 181,420258 s |
| Zapis/ponowna kontrola odpowiedzi | 1,604341 s |
| Cały przebieg według zegara drivera | **1602,079343 s** |

Składowe capture zawierają się w jego pełnym czasie. Zegar całości biegnie od
przygotowania katalogów do zakończenia kontroli promowanych odpowiedzi, bez
startu/importów Pythona i końcowego zapisu raportu. Dodatkowy audyt po wydaniu
i redakcja raportu są poza nim. Suma czasów równoległych procesów nie jest
czasem całości. Zakresy surowych pomiarów są w JSON.

Najwyższe szczyty pojedynczego mierzonego procesu (master):
**4 964 487 168 B PeakWorkingSetSize** — rezydentne;
**6 660 345 856 B PeakPagefileUsage** — commit procesu, nie zapis na dysk.
Definicja etapu 4: natywne `GetProcessMemoryInfo`, żądane oczekiwania 20 ms
i udany odczyt po zakończeniu przy otwartym uchwycie. Scheduler może wydłużyć
odstępy. Liczniki nie obejmują dzieci; maksimum procesów nie jest łączną
pamięcią całego równoległego przebiegu.

| Źródło / artefakt | Bajty |
| --- | ---: |
| `ChromiumSource.lean` / `.olean` | 691 407 / 36 170 144 |
| `SourceNames.lean` / `.olean` | 829 019 / 21 525 232 |
| Wszystkie źródła Lean / `.olean` świeżego przebiegu | 25 111 263 / 581 936 720 |

`.olean` zawiera dane, kod i dowody, nie sam term akceptacji. To pojedynczy
pełny pomiar, nie benchmark ani deklaracja przyspieszenia. Historyczne
749,257 → 1,550 s dotyczyło liści kernela i dodania lematów; 9,992150 s było
całym świeżym procesem instancji etapu 4. Cały czas etapu 3 i jego szczyt
pamięci są nieznane, a artefakty etapu 4 wzrosły. Nie powtarzano kosztownego
pełnego dowodu etapu 3 dla pomiarów ani nie porównuje się szybkości różnych
obowiązków.

`full-01` zachowano jako instancję źródłową bez pełnej akceptacji etapu.
`full-02` przerwano przed grupami dla rozdzielenia pomiarów i związania kodu
ze stanem początkowym; logi i [diagnostyka](../verification/stage5-v2-interrupted-02.json)
pozostały zachowane. Tylko `full-03` jest końcowym pełnym przebiegiem.

## Mechaniczna ocena i zachowanie bazy

| Brama | Wynik | Dowód wykonania |
| --- | --- | --- |
| G1 | PASS | 111 plików przed/po, historia etapów 3/4 i cztery archiwa zachowane. |
| G2 | PASS | Kotwica, pełne źródła/obiekty i bajty Lean. |
| G3 | PASS | Świeże 30 grup, 1864 dowody plików i konkretne `source_bound`. |
| G4 | PASS | Świeże `ChromiumFast` i `ChromiumSource.source_to_answer`. |
| G5 | PASS | Pełna sekwencja/Nodup i ponownie odczytane JSON/tekst. |
| G6 | PASS | 85 końcowych testów, 1547 porównań i wszystkie A–L. |
| G7 | PASS | Jedno pełne polecenie w nowym katalogu; pełne powtórne generowanie. |
| G8 | PASS | Audyty, niezależny przegląd i jawna granica twierdzeń/IO. |

Dodatkowy końcowy audyt potwierdził 41 skompilowanych obiektów, pełne odpowiedzi,
111 plików, cztery archiwa, HEAD i historię etapu 3. Archiwów nie rozpakowywano
na implementację. Nie zmieniano globalnego Git, korpusu ani niezwiązanych zmian.

Pozostają założenia: kernel/SDK Lean, standardowe aksjomaty, uczciwe API
systemu/plików/procesów i pamięć weryfikatora, kotwica historii oraz odporność
hashy na kolizje. Kontrole zmian nie pokonują napastnika kontrolującego sam
system albo prywatny oczekiwany stan weryfikatora. Brak dowodu pełnego parsera
i serializacji jest jawny; nie zastąpiono go deklaracją bezwarunkowej gwarancji
całego środowiska.
