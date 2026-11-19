# Dwa łańcuchy R2 przez pięć zmian Electron

## Przypięta historia

Wybrano sześć kolejnych commitów z oficjalnej linii `first-parent` Electron,
kończącej się na dotychczasowym pinie `v38.1.2`. Dla każdego commitu sprawdzono
SHA-1 surowego obiektu, jego drzewo i wartość pierwszego rodzica. Chromium
pozostało przy `3927f129b801f969d4abdb1458d55174cc062723` z zakresem `chrome/`,
a Brave Core przy `38bf45887ca5336841cddb4200e6deee32ce45a8` z pełnym drzewem.
Zakres Electron to pełne drzewo. [Bazowy manifest korpusu](../verification/r2-scale-manifest.json)

| Wersja | Commit Electron | Drzewo Electron | Ścieżki Electron | Ścieżki całego korpusu |
| --- | --- | --- | ---: | ---: |
| A0 | `2d397883a5459557448e6b86cecc1359919cda76` | `341e9d2c74dbf911459e6bb6d795f6d1531d454a` | 2699 | 133 564 |
| A1 | `35639ad8015e1c2dd5cdbf51031dd27ca13a4546` | `f71d8c7047aa5ea6c3e58e0ff89eefe9b69ea23f` | 2699 | 133 564 |
| A2 | `8cd29d24b1be40bb598d909f2b5b808266fa5266` | `07c8780732913c140071179ff7fe5027ac85c3cd` | 2699 | 133 564 |
| A3 | `5e51c882ee25789183771c0173d01aafb9ee96dd` | `07aec82536905a3e425c332a61b3ebefa0b6f782` | 2699 | 133 564 |
| A4 | `f43348e75cf220daec81a7448e6983af88951fdb` | `c7c68ec382f1c1e6526a70fafd57f06c885afd49` | 2699 | 133 564 |
| A5 | `d60ae179985685d75d238ee33e17c15a7b53d703` | `fa2587baa940913befc5d539afef827a695dfb73` | 2700 | 133 565 |

Historię pogłębiono i uzupełniono 35 brakujących blobów w osobnej kopii.
Pobieranie zakończyło się 18 listopada 2026 o 22:01:33 czasu warszawskiego.
Przed pomiarem zamrożono `chrome://` i `140.0.7339.133`. Rozpoznanie po stronie
Electron użyło `git grep` dla wszystkich sześciu wersji. Dla stałych części
korpusu odczytano istniejący indeks. [Zamrożone wersje, literały i rozpoznanie](../verification/r2-history-plan.json)

## Pomiar i łańcuchy

Pomiar odbył się lokalnie po zakończeniu pobierania. Środowisko procesu Git
blokowało pobieranie obiektów na żądanie, a pamięć podręczna systemu plików
była aktywna i nie była czyszczona. Początek próby oznacza dostarczenie
identyfikatora kolejnego commitu danemu wariantowi. Warianty uruchamiano
sekwencyjnie, naprzemiennie zaczynając od aktualizacji lub pełnego skanu.
Przygotowanie manifestu liczy się raz na dwa literały w każdym wariancie.
Pełny skan przygotowuje raz indeks Electron i używa istniejących indeksów
Chromium i Brave Core. Odpowiedzi obu literałów uruchamiano kolejno i mierzono
do powrotu publicznego polecenia po publikacji. Porównania bajtów wykonano
po pomiarze.

Każdy literał zaczyna się od osobnego publicznego `query-verified` dla A0.
W krokach od A2 do A5 podstawą jest opublikowany wynik `update-verified`
z poprzedniego kroku dla tego samego literału. Ścieżka podstawy, jej skrót,
skrót poprzedniego manifestu i skrót wyniku są zapisane w surowych danych.
Pełny skan każdej wersji uruchamiano oddzielnie i porównywano z aktualizacją.

## Wyniki i czas oczekiwania

Oba łańcuchy były ciągłe od A0 do A5. Wszystkie **10 par** `answer.jsonl`
było identycznych bajtowo. `chrome://` miało 5866 trafień we wszystkich
wersjach. Dla `140.0.7339.133` wynik zwiększył się z jednego do dwóch
trafień w A3, gdy pojawiła się ścieżka `electron/electron / DEPS`.
W pozostałych krokach zbiory ścieżek pozostały takie same. Żadna pasująca
ścieżka nie zniknęła, a offset bajtowy i numer wiersza pierwszego trafienia
pozostały takie same na wszystkich zachowanych ścieżkach.

| Wersja A5 | Trafienia | Wspólny SHA-256 aktualizacji i pełnego skanu |
| --- | ---: | --- |
| `chrome://` | 5866 | `ee0dff9794321706a9839589f64b5ba7a678e4e3975df548356b033ac8ab7705` |
| `140.0.7339.133` | 2 | `316793e6dbdd8c339efd9dccb50965108d596abad1c66b64b36233ed1d939a98` |

