# Fineract R2 — zweryfikowane wyszukiwanie literału

Polecenie `query-verified` bierze kandydatów z indeksu SQLite. Osobny algorytm
odczytuje przypięty commit, drzewa i wszystkie zwykłe bloby z lokalnego Git.
Sprawdza ich identyfikatory SHA-1, wyznacza pierwsze wystąpienie literału
w surowych bajtach i porównuje wszystkie rekordy odpowiedzi, również przy
braku trafień. Sprawdzenie obejmuje identyfikatory blobów, offsety, wiersze,
pochodzenie, kompletność i ścisły format JSONL.
[Kontrakt R2](fineract-r2-contract.json)

## Uruchomienie w PowerShell

Potrzebne są Windows 10 lub nowszy, Python 3.10+, Git i `psutil` 7.2.2.
Polecenia uruchom w głównym katalogu projektu. Zmienna `$pilotPython` może
wskazywać pełną ścieżkę do interpretera. Jeśli `psutil` jest w osobnym
lokalnym katalogu zależności, wskaż ten katalog w `PYTHONPATH`.

```powershell
$pilotPython = (Get-Command python).Source
$pilotGit = 'local/fineract-r1/source.git'
$pilotContract = 'docs/fineract-r2-contract.json'
$pilotIndex = 'local/fineract-r2/manual/index.sqlite'
$env:PYTHONPATH = (Join-Path (Get-Location) 'local/fineract-r2/deps')

if (-not (Test-Path -LiteralPath "$pilotGit/objects")) {
  git init --bare --object-format=sha1 $pilotGit
  git -C $pilotGit fetch --no-tags --depth=1 https://github.com/apache/fineract.git 'd63beed7ccfeadaffa0c7842b1011bc88451376f:refs/fineract-r1/pin'
}

& $pilotPython -B scripts/fineract_r2.py build --git-dir $pilotGit `
  --contract $pilotContract --index $pilotIndex

& $pilotPython -B scripts/fineract_r2.py query-verified --git-dir $pilotGit `
  --contract $pilotContract --index $pilotIndex --literal 'LoanTransaction' `
  --output-dir local/fineract-r2/manual/query-01
```

Można użyć zgodnego indeksu R1. Każde wywołanie `query-verified` wymaga nowego
katalogu wynikowego. Opcjonalne `--log-dir` zapisuje przebieg nadzorcy w osobnym
nowym katalogu. `--timeout` pozwala skrócić domyślny limit 60 s na zapytanie
lub 300 s na budowę. Proces nadrzędny pracuje z priorytetem Normal.

Po sukcesie katalog zawiera `answer.jsonl` i `verification.json`. Potwierdzenie
wiąże SHA-256 dokładnych bajtów odpowiedzi z hashem kontraktu, literałem,
snapshotem, zakresem źródeł i metodą sprawdzenia. JSONL zawiera nagłówek, po
jednym rekordzie na pasującą ścieżkę oraz końcowy rekord z licznikiem. Offset
jest liczony od zera, a wiersz od jedynki według poprzedzających bajtów LF.
Nazwy Git spoza UTF-8 są zapisywane jako odwracalne sekwencje JSON
`\udcXX` zgodnie z konwencją `surrogateescape`.

| Kod | Status | Znaczenie |
| --- | --- | --- |
| 0 | `VERIFIED` | Pełna zgodność i opublikowany katalog odpowiedzi. |
| 0 | `BUILT` | Nadzorowana budowa i opublikowany indeks. |
| 2 | `MISMATCH` | Odpowiedź indeksu różni się od źródeł lub łamie format. |
| 3 | `BLOCKED` | Przypięty zakres Git jest niedostępny lub niekompletny. |
| 4 | `ERROR` | Niepoprawne wejście, przekroczony limit, przerwanie lub błąd wykonania. |

## Publikacja i granica zaufania

Kandydat powstaje w katalogu roboczym obok wskazanej lokalizacji. Nadzorca
czeka na koniec procesu i usuwa pozostałych członków Windows Job Object.
Kontroler ponownie sprawdza SHA-256, zapisuje potwierdzenie i publikuje oba
pliki jedną zmianą nazwy katalogu na tym samym woluminie. Windows odrzuca
zmianę nazwy, jeśli cel już istnieje. Wcześniejszy błąd, rozbieżność, timeout
lub przerwanie nie publikuje odpowiedzi. Zmiana nazwy to punkt zatwierdzenia.
Kontroler ignoruje Ctrl+C podczas końcowego przemianowania i zwracania statusu.
Przymusowe zakończenie procesu może pozostawić katalog roboczy
`.fineract-r2-stage-*` albo wcześniej opublikowany, kompletny katalog.

Zakładamy zaufany kontrakt, interpreter, Git i lokalny katalog wykonania.
Gwarancja obejmuje konkretną odpowiedź względem przypiętych obiektów Git.
Weryfikator nie poświadcza integralności nieużywanych części indeksu.
Limity pamięci i artefaktów nadzorca sprawdza przez próbkowanie drzewa
procesów, a limit czasu obejmuje nadzorowane procesy i kontrolę przed
publikacją. Historyczne `python -m repo_proof.git_search query` to
wyszukiwanie R1 bez automatycznej niezależnej weryfikacji.

## Odtworzenie przebiegu

Wybierz nowe nazwy katalogów i pliku raportu. Przebieg sam wykonuje wymagane
testy, nadzorowaną budowę, trzy przejścia historyczne oraz po jednym
przejściu rozwojowym i końcowym.

```powershell
& $pilotPython -B scripts/run_fineract_r2.py --git-dir $pilotGit `
  --run-dir local/fineract-r2/repro-01 `
  --report local/fineract-r2/repro-01-summary.json
