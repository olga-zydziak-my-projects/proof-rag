# Etap 6 — niezależny przegląd

Status końcowego niezależnego przeglądu: **PASS**. Przegląd obejmuje kod oraz
kompletne artefakty przebiegu `local/stage6/full-03`. Jego raport
`verification/stage6-checks-03.json` ma `STAGE6_CHECKS_PASS` i SHA-256
`8bbb063ab84b227a1ab4b31529e1b8233157a518eaf644072eaae1d1474dba88`.
Maszynowy zapis przeglądu, tożsamości 69 przejrzanych plików oraz wyniki
osobnych kontroli zapytań znajdują się w
[stage6-review-final.json](../verification/stage6-review-final.json).

Końcowa akceptacja etapu łączy wynik przebiegu z tym niezależnym przeglądem;
sam napis `PASS` nie zastępuje wskazanych dowodów wykonania.

## Sprawdzona kompozycja

`ChromiumSource.source_bound` nie zależy od korzenia zapytania. Można go użyć
z nowym korzeniem i nowym `EnhancedCertificate`, zachowując dokładnie ten sam
graf, źródła i mapowanie nazw. Eksporter etapu 6 jawnie używa
`ChromiumFast.graph`, tworzy nowy korzeń, tabelę świadków i pełną listę ID.
Nowe `QueryProof.accepted`, `answer_checked`, `paths_unique` oraz
`source_to_answer` wymagają świeżego sprawdzenia konkretnej odpowiedzi.

Lista ścieżek w Lean jest zdefiniowana przez mapowanie całej listy ID przez
uwierzytelnione `SourceNames.names`. Audyt zewnętrzny odczytuje wszystkie ID,
świadków, rangi i wskazania krawędzi oraz porównuje pełny wynik z oczekiwaniami
wywołującego. Nie wystarczają liczebność ani nazwa twierdzenia. Audyt kontroluje
również pełne sygnatury twierdzeń, dozwolone polecenia i opcje Lean.

## Granica ponownego użycia dowodu

Oczekiwane tożsamości importowanych źródeł i 41 obiektów `.olean` pochodzą z
raportu akceptacji zapisanego w commicie
`7cbad10af87dc97bae4b23603921441aa899f7b0`. Manifest cache nie wybiera własnych
oczekiwanych hashy. Sprawdzane są całe bajty i dokładny inwentarz zależności;
nadmiarowe moduły, brakujące pliki, zmiana specyfikacji lub ponowne obliczenie
hashy zmienionego cache nie autoryzują nowej wersji.

Każde zapytanie ponownie kontroluje snapshot i pełne parsowanie źródeł.
Walidacja cache przed i po użyciu porównuje również wszystkie bajty źródeł
zakodowanych w Lean. Źródłowy dowód jest **ponownie używany**, a nie świeżo
wykonywany. Import starego modułu zawierającego także odpowiedź dla
`time.mojom` nie upoważnia do użycia tej starej odpowiedzi dla nowego korzenia.

Zaufane pozostają Git i kotwica historii, implementacja IO i Python,
odporność hashy, pamięć procesu oraz kernel i SDK Lean ze standardowymi
aksjomatami. Sprawdzenie wersji i niezmienności pliku wykonywalnego podczas
zapytania nie jest niezależnym dowodem autentyczności całego SDK. Gwarancja
nadal dotyczy zadeklarowanej projekcji importów bajtowych, nie całej gramatyki
ani zachowania programu Chromium.

Przebieg wymaga prywatnego zaufanego katalogu wykonania bez wrogich równoległych
zapisów do importowanych plików. Kontrole przed i po użyciu wykrywają trwałe
podmiany, ale nie ustanawiają odporności na krótką podmianę i przywrócenie
bajtów całkowicie między kontrolami. Takiej silniejszej gwarancji nie
przypisujemy obecnemu mechanizmowi.

## Odpowiedź i odmowa

JSON wiąże pełną uporządkowaną listę, korzeń/ID, politykę włączenia korzenia,
snapshot i tożsamość dowodu źródłowego. Porównanie kanoniczne odróżnia typy
takie jak `false` i `0`. Odpowiedź tekstowa jest niezależnie parsowana i
porównywana z tymi samymi oczekiwaniami. Po zapisaniu oraz przeniesieniu plików
pod nazwy końcowe ponownie porównuje się pełne bajty.

Niepowodzenie kompilacji, nieznany korzeń i podmiana wejścia nie wydają nowej
odpowiedzi. Awaria końcowego zapisu raportu cofa promocję odpowiedzi; istniejące
katalogi wyników nie są nadpisywane. Założenia dotyczące działającego systemu
plików pozostają jawne.

## Niezależne oczekiwania i wykryte problemy

`scripts/stage6_select_queries.py` nie importuje generatora, checkera ani
eksportera projektu. Wylicza punkt stały przez wielokrotne skanowanie wszystkich
krawędzi, oddzielnie dla każdego z 1864 korzeni. Wybrane 12 zapytań daje
liczebności **477, 1, 1, 2, 2, 5, 10, 20, 50, 100, 240, 423**. Pełne listy
i podsumowanie wszystkich korzeni zapisano w
`verification/stage6-query-selection.json`.

