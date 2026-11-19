# Świeżość odpowiedzi R2 po lokalnym `git push`

Eksperyment objął 133 564 zwykłe ścieżki w trzech repozytoriach. Zakres pozostał taki jak w [eksperymencie historycznym](r2-history-experiment.md). W Chromium obejmował katalog `chrome/`, a w Electron i Brave Core całe drzewa. Electron w A2 i A3 miał po 2699 ścieżek.

| Repozytorium | Gałąź lokalnego serwera | Przed `push` | Po `push` |
| --- | --- | --- | --- |
| Chromium | `chromium-pin` | `3927f129b801f969d4abdb1458d55174cc062723` | `3927f129b801f969d4abdb1458d55174cc062723` |
| Electron | `38-x-y` | `8cd29d24b1be40bb598d909f2b5b808266fa5266` | `5e51c882ee25789183771c0173d01aafb9ee96dd` |
| Brave Core | `brave-pin` | `38bf45887ca5336841cddb4200e6deee32ce45a8` | `38bf45887ca5336841cddb4200e6deee32ce45a8` |

A3 jest oficjalnym commitem Electron i bezpośrednim dzieckiem A2. Lokalny serwer Electron i agent mieli osobne magazyny obiektów. Serwer rozpoczął od A2, a kopia autora wykonała rzeczywisty `git push` na `refs/heads/38-x-y`. Agent nadal miał opublikowany wynik dla A2 bezpośrednio przed drugim pytaniem. Jego magazyn Electron nie zawierał A3. Dwa nieruchome serwery oraz odpowiadające im magazyny agenta korzystały z historycznych obiektów przez alternates. Operacje Git w demonstracji miały dostęp wyłącznie do protokołu `file`.

## Co robi polecenie

`fineract_r2_current.py query` przyjmuje literał i opcjonalnie `--corpus` (domyślnie `default`). Ścieżkę do zaufanej konfiguracji administrator podaje w `REPO_PROOF_CURRENT_CONFIG` lub `--config`. Konfiguracja zawiera źródła `remote`, gałęzie `branch`, tożsamości repozytoriów `repository` i `url`, granice `directories`, katalog stanu `workspace` i opcjonalny `seed_index`. Demonstracja tworzy gotowy przykład `config.json`.

Przy każdym pytaniu `git ls-remote` odczytuje wskazanie każdej gałęzi u jej źródła. Agent zapisuje wybrane identyfikatory w `selection.json` przed pobraniem obiektów. W razie potrzeby pobiera commit po zapisanym SHA. Pytanie kończy się błędem, jeśli brakuje niezbędnych obiektów i pobranie ich ze źródła się nie uda. Dla trzech repozytoriów jest to zestaw kolejnych odczytów na początku pytania, każdy z własnym znacznikiem czasu.

Pierwsza odpowiedź przechodzi przez `query-verified`. Kolejna korzysta z `update-verified`, jeśli dla tego literału i zakresu dostępna jest poprzednia zweryfikowana publikacja. CLI zwraca wszystkie rekordy w tablicy JSON `answer` oraz gałęzie i commity w `selection.repositories`. Każda udana publikacja zachowuje przypięty manifest, wybór wersji oraz pliki `answer.jsonl` i `verification.json`.

Dla tego samego literału i konfiguracji korpusu pierwszeństwo `latest/` wyznacza kolejność odczytów gałęzi u źródeł. Transakcja SQLite porządkuje te odczyty między procesami i nadaje im rosnące numery. Pobieranie obiektów, wyszukiwanie i weryfikacja odbywają się poza blokadą. Po udanej publikacji proces pod tą samą blokadą porównuje numer odczytu z numerem zapisanym w `latest/` i atomowo podmienia wskaźnik tylko przy wyższym numerze. Reguła działa przy płytkiej historii Git. Każda poprawna odpowiedź jest dostępna pod własnym adresem, również gdy `latest/` wskazuje już publikację z późniejszego odczytu.

## Dowód

