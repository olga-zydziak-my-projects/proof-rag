# Czas niezależnej weryfikacji Git w R2

## Metoda

Użyto istniejącego indeksu SQLite oraz tego samego manifestu obejmującego
133 565 ścieżek z Chromium, Electron i Brave Core. Każdy wariant wykonał po
trzy próby każdego z czterech zamrożonych zapytań, pojedynczo i w tej samej
kolejności. Czas zegarowy obejmuje start publicznego `query-verified`, pełną
weryfikację, publikację i zakończenie procesu. Pamięć podręczna systemu
plików była aktywna i nie była czyszczona.
[Korpus i poprzedni pomiar](r2-scale-results.md) · [Zapytania](../verification/r2-scale-queries.json)

Profilowanie stanowi osobny przebieg. `cProfile` mierzy wywołania odczytu
potoku `git cat-file --batch`, kontrolę SHA-1 i wyszukiwanie literału.
Czas odczytu potoku obejmuje wspólnie m.in. pracę Git przy odczycie i
dekompresji oraz czekanie procesu Pythona na dane. Git wytwarza dane w osobnym
procesie, więc jego praca może nakładać się na liczenie SHA-1 i szukanie
literału. Porównanie całej odpowiedzi mierzono osobno zegarem.

## Profil przed zmianą

| Zapytanie | Cały skan [s] | Potok `cat-file` [s] | Kontrola SHA-1 [s] | Szukanie literału [s] | Reszta skanu [s] | Porównanie [s] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `BUILD=7339` | 10,606 | 6,364 | 1,233 | 0,537 | 2,473 | 0,001 |
| `electron::` | 10,933 | 6,209 | 1,240 | 0,987 | 2,497 | 0,002 |
| `chrome://` | 10,661 | 6,334 | 1,245 | 0,585 | 2,497 | 0,023 |
| Literał bez trafień | 10,570 | 6,316 | 1,243 | 0,559 | 2,453 | 0,001 |

Odczyt potoku był największą pozycją we wszystkich próbach. Dla `chrome://`
na Chromium przypadło 5,640 s całego skanu, na Brave Core 4,741 s, a na Electron
0,280 s. Reszta skanu obejmuje m.in. spis i przejście drzew, przygotowanie
żądań Git, obsługę rekordów oraz narzut profilera.
[Surowy profil](../local/r2-scale/profile-study-01/profile-before.json)

Kontroler korpusu uruchamia teraz równolegle do trzech niezależnych skanów Git.
Każdy skan używa tego samego weryfikatora i sprawdza całą przypiętą zawartość.
Porównanie odpowiedzi czeka na wszystkie wyniki i czyta je w kolejności
manifestu. W pomiarze po zmianie `git_scan` oznacza czas zegarowy równoległego
etapu. Czasy skanów poszczególnych repozytoriów mogą się nakładać.

## Pełna odpowiedź przed zmianą i po niej

| Zapytanie | Trafienia | Pierwszy przed [s] | Mediana przed (zakres) [s] | Pierwszy po [s] | Mediana po (zakres) [s] | Oszczędność mediany [s] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `BUILD=7339` | 1 | 10,693 | 10,601 (10,466–10,693) | 6,230 | 6,230 (6,225–6,274) | 4,371 |
| `electron::` | 277 | 10,948 | 10,948 (10,789–10,991) | 6,548 | 6,548 (6,547–6,557) | 4,400 |
| `chrome://` | 5866 | 11,307 | 11,312 (11,307–11,327) | 6,961 | 6,940 (6,848–6,961) | 4,373 |
| Literał bez trafień | 0 | 10,739 | 10,542 (10,497–10,739) | 6,318 | 6,248 (6,174–6,318) | 4,294 |

Mediany pełnego etapu Git spadły z 10,212–10,390 s do 5,903–6,079 s.
Najwyższe próbkowane RSS drzewa procesów wzrosło z 519 do 929 MiB. Wszystkie
24 próby zakończyły się `VERIFIED`. Każda z 12 par plików `answer.jsonl`
była identyczna bajtowo. Potwierdzenia obu wariantów obejmowały wszystkie trzy
repozytoria i te same inwentarze.
[Surowe pomiary przed](../local/r2-scale/profile-study-01/before/measurements.json) · [Surowe pomiary po](../local/r2-scale/profile-study-01/after/measurements.json) · [Porównanie i skróty](../local/r2-scale/profile-study-01/comparison.json)

## Ponowna próba pominięcia

Na kopii indeksu dla `chrome://` pominięto ścieżkę
`chromium/chromium / chrome/android/features/dev_ui/dev_ui_module.gni`.
Kandydat miał 5865 zamiast 5866 rekordów, a pozostałe trafienia zachowały
te same bajty i kolejność. Po optymalizacji publiczne polecenie zwróciło
`MISMATCH` z kodem `2` w 7,044 s. Katalog docelowy nie powstał. Ponowienie
na oryginalnym indeksie w 7,388 s przywróciło pełną odpowiedź identyczną
bajtowo z bazową. Odciski pakietów Git i oryginalnego fragmentu indeksu
zgadzały się w obu przebiegach. Przeszło 41 testów pamięci i R2, w tym
regresja błędu sprzątania po publikacji.
[Dowód próby](../local/r2-scale/profile-study-01/after/omission-evidence.json)

## Odtworzenie w PowerShell

Uruchom z katalogu projektu. Kopia kodu zmierzonego przed zmianą znajduje się
w ignorowanym `local/r2-scale/profile-study-01/reference`. `measure` zapisuje
pełne odpowiedzi, surowe czasy, logi oraz dowód pominięcia i odzyskania
w nowym katalogu wariantu.

```powershell
$python = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $python -B -X utf8 -c 'import sys; print(sys.version)'
$env:PYTHONPATH = Join-Path (Get-Location).Path 'local/fineract-r2/deps'
$reference = 'local/r2-scale/profile-study-01/reference'
$repro = 'local/r2-scale/oracle-repro-01'
$corpusArgs = @(
  '--sources', 'local/r2-scale/sources',
  '--manifest', 'verification/r2-scale-manifest.json',
  '--queries', 'verification/r2-scale-queries.json'
)
$index = 'local/r2-scale/index-01'

& $python -B -X utf8 "$reference/scripts/run_r2_corpus.py" measure @corpusArgs `
  --index $index --run-dir "$repro/before"
if ($LASTEXITCODE -ne 0) { throw 'Pomiar bazowy nie powiódł się.' }

& $python -B -X utf8 scripts/profile_r2_corpus.py @corpusArgs --code-root $reference `
  --answers "$repro/before" --report "$repro/profile-before.json"
if ($LASTEXITCODE -ne 0) { throw 'Profilowanie nie powiodło się.' }

& $python -B -X utf8 scripts/run_r2_corpus.py measure @corpusArgs `
  --index $index --run-dir "$repro/after"
if ($LASTEXITCODE -ne 0) { throw 'Pomiar po zmianie nie powiódł się.' }

foreach ($case in 'single', 'many', 'cross', 'zero') {
  foreach ($trial in '01', '02', '03') {
    $beforeFile = (Resolve-Path -LiteralPath "$repro/before/$case-$trial/answer.jsonl").Path
    $afterFile = (Resolve-Path -LiteralPath "$repro/after/$case-$trial/answer.jsonl").Path
    & fc.exe /b $beforeFile $afterFile
    if ($LASTEXITCODE -ne 0) { throw "Różne odpowiedzi dla $case-$trial" }
  }
}
```
