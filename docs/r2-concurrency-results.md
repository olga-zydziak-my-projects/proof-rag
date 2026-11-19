# R2 pod równoczesnym obciążeniem od 1 do 20 osób

| Scenariusz | Jedna osoba, mediana | Najwolniejsza osoba przy 20 | Czy każda dostała pełną poprawną odpowiedź przy 20? |
| --- | ---: | ---: | --- |
| Wszyscy pytają o `chrome://` | **0,953 s** | **6,613 s** | Tak, **60/60** w trzech falach |
| Różne literały, przy jednej osobie `BUILD=7339` | **0,774 s** | **2,700 s** | Tak, **60/60** w trzech falach |

W każdej z sześciu fal przy 20 osobach rzeczywiście nakładało się 20 procesów CLI. W scenariuszu różnych pytań użytkownik szukający `BUILD=7339` otrzymał jedno trafienie po **2,190 s, 2,406 s i 2,149 s**. Mediana jego osobnych prób to **0,796 s**. Największa lista w tych falach zawierała 11 383 ścieżki.

## Wyniki dla wszystkich poziomów

Trzy fale na wiersz. Czasy są w sekundach, pamięć jest w MiB. Kolumna „Nakładanie” podaje maksimum faktycznie równoczesnych wywołań w każdej z trzech fal.

| Pytania | Osoby | Mediana | Maksimum | Pełne odp./s | Szczyt RAM | Poprawne | Błędy | Nakładanie |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Identyczne | 1 | 0,953 | 1,002 | 1,036 | 84 | 3/3 | 0 | 1 / 1 / 1 |
| Identyczne | 2 | 1,140 | 3,223 | 1,090 | 128 | 6/6 | 0 | 2 / 2 / 2 |
| Identyczne | 4 | 1,282 | 1,718 | 2,345 | 192 | 12/12 | 0 | 4 / 4 / 4 |
| Identyczne | 8 | 2,202 | 3,080 | 2,783 | 301 | 24/24 | 0 | 8 / 8 / 8 |
| Identyczne | 12 | 2,739 | 4,393 | 2,886 | 410 | 36/36 | 0 | 12 / 12 / 12 |
| Identyczne | 16 | 4,211 | 5,514 | 3,030 | 498 | 48/48 | 0 | 16 / 16 / 16 |
| Identyczne | 20 | 4,974 | 6,613 | 3,071 | 605 | 60/60 | 0 | 20 / 20 / 20 |
| Różne | 1 | 0,774 | 0,847 | 1,256 | 76 | 3/3 | 0 | 1 / 1 / 1 |
| Różne | 2 | 0,869 | 0,985 | 2,090 | 153 | 6/6 | 0 | 2 / 2 / 2 |
| Różne | 4 | 0,923 | 1,109 | 3,879 | 303 | 12/12 | 0 | 4 / 4 / 4 |
| Różne | 8 | 1,403 | 1,724 | 5,018 | 548 | 24/24 | 0 | 8 / 8 / 8 |
| Różne | 12 | 1,769 | 2,022 | 6,049 | 847 | 36/36 | 0 | 12 / 12 / 12 |
| Różne | 16 | 1,899 | 2,263 | 7,254 | 1171 | 47/48 | 1 | 16 / 16 / 16 |
| Różne | 20 | 2,228 | 2,700 | 7,741 | 1187 | 60/60 | 0 | 20 / 20 / 20 |

Czasy całych fal przy 20 osobach to **6,613 / 6,579 / 6,343 s** dla identycznych pytań oraz **2,531 / 2,700 / 2,520 s** dla różnych. W sumie zaliczono **377 z 378** żądań w falach i **60 z 60** osobnych prób. W trzeciej fali 16 różnych pytań `navigator.clipboard` zwróciło `ERROR` po 1,844 s, z kodem 4 i `WinError 5` podczas przenoszenia katalogu logu `monitor` do `query-log`. Żądania nie ponowiono w ramach fali. Nie odnotowano timeoutu ani limitu pamięci. Przy 20 osobach najmniej dostępnej pamięci systemowej widoczne w próbkach wyniosło 4,75 GiB. Poziom 20 zmierzono w całości i zakończył się kompletem poprawnych odpowiedzi w obu scenariuszach.

Przy identycznym pytaniu mediana fazy ustalania gałęzi, która obejmuje czekanie na blokadę `latest`, wzrosła z **0,190 s do 2,666 s**. Mediana fazy weryfikacji i publikacji zmieniła się z **0,330 s do 0,348 s**. W falach 20 klientów ostatnie odczyty gałęzi dla identycznego literału były rozciągnięte na **5,114–5,236 s**, wobec **0,116–0,172 s** dla różnych literałów. Ten pomiar wskazuje na kolejkę przed odczytem gałęzi pod wspólną blokadą dla `chrome://`. Dla różnych literałów przy 20 klientach mediana ustalania gałęzi wyniosła 0,619 s, przygotowania manifestu 0,546 s, a weryfikacji i publikacji 0,605 s.

## Literały i własny czas bazowy

Każdy literał zmierzono solo trzy razy przed falami. Ostatnia kolumna porównuje medianę tego samego literału w trzech falach 20 osób z jego medianą solo.

