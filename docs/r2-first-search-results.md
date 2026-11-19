Przy 20 równoczesnych pierwszych wyszukiwaniach typowy użytkownik czekał **107,777 s**, najwolniejszy **109,823 s**, a pełny poprawny wynik zwróciło **60 z 60 żądań**.

## Fale i porównanie z gotowymi odpowiedziami

| Fala | Czas do ostatniego wyjścia CLI | Pełne poprawne | Maks. równoczesnych CLI | Szczyt próbkowanego RAM |
| --- | ---: | ---: | ---: | ---: |
| 1 | 109,633 s | 20/20 | 20 | 13 778 MiB |
| 2 | 109,490 s | 20/20 | 20 | 13 056 MiB |
| 3 | 109,823 s | 20/20 | 20 | 13 581 MiB |

Przepustowość wyniosła **0,182 pełnej odpowiedzi/s**. Windows potwierdził 20 nakładających się wywołań w każdej fali. Zakończyło się także **20/20 prób solo**. Nie było błędów ani timeoutów. Najmniejsza dostępność RAM hosta widoczna w próbkach to 0,911 GiB w pierwszej fali.

| Dwadzieścia różnych literałów | Mediana | Najdłużej | Pełne odp./s | Szczyt próbkowanego RAM |
| --- | ---: | ---: | ---: | ---: |
| Pierwsze wyszukiwanie, gotowy indeks | 107,777 s | 109,823 s | 0,182 | 13 778 MiB |
| Poprzedni pomiar, gotowe odpowiedzi | 2,228 s | 2,700 s | 7,741 | 1 187 MiB |

## Na co czekał użytkownik

Mediany faz dla udanych prób. Pełny skan Git, wyszukiwanie kandydata w indeksie i porównanie należą do fazy zapytania R2. Median poszczególnych faz nie należy sumować.

| Faza | Solo, pierwsze wyszukiwanie | 20 osób, pierwsze wyszukiwanie | 20 osób, gotowe odpowiedzi |
| --- | ---: | ---: | ---: |
| Ustalenie gałęzi | 0,202 s | 0,585 s | 0,619 s |
| Przygotowanie manifestu, w tym odczyt inwentarza Git | 3,832 s | **35,849 s** | 0,546 s |
| Udostępnienie gotowych części indeksu procesowi | 0,006 s | 0,017 s | — |
| Zapytanie R2 z publikacją | 11,683 s | **70,261 s** | 0,605 s |
| ↳ Niezależny pełny skan Git | 11,088 s | **67,746 s** | — |
| ↳ Wyszukiwanie kandydata w indeksie | 0,310 s | 1,158 s | — |
| ↳ Końcowe porównanie rekordów R2 | 0,005 s | 0,007 s | — |

Pomiar pełnego skanu Git łączy odczyt i dekompresję obiektów, sprawdzanie ich tożsamości oraz szukanie literału w bajtach. To najdłuższa faza. We wszystkich 80 próbach potwierdzono użycie gotowego indeksu przez **240 dowiązań twardych** do oryginalnych trzech plików SQLite. W katalogach wykonań nie powstał manifest budowy ani log `build`. Wszystkie commity były dostępne lokalnie i liczba wywołań `fetch` wyniosła zero.

W następnym eksperymencie warto zmierzyć współdzielenie jednego niezależnego skanu Git i jednego przygotowania manifestu przez pytania o ten sam zestaw commitów. Każdy literał zachowałby własny pełny wynik i osobne porównanie rekordów.

## Czas każdego literału

Wszystkie czasy są w sekundach i obejmują odebranie pełnego JSON-u. Osoba z jednym trafieniem czekała dłużej od osoby z największą listą w dwóch z trzech fal.

