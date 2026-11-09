# Etap 4 — mniejszy koszt dowodu, ta sama gwarancja

Stan: **ukończony**, 9 listopada 2026. Kernel Lean 4.35.0 przyjął
`ChromiumFast.accepted`, `ChromiumFast.erased_accepted` i `ChromiumFast.exact`.
Pełne dane pozostały identyczne: 1864 węzły, 4419 krawędzi, 477 wyników dla
`mojo/public/mojom/base/time.mojom`. Wynik zawiera korzeń; uniwersum nadal
obejmuje wszystkie 213 izolowanych węzłów. Przeszło **71 testów**. Niezależny przegląd objął most formalny,
pełne pokrycie danych i próby podmian.

Etap 3 utrwalono lokalnym commitem `3184813`. Jego kod, dane i historyczne
raporty zachowano; nie publikowano zmian ani nie zmieniano globalnej
konfiguracji Git. Nowy driver kontroluje ich niezmienność przez SHA-256 przed
i po przebiegu. Treść nowego eksportu porównuje się niezależnie w całości,
bez polegania na samych skrótach i liczebnościach.

Wyniki źródłowe: [mikroeksperymenty](../verification/stage4-microbench.json),
[pełny przebieg](../verification/stage4-checks.json),
[porównanie i definicje pomiarów](../verification/stage4-analysis.json),
[demonstracja podmiany grafu](../verification/stage4-tampering.json).

## Najpierw małe eksperymenty

`scripts/stage4_microbench.py` używa deterministycznego grafu 256 węzłów
i 256 krawędzi, z blokami krawędzi po 32 i świadków po 8. Każdy z 12
przypadków ma trzy świeże procesy dowodowe. Wcześniej kompiluje się jeden
`MicroData.olean`; import tej samej bazy jest jawny w raporcie. Nie importuje
się dowodu Chromium i nie powtarzano drogiego starego pełnego sprawdzenia.

Poniżej mediany **kontroli kernela wraz z dodaniem lematów**, w ms:

| Ten sam obowiązek / zmiana reprezentacji | Baza | Wariant |
| --- | ---: | ---: |
| Szukanie tej samej krawędzi: początek / koniec listy | 1 | 24 |
| Krawędź na końcu: `contains` / sprawdzona pozycja w nazwanym bloku | 24 | 2 |
| 32 późne odczyty: dwa odczyty / pojedynczy odczyt | 12 | 12 |
| 32 późne odczyty: routing liniowy / zbalansowany | 12 | 7 |
| Domknięcie tego samego ostatniego bloku: globalne `take/drop` / bezpośrednio | 31 | 12 |
| To samo bezpośrednie domknięcie, dodatkowo zbalansowany routing | 12 | 8 |
| Całe identyczne domknięcie: globalne dzielenie / łączenie nazwanych bloków | 170 | 62 |

Pierwsza para zmienia kolejność, zachowując dokładnie zbiór krawędzi.
Wariant pozycyjny dowodzi **tego samego** `edgeEnd.contains target = true`
przez sprawdzony element bloku i udowodnioną przynależność bloku do listy.
Pełna zgodność obserwacji dwóch tabel świadków jest sprawdzona przez kernel.
W obu wariantach łączenia celem jest domknięcie całej identycznej listy.
Surowe powtórzenia, cele i czasy całych procesów są w raporcie.

Pojedynczy odczyt nie dał tu mierzalnej poprawy; zachowujemy wynik negatywny.
Wybrano sprawdzane wskazania krawędzi, bezpośrednie bloki oraz zbalansowane
drzewa odczytu. Nie zakładano, że tablice szybkie w VM będą szybkie w kernelu.
Rozdzielczość zegarów wewnętrznych wynosi 1 ms; trzy powtórzenia na małych
danych nie są stabilną gwarancją wydajności. Nie wymuszano izolacji CPU.

## Reprezentacja i formalny most

Nowy moduł [FastChecker.lean](../formal/FastChecker.lean) zachowuje `Fin n`
i oryginalny kierunek importer → importowany. `BlockedGraph.blocks` jest
listą rzeczywistych list krawędzi. `eraseGraph` spłaszcza ją do starego grafu.
`EnhancedCertificate.entries` jest funkcją na wszystkich `Fin n`.
Świadek zawiera rodzica, rangę oraz opcjonalną parę `(blok, pozycja)`.
Korzeń wymaga rodzica równego sobie, rangi zero i braku wskazania. Pozostałe
wyniki muszą mieć wskazanie rzeczywistej krawędzi `(v, parent)`.

`edgeHint` wykonuje **dwa bezpieczne odczyty `getElem?`** i porównuje
otrzymaną parę z oczekiwaną krawędzią. Brak bloku lub pozycji daje odrzucenie,
bez modulo, domyślnego wierzchołka ani zaufanego indeksu. To nadal odczyty
list, a nie operacja o udowodnionym stałym koszcie. `edgeHint_sound` wyprowadza
przynależność znalezionej krawędzi do rzeczywistego spłaszczonego grafu.

