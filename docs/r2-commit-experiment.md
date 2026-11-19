# Aktualizacja odpowiedzi R2 po nowym commicie

## Korpus i zmiana

Eksperyment objął te same 133 565 zwykłych ścieżek z Chromium, Electron i
Brave Core. Punkt wyjścia to opublikowana odpowiedź A dla `chrome://` z
`local/r2-scale/profile-study-01/after/cross-01`. Sprawdzono jej położenie,
status `VERIFIED`, literał, skrót manifestu i SHA-256 odpowiedzi
`9e975031b6e3a6c72f3130f3f69248ae328e14a65046aa4591bf6ccda9a79ced`.
[Manifest A](../verification/r2-scale-manifest.json)

Jedyny nowy commit powstał lokalnie w odizolowanej kopii Electron. Chromium
i Brave Core pozostały przy tych samych przypiętych commitach.

| Electron | Commit | Drzewo |
| --- | --- | --- |
| A | `d60ae179985685d75d238ee33e17c15a7b53d703` | `fa2587baa940913befc5d539afef827a695dfb73` |
| B | `a02e699e313706bceb6ed97219d30d825d73597d` | `ecf75fcf93ce54516b0929965facccae5fc2d0e4` |

- Do `docs/README.md` dodano `chrome://`.
- Z `docs/api/content-tracing.md` usunięto wszystkie wystąpienia literału.
- `docs/tutorial/debugging-main-process.md` przemianowano na `docs/tutorial/debugging-main-process-r2-experiment.md`. Git wykazał `R100`, a blob zachował identyfikator `811c87a20057839f6dfd9446ac8729b564fb4da8`.

[Scenariusz Git](../verification/r2-commit-scenario.json) · [Manifest B](../verification/r2-commit-manifest-b.json)

## Co mierzymy

Każda próba zaczyna się od przekazania tego samego dostępnego identyfikatora
B. Gotowe są lokalne obiekty Git, indeksy A oraz zweryfikowana odpowiedź A.
Manifest B, indeks Electron B i wynik nie są przygotowane dla żadnej próby.
Odtworzenie zapisu eksperymentalnego commitu i przygotowanie izolowanych kopii
źródeł należą do konfiguracji eksperymentu. Czas zegarowy kończy się po
publikacji i wyjściu publicznego polecenia. Pomiar operacji zapytania zaczyna
się po przygotowaniu wymaganych danych B. Kontrole wyników wykonano poza
czasem obu wariantów. Kolejność w trzech parach to delta–pełny, pełny–delta,
delta–pełny. Pamięć podręczna systemu plików była aktywna i nie była czyszczona.

Obie ścieżki ponownie wyznaczają manifest B z lokalnego Git. Obejmuje to
inwentarz ścieżek i sprawdzenie typów oraz rozmiarów blobów. Pełne przeliczenie
buduje indeks Electron B i używa indeksów Chromium i Brave Core bez zmian.
Publiczne `query-verified` równolegle odczytuje pełne przypięte treści
wszystkich trzech repozytoriów i porównuje je z kandydatem z indeksu.

`update-verified` używa wyłącznie zweryfikowanej odpowiedzi A, obu manifestów
i lokalnych obiektów Git. Sam wykrywa różnice, sprawdza skróty commitów i
odmiennych drzew, przenosi świadków z niezmienionych ścieżek i odczytuje
bloby nowych lub zmienionych ścieżek. Odpowiedź zawiera proweniencję B i jest
publikowana atomowo. Potwierdzenie zapisuje metodę aktualizacji i skrót
odpowiedzi A. Pełne `query-verified` jest osobnym sprawdzeniem, a wyniki B nie
są wejściem operacji aktualizacji.

## Wyniki

Każda komórka podaje medianę i zakres trzech prób w sekundach. Oszczędność od
udostępnienia commitu do pełnej odpowiedzi wyniosła **9,889 s**. Dla samego
publicznego polecenia na przygotowanych danych B różnica wyniosła **6,179 s**.

