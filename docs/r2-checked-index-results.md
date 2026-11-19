Przy 20 równoczesnych pierwszych wyszukiwaniach mediana wyniosła **2,712 s**, najwolniejszy użytkownik czekał **3,702 s**, pełne poprawne odpowiedzi otrzymało **60 z 60 klientów**, a pominięcie jednego trafienia dało **`MISMATCH`, kod 2 i brak publikacji**.

Jednorazowe przygotowanie indeksu weryfikatora zajęło **164,138 s**. Opublikowane dane weryfikatora zajęły **2 690 102 166 B (2,51 GiB)** obok istniejącego indeksu wyszukiwarki. Szczyt próbkowanej pamięci drzewa procesów wyniósł **908 MiB**. Identyfikator indeksu to SHA-256 pokwitowania `0e4d35e67f0180af690929b07becdd61e548a87e4d44f507ef8ddc065a6059d9`. Zapisano go przed rozpoznaniem literałów.

| Te same 20 nowych literałów | Mediana | Najdłużej | Pełne odp./s | Szczyt RAM | Poprawne |
| --- | ---: | ---: | ---: | ---: | ---: |
| Wspólny sprawdzony indeks | **2,712 s** | **3,702 s** | 5,845 | 1681 MiB | 60/60 |
| Dotychczasowy pełny skan Git | **108,518 s** | **110,249 s** | 0,181 | 11 869 MiB | 20/20 |

Mediana spadła około **40 razy**. Historyczne **107,777 s** pochodzi z pełnego skanu dla innego zestawu literałów. Trzy mierzone fale trybu sprawdzonego indeksu trwały **3,137 / 3,426 / 3,702 s**. Każda fala osiągnęła 20 rzeczywiście nakładających się procesów. Wszystkie **20 prób solo** przeszło. W zaplanowanych próbach nie wystąpiły błędy ani timeouty. Po dodaniu kontroli kanonicznej pisowni identyfikatora bloba, już po próbach solo i pierwszej fali, dodatkowa fala na końcowym kodzie również zwróciła 20/20 zgodnych odpowiedzi przy 20 nakładających się procesach. Trwała 3,026 s i jest osobno zapisana w surowych danych.

## Co zmieniło czas

| Mediana fazy lub odczytu na pytanie przy 20 klientach | Sprawdzony indeks | Pełny skan Git |
| --- | ---: | ---: |
| Przygotowanie lub odczyt przypiętego manifestu | 0,002 s | 38,101 s |
| Wyszukanie kandydata w indeksie | 0,876 s | 0,698 s |
| Niezależna weryfikacja | 0,361 s | 68,021 s |
| Bloby odczytane przez weryfikator | 304,5 | 121 335 |
| Bajty treści blobów weryfikatora | 63,92 MB | 1787,25 MB |

W nowym trybie weryfikator czytał **0–6038 blobów** i **0–208,53 MB treści** na żądanie. Dodatkowo mediana odczytu wyniosła 1,54 MB list trójek i 4,88 MB danych uwierzytelniających. Wyszukiwarka osobno czytała treść kandydatów ze swojego indeksu, również z medianą 63,92 MB. Są to zliczone bajty danych, które odczytał kod. Pomiar nie obejmuje fizycznych odczytów stron SQLite ani cache systemowego. Pełny skan Git wykonał się **0 razy** w 60 żądaniach nowego trybu i **20 razy** w porównywanej fali starego trybu. Osobne skany kontrolne odbyły się przed falami.

## Próba pominięcia

W fizycznej kopii pliku indeksu wyszukiwarki dla Electron przekierowano dokładnie jedną ścieżkę na istniejący blob bez `content::WebContents`. Zniknęło **`electron/electron / patches/chromium/can_create_window.patch`**. Kandydat miał **5664** trafienia wobec poprawnych **5665**. Pozostałe rekordy były identyczne i w tej samej kolejności, a liczniki kandydata zgadzały się z jego listą. SHA-256 niepełnego pliku zgadzał się z hashem kandydata odrzuconego przez publiczne CLI na etapie porównania.

Odpowiedź nie została opublikowana, a bajty wcześniejszego `latest` pozostały identyczne. SHA-256 oryginalnego indeksu Electron i osobnej bazy weryfikatora pozostały zgodne z wartościami sprzed próby. Po przywróceniu wskazania na prawidłowy indeks opublikowana odpowiedź była identyczna bajt w bajt z pełnym skanem Git. Jej SHA-256 to `d36fd03222f85be3fb81cbe9fc74f61f7bbf6204ae3f30a5d549e5994fc22021`.