Para dwóch różnych odpowiedzi o liczebności 2 pozwala testować podmianę,
której nie wykryłoby porównanie liczebności. Uwzględniono plik izolowany,
plik importujący inne pliki bez własnych zależnych oraz głęboki łańcuch.
Rzeczywisty graf jest acykliczny; cykle pozostają testami syntetycznymi.

W przeglądzie wykryto i poprawiono: możliwość pominięcia dodatkowej przesłanki
w audycie sygnatury twierdzenia, nieścisłą równość typów w audytorze,
przedwczesne rozwiązywanie aliasów ścieżek przed kontrolą dowiązań oraz brak
wycofania odpowiedzi po awarii końcowego zapisu raportu. Kontrole obejmują
teraz również dodatkowe polecenia Lean mogące zmieniać rozwiązywanie nazw
lub sposób weryfikacji. Odpowiednie regresje przeszły.

W kontrolach cache rzeczywiste utworzenie dowiązania/junction zostało
pominięte po odmowie systemu; osobny test atrybutu Windows reparse point
przeszedł. Końcowy raport zachowuje informację o tym pominięciu.

## Końcowe uzgodnienie dowodów wykonania

Niezależne ponowne odczytanie artefaktów `full-03` potwierdziło:

- wszystkie 12 kompletnych list JSON, tekstowych i list ID Lean zgadza się
  z osobno wyliczonym punktem stałym; korzeń i pełne metadane są zgodne;
- każdy certyfikat spełnia osobno odczytane obowiązki rodziców, rang, korzenia
  i domknięcia po całym grafie;
- 12 procesów nowych dowodów zakończyło się kodem 0; hashe źródeł, obiektów
  `.olean`, raportów i rzeczywiste logi zgadzają się z zapisem wykonania;
- dla każdego zapytania wszystkie cztery wypisane audyty twierdzeń używają
  wyłącznie dopuszczonych standardowych aksjomatów;
- wszystkie 41 modułów cache zgadza się z raportem w stałym commicie etapu 5,
  a źródła programu są zgodne z tożsamościami rzeczywiście uruchomionego kodu;
- osobne powtórzenie zapytania dało identyczne pełne bajty certyfikatu,
  źródła Lean, JSON i odpowiedzi tekstowej;
- odrzucono 28 rzeczywistych podmian oraz błędny korzeń przez publiczne CLI;
- zestaw obejmował **115 testów: 114 przeszło, 1 pominięto** z powodu odmowy
  systemu opisanej powyżej; zachowany test różnicowy rzeczywiście przeszedł
  i obejmuje **1547 przypadków = 512 × 3 + 9 + 2**;
- ponowne porównanie wszystkich 149 zachowywanych plików nie wykazało zmian.

To niezależny przegląd kodu i relacji pomiędzy kompletnymi artefaktami.
Przegląd nie uruchamiał ponownie całego zestawu dowodów ani regresji.

Dodatkowo uzgodniono artefakty końcowego wywołania publicznego CLI w
`local/stage6/cli-final-01`: korzeń
`ash/style/mojom/color_scheme.mojom`, 2 wyniki, `STAGE6_QUERY_PASS`,
28,541031 s. Pełne bajty certyfikatu, źródła Lean i obu odpowiedzi są równe
odpowiadającemu zapytaniu z `full-03`. Rzeczywiste logi, obiekt dowodu i
tożsamości uruchomionego kodu również się zgadzają. To osobna obserwacja poza
czasem pełnego przebiegu, nie dodatkowy nowy korzeń w zestawie 12 zapytań.

## Zachowana nieudana próba

`verification/stage6-checks-01.json` ma `STAGE6_CHECKS_FAILED`, zero przyjętych
zapytań i brak `answer.json`. Pierwsza kompilacja zatrzymała się, ponieważ
zachowana taktyka `ProofTiming` zapisuje względny plik
`local/stage3-proof-progress.txt`, a izolowany katalog procesu nie zawierał
podkatalogu `local`. Poprawka zapewnia każdemu zapytaniu prywatny katalog
`process-cwd/local`, oddzielony od katalogów importowanych modułów. Nie zmienia
twierdzeń ani istniejącej taktyki. Ta nieudana próba nie jest akceptacją ani
częścią pomiarów późniejszego pomyślnego przebiegu.

`full-02` również zachowano jako `STAGE6_CHECKS_FAILED`: 12 zapytań,
powtórzenie, podmiany i ówczesny zestaw 113 testów zakończyły się poprawnie,
ale błędna kontrola raportująca wymagała dosłownego napisu `1547` w wyjściu
unittest. Zachowany test przechwytuje wynik Lean wewnętrznie i nie wypisuje
tej liczby. Poprawiono rozpoznawanie pomyślnego wyniku dokładnie tego testu,
zachowano jego kod i dodano dwa testy raportowania. Pełny stabilny przebieg
akceptacyjny to `full-03`; wcześniejszych prób nie oznaczono wstecznie jako
zaakceptowanych. Dodatkowy nieudany `cli-smoke-01` ujawnił potrzebę jawnego
`--root=<katalog-modułu>` Lean przy izolowanym katalogu procesu; późniejsza
rzeczywista próba CLI oraz cały `full-03` używają poprawionego wywołania.
