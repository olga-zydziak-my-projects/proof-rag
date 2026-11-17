# Pilotaż wyszukiwania literałów w Apache Fineract

**PASS — 8/8 zapytań.** Dla każdego zapytania niezależny odczyt obiektów Git
potwierdził pełny zbiór ścieżek, identyfikatory blobów, pierwsze offsety bajtowe
i numery wierszy. Siedem odpowiedzi zawierało trafienia. Sentinel zwrócił pusty
zbiór. Trzy powtórzenia zwróciły te same bajty JSONL dla każdego zapytania.
[Kontrakt v1](fineract-r1-contract.json) ·
[Podsumowanie maszynowe](../verification/fineract-r1/summary.json) ·
[Raport niezależnego weryfikatora](../verification/fineract-r1/verification.json)

## Zakres

Commit `d63beed7ccfeadaffa0c7842b1011bc88451376f` wskazuje drzewo
`04e7b93943ea30b4557d651fd0e6ef6e98f61c0d`. W drzewie naliczono 8 637
ścieżek typu blob i zero gitlinków. Indeks obejmuje wszystkie 8 635 zwykłych
plików, 8 609 unikalnych blobów i 96 188 447 bajtów po deduplikacji.
Sprawdzono SHA-1 każdego bloba i uzgodniono z Git pełne zbiory ścieżek
i identyfikatorów blobów. Wyszukiwanie obejmuje również testy, konfiguracje,
pliki binarne i ewentualne wskaźniki LFS w postaci zapisanej w Git.

Inwentarz odnotował dwa dowiązania symboliczne wyłączone z wyszukiwania.

| Ścieżka | Identyfikator bloba dowiązania |
| --- | --- |
| `.claude/skills/fineract-database` | `55f9dc105ec3cf0e7b722d66b24caa5e323ec816` |
| `.claude/skills/fineract-testing` | `74f01001197acc7536c56852a75b3649d460ade0` |

## Pomiary i kompletne odpowiedzi

Budowa lokalnego indeksu SQLite zajęła **19,06 s** bez pobierania Git
(19,22 s z narzutem uruchomienia CLI). Indeks ma **159 535 104 B**
(152,14 MiB). Szczytowy zbiór roboczy procesu budowy wyniósł **140,11 MiB**,
a największy spośród procesów zapytań **27,48 MiB**. Te pomiary pamięci
obejmują proces Pythona wraz z SQLite. Niezależny odczyt Git dla wszystkich
ośmiu zapytań zajął **0,94 s**, a pełna weryfikacja z porównaniem plików
wynikowych **1,05 s**.

| Literał i kompletna odpowiedź JSONL.gz | Trafienia | Bloby sprawdzone | Wyszukiwanie pierwsze / średnia powtórzeń (ms) | CLI pierwsze / średnia powtórzeń (ms) |
| --- | ---: | ---: | ---: | ---: |
| [`Loan`](../verification/fineract-r1/01.jsonl.gz) | 3 218 | 3 220 | 126,7 / 115,3 | 263,2 / 246,1 |
| [`loan`](../verification/fineract-r1/02.jsonl.gz) | 3 613 | 3 627 | 132,0 / 130,2 | 270,1 / 260,2 |
| [`LoanTransaction`](../verification/fineract-r1/03.jsonl.gz) | 718 | 765 | 53,6 / 55,1 | 172,3 / 176,4 |
| [`BigDecimal`](../verification/fineract-r1/04.jsonl.gz) | 1 362 | 1 362 | 40,8 / 48,7 | 159,5 / 168,8 |
| [`org.apache.fineract`](../verification/fineract-r1/05.jsonl.gz) | 7 347 | 7 344 | 107,6 / 115,3 | 243,0 / 259,4 |
| [`tenant_id`](../verification/fineract-r1/06.jsonl.gz) | 7 | 46 | 17,4 / 18,5 | 134,8 / 138,4 |
| [`.`](../verification/fineract-r1/07.jsonl.gz) | 8 575 | 8 609 | 148,1 / 147,3 | 296,7 / 298,6 |
| [`R1_ABSENCE_SENTINEL_9F807CD3`](../verification/fineract-r1/08.jsonl.gz) | 0 | 0 | 3,8 / 4,4 | 125,4 / 114,5 |

Pomiary z 17 listopada 2026 wykonano na Intel Core Ultra 9 275HX
(24 procesory logiczne, 32 GiB RAM), Windows 11, Python 3.12.14,
Git 2.55.0.windows.2 i SQLite 3.53.1. Dla każdego literału wykonano jedno
zapytanie w pierwszym przejściu po budowie i trzy w kolejnych przejściach,
w tej samej kolejności. Każde uruchomienie użyło nowego procesu. Pamięci
podręcznej systemu plików nie czyszczono. Czas wyszukiwania kończy się po
ustaleniu dopasowań w blobach. Czas CLI obejmuje także uruchomienie procesu,
przypisanie ścieżek, serializację JSONL, `fsync` i publikację pliku.
Kompresję archiwów i weryfikację wykonano poza pomiarem CLI.
Literały od trzech znaków korzystają z przecięcia list blobów dla trigramów
i sprawdzenia ich bajtów. Krótsze literały, w tym `.`, skanują wszystkie
unikalne bloby. Większa liczba trafień niż sprawdzonych blobów jest możliwa,
gdy kilka ścieżek wskazuje ten sam blob.