## Czasy poszczególnych pytań

Po publikacji indeksu rozpoznano 27 nowych literałów ASCII na podstawie identyfikatorów, adresów i nagłówków z korpusu. Ustalono kolejność od szeroko występującego literału przez kontrolę zerową i najrzadszy dodatni wynik, a potem wzięto 17 kolejnych dodatnich propozycji w kolejności rozpoznania. Osobny pełny skan potwierdził liczbę trafień w każdym repozytorium. Wszystkie czasy w tabeli są w sekundach.

| Literał | Trafienia | Solo | Fala 1 | Fala 2 | Fala 3 | Pełny skan przy 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `content::WebContents` | 5665 | 1,209 | 2,859 | 3,110 | 3,441 | 110,202 |
| `R2_CHECKED_ABSENCE_48C7DE962EBB` | 0 | 0,769 | 1,600 | 1,651 | 2,050 | 86,795 |
| `Electron is built on` | 2 | 1,494 | 3,137 | 3,426 | 3,702 | 107,993 |
| `mojo::PendingReceiver` | 1461 | 0,936 | 2,244 | 2,504 | 2,718 | 109,455 |
| `node::Environment` | 18 | 0,843 | 2,074 | 2,216 | 2,426 | 103,785 |
| `v8::Isolate` | 368 | 0,972 | 1,815 | 1,888 | 2,005 | 108,426 |
| `WebContentsObserver` | 1012 | 1,189 | 2,670 | 2,921 | 3,179 | 110,151 |
| `BraveWallet` | 940 | 1,021 | 2,498 | 2,747 | 2,852 | 94,880 |
| `chrome-untrusted://` | 309 | 0,935 | 2,157 | 2,282 | 2,552 | 103,707 |
| `ExtensionHost` | 169 | 1,357 | 3,021 | 3,248 | 3,553 | 68,665 |
| `base::BindOnce` | 5410 | 1,219 | 2,912 | 3,195 | 3,502 | 110,249 |
| `WeakPtrFactory` | 3460 | 1,081 | 2,559 | 2,753 | 3,106 | 109,801 |
| `SkBitmap` | 778 | 0,838 | 2,090 | 2,183 | 2,650 | 109,531 |
| `GetBrowserContext` | 1313 | 1,405 | 3,137 | 3,397 | 3,701 | 110,057 |
| `navigator.userAgent` | 127 | 0,966 | 2,496 | 2,747 | 3,003 | 109,801 |
| `X-Content-Type-Options` | 20 | 0,873 | 1,949 | 2,112 | 2,449 | 100,621 |
| `ELECTRON_ENABLE_LOGGING` | 8 | 0,871 | 2,220 | 2,411 | 2,705 | 108,609 |
| `BrowserMainParts` | 140 | 1,329 | 3,029 | 3,304 | 3,596 | 69,074 |
| `ChromeContentBrowserClient` | 120 | 1,268 | 2,920 | 3,187 | 3,499 | 110,166 |
| `BRAVE_SHIELDS` | 116 | 0,740 | 1,742 | 1,947 | 2,051 | 79,726 |

## Co poświadcza indeks

Podczas przygotowania weryfikator sprawdza SHA-1 przypiętego commitu, drzew i blobów. Odtwarza wszystkie zwykłe ścieżki w zakresie z bajtów drzew. Dla każdego bloba niezależnie wyznacza wszystkie trójki z drukowalnych bajtów ASCII. Porównuje każde mapowanie ścieżki, pełną treść każdego bloba i każdą uporządkowaną listę identyfikatorów dla trójki z istniejącym indeksem. Porównanie obejmuje również brak lub nadmiar wierszy. Dopiero wtedy zapisuje osobną bazę weryfikatora i atomowo publikuje cały katalog.

Zaufanym punktem odniesienia jest SHA-256 pokwitowania wpisany w konfiguracji agenta. Pokwitowanie wiąże wersję formatu, dokładny manifest repozytoriów, commitów i zakresów oraz katalogi skrótów. Dla każdej użytej trójki weryfikator uwierzytelnia zarówno listę, jak i dowód jej braku. Przecięcie uwierzytelnionych list zawiera każdy blob, który może zawierać cały literał. Weryfikator sprawdza bajty każdego takiego bloba i pełny zestaw przypisanych ścieżek względem skrótu, a następnie wyznacza pierwsze wystąpienie. Baza wyszukiwarki pozostaje osobna. Zmiana katalogu skrótów lub danych użytych do odpowiedzi kończy się błędem, a kompletna odpowiedź przechodzi jeszcze porównanie z wynikiem wyszukiwarki przed atomową publikacją.