```

[Raport pomiarów](fineract-r2-results.md)

## Pytanie o kod bieżącej gałęzi lub PR-a

`ask` korzysta z konfiguracji `fineract_r2_current.py` i rejestracji
`fineract_r2_pr.py`. Wymaga SDK `anthropic`, klucza w `ANTHROPIC_API_KEY`
i konfiguracji korpusu z publicznym kodem. Pytanie i potrzebne fragmenty źródła
otrzymuje Claude Sonnet 5.5 (`claude-sonnet-5-5`) z poziomem wysiłku `medium`.

```powershell
$qaConfig = 'local/r2-current/config.json'
$qaQuestion = 'Klient złożył wniosek 12 maja. Czy według reguły daty można go zatwierdzić również 12 maja?'
& $pilotPython -B -X utf8 scripts/fineract_r2_ask.py ask --config $qaConfig $qaQuestion
& $pilotPython -B -X utf8 scripts/fineract_r2_ask.py ask --config $qaConfig --repo fineract --pr 1 $qaQuestion
& $pilotPython -B -X utf8 scripts/fineract_r2_ask.py ask --config $qaConfig --review-conclusion $qaQuestion
```

Każde pytanie pobiera aktualne commity i przypina manifest. Wyszukiwania R2,
odczyty metod, wywołania i sprawdzenie cytatów korzystają z tej samej wersji.
Jeśli gotowy indeks poświadczony dotyczy innego commitu, R2 używa pełnej
weryfikacji wyszukiwania przypiętej wersji. Kolejne pytanie ponownie pyta źródło.

Wynik JSON zawiera widok, commity, skrót manifestu, cytaty i czasy. Pole
`checks.citations` opisuje kontrolę cytatów. Pole `checks.business_conclusion`
ma w trybie domyślnym wartość `NOT_CHECKED`.

Opcja `--review-conclusion` uruchamia dodatkową kontrolę przed wydaniem odpowiedzi.
Sonnet dostaje pytanie, proponowaną odpowiedź i fragmenty przypiętego kodu.
Sprawdza, czy opisane zachowanie wynika z tych fragmentów. Jeśli zgłasza
zastrzeżenie, autor odpowiedzi dostaje jego uzasadnienie i ma jedną próbę
poprawy. Recenzent ponownie sprawdza poprawioną odpowiedź, widząc
również te fragmenty, których autor już nie cytuje. Jeśli nadal brakuje
dowodu lub recenzent nie dostarczy kompletnej oceny, CLI zwraca `BLOCKED`.
Niezgodność cytatu z Git daje `MISMATCH`.

W opublikowanej odpowiedzi pole `checks.citations` ma wartość `VERIFIED`,
a `checks.business_conclusion` ma wartość `MODEL_REVIEWED`. Drugie pole
oznacza ocenę modelu na podstawie pokazanych fragmentów. Pole
`conclusion_review` zawiera zakresy, wynik oceny i informację o próbie poprawy.
[Porównanie obu trybów na pięciu pytaniach o Electron](../verification/qa-conclusion-review-01.json).

Dla samodzielnych deklaracji takich jak „Nie uruchamiałem kodu” i „Kodu
nie uruchamiałem” bramka korzysta z historii narzędzi bieżącego pytania.
W polu `tool_history.events` zapisuje wywołania wyszukiwania i odczytu
oraz ich wyniki. Przy kompletnej historii samych odczytów ocena tej deklaracji
wskazuje `basis: tool_history` i `observed_value: false`. Gdy agent dodaje
„wniosek wynika z samej lektury”, potrzebny jest odczyt, który zwrócił
treść. Przy niepełnej historii bramka nie może potwierdzić takiej deklaracji.
Zdania opisujące również skutek działania programu nadal przechodzą ocenę
na podstawie przypiętego kodu.
[Próby z Claude’em dla obu rodzajów dowodu](../verification/qa-conclusion-history-01.json).

`tests/fineract_approval_demo.py` odtwarza próbę na lokalnej kopii Apache
Fineracta. Wskaż nowe `--work-dir` i `--measurements`. Skrypt wykona lokalny
push testowy i zapisze przebieg, w tym błędy oraz czasy pytań liczone od
uruchomienia procesu CLI do odebrania odpowiedzi.