## Zweryfikowane trafienie i kontrole

`LoanTransaction` występuje w pliku
`fineract-loan/src/main/java/org/apache/fineract/portfolio/loanaccount/domain/LoanTransaction.java`
w `apache/fineract` na przypiętym commicie. Pierwsze trafienie zaczyna się na
bajcie **2779** (licząc od zera), w wierszu **63**. ID bloba to
`6501c92679e58321459d43a6c7b8823e6ca0cc20`.
[Plik na przypiętym commicie](https://github.com/apache/fineract/blob/d63beed7ccfeadaffa0c7842b1011bc88451376f/fineract-loan/src/main/java/org/apache/fineract/portfolio/loanaccount/domain/LoanTransaction.java#L63)

Osobne repozytorium kontrolne zawierało dwie ścieżki z identyczną zawartością,
dwa wystąpienia literału w jednym blobie, bajt NUL i końcowy wiersz bez LF.
Poprawne wyniki przeszły weryfikację. Weryfikator odrzucił przesunięcie offsetu
z 9 na 20, gdzie występuje drugi egzemplarz literału, oraz usunięcie jednej
pasującej ścieżki z odpowiedzi przy odpowiednio zmniejszonym liczniku.

## Odtworzenie

Wymagane są Python 3.10+ i Git. Polecenia PowerShell uruchom z głównego
katalogu projektu. W istniejącym lokalnym magazynie Git można pominąć
inicjalizację i pobranie, jeśli ma wszystkie obiekty przypiętego snapshotu.
`--work-dir` i `--evidence-dir` wskazują nowe katalogi.

```powershell
$pilotPython = (Get-Command python).Source
$pilotCommit = 'd63beed7ccfeadaffa0c7842b1011bc88451376f'
$pilotGit = 'local/fineract-r1/source.git'
git init --bare --object-format=sha1 $pilotGit
git -C $pilotGit fetch --no-tags --depth=1 https://github.com/apache/fineract.git "${pilotCommit}:refs/fineract-r1/pin"

& $pilotPython scripts/run_fineract_r1.py --git-dir $pilotGit `
  --work-dir local/fineract-r1/repro-01 `
  --evidence-dir local/fineract-r1/repro-evidence-01 --warm-passes 3
```

Pojedyncza budowa, wyszukanie i ponowna weryfikacja dostarczonych odpowiedzi.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
$pilotContract = 'docs/fineract-r1-contract.json'
$pilotIndex = 'local/fineract-r1/manual/index.sqlite'
& $pilotPython -m repo_proof.git_search build --git-dir $pilotGit `
  --contract $pilotContract --index $pilotIndex
& $pilotPython -m repo_proof.git_search query --contract $pilotContract `
  --index $pilotIndex --literal LoanTransaction --preview 5 `
  --output local/fineract-r1/manual/loan-transaction.jsonl
& $pilotPython scripts/verify_fineract_r1.py --git-dir $pilotGit `
  --contract $pilotContract --result-dir verification/fineract-r1
```

CLI wypisuje licznik i ograniczony podgląd. Plik JSONL można czytać wierszami.
Zawiera nagłówek z pinem i literałem, osobny rekord na trafienie i końcowy
rekord z licznikiem. Pusta odpowiedź ma nagłówek i rekord końcowy z licznikiem
0. Przebieg kończy się kodem 0 dla PASS, 1 dla FAIL lub 3 dla BLOCKED.

## Przebieg i ograniczenia

Pobranie wymagało dostępu sieciowego i jednorazowego ustawienia
`safe.directory` dla lokalnego magazynu Git utworzonego przez konto
piaskownicy. Kontrakt v1 został zapisany przed odczytem wyników. Kontrole i
mierzony przebieg przeszły bez zmian implementacji podczas pomiaru.

Druga budowa z tego samego magazynu Git dała identyczny plik SQLite
(SHA-256 `143469e35be1b59b66f523c045dbe753234f6072a3db1d58df85eb487ca0d494`).
Powtórzony przebieg uzyskał 8/8 i identyczne osiem archiwów wynikowych.
Próby z brakującym indeksem, brakującym commitem oraz pustym, wielowierszowym
i spoza ASCII literałem zakończyły się błędem przed publikacją wyniku.

Implementację umieszczono jako osobne CLI w otwartym `repo-proof-lab`.
W dostępnych checkoutach nie znaleziono `bank_agent_r0` ani opcjonalnego
`github_repo_corpus_manifest_2026-11-08.json`. Uruchomiono 15 istniejących
testów CLI i korpusu z `repo-proof-lab`. Zakres pomiaru obejmuje jeden
snapshot jednego repozytorium oraz osobne repozytorium kontrolne.