| Literał | Trafienia | Solo, s | Przy 20 różnych, s | Stosunek |
| --- | ---: | ---: | ---: | ---: |
| `BUILD=7339` | 1 | 0,796 | 2,190 | 2,75× |
| `chrome://` | 5866 | 0,979 | 2,394 | 2,45× |
| `R2_SCALE_ABSENCE_SENTINEL_5F4C9029F1A6` | 0 | 0,796 | 2,249 | 2,82× |
| `electron::` | 277 | 0,798 | 2,121 | 2,66× |
| `navigator.clipboard` | 47 | 0,810 | 2,141 | 2,64× |
| `namespace content` | 2213 | 0,836 | 2,267 | 2,71× |
| `140.0.7339.133` | 2 | 0,821 | 2,152 | 2,62× |
| `mojom::` | 8910 | 1,050 | 2,461 | 2,35× |
| `X-Frame-Options` | 13 | 0,792 | 2,135 | 2,69× |
| `content::BrowserContext` | 3807 | 0,909 | 2,208 | 2,43× |
| `namespace blink` | 231 | 0,802 | 2,204 | 2,75× |
| `brave://` | 262 | 0,793 | 2,207 | 2,78× |
| `test::` | 5759 | 0,941 | 2,379 | 2,53× |
| `chrome-extension://` | 438 | 0,790 | 2,121 | 2,68× |
| `BUILDFLAG(IS_WIN)` | 1595 | 0,868 | 2,260 | 2,60× |
| `RenderFrameHost` | 1798 | 0,872 | 2,207 | 2,53× |
| `BrowserWindow` | 1128 | 0,820 | 2,144 | 2,61× |
| `electron_api` | 124 | 0,776 | 2,143 | 2,76× |
| `addEventListener(` | 1802 | 0,841 | 2,207 | 2,62× |
| `std::move(` | 11383 | 1,115 | 2,531 | 2,27× |

## Korpus

Windows, Python 3.12.10, 24 procesory logiczne i 31,4 GiB RAM. Dane to **133 565 rzeczywistych zwykłych plików**. Wszystkie gałęzie wskazywały te same commity od początku do końca pomiaru. Źródła to trzy osobne lokalne repozytoria bare pod `local/r2-scale/load-01/server/`. Serwery i agent czytały istniejące obiekty Git przez alternates. Git miał dostęp wyłącznie przez protokół `file`.

| Repozytorium | Gałąź | Commit | Pliki w zakresie |
| --- | --- | --- | ---: |
| Chromium, `chrome/` | `bench/chromium` | `3927f129b801f969d4abdb1458d55174cc062723` | 80 782 |
| Electron, całe drzewo | `bench/electron` | `d60ae179985685d75d238ee33e17c15a7b53d703` | 2 700 |
| Brave Core, całe drzewo | `bench/brave-core` | `38bf45887ca5336841cddb4200e6deee32ce45a8` | 50 083 |

## Metoda

Klienci otrzymali jeden sygnał startu i uruchomili niezależne procesy `fineract_r2_current.py query <literał>`. Każdy klient równolegle odbierał cały `stdout`. Koniec pomiaru to odebranie JSON-u i zakończenie procesu. Zegar fali kończył się wraz z ostatnim klientem. Nakładanie wywołań ustalono z czasów utworzenia i zakończenia faktycznych procesów CLI w Windows (`GetProcessTimes`). Szczyt RAM to największa próbkowana suma working setów procesów CLI i ich potomków w trzech falach. Próbnik odczekiwał 25 ms między odczytami. Współdzielone strony mogą być liczone w kilku working setach.

Wszystkie wywołania korzystały z jednego workspace, wspólnego `latest` oraz istniejących indeksów. Dla każdego literału osobno opublikowano wynik startowy przez publiczne CLI i wynik kontrolny przez pełne `query-verified`. Po przygotowaniu wykonano trzy próby solo na literał i trzy fale na każdy poziom oraz scenariusz. W falach różnych pytań brano pierwsze N literałów z tabeli. Kolejność scenariuszy zmieniano między falami. Systemowy cache pozostawiono aktywny. W mierzonych wywołaniach gałęzie były stałe, więc ciepła ścieżka `update-verified` sprawdzała poprzednią zweryfikowaną odpowiedź i brak zmian. Pełne skany Git odbyły się podczas przygotowania, przed pomiarem.

Po zakończeniu każdej fali sprawdzono kod wyjścia, status, gałęzie i commity, manifest, skrót SHA-256, zgodność wszystkich rekordów w JSON-ie ze zweryfikowaną publikacją na dysku oraz zgodność jej bajtów z osobnym pełnym skanem Git. Przepustowość to liczba poprawnych pełnych odpowiedzi podzielona przez sumę czasów trzech fal. Mediana i maksimum uwzględniają czas do zakończenia każdego żądania. Błędne żądanie nie zwiększa przepustowości. Wynik diagnostycznej próby przed startem pozostaje osobno w `local/r2-scale/load-01/responses/smoke/`.

## Odtworzenie w PowerShell

Uruchom z katalogu projektu z dostępnymi `local/r2-scale/sources`, `local/r2-scale/index-01` i zależnością `psutil`.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw 'Python nie uruchomił się' }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"
$run = 'local/r2-scale/load-' + [guid]::NewGuid().ToString('N').Substring(0, 6)
& $projectPython -B -X utf8 scripts/measure_r2_concurrency.py `
    --work-dir $run --measurements (Join-Path $run 'measurements.json')
if ($LASTEXITCODE -ne 0) { throw 'Pomiar nie zakończył się' }

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current
```

Surowe dane zawierają każde żądanie, czasy faz, odpowiedzi kontrolne oznaczone SHA-256 i ścieżki do przechwyconego wyjścia oraz próbek RAM. [Surowe pomiary](../verification/r2-concurrency-measurements.json).


Na tym samym kodzie przeszło **45 testów regresyjnych**. Implementacja mierzonego CLI pozostała w stanie wejściowym.