| Trafienie | A2 | A3 | Pierwsze wystąpienie w A3 |
| --- | --- | --- | --- |
| `brave/brave-core / package.json` | tak | tak | bajt 4153, wiersz 75 |
| `electron/electron / DEPS` | | tak | bajt 66, wiersz 5 |

SHA-256 odpowiedzi A2 to `e87b901f2eadbccf7e4bf09eee5a3370510b3a06c454a265fa11dba35ba5982f`. Odpowiedź A3 była identyczna bajt po bajcie z pełnym równoległym skanem trzech przypiętych repozytoriów. Oba pliki mają SHA-256 `95d22087fbd1848225b535a918ab1f78cd241df2c99260f6f298be301e30dc54`. Skan kontrolny uruchomiono dopiero po publikacji A3, z niezależnie przypiętym manifestem i gotowym indeksem A3. Aktualizacja sprawdziła trzy zmienione zwykłe ścieżki Electron i przeczytała 25 559 bajtów ich blobów.

Po odłączeniu lokalnego źródła Electron identyczne pytanie zwróciło `BLOCKED` z kodem `3` i komunikatem „Nie można potwierdzić bieżącej wersji electron/electron (38-x-y)” z wyjaśnieniem Git. Wskaźnik ostatniej publikacji i poprzednia odpowiedź A3 pozostały dostępne pod tym samym adresem.

## Czasy z przebiegu `fresh-03`

| Etap | Czas |
| --- | ---: |
| Pierwsze pytanie A2 do końca CLI, z przygotowaniem indeksu Electron | 22,989 s |
| Zakończenie `push` do atomowej publikacji A3 | 1,300 s |
| Początek drugiego pytania do atomowej publikacji A3 | 1,241 s |
| Początek drugiego pytania do końca CLI z obydwoma trafieniami | 1,269 s |
| Odczyt trzech gałęzi u źródeł | 0,199 s |
| Pobranie A3 do magazynu agenta | 0,140 s |
| Lokalne przygotowanie i zapis manifestu A3 | 0,274 s |
| Wywołanie `update-verified` z publikacją | 0,493 s |
| Pełne kontrolne `query-verified` z gotowym indeksem A3, do końca CLI | 6,603 s |

Moment publikacji jest rejestrowany bezpośrednio po atomowym przemianowaniu katalogu odpowiedzi. Czasy etapów pomijają część pracy programu, np. uruchomienie interpretera. Aktualizacja A3 użyła opublikowanego wyniku A2 i nie budowała indeksu. Stan systemowej pamięci podręcznej nie był zerowany. To czasy lokalnego serwera Git, a koszt pierwszego pytania obejmuje wykorzystanie gotowych indeksów Chromium i Brave Core. [Surowe pomiary, znaczniki czasu, polecenie `push` i pełne odpowiedzi CLI](../verification/r2-freshness-measurements.json).

## Odtworzenie w PowerShell

Uruchom z katalogu projektu. Skrypt wykorzystuje istniejące `local/r2-scale/index-01` oraz `local/r2-scale/history-study-01`. Tworzy osobny lokalny serwer, kopię autora, stan agenta, wykonuje oba pytania, skan kontrolny i próbę odłączenia serwera.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw "Python nie uruchomił się" }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"

$run = "local/r2-scale/f-" + [guid]::NewGuid().ToString('N').Substring(0, 8)
$measurements = Join-Path $run 'measurements.json'
& $projectPython -B -X utf8 scripts/run_r2_freshness_experiment.py `
    --work-dir $run --measurements $measurements
if ($LASTEXITCODE -ne 0) { throw "Demonstracja świeżości nie powiodła się" }

$env:REPO_PROOF_CURRENT_CONFIG = (Resolve-Path (Join-Path $run 'config.json')).Path
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query '140.0.7339.133'

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current
```

W domyślnym katalogu tymczasowym Windows przeszły wszystkie 43 testy, w tym nowy test z rzeczywistym lokalnym `push`, pełnym skanem kontrolnym i odłączeniem źródła.