| Przejście | Zmienione ścieżki | Bajty blobów delty na literał | Bajty blobów delty łącznie | Obie odpowiedzi po aktualizacji [s] | Obie odpowiedzi po pełnym skanie [s] |
| --- | ---: | ---: | ---: | ---: | ---: |
| A0 → A1 | 30 | 178 401 | 356 802 | 2,034 | 18,072 |
| A1 → A2 | 1 | 8 642 | 17 284 | 1,898 | 18,398 |
| A2 → A3 | 3 | 25 559 | 51 118 | 1,849 | 17,924 |
| A3 → A4 | 1 | 11 641 | 23 282 | **2,156** | 18,480 |
| A4 → A5 | 2 | 2 409 | 4 818 | 2,035 | 18,074 |

Liczba bajtów dotyczy surowych blobów faktycznie odczytanych przez
`update-verified`. Wyznaczenie manifestu obejmuje osobny odczyt metadanych
korpusu. Pierwszy start obu pełnych odpowiedzi A0 zajął 20,675 s, w tym
1,523 s na manifest i 4,179 s na indeks Electron.

| Wersja | Wariant | Manifest [s] | Indeks [s] | `chrome://` z publikacją [s] | `140.0.7339.133` z publikacją [s] | Pierwsza odpowiedź od commitu [s] |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A1 | aktualizacja | 0,864 | 0,000 | 0,637 | 0,532 | 1,502 |
| A1 | pełny skan | 0,855 | 4,179 | 6,775 | 6,263 | 11,809 |
| A2 | aktualizacja | 0,837 | 0,000 | 0,552 | 0,509 | 1,389 |
| A2 | pełny skan | 0,868 | 4,182 | 6,951 | 6,396 | 12,001 |
| A3 | aktualizacja | 0,840 | 0,000 | 0,547 | 0,462 | 1,387 |
| A3 | pełny skan | 0,815 | 3,910 | 6,978 | 6,221 | 11,703 |
| A4 | aktualizacja | 0,982 | 0,000 | 0,638 | 0,536 | 1,620 |
| A4 | pełny skan | 0,883 | 4,121 | 6,969 | 6,507 | 11,972 |
| A5 | aktualizacja | 0,892 | 0,000 | 0,585 | 0,558 | 1,477 |
| A5 | pełny skan | 0,848 | 3,948 | 6,984 | 6,293 | 11,780 |

Surowe pomiary zawierają polecenia, manifesty, ciągłe skróty wejścia i wyjścia
dla obu literałów oraz dokładne różnice ścieżek i pozycji pierwszego trafienia.
Hash oryginalnych pakietów Git i indeksów zgadzał się z wcześniejszymi zapisami.
Przeszły **42 testy** w domyślnym katalogu tymczasowym
`C:\Users\User\AppData\Local\Temp`. Nazwy katalogów testowych skrócono do `cln`
i `upd`. [Surowe pomiary, skróty i różnice](../verification/r2-history-measurements.json)

## Odtworzenie w PowerShell

Uruchom z głównego katalogu projektu. Ten wariant korzysta z pobranej kopii
historii oraz z przypiętego planu. Nadaj katalogowi pomiaru nową nazwę.

```powershell
$python = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $python -B -X utf8 -c 'import sys; print(sys.version)'
$env:PYTHONPATH = Join-Path (Get-Location).Path 'local/fineract-r2/deps'
$study = 'local/r2-scale/history-study-01'
$repro = 'local/r2-scale/history-repro-01'

& $python -B -X utf8 scripts/run_r2_history_experiment.py measure `
  --work-dir $study --base-index local/r2-scale/index-01 `
  --plan verification/r2-history-plan.json --run-dir $repro
if ($LASTEXITCODE -ne 0) { throw 'Pomiar lub porównanie nie powiodło się.' }
```

Aby odtworzyć pozyskanie i rozpoznanie, użyj nowego katalogu kopii. `acquire`
pobiera brakujące publiczne obiekty wyłącznie do tej kopii. `freeze` zapisuje
ponownie wybór i wyniki rozpoznania w osobnym pliku.

```powershell
$copy = 'local/r2-scale/history-copy-repro-01'
& $python -B -X utf8 scripts/run_r2_history_experiment.py acquire `
  --sources local/r2-scale/sources --work-dir $copy
if ($LASTEXITCODE -ne 0) { throw 'Pozyskanie historii nie powiodło się.' }
& $python -B -X utf8 scripts/run_r2_history_experiment.py freeze `
  --work-dir $copy --base-index local/r2-scale/index-01 `
  --many 'chrome://' --few '140.0.7339.133' --plan "$copy/plan.json"
if ($LASTEXITCODE -ne 0) { throw 'Rozpoznanie nie powiodło się.' }
```
