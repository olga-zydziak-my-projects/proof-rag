# Lokalna pamięć projektu w Fineract R2

Uruchom polecenia w PowerShell z głównego katalogu `repo-proof-lab`.
`$r2Answer` wskazuje zachowany wynik `LoanTransaction`. Jeśli go nie masz,
możesz opublikować odpowiedź w `local/fineract-r2/manual/query-01` i użyć
tego katalogu. [Instrukcja Fineract R2](fineract-r2-usage.md)

```powershell
$projectPython = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $projectPython) {
  $projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
}
$memoryCli = 'scripts/project_memory.py'
$r2Answer = 'local/fineract-r2/run-02/historical/01-03/answer'

& $projectPython -B -X utf8 $memoryCli zapamiętaj --project apache/fineract 'pokazuj pliki testowe osobno'
& $projectPython -B -X utf8 $memoryCli 'pokaż, co pamiętasz' --project apache/fineract
& $projectPython -B -X utf8 $memoryCli 'pokaż-wynik' $r2Answer
& $projectPython -B -X utf8 $memoryCli zapomnij --project apache/fineract
& $projectPython -B -X utf8 $memoryCli 'pokaż, co pamiętasz' --project apache/fineract
& $projectPython -B -X utf8 $memoryCli 'pokaż-wynik' $r2Answer
```

Domyślna baza SQLite znajduje się w `local/project-memory/preferences.sqlite3`
w katalogu `repo-proof-lab`, niezależnie od katalogu uruchomienia CLI. Git
ignoruje `local/`. Aby użyć osobnej bazy, dodaj `--db <ścieżka>` przed nazwą
polecenia. Obsługa pamięci i prezentacja wymagają tylko Pythona 3.10+.

Preferencja jest przypisana do identyfikatora projektu, więc obowiązuje także
po zmianie commitu. `pokaż-wynik` odczytuje identyfikator z potwierdzenia R2,
sprawdza status `VERIFIED` i SHA-256 pliku `answer.jsonl`. Włączona preferencja
wydziela ścieżki, w których `src` i `test` są sąsiadującymi katalogami. Po
usunięciu wpisu CLI znów wyświetla jedną listę wszystkich ścieżek.
