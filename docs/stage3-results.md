# Etap 3 — wykonywalny checker Lean

Stan: **etap ukończony**, 9 listopada 2026. Kernel Lean 4.35.0 sprawdził
ogólne `RepoProof.check_exact` oraz pełne `Chromium.accepted` i
`Chromium.exact`. Końcowe 67 testów przeszło, w tym 1547 porównań Python–Lean.
Raport: [stage3-checks.json](../verification/stage3-checks.json);
transkrypt kernela: [stage3-kernel.txt](../verification/stage3-kernel.txt).

## Model i twierdzenie

`formal/Checker.lean` zawiera czysty `check`. Uniwersum `Fin n` zachowuje
wszystkie węzły, także izolowane. Graf to lista oryginalnych krawędzi
importer → importowany. Certyfikat to funkcja `Fin n → Option Witness`, zawierająca `none`
lub jednego świadka `(parent, rank)` na węzeł. Typ eliminuje duplikaty
rekordów; rangi mają typ `Nat`, identyfikatory mają jawny dowód ograniczenia.
Korzeń jest niezależnym argumentem. Jego Pythonowe `parent=null` kodujemy
jako `parent=root`, z rangą zero.

Checker kontroluje obecność korzenia, każdego świadka i wszystkie krawędzie.
Przechodzi po `List.range n`; `indexCheck` tworzy `Fin n` wyłącznie z dowodem
`i < n`, a niepoprawny indeks odrzuca. Dowód pokrycia używa `List.mem_range`.
Rodzic musi być wynikiem, istnieje oryginalna krawędź do niego, a jego ranga
jest ściśle mniejsza. Rangi nie muszą być kolejne ani opisywać najkrótszej
ścieżki. Cykle grafu są dozwolone, cykliczne uzasadnienia świadków odpadają.

`RepoProof.check_exact` wyprowadza z `check g root c = true` dokładnie
przesłanki `RepoProof.exact_dependents`, następnie stosuje to twierdzenie.
Nie zakłada poprawności świadków. Wynik jest równoważny
`Reach (ReverseEdge Import) root v`: oryginalnie v ma ścieżkę do root.
Poprawny zbiór z uszkodzonymi świadkami może zostać odrzucony; nie dowodzimy
równoważności akceptacji z samą dokładnością zbioru.

Sześć dotychczasowych twierdzeń pozostało bez zmian i bez aksjomatów.
Audyt nowego dowodu wykazuje standardowe `propext`, `Classical.choice`,
`Quot.sound`, wynikające z użytych taktyk upraszczania. Nie dodano własnych
aksjomatów. Nie użyto `sorry`, `admit` ani `native_decide`.

## Serializacja i konkretne dane

`scripts/export_stage3.py` i `src/repo_proof/lean_export.py` walidują JSON
oddzielnie od twierdzenia o poprawnie typowanych danych. Odrzucają powtórzone
klucze JSON, duplikaty węzłów/krawędzi/rekordów, obce identyfikatory,
nieprawidłowe schematy, ujemne rangi i wartości logiczne w miejscu rang.
Nie ma modulo ani zastępowania błędnego identyfikatora wartością domyślną.
Domyślna ranga zero dla `none` w definicji matematycznej nie naprawia wejścia:
warunek obecności rodzica jest sprawdzany niezależnie.

`formal/Chromium.lean` zawiera pełną tabelę 1864 ścieżek (w tym 213 węzłów
izolowanych), wszystkie 4419 krawędzi, jawny korzeń o numerze 995 i wszystkich
477 świadków. Eksport jest deterministyczny. Oddzielny
`scripts/review_stage3_binding.py`, napisany w niezależnym przeglądzie,
parsuje rzeczywiste literały Lean i porównuje całą zawartość z `local/stage2`,
a nie tylko liczebności lub hashe eksportera. Porównuje też `extraction.graph`
i `query.result`, a wynik odtwarza przez niezależny punkt stały. Testy podmian
obejmują korzeń, rozmiar uniwersum, ścieżkę, rodzica i rangę.

`Chromium.accepted` zostało sprawdzone przez kernel. `Chromium.exact`
stosuje ogólne `check_exact` do tego dowodu. Audyt obu jest częścią polecenia
Lean. Samo `--run`, zewnętrzny audyt i testy nie są tym dowodem.
Oba twierdzenia instancji mają dokładnie zależności `propext`,
`Classical.choice`, `Quot.sound`. `member` i `rank` nie mają aksjomatów,
`all_split` używa `propext`; pełne listy pozostałych deklaracji są w raporcie.

Dane są podzielone na jawne bloki do 64 pozycji. Niezależny audyt wymaga
każdego bloku dokładnie raz, we właściwej kolejności, oraz pełnego pokrycia
funkcji świadków i poprawnych granic jej rozgałęzień. `all_split` dowodzi
rozbicia kontroli całej listy na `take` i `drop`; każdy liść nadal sprawdza
kernel, bez pominięcia węzłów lub krawędzi.

