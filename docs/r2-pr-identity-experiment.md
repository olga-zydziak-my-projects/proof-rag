**Tak, Electron #1 i Brave Core #1 działały jednocześnie. Tak, aktualizacja Electron pozostawiła commit, gotowy indeks, wskaźniki i bajty odpowiedzi Brave bez zmian.**

## Wynik eksperymentu

Użyto rzeczywistego korpusu 133 565 plików Chromium, Electron i Brave Core. Pełny skan wszystkich bazowych commitów potwierdził zero trafień dla literału `R2_PR_SCOPE_06FCB39166794F25A7451FE6BBEDD677`. Przed oboma zdarzeniami `opened` zrobiono lokalne commity i rzeczywiste `git push`. Każde repozytorium miało swoją gałąź o tej samej nazwie `r2-pr-1`.

| Widok | Pierwsze pytanie | Po drugim `push` i `synchronize` Electron |
| --- | --- | --- |
| Bazowy | 0 trafień | Gałęzie bazowe pozostały na tych samych commitach |
| Electron #1 | `electron-pr-only.txt` | `electron-pr-only.txt`, `electron-pr-second.txt` |
| Brave Core #1 | `brave-pr-only.txt` | `brave-pr-only.txt` |

Pierwsze procesy dla obu widoków rzeczywiście się nałożyły. Oba od razu wybrały `query-checked` i zwróciły `VERIFIED`, korzystając z osobnych indeksów przygotowanych przez zdarzenia `opened`. Odświeżenie Electron zmieniło jego commit z `b3a731fc…` na `50872594…` oraz aktywne pokwitowanie indeksu. W Brave pozostał commit `63522b35…`, identyfikator indeksu `bd72de19670b809c35cadb5810c9e08a980fdcfbad5c6ad024b1cdd2786f1fd4` i SHA-256 pełnej odpowiedzi `b7d76a43d68dc228f9e64edaaf6469a08581613cc0af2a8c7e23d9b68d28f022`.

Każde z siedmiu poprawnych zapytań porównano z niezależnym pełnym skanem Git dla jego wersji. Sprawdzono `VERIFIED`, commity wszystkich trzech repozytoriów, wszystkie rekordy wypisane przez CLI i bajty opublikowanego `answer.jsonl`. Widok Electron zastępował tylko commit Electron, widok Brave zastępował tylko commit Brave, a Chromium w każdym widoku pozostał na `3927f129…`.

Niejednoznaczne `query --pr 1` i zdarzenie `synchronize` z samym numerem zwróciły kod **4**. Komunikat wymienił `brave-core` i `electron`, wskazał opcję `--repo` oraz pole `repository` dla zdarzenia. Pliki `view.json`, `ready.json` i oba zestawy wskaźników `latest` przeszły kontrolę skrótów sprzed i po odrzuceniu. Następne jawnie wskazane zapytania nadal zwróciły właściwe wyniki.

Nowe widoki mają katalog wyznaczony przez korpus, ID repozytorium i numer PR-a. Katalog obejmuje stan agenta, wydania indeksu i blokady. Zapisany widok ze starego katalogu `pr-1` jest rozpoznawany przez jego metadane i dalej korzysta z własnego stanu. Skrócono też nazwy tymczasowych plików SQLite, żeby uwzględnić dłuższą ścieżkę nowego widoku na Windows.

Przeszły **54 testy**, w tym wszystkie 52 dotychczasowe i dwie nowe regresje.

## Odtworzenie w PowerShell

Uruchom z katalogu projektu. Wymagane są istniejące lokalne obiekty z `local/r2-scale/sources`, części wyszukiwarki w `local/r2-scale/index-01`, poświadczone dane `local/r2-scale/checked-01` i zależność `psutil`. Skrypt tworzy nową kopię eksperymentu, wykonuje trzy rzeczywiste lokalne `push` i podaje zdarzenia PR jako JSON na stdin.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw 'Python nie uruchomił się' }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"
$env:GIT_ALLOW_PROTOCOL = 'file'
$env:GIT_NO_LAZY_FETCH = '1'

$run = 'local/r2-scale/pc-' + [guid]::NewGuid().ToString('N').Substring(0, 4)
$raw = Join-Path $run 'measurements.json'
& $projectPython -B -X utf8 scripts/run_r2_pr_identity_experiment.py --work-dir $run --measurements $raw
if ($LASTEXITCODE -ne 0) { throw 'Eksperyment nie zakończył się' }

$env:REPO_PROOF_CURRENT_CONFIG = (Resolve-Path (Join-Path $run 'config.json')).Path
$literal = (Get-Content -LiteralPath $raw -Raw | ConvertFrom-Json).literal
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query --repo electron --pr 1 $literal
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query --repo brave-core --pr 1 $literal
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query $literal

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current test_r2_checked
```

[Surowe wyniki, commity, skróty i polecenia Git](../verification/r2-pr-identity.json).
