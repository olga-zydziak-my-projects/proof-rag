# Zweryfikowane wyszukiwanie R2 w trzech repozytoriach

## Zakres i bajty źródłowe

Electron i Brave Core bazują na Chromium. Ich przypięte konfiguracje wskazują
Chromium 140.0.7339.133, tak jak w etapie 9. Korpus Mojom z tamtego etapu miał
osobny zakres. Lokalne kopie z etapu 9 zawierały część obiektów. Dla tego
przebiegu pobrano przypięte drzewa i bloby do `local/r2-scale/sources`.
Przed pobraniem drzew wolne było 337 767 374 848 B.
[Powiązanie repozytoriów i źródła](stage9-corpus.md)

| Repozytorium | Zakres | Zwykłe ścieżki | Unikalne bloby w repo | Bajty po ścieżkach |
| --- | --- | ---: | ---: | ---: |
| Chromium | cały `chrome/` | 80 782 | 74 089 | 789 787 272 |
| Electron | pełne drzewo | 2 700 | 2 662 | 26 420 423 |
| Brave Core | pełne drzewo | 50 083 | 44 584 | 1 031 524 918 |
| Cały korpus | trzy przypięte drzewa | **133 565** | **121 309** | **1 847 732 613** |

Globalna suma blobów deduplikuje identyczne identyfikatory między repozytoriami.
Ich bajty zajmują 1 787 212 228 B przed kompresją. Zakres obejmuje wszystkie
zwykłe ścieżki w granicach ustalonych przed wyborem literałów. Manifest podaje
również 19 dowiązań symbolicznych i 35 gitlinków poza tą kategorią. Każde
zapytanie odczytuje przypięte obiekty Git lokalnie, bez dociągania braków,
sprawdza SHA-1 ich rzeczywistych bajtów i porównuje ich liczności i rozmiary
z manifestem. [Zamrożony zakres](../verification/r2-scale-scope.json) · [Manifest](../verification/r2-scale-manifest.json)

Kandydat powstaje z indeksów SQLite R2. Jedna odpowiedź JSONL zawiera po jednej
sekcji R2 na repozytorium, także dla zera trafień, oraz wspólny rekord końcowy.
Niezależny odczyt rekonstruuje ścieżki z surowych drzew Git i sprawdza każdy
rekord, jego pochodzenie, pierwszy offset bajtowy i numer wiersza. Kontroler
publikuje zweryfikowaną odpowiedź i potwierdzenie przez jedno przemianowanie
katalogu po zakończeniu nadzorowanego procesu.

## Budowa i rozpoznanie

Budowa zakończyła się w **172,959 s** od startu publicznego polecenia.
Trzy bazy SQLite mają razem **2 572 922 880 B**. Szczyt próbkowanej pamięci
rezydentnej kontrolera i procesów nadzorowanych wyniósł **1 033 183 232 B**
(około 985 MiB), a prywatnej **741 781 504 B**. Kontroler użył Windows Job
Object, a interwał próbkowania wynosił 20 ms. [Surowy pomiar budowy](../verification/r2-scale-build.json)

Oddzielne rozpoznanie odczytało indeks i ustaliło klasy oraz oczekiwane
liczności. Nie wliczono go do czasów zapytań. Nie wykazało plików z sygnaturą
wskaźnika Git LFS. Cztery literały zamrożono przed pierwszym mierzonym
zapytaniem. [Rozpoznanie](../verification/r2-scale-reconnaissance.json) · [Zapytania](../verification/r2-scale-queries.json)

## Czas pełnej odpowiedzi

Każdy literał uruchomiono trzy razy jako osobne publiczne polecenie. Pomiar
zaczyna się przed uruchomieniem procesu i kończy po jego wyjściu z opublikowaną
odpowiedzią. Pamięć podręczna systemu plików była aktywna i nie była czyszczona.
Pierwszy pomiar oznacza pierwszą próbę po budowie i rozpoznaniu. Wszystkie 12
prób uzyskało `VERIFIED`. Powtórzenia tego samego literału dały identyczne
bajty odpowiedzi. [Surowe pomiary](../verification/r2-scale-measurements.json)

| Literał | Chromium / Electron / Brave Core | Razem | Pierwszy [s] | Mediana [s] | Zakres [s] |
| --- | ---: | ---: | ---: | ---: | ---: |
| `BUILD=7339` | 1 / 0 / 0 | 1 | 11,270 | 11,270 | 11,013–11,683 |
| `electron::` | 0 / 277 / 0 | 277 | 11,354 | 11,472 | 11,354–12,200 |
| `chrome://` | 5098 / 13 / 755 | 5866 | 11,743 | 11,743 | 11,659–12,398 |
| `R2_SCALE_ABSENCE_SENTINEL_5F4C9029F1A6` | 0 / 0 / 0 | 0 | 11,177 | 11,103 | 10,663–11,177 |