## Weryfikacja i pomiary

Pełne polecenie odtwarzające: `scripts/check_stage3.py --lean <lean.exe>`.
Wymaga Lean 4.35.0, Pythona, lokalnych artefaktów etapu 2 oraz korpusu do
demonstracji kontroli źródłowej. Raport zapisuje w
`verification/stage3-checks.json`; nieudana kontrola nie daje `complete=true`.

`ProofTiming.lean` używa tego samego budowania termu i `mkAuxLemma`, co
`decide +kernel` w Lean 4.35.0. Osobno mierzy konstrukcję termu oraz
synchroniczną kontrolę kernela wraz z dodaniem pomocniczego lematu do
środowiska. Późniejszy dowód odwołuje się do sprawdzonego lematu.
Nie jest to zaufane obliczenie natywne. `RunChecker.lean` wykonuje Boolean
w VM Lean; jego wewnętrzny zegar obejmuje checker i wypisanie wartości,
bez importu modułów i startu procesu. Czas całego procesu jest osobną miarą.

Kontrole wykonano oddzielnymi rzeczywistymi poleceniami; raport wskazuje
ten sposób uruchomienia. `check_stage3.py` odtwarza całą sekwencję od początku.
Pojedynczy pomyślny przebieg na tym komputerze dał:

| Pomiar | Czas | Dokładny zakres |
| --- | ---: | --- |
| Eksport | 0,020616 s | Odczyt JSON, walidacja, generowanie i zapis Lean; bez startu Pythona |
| Proces eksportera | 0,068028 s | Cały proces Pythona |
| Niezależne porównanie pełnych danych | 0,351574 s | Cały proces audytu |
| Checker w VM Lean | 1,501 s | Wywołanie checkera i wypisanie `true` |
| Proces `lean --run` | 3,279 s | Importy, uruchomienie i wykonanie programu |
| Konstrukcja 161 termów liści dowodu | 0,081 s | Suma wewnętrznych zegarów, rozdzielczość 1 ms |
| Kernel 161 liści + dodanie lematów | 749,257 s | Suma synchronicznych kontroli `mkAuxLemma` |
| Moduł ogólnego checkera | 0,813 s | Cały proces Lean, wraz z elaboracją i kontrolą |
| 67 testów | 167,637 s | Wewnętrzny zegar unittest, 1547 porównań różnicowych |

Czasy liści nie obejmują dowodów ograniczeń identyfikatorów w danych,
elaboracji danych, importów ani końcowego połączenia przez `all_split`.
Te obowiązki również sprawdził kernel w zakończonym uruchomieniu; nie
przypisujemy im osobnego wyizolowanego czasu. Nie należy traktować dwóch
sum liści jako pełnego czasu procesu Lean. Wcześniejsze przerwane próby
o dużym zużyciu pamięci nie są akceptacją ani częścią tych pomiarów.

Powtórny eksport trwał wewnętrznie 0,023243 s i dał identyczne bajty całego
pliku Lean; porównano je również z plikiem użytym w pomyślnej kompilacji.
Końcowe kontrole wykazały `complete=true`. Nie stosowano timeoutu jako
zamiennika wyniku i nie uznano wykonania programu za dowód kernela.

Testy różnicowe porównują Python i Lean dla 1536 kombinacji małego grafu
z korzeniem oraz przypadków błędnych świadków, brakującego i fałszywego
wyniku, braku korzenia, cykli i rang z przerwami. Sprawdzają też podmianę
jawnego korzenia i grafu. Zgodność dwóch implementacji pozostaje testem,
a nie formalnym dowodem zgodności Pythona z Lean.

Demonstracja usunięcia krawędzi przed wygenerowaniem certyfikatu jest
zachowana w `verification/stage3-tampering.json`. Checker grafowy przyjmuje
zmieniony graf i 473 wyniki; odtworzenie grafu ze źródeł wykrywa podmianę.

## Nadal zaufane granice

Twierdzenie dotyczy dokładnie danych Lean i relacji importów w tym grafie.
Nie dowodzi parsera Mojom ani ekstrakcji, Git/manifestu/hashy, eksportera
ani mapowania ścieżek, odczytu plików i wyświetlanej odpowiedzi. Niezależny
audyt pełnej treści zmniejsza ryzyko błędu związania danych, lecz nie jest
formalnym dowodem eksportera. Ufamy kernelowi Lean i wymienionym standardowym
aksjomatom logicznym. Pythonowy checker nadal nie ma dowodu równoważności
z Lean. Zapytanie nie dowodzi wpływu zmiany na zachowanie Chromium.
Nie dodano LLM, Soufflé, Magic Sets ani nowego cache.

Stan etapu 2 utrwalono lokalnym commitem `792f27d`. Nie publikowano zmian
ani nie zmieniano globalnej konfiguracji Git.
