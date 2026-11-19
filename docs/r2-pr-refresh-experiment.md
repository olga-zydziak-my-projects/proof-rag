Tak. Pierwsze pytanie, uruchomione **1,000 s po `push`**, znalazło nowy plik w PR #1. Pełna odpowiedź dotarła **20,973 s po `push`**, czyli po **19,972 s od początku pytania**. Indeks B był gotowy po **10,518 s**, a następne pytanie na tym indeksie trwało **0,727 s**.

## Kolejność i poprawność

| Zdarzenie | Wynik |
| --- | --- |
| Zakończenie rzeczywistego `git push` | 0,000 s. Tylko `r2-pr-1` przeszła z A na B |
| Start pierwszego pytania o PR #1 | 1,000 s. Odczyt serwera wskazał B |
| Gotowy indeks B | 10,518 s. Atomowa zmiana wskaźnika po ponownym sprawdzeniu gałęzi |
| Odebranie pełnego JSON-u pierwszego pytania | 20,973 s. `VERIFIED`, B, jedno trafienie przez `query-verified` |
| Następne pytanie o PR #1 | 0,727 s od uruchomienia do końca CLI. `VERIFIED`, B, `query-checked` |

Pierwsze pytanie rozpoczęło pełną weryfikację, gdy indeks B był jeszcze w przygotowaniu. Indeks został aktywowany **10,455 s przed odebraniem pierwszej odpowiedzi**. Trwające pytanie dokończyło własną weryfikację przypiętej wersji B.

Gałąź `main` zwróciła `VERIFIED` dla A i zero trafień. Osobne pytanie o `'engflow_reclient_configs_version':` w PR #1 zwróciło `electron/electron / DEPS` dla B. Widok obejmował całe drzewo Electron. Żadne pytanie w widoku PR nie zwróciło A po potwierdzeniu B. Wszystkie cztery pełne odpowiedzi CLI zgodziły się bajt w bajt z trzema osobnymi skanami Git. SHA-256 pierwszej i następnej odpowiedzi o nowy plik to `6257f299379c39e62518437cdab95ee35c8e934411e235ac2af2ccc9fc5d08ef`.

## Co zaktualizowano

Korpus miał **133 565 plików w A i 133 566 w B**. Electron A to `d60ae179985685d75d238ee33e17c15a7b53d703`, a jego dziecko B to `74a561a900778d8a870b57267cc8919e469b9ce4`. Jedyna zmiana Git to dodanie `docs/r2-pr-refresh-experiment.txt` z literałem `R2_PR1_521824C46A214AF7985187DFE2ECE1B3`. Chromium i Brave Core pozostały na przypiętych commitach poprzedniego pomiaru.

Zdarzenie `synchronize` samo uruchomiło odświeżanie w osobnym procesie. Dla Chromium i Brave Core użyto twardych dowiązań do obu istniejących części, wyszukiwarki i weryfikatora. Całą część Electron odbudowano i niezależnie sprawdzono. Obejmowała **2701 ścieżek, 2663 bloby i 26 311 211 B treści**. Powstało **51 535 872 B** danych wyszukiwarki i **93 738 240 B** danych weryfikatora Electron. Przygotowanie manifestu z pobraniem danych trwało 0,410 s, budowa indeksu wyszukiwarki 4,306 s, a przygotowanie i publikacja danych weryfikatora 5,203 s. Pierwsze pytanie w swojej ścieżce zapasowej niezależnie zbudowało część Electron i przeskanowało cały korpus.

Manifest wejściowy przygotowania jest odczytywany raz. Lista repozytoriów, SHA-256 i publikowana kopia pochodzą z tych samych bajtów. Deterministyczna regresja podmienia plik wejściowy na manifest B tuż po odczycie A i sprawdza, że opublikowano oryginalne bajty oraz SHA-256 A.

## Co było rzeczywiste

Git utworzył lokalne gałęzie, commit B i wykonał `push` z osobnej kopii autora do lokalnego serwera bare. Agent i proces odświeżający niezależnie odczytali referencje z serwera oraz pobrali brakujący B. Zdarzenia GitHuba `opened` i `synchronize` zasymulowano lokalnymi dokumentami JSON podanymi na stdin. `opened` zarejestrowało PR #1 na podstawie zdarzenia, gdy obie gałęzie wskazywały A. Konfiguracja początkowa zawierała tylko gałąź bazową. Systemowa pamięć plików pozostała aktywna.

Do tabeli użyto kompletnego przebiegu `pr-03`. W `pr-01` pierwsza próba ujawniła problem z długością ścieżki tymczasowej SQLite na Windows, a w `pr-02` pierwsze pytanie i odświeżanie udały się, lecz kontrola założyła jedno trafienie dla hasha występującego w trzech niezmienionych plikach. Oba wcześniejsze workspace’y zachowano. Po skróceniu nazwy tymczasowego pliku SQLite i wybraniu unikalnego literału w `DEPS` pełny przebieg przeszedł.

## Odtworzenie w PowerShell

Uruchom z katalogu projektu, z gotowym `local/r2-scale/checked-01`, indeksem wyszukiwarki `local/r2-scale/index-01`, obiektami `local/r2-scale/sources` i lokalną zależnością `psutil`.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw 'Python nie uruchomił się' }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"
$env:GIT_ALLOW_PROTOCOL = 'file'
$env:GIT_NO_LAZY_FETCH = '1'

$run = 'local/r2-scale/p-' + [guid]::NewGuid().ToString('N').Substring(0, 6)
$raw = Join-Path $run 'measurements.json'
& $projectPython -B -X utf8 scripts/run_r2_pr_experiment.py --work-dir $run --measurements $raw
if ($LASTEXITCODE -ne 0) { throw 'Eksperyment PR nie zakończył się' }

$env:REPO_PROOF_CURRENT_CONFIG = (Resolve-Path (Join-Path $run 'config.json')).Path
$literal = (Get-Content -Raw -LiteralPath $raw | ConvertFrom-Json).literal
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query --pr 1 $literal
& $projectPython -B -X utf8 scripts/fineract_r2_current.py query $literal

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current test_r2_checked
```

Przeszło **51 testów**, w tym 49 dotychczasowych i dwie nowe regresje.

[Surowe czasy, zdarzenia i wyniki porównań](../verification/r2-pr-refresh-measurements.json).
