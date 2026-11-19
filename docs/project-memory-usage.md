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

## Sesja w jednym procesie

Po otwarciu wyników w rozmowach A i B uruchom sesję z tą samą bazą.

```powershell
& $projectPython -B -X utf8 $memoryCli --db $memoryDb sesja --rozmowa A
```

Wpisz kolejno pytania i polecenia przełączania rozmowy.

```text
a które z tych plików są testami?
/rozmowa B
a które z tych plików są testami?
/rozmowa A
a które z tych plików są testami?
/koniec
```

`/koniec` i koniec wejścia zamykają sesję. Przed wyświetleniem listy program
ponownie czyta aktywny wynik z SQLite i weryfikuje oba pliki R2. Zmiana
aktywnego wyniku przez drugi proces jest widoczna przy następnym pytaniu.
Po błędzie można nadal pytać i przełączać rozmowy.

Opcja `sesja --rozmowa A --interpreter claude` pozwala zadawać pytania
własnymi słowami. Oba znane sformułowania działają lokalnie. Przy pierwszym
innym pytaniu sesja tworzy klienta Anthropic i używa go do końca sesji.

Pomiar można odtworzyć poleceniem poniżej z zainstalowanym SDK `anthropic==2.8.0`.
Skrypt porównuje całe odpowiedzi z opublikowanymi wynikami na osobnej bazie.
Odtwarza zapisane odpowiedzi dostawcy w lokalnym transporcie SDK bez połączenia
z API. Mierzy pierwszą odpowiedź od startu procesu oraz 16 kolejnych do
odebrania ostatniego wiersza.

```powershell
& $projectPython -B -X utf8 scripts/measure_project_memory_session.py
```

## Pytania własnymi słowami

Domyślnie `zapytaj` działa lokalnie i obsługuje dwa ustalone sformułowania.
Opcjonalne `--interpreter claude` i `--interpreter dspy` wysyłają pytanie
oraz instrukcję klasyfikacji do Anthropic API. Odczyt SQLite, sprawdzenie
artefaktów i wyświetlenie ścieżek odbywają się lokalnie.

```powershell
& $projectPython -B -X utf8 -m pip install -r requirements-project-memory-intent.txt
& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'zapytaj' --rozmowa A --interpreter claude 'Daj mi same ścieżki do testów z tego wyniku.'
& $projectPython -B -X utf8 $memoryCli --db $memoryDb 'zapytaj' --rozmowa B --interpreter dspy 'Wyłuskaj z tej zbieraniny testy i wypisz ich pliki.'
```

Tryby eksperymentalne wymagają `ANTHROPIC_API_KEY` w środowisku procesu.
Polecenia wykonują płatną klasyfikację. Zestaw pytań, budżet wspólny dla obu
wariantów i polecenia odtworzenia opisuje [raport eksperymentu](project-memory-intent-results.md).

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