| Literał | Trafienia | Solo | Fala 1 | Fala 2 | Fala 3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **`BUILD=7339`** | **1** | **15,062** | **106,759** | **73,145** | **108,108** |
| `chrome://` | 5866 | 15,906 | 93,340 | 109,490 | 76,494 |
| `R2_SCALE_ABSENCE_SENTINEL_5F4C9029F1A6` | 0 | 16,054 | 107,884 | 106,171 | 107,096 |
| `electron::` | 277 | 15,963 | 107,996 | 89,663 | 107,855 |
| `navigator.clipboard` | 47 | 15,974 | 74,494 | 107,895 | 108,097 |
| `namespace content` | 2213 | 16,602 | 109,633 | 109,386 | 109,823 |
| `140.0.7339.133` | 2 | 15,637 | 108,299 | 107,305 | 108,145 |
| `mojom::` | 8910 | 15,986 | 103,774 | 107,178 | 66,442 |
| `X-Frame-Options` | 13 | 15,926 | 106,791 | 94,186 | 90,151 |
| `content::BrowserContext` | 3807 | 15,731 | 105,450 | 108,106 | 108,361 |
| `namespace blink` | 231 | 16,271 | 108,944 | 98,794 | 105,694 |
| `brave://` | 262 | 16,049 | 108,779 | 108,116 | 107,699 |
| `test::` | 5759 | 16,995 | 109,206 | 109,209 | 109,543 |
| `chrome-extension://` | 438 | 15,905 | 108,593 | 107,296 | 107,377 |
| `BUILDFLAG(IS_WIN)` | 1595 | 15,414 | 108,780 | 108,201 | 106,633 |
| `RenderFrameHost` | 1798 | 15,379 | 108,009 | 72,985 | 108,947 |
| `BrowserWindow` | 1128 | 15,514 | 74,505 | 108,307 | 94,062 |
| `electron_api` | 124 | 16,028 | 103,341 | 107,929 | 108,228 |
| `addEventListener(` | 1802 | 15,298 | 108,844 | 73,341 | 94,729 |
| **`std::move(`** | **11 383** | **16,294** | **74,653** | **109,029** | **80,283** |

## Warunki i dowód pierwszego wyszukiwania

Korpus obejmował 133 565 zwykłych plików. Gałęzie trzech lokalnych repozytoriów bare były przypięte przez cały eksperyment. Agent miał dostęp do tych samych lokalnych obiektów Git przez alternates. Systemowa pamięć podręczna plików pozostawała aktywna.

| Repozytorium | Zakres | Commit | Pliki |
| --- | --- | --- | ---: |
| Chromium | `chrome/` | `3927f129b801f969d4abdb1458d55174cc062723` | 80 782 |
| Electron | całe drzewo | `d60ae179985685d75d238ee33e17c15a7b53d703` | 2 700 |
| Brave Core | całe drzewo | `38bf45887ca5336841cddb4200e6deee32ce45a8` | 50 083 |

Każda próba solo miała osobny workspace. Każda z trzech fal miała nowy workspace wspólny dla 20 klientów. Tuż przed startem sprawdzono, że w każdym workspace były wyłącznie `config.json` i `sources/`. W zapisie kontroli sprzed startu liczba publikacji i wskaźników `latest` wynosiła zero. Przed uruchomieniem klientów sprawdzono też przypięte drzewa Git, metadane SQLite i liczbę ścieżek oraz blobów w każdej części indeksu. SHA-256 trzech plików indeksu zgadzały się z pokwitowaniem jego wcześniejszej budowy.

Po wspólnej barierze każdy klient uruchomił publiczne `fineract_r2_current.py query <literał>` w osobnym procesie. Czas kończył się po odebraniu całego `stdout` i zamknięciu procesu. Odczyt następował równolegle. Nakładanie zmierzono z czasów życia procesów Windows. Szczyt pamięci to próbkowana suma working setów CLI i ich potomków. Współdzielone strony mogą być liczone w kilku working setach. Przepustowość to liczba pełnych poprawnych odpowiedzi podzielona przez sumę czasów trzech fal.

Po pomiarze sprawdzano kod wyjścia, `VERIFIED`, `query-verified`, literał, wszystkie commity, manifest i SHA-256. Weryfikowano też wszystkie rekordy JSON-u z CLI względem opublikowanego `answer.jsonl` oraz plik odpowiedzi bajt w bajt względem osobnego pełnego skanu Git. Użyto 20 kontroli z poprzedniego pomiaru pod `local/r2-scale/load-01/control/`. Odczytano je w programie pomiarowym poza workspace’ami agentów i sprawdzono ich pokwitowania, pełny hash manifestu oraz hash każdego pliku. Ścieżka agenta nie odczytywała tych wyników.

## Odtworzenie w PowerShell

Uruchom z katalogu projektu, z dostępnymi `local/r2-scale/sources`, `local/r2-scale/index-01` i zależnością `psutil`.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw 'Python nie uruchomił się' }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"
$run = 'local/r2-scale/fst-' + [guid]::NewGuid().ToString('N').Substring(0, 6)
& $projectPython -B -X utf8 scripts/measure_r2_concurrency.py `
    --first-search --control-run 'local/r2-scale/load-01' `
    --work-dir $run --measurements (Join-Path $run 'measurements.json')
if ($LASTEXITCODE -ne 0) { throw 'Pomiar nie zakończył się' }

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current
```

Samo `--first-search` przygotowuje nowe osobne kontrole Git. Wywołanie bez `--first-search` zachowuje poprzedni tryb pomiaru z opublikowanymi odpowiedziami. [Surowe wyniki pierwszego wyszukiwania](../verification/r2-first-search-measurements.json) · [Poprzedni pomiar](r2-concurrency-results.md).

Na mierzonej implementacji przeszło 45 testów regresyjnych.
