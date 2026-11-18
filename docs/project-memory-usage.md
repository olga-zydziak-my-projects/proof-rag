# Lokalna pamięć projektu i rozmów w Fineract R2

## Wybór interpretera

Uruchom ten blok w PowerShell z głównego katalogu `repo-proof-lab`.
Sprawdza on, czy kandydat rzeczywiście uruchamia Pythona 3.10 lub nowszego
z modułem `sqlite3`.

```powershell
$pythonCandidates = @(
  (Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe')
  (Get-Command python.exe -CommandType Application -All -ErrorAction SilentlyContinue).Source
)
$projectPython = $null
foreach ($candidate in $pythonCandidates) {
  if (-not $candidate) { continue }
  try {
    $probe = & $candidate -B -X utf8 -c 'import sqlite3, sys; print(sys.version_info >= (3, 10))' 2>$null
    if ($LASTEXITCODE -eq 0 -and $probe -ceq 'True') {
      $projectPython = $candidate
      break
    }
  } catch { continue }
}
if (-not $projectPython) {
  throw 'Dodaj ścieżkę do działającego Pythona 3.10+ do listy $pythonCandidates.'
}
$memoryCli = 'scripts/project_memory.py'
$memoryDb = Join-Path (Get-Location).Path 'local/project-memory/rozmowy-demo.sqlite3'
```

## Aktywny wynik w dwóch rozmowach

Przykład używa zachowanych wyników `LoanTransaction` i `BigDecimal`.
Jeśli katalogów brakuje, opublikuj oba wyniki w osobnych katalogach i wskaż ich
ścieżki w `$r2Answer` i `$r2Other`. [Instrukcja Fineract R2](fineract-r2-usage.md)

Po publikacji uruchom `otwórz-wynik` i wskaż katalog docelowy użyty w
`query-verified --output-dir`. Możesz podać ścieżkę względną. Pole
`output_directory` w `verification.json` musi wskazywać ten sam katalog
bezwzględną ścieżką. `zapytaj` sprawdza tę lokalizację również przy wznowieniu.

```powershell
$r2Answer = 'local/fineract-r2/run-02/historical/01-03/answer'
$r2Other = 'local/fineract-r2/run-02/historical/01-04/answer'

& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'otwórz-wynik' --rozmowa A $r2Answer
& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'otwórz-wynik' --rozmowa B $r2Other
```

Każde polecenie uruchamia nowy proces Pythona. Po zamknięciu PowerShell wróć
do katalogu projektu i ponownie uruchom blok wyboru interpretera z tą samą
ścieżką do bazy. Wznów rozmowę bez ponownego otwierania wyniku.

```powershell
& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'zapytaj' --rozmowa A 'które z tych plików są testami?'
& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'zapytaj' --rozmowa B 'a które z tych plików są testami?'
```

Rozmowa A zwraca 294 ścieżki spod `src/test/` z 718 trafień dla `LoanTransaction`.
Rozmowa B odpowiada na podstawie wyniku `BigDecimal`. Jawne pytanie o testy
działa przy dowolnym ustawieniu preferencji projektu.

SQLite przechowuje katalog otwarty dla danej rozmowy i odciski SHA-256 obu
plików R2. Pliki zostają w katalogu wyniku. Jeśli zapamiętany wynik jest
niedostępny albo jego pliki się zmieniły, użyj ponownie `otwórz-wynik` w tej
rozmowie i wskaż zweryfikowany katalog.

## Preferencja wyświetlania projektu

```powershell
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
