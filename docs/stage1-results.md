# Wyniki etapu 1 — 9 listopada 2026

Etap 1 jest ukończony w zadeklarowanym zakresie: prototyp grafowy działa,
korpus ma kompletny manifest metadanych oraz całą wybraną treść `.mojom`,
pobranie można wznowić, a kontrakt pierwszego zapytania jest określony.
Nie wyliczono jeszcze pełnego grafu importów Chromium ani odpowiedzi na nim.

## Lokalizacje i pochodzenie

Projekt pozostaje w istniejącym katalogu
`C:\Users\User\Documents\Codex\2026-11-08\nie\outputs\repo-proof-lab`.
Nie znaleziono `AGENTS.md` w tym katalogu, podkatalogach ani katalogach
nadrzędnych. Założono lokalne Git; nie zmieniano konfiguracji globalnej,
nie ustawiano zdalnego repozytorium narzędzia, nie publikowano zmian.
Repozytorium nie ma jeszcze lokalnego commitu; pliki projektu są nieśledzone.
`.gitignore` pomija lokalną konfigurację, cache, duże dane, indeksy i pliki
tymczasowe. Oryginalny prototyp nie wymagał kopiowania.

Dane są poza projektem:

```text
C:\Users\User\Documents\Codex\2026-11-08\nie\outputs\chromium-corpus-27cec857a08a
```