CLI pobiera wskazania wszystkich gałęzi przy każdym pytaniu. Gdy przypięty zestaw commitów się zmienia, wraca do dotychczasowej weryfikacji Git dla nowego zestawu. Literały jedno- i dwubajtowe korzystają z niezależnego pełnego skanu Git. Regresja na małym repozytorium sprawdziła tę ścieżkę i odnotowała jedno użycie pełnego skanu. Pozostałe nowe regresje sprawdziły m.in. wiele ścieżek tego samego bloba, zmianę gałęzi przez prawdziwy lokalny `push` oraz odrzucenie zmodyfikowanych list i mapowań.

## Warunki i odtworzenie

Korpus zawierał 133 565 zwykłych plików. Chromium obejmował `chrome/` z commitu `3927f129b801f969d4abdb1458d55174cc062723`, Electron całe drzewo `d60ae179985685d75d238ee33e17c15a7b53d703`, a Brave Core całe drzewo `38bf45887ca5336841cddb4200e6deee32ce45a8`. Wszystkie trzy źródła były lokalnymi repozytoriami bare. Cache Windows pozostał aktywny.

Każda fala startowała w nowym wspólnym workspace z zerem publikacji i zerem `latest`. Próby solo miały osobne workspace’y. Osobne kontrole pełnym skanem Git powstały przed pomiarami. Klienci zwolnieni wspólną barierą uruchamiali publiczne `fineract_r2_current.py query <literał>` w osobnych procesach. Zegar kończył się po odebraniu całego stdout i zakończeniu procesu. Czas życia CLI zmierzono przez Windows `GetProcessTimes`. Pamięć to próbkowana suma working setów CLI i potomków. Współdzielone strony mogą być liczone więcej niż raz.

Poniższe polecenia wykonaj z katalogu projektu. Wymagają gotowych lokalnych obiektów i indeksu `local/r2-scale/index-01`, manifestu z [poprzedniego pomiaru](r2-first-search-results.md) oraz `psutil`. Pierwszy krok odtwarza tę samą tożsamość zweryfikowanego indeksu dla zamrożonego zestawu pytań.

```powershell
$projectPython = Join-Path $env:LOCALAPPDATA 'Python/pythoncore-3.12-64/python.exe'
& $projectPython --version
if ($LASTEXITCODE -ne 0) { throw 'Python nie uruchomił się' }
$env:PYTHONPATH = "$PWD/src;$PWD/local/fineract-r2/deps;$PWD/tests"
$env:GIT_ALLOW_PROTOCOL = 'file'
$env:GIT_NO_LAZY_FETCH = '1'
$id = [guid]::NewGuid().ToString('N').Substring(0, 6)
$checked = "local/r2-scale/ci-$id"
$prepPath = "$checked-preparation.json"
$prep = & $projectPython -B -X utf8 scripts/prepare_checked_r2_index.py `
    --sources local/r2-scale/sources --manifest local/r2-scale/first-01/manifest.json `
    --index local/r2-scale/index-01 --output $checked
if ($LASTEXITCODE -ne 0) { throw 'Przygotowanie nie zakończyło się' }
$prep | Set-Content -Encoding ASCII -LiteralPath $prepPath

$run = "local/r2-scale/cx-$id"
& $projectPython -B -X utf8 scripts/measure_r2_checked.py `
    --work-dir $run --checked-index $checked --preparation $prepPath `
    --queries verification/r2-checked-queries.json `
    --measurements (Join-Path $run 'measurements.json') `
    --omission (Join-Path $run 'omission.json')
if ($LASTEXITCODE -ne 0) { throw 'Eksperyment nie zakończył się' }

Remove-Item Env:FINERACT_R2_TEST_ROOT -ErrorAction SilentlyContinue
& $projectPython -B -X utf8 -m unittest test_fineract_r2 test_project_memory `
    test_project_memory_intent test_project_memory_session test_r2_current test_r2_checked
```

[Pokwitowanie kosztu przygotowania](../verification/r2-checked-preparation.json) · [Zamrożony zestaw pytań i rozpoznanie](../verification/r2-checked-queries.json) · [Surowe pomiary i odczyty każdego żądania](../verification/r2-checked-measurements.json) · [Dowód pominięcia](../verification/r2-checked-omission.json).


Przeszło **49 testów**, w tym 45 dotychczasowych i cztery nowe.