| Literał | Kandydat z indeksu [s] | Odczyt i skan Git [s] | Porównanie [s] | Publikacja [s] |
| --- | ---: | ---: | ---: | ---: |
| `BUILD=7339` | 0,113 | 10,921 | 0,001 | 0,004 |
| `electron::` | 0,281 | 10,940 | 0,002 | 0,004 |
| `chrome://` | 0,796 | 10,696 | 0,025 | 0,004 |
| `R2_SCALE_ABSENCE_SENTINEL_5F4C9029F1A6` | 0,114 | 10,773 | 0,001 | 0,003 |

Powyżej podano mediany etapów. Najdłużej trwała niezależna weryfikacja
źródeł Git. Odczyt obejmował cały zakres także dla zera trafień. Dodatkowy
czas zegarowy obejmuje uruchomienie i domknięcie nadzorowanych procesów.

## Pominięcie jednej ścieżki

Dla `chrome://` zmieniono w kopii indeksu tylko mapowanie ścieżki
`chromium/chromium / chrome/android/features/dev_ui/dev_ui_module.gni`.
Indeks wskazywał dla niej istniejący blob bez literału. Oryginalne trafienie
ma offset bajtowy 184 i wiersz 6. Kandydat zawierał **5865 zamiast 5866**
trafień. Wszystkie pozostałe rekordy trafień były identyczne bajt w bajt i
w tej samej kolejności. Sekcje i liczniki kandydata przeszły kontrolę składni.

Publiczne `query-verified` sprawdziło ten sam kandydat i zwróciło `MISMATCH`
z kodem **2** i komunikatem `chromium/chromium: result omits 1 Git path(s)`.
Kontroler zakończył pracę w 11,349 s, a katalog docelowy nie powstał. Powtórka na
oryginalnym indeksie zwróciła `VERIFIED` i pełne 5866 rekordów w 11,905 s.
Odpowiedź była identyczna bajtowo z bazową i miała SHA-256
`9e975031b6e3a6c72f3130f3f69248ae328e14a65046aa4591bf6ccda9a79ced`.
Odciski źródłowych pakietów Git i oryginalnego fragmentu indeksu, którego
kopię zmodyfikowano, były identyczne przed próbą i po niej.
[Dowód pominięcia i odzyskania](../verification/r2-scale-omission.json)

Pełne odpowiedzi, skrócony kandydat, logi kontrolera i kopia indeksu są w
ignorowanym `local/r2-scale/measure-01`. Przeszło 40 testów pamięci i R2,
w tym 19 testów R2. Dwa nowe testy sprawdzają zawężony odczyt Git i obowiązkową
sekcję bez trafień.

## Odtworzenie w PowerShell

Uruchom z katalogu `repo-proof-lab`. Przykład korzysta z dostępnego tu
Pythona 3.12 i lokalnego `psutil` 7.2.2. Jeżeli masz już pobrane bloby,
`--sources` może wskazać ten sam katalog źródeł. Nadaj nową nazwę katalogom
budowy, logów i pomiaru.

```powershell
$python = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $python -B -X utf8 -c 'import sys; print(sys.version)'
$env:PYTHONPATH = Join-Path (Get-Location).Path 'local/fineract-r2/deps'
$run = 'local/r2-scale/repro-01'
$sources = "$run/sources"
$manifest = "$run/manifest.json"
$index = "$run/index"

& $python -B -X utf8 scripts/prepare_r2_corpus.py --fetch --sources $sources --manifest $manifest

$buildTime = Measure-Command {
  $build = & $python -B -X utf8 scripts/fineract_r2_corpus.py build `
    --sources $sources --manifest $manifest --index $index --log-dir "$run/build-log"
  if ($LASTEXITCODE -ne 0) { throw ($build -join "`n") }
}
$buildTime.TotalSeconds
$build

& $python -B -X utf8 scripts/run_r2_corpus.py measure --sources $sources `
  --manifest $manifest --index $index --run-dir "$run/measure" `
  --queries verification/r2-scale-queries.json
```

Pojedyncze zapytanie ma tę samą publiczną ścieżkę co powtórzenia oraz próba
pominięcia.

```powershell
& $python -B -X utf8 scripts/fineract_r2_corpus.py query-verified `
  --sources $sources --manifest $manifest --index $index `
  --literal 'chrome://' --output-dir "$run/example-answer" --log-dir "$run/example-log"
```