`fastLocalCheck` odczytuje rekord rodzica raz; wymaga jego obecności i
ściśle mniejszej naturalnej rangi. `fastCheck` sprawdza niezależny korzeń,
wszystkie indeksy `List.range n` oraz domknięcie **każdego rzeczywistego bloku
i każdej jego krawędzi**. Zachowane są cykle grafu i rangi z przerwami.

Udowodniono:

```text
fastCheck g root enhanced = true
→ check (eraseGraph g) root (eraseHints enhanced) = true
```

To `fastCheck_refines`. `fastCheck_exact` stosuje ten most i istniejące
`check_exact`, a więc również `exact_dependents`. Nie przyjmuje poprawności
świadków jako niezweryfikowanej przesłanki. Nie twierdzimy odwrotnej
równoważności: poprawne stare świadki z uszkodzonym wskazaniem są odrzucane.

`all_range'_split` łączy bezpośrednio małe zakresy `range' start length`,
bez wielokrotnego odcinania globalnych prefiksów. `all_cons_true` łączy
kontrole nazwanych bloków. `fastCheck_of_parts` wyprowadza cały Boolean z tych
części. W nowym pełnym dowodzie jest 103 liści: korzeń, 32 zakresy indeksów
i 70 bloków krawędzi. Nie pominięto żadnego obowiązku.

`ChromiumFast.erased_accepted` otrzymuje przyjęcie przez stary checker
**przez zastosowanie mostu**, bez ponownej redukcji starego pełnego checkera.
`ChromiumFast.exact` wyprowadza dokładność z `fastCheck_exact`.
Nie użyto `sorry`, `admit`, `native_decide` ani dodatkowych aksjomatów.
Jawne audyty ogólne i konkretne są w pełnym raporcie. Trzy twierdzenia
instancji korzystają z `propext`, `Classical.choice`, `Quot.sound`;
nie opisujemy ich jako wolnych od aksjomatów.

## Pełne dane i odporność

`scripts/export_stage4.py` tworzy osobny `formal/ChromiumFast.lean`.
Ścieżki i krawędzie pozostają w pełnych, uporządkowanych blokach; nowa tabela
świadków ma zbalansowane drzewa z dokładnie jedną pozycją dla każdego ID.
Eksport używa niezmienionej, ścisłej walidacji serializacji etapu 3.
Powtórzenie eksportu dało identyczne bajty całego nowego pliku.

Niezależny `scripts/review_stage4_binding.py` parsuje rzeczywisty tekst
nowego eksportu, sprawdza pełne pokrycie drzew i odwołań do bloków,
rodziców, rangi, wynik, korzeń oraz wszystkie 476 wskazań. Stary i nowy plik
Lean są porównane w całości z tymi samymi pełnymi artefaktami etapu 2;
te dwie pełne równości ustanawiają zewnętrzną zgodność z etapem 3.
Nie ograniczono porównań do hashy ani liczebności.

71 testów zachowuje wszystkie 67 dotychczasowych. Nowe testy obejmują:
błędny blok i pozycję; prawidłową pozycję wskazującą złą krawędź; brak
wskazania i niedozwolone wskazanie korzenia; pominięte/powtórzone bloki;
niepełną tabelę; rodzica, rangę, korzeń oraz fałszywy/pominięty wynik.
Wykonano także 13 małych obserwacji nowego checkera w Lean oraz dotychczasowe
1547 porównań Python–Lean. Zgodność programów pozostaje testem.

Pominięte lub powtórzone **dane grafu** odrzuca audyt względem oczekiwanej
pełnej instancji. Sam checker dotyczy grafu będącego jego wejściem.
Zachowana demonstracja usuwa krawędź przed wygenerowaniem nowego certyfikatu:
Python przyjmuje zmieniony graf i 473 wyniki, a warstwa źródłowa wykrywa
podmianę. Optymalizacja nie zmienia tej granicy.

## Końcowy pojedynczy przebieg i porównanie

Przed świeżym procesem instancji skompilowano osobno `Reachability`,
`Checker`, `ProofTiming` i `FastChecker` (ich czasy i hashe `.olean` są
w raporcie), używając prekompilowanych bibliotek Std/Lean przypiętego SDK.
**Nie importowano `Chromium.olean`.** Proces instancji czytał cały nowy plik
źródłowy i świeżo sprawdzał dane, ograniczenia ID, wszystkie liście oraz
końcowe dowody. Brak opcji incremental i brak importu własnego gotowego
`ChromiumFast.olean` w tym pomiarze. Późniejszy pomiar VM importował już
gotowy nowy `.olean`; jest osobnym wykonaniem, nie dowodem.