Lokalizacja jest w ignorowanym `local/corpus.json`. Repozytorium źródłowe:
`https://github.com/chromium/chromium`. Faktycznie odczytany commit:
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`; czas commitu
`2026-11-08T23:16:26Z`; główne drzewo
`25131300fa459906dedb84bf592a8537b7848771`.

## Rzeczywiste liczby

| Wielkość | Wynik |
| --- | ---: |
| Wpisy rekurencyjne, razem z katalogami | 564 613 |
| Katalogi, bez katalogu głównego | 46 792 |
| Zwykłe pliki Git | 517 527 |
| Dowiązania symboliczne | 21 |
| Gitlinki, bez rozwijania | 273 |
| Wpisy liściowe | 517 821 |
| Wybrane zwykłe pliki `.mojom` | 1 864 |
| Oryginalne bajty `.mojom` | 6 946 142 |
| Dodatkowe pliki referencyjne parsera | 3 |
| Bajty plików referencyjnych | 50 764 |
| Wszystkie zmaterializowane bajty / unikalne bloby | 6 996 906 / 1 867 |
| Manifest JSON | 126 445 600 bajtów |
| Surowa lista drzewa Git | 73 244 425 bajtów |
| Częściowy magazyn Git po usunięciu porzuconego packa | 21 972 209 bajtów |
| Cały korpus: długości logiczne plików | 228 659 214 bajtów |
| Cały korpus: przydzielona przestrzeń plików | 232 452 160 bajtów, ok. 221,68 MiB |
| Wolne miejsce przed rozpoczęciem prac | 364 057 993 216 bajtów, ok. 339,06 GiB |
| Wolne miejsce w końcowym pomiarze offline | 363 023 056 896 bajtów |

Alokację plików zmierzono na Windows przez
[`FILE_STANDARD_INFO.AllocationSize`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info).
Nie obejmuje ona metadanych systemu plików i wpisów katalogów. Różnica
wolnego miejsca na całym dysku nie jest rozmiarem korpusu: inne procesy
również korzystają z dysku. Nie zmierzono pełnego rozmiaru źródeł Chromium
ani liczby bajtów transportu sieciowego. Podane pobrane bajty to długości
oryginalnych, nieskompresowanych blobów; packi mają inny rozmiar.

| Uruchomienie | Czas | Nowe bloby / bajty materializacji |
| --- | ---: | ---: |
| Zakończona próba przygotowania | 21,257 s | 1 867 / 6 996 906 |
| Końcowe ponowienie z lokalnym cache | 13,313 s | 0 / 0 |
| Końcowa pełna weryfikacja offline | 6,603 s | brak zapisów korpusu |

To pomiary konkretnych uruchomień, częściowo równoległych z testami;
nie są kontrolowanym benchmarkiem wyszukiwania. Czas pierwszej zakończonej
próby nie obejmuje wcześniejszej przerwanej próby ani czasu implementacji.
W początkowej wersji kontrola obecności commitu dopuściła niejawne pobranie
Git. Przerwano je i poprawiono kontrolę na `GIT_NO_LAZY_FETCH=1`.
Po zatrzymaniu procesów usunięto konkretny porzucony `tmp_pack` o długości
848 306 187 bajtów. Pierwszy raport zachowuje historyczny rozmiar logiczny
z tym plikiem; aktualny stan odpowiada raportom ponowienia i offline.
Historyczny pomiar alokacji z pierwszej próby oznaczono jako nieznany:
poprzednio użyte API nie mierzyło alokacji zwykłych plików. Manifest i jego
skrót nie zmieniły się w wyniku tej poprawki.

## Sprawdzone własności

SHA-256 manifestu w przygotowaniu, ponowieniu i sprawdzeniu offline:

```text
1e6fe63490e2007c56b088194f0c2acb61abc834aeefb4edb2bbfe6399bc2e4a
```

Skrypt porównuje wskazany commit i OID drzewa, pełne wyjście `ls-tree -r -t -z`
z osobną listą liści `ls-tree -r -z`, wszystkie wpisy manifestu oraz liczbę
wybranych plików. Każdy opublikowany blob jest sprawdzany względem Git OID
na oryginalnych bajtach, rozmiaru i SHA-256. Ponowienie wykorzystało 1 867
blobów, zażądało z sieci 0 nowych obiektów. `verify` blokuje automatyczne
pobrania Git. Kompletność metadanych i kompletność wybranej treści są osobnymi
polami; `full_chromium_content_complete` pozostaje fałszywe.

Stan bazowy odtworzono samodzielnie: **17 testów Python** oraz sześć twierdzeń
Lean bez aksjomatów; obie manipulacje wynikiem odrzucono. Po zmianach:
**30 testów Python**, w tym 13 testów korpusu, oraz ponownie wszystkie sześć
twierdzeń i demonstracja manipulacji. Testy grafu nadal sprawdzają wszystkie
1 536 kombinacji grafu i korzenia. Plik `formal/Reachability.lean` zachował
identyczny SHA-256 względem stanu bazowego.

Testy korpusu korzystają z rzeczywistych, lokalnych obiektów Git i obejmują:
zwykłe pliki, katalogi, dowiązania, gitlinki, nietypowe nazwy, CRLF, błędny
commit, pominięcia wpisów, zmienione skróty, uszkodzone bajty, awarię transportu,
przerwanie materializacji, wznowienie i niekompletny `.part`. Dwa niezależne
przeglądy objęły kontrakt formalny i implementację pobierania; dodatkowo
porównano liczby z rzeczywistym drzewem Git. To kontrole implementacji,
a nie formalny dowód manifestu lub parsera.

Pełne raporty maszynowe: `verification/baseline.json`, `latest.json`,
`corpus-first.json`, `corpus-repeat.json`, `corpus-offline.json` i
`stage1-summary.json`. Polecenia odtwarzające są w [README](../README.md).

## Co pozostaje do udowodnienia i wykonania

[Kontrakt zapytania](query-contract.md) obejmuje korzeń i odwrotną osiągalność
w grafie zwykłych plików `.mojom` z głównego repozytorium. Warunki importów
nie są ewaluowane; znane cele zewnętrzne są raportowane jako granica zakresu.
Brak treści wewnątrz zakresu, niepewna składnia lub ścieżka wymuszają
`unresolved`. Nie jest to twierdzenie o wpływie zmiany na zachowanie programu.

Formalnie sprawdzono matematyczne warunki certyfikatu grafu. Nadal ufamy Git,
narzędziom odczytu i założeniom kryptograficznym; Python nie ma dowodu
zgodności z Lean. Następny krok to ekstraktor z pełną diagnostyką według
kontraktu, związanie grafu z manifestem oraz osobne pomiary ekstrakcji,
wyszukiwania, certyfikowania i niezależnej weryfikacji. Dowód poprawności
i kompletności ekstrakcji jest osobnym obowiązkiem.