| Etap | Aktualizacja | Pełne przeliczenie |
| --- | ---: | ---: |
| Od commitu do opublikowanej odpowiedzi | **1,372 (1,368–1,397)** | **11,261 (11,175–11,341)** |
| Wyznaczenie manifestu B | 0,830 (0,827–0,849) | 0,839 (0,820–0,858) |
| Przygotowanie indeksu B | 0,000 | 3,638 (3,608–3,783) |
| Zapytanie i publikacja przy gotowych danych B | 0,540 (0,523–0,568) | 6,719 (6,709–6,804) |

Algorytm delty porównał 212 wpisów w zmienianych drzewach Electron. Różnica
objęła cztery zwykłe ścieżki, bo zmianę nazwy obsłużono jako usunięcie i
dodanie. Sprawdzono treść trzech ścieżek w B. Odczytano **trzy bloby o łącznej
treści 10 445 B**, osiem obiektów drzew i dwa obiekty commitów. Łączny odczyt
ładunków tych obiektów wyniósł **30 530 B**. Ta liczba dotyczy delty Git. Koszt
wyznaczenia manifestu dla całego korpusu jest osobno ujęty w tabeli.

Każda z sześciu prób opublikowała `VERIFIED` i **5866 trafień**. Każda pełna
odpowiedź B miała te same bajty, z SHA-256
`3e98fa0a2fbe7c7eae87944ae0c49f0098c3b1500cb80ba4b44d9d131525834f`.
Jawnie sprawdzono obecność `docs/README.md`, brak `docs/api/content-tracing.md`
i starej nazwy oraz dokładnie jedno trafienie pod nową nazwą. Sprawdzono też
5864 zachowane trafienia, świadków dwóch nowych ścieżek i proweniencję wszystkich
rekordów. Oryginalne pakiety Git, przypięte commity, indeksy i odpowiedź A
zweryfikowano względem zachowanych skrótów i pinów.
[Surowe pomiary, komendy i porównania](../verification/r2-commit-measurements.json)

Przeszły 42 testy pamięci i R2. Nowa regresja porównuje bajty aktualizacji
z pełnym publicznym zapytaniem przy stałej liczbie trafień, sprawdza zmianę
ścieżek i commitów oraz odrzucenie bazowej odpowiedzi o zmienionych bajtach.

Powyższa seria używa bezpośrednich kopii istniejących pakietów Git. Wstępna
seria z `alternates` zwróciła identyczne odpowiedzi, z medianami od commitu
2,834 s dla aktualizacji i 18,058 s dla pełnego przeliczenia. Jej pomiary
zachowano oddzielnie. [Wstępna seria](../local/r2-scale/commit-study-02/measure-01/measurements.json)

## Odtworzenie w PowerShell

Uruchom z katalogu projektu z istniejącymi źródłami i indeksami w
`local/r2-scale`. Użyj nowej nazwy katalogu na izolowane kopie i pomiary.

```powershell
$python = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $python -B -X utf8 -c 'import sys; print(sys.version)'
$env:PYTHONPATH = Join-Path (Get-Location).Path 'local/fineract-r2/deps'
$study = 'local/r2-scale/commit-repro-01'
$baseArgs = @(
  '--work-dir', $study,
  '--base-manifest', 'verification/r2-scale-manifest.json',
  '--base-answer', 'local/r2-scale/profile-study-01/after/cross-01'
)

& $python -B -X utf8 scripts/run_r2_commit_experiment.py setup @baseArgs `
  --sources local/r2-scale/sources
if ($LASTEXITCODE -ne 0) { throw 'Tworzenie lokalnego commitu nie powiodło się.' }

& $python -B -X utf8 scripts/run_r2_commit_experiment.py measure @baseArgs `
  --base-index local/r2-scale/index-01 --run-dir "$study/measure"
if ($LASTEXITCODE -ne 0) { throw 'Pomiar lub kontrola bajtów nie powiodły się.' }
```