| Pomiar | Etap 3 | Etap 4 |
| --- | ---: | ---: |
| Cały świeży proces instancji Lean | nieznany | **9,992150 s** |
| Suma konstrukcji termów liści | 81 ms / 161 liści | 25 ms / 103 liście |
| Suma kontroli kernela + dodania lematów liści | 749 257 ms | **1 550 ms** |
| Checker w VM + wypisanie `true` | 1,501 s | 1,730 s |
| Cały proces VM | 3,279 s | 3,242847 s |

Zgodnie zdefiniowana suma kontroli liści spadła około **483 razy**.
To **nie** jest przyspieszenie całego procesu: pełnego czasu bazowego nie
znamy. Obie sumy liści pomijają elaborację danych, dowody ograniczeń ID,
importy i końcowe składanie dowodu; cały nowy proces je obejmuje. Zegar
liści i `mkAuxLemma` pozostały niezmienione. Sumy bardzo krótkich konstrukcji
są bliskie rozdzielczości zegara i nie służą do wyliczania osobnego speedupu.
W pojedynczym pomiarze VM nie stwierdzono poprawy; celem była redukcja kernela.

Szczytowe wartości nowego procesu instancji:

- **1 509 036 032 B** (1439,129 MiB) `PeakWorkingSetSize`: rezydentna pamięć
  procesu według natywnego licznika Windows.
- **2 869 403 648 B** (2736,477 MiB) `PeakPagefileUsage`: szczytowy commit
  procesu, nie rozmiar zapisu na dysk ani sama pamięć rezydentna.

`GetProcessMemoryInfo` odczytywano między żądanymi oczekiwaniami 20 ms
i po zakończeniu, z nadal otwartym uchwytem procesu. Scheduler może wydłużyć
odstępy. Końcowy odczyt powiódł się, więc natywne liczniki szczytu obejmują
cały czas życia procesu, a nie tylko próbki bieżącego working setu.
Nie obejmują innych procesów. W surowym polu `memory.scope` sformułowanie
`<=20ms` oznacza żądany interwał, nie gwarancję schedulera; dokładną definicję
zapisano także w raporcie porównawczym. Bazowego szczytu nie znamy i nie
wyliczamy redukcji pamięci. Zegar całego procesu obejmuje otwarcie logów,
`Popen` i oczekiwanie na zakończenie; odczyt/dekodowanie logów jest poza nim.

| Plik źródłowy / artefakt | Bajty |
| --- | ---: |
| Bazowy `Chromium.lean` | 520 972 |
| Nowy `ChromiumFast.lean` | 579 802 |
| Bazowy `Chromium.olean` | 16 318 760 |
| Nowy `ChromiumFast.olean` | 17 399 344 |
| Nowy ogólny `FastChecker.lean` / `.olean` | 7 470 / 348 408 |

Źródło instancji wzrosło o około 11,3%, a `.olean` o 6,6%. `.olean` zawiera
dane, kod i dowody, nie wyłącznie term przyjęcia. Nie obiecujemy zmniejszenia
artefaktu. Pełny wynik jest pojedynczą obserwacją na tym komputerze, nie
stabilną gwarancją wydajności ani benchmarkiem całego agenta.

## Odtworzenie

Z katalogu projektu, po ustawieniu `$py` i `$lean` jak w głównym README:

```powershell
# Małe powtórzenia; wybierz nieistniejący plik raportu:
& $py scripts/stage4_microbench.py --lean $lean --repeats 3 `
  --report local/stage4/microbench-recheck-01.json

# Cała nowa instancja, pomiary pamięci/czasu, audyty, testy i demo źródłowe:
& $py scripts/check_stage4.py --lean $lean `
  --report local/stage4/recheck-01.json
```

Driver pomiarowy wymaga Windows i nie wymaga dodatkowych pakietów Pythona.
Potrzebne są lokalne artefakty etapu 2 oraz korpus do demonstracji źródłowej.
Istniejący raport jest odrzucany przed rozpoczęciem pracy; do kolejnego
przebiegu wybierz nową nazwę. Dane i dowód nowej instancji można odtworzyć
osobno przez `export_stage4.py`, `review_stage4_binding.py` i
`lean -o formal/ChromiumFast.olean formal/ChromiumFast.lean`, po kompilacji
modułów ogólnych i ustawieniu `LEAN_PATH=formal`.

## Pozostałe granice

Nie dowiedziono parsera Mojom, ekstrakcji, Git/manifestu/hashy, eksportera,
mapowania ścieżek, powiązania wyświetlanej odpowiedzi ani zgodności Pythona
z Lean. Pełny audyt mapowania jest kontrolą zewnętrzną. Formalny most
rozwiązuje wyłącznie związek nowego checkera z już dowiedzioną gwarancją
względem dostarczonego grafu. Nie dodano LLM, Soufflé ani Magic Sets.
