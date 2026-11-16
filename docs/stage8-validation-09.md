# Końcowa walidacja etapu 8, przebieg 09

**STAGE8_PASS**, 16 listopada 2026. [Raport zbiorczy 09](../verification/stage8-status-09.json) ponownie ocenia wszystkie 12 obowiązkowych bramek przez niezmienioną funkcję `stage8_acceptance.evaluate`. Każda bramka ma wynik true. [Niezależny przegląd końcowy](../verification/stage8-final-review-09.json) nie zawiera uwag blokujących.

Punktem wyjścia były czyste drzewo, gałąź `codex/stage8-multirepo` i commit `55522fa1815db14423c28a5ecf7a0a5fb12b8886`. Wszystkie 125 plików kodu i testów zachowało dokładne hashe z final-06. Nie zmieniono implementacji, historycznych testów ani README projektu. Nowe sterowniki kontrolne mają osobne hashe i niezależne przeglądy.

## Zasoby i rzeczywisty profil procesów

Obserwacja Windows trwała 66,656 s. Sześć próbek CPU wynosiło 3,0–9,7%, przy dostępnej pamięci około 10,8–10,9 GiB. WSL przed obserwacją i po niej nie zawierał `orto_r4.py`. Proces vmmemWSL zużył pomiędzy pierwszą i ostatnią próbką 0,656 s CPU. Kolejne odczyty przed testami i po nich również nie wykazały tego zadania liquidpatrol. Nie zatrzymywano żadnego zadania użytkownika ani nie zmieniano ustawień systemowych.

Proces testowy i wszystkie zaobserwowane procesy Lean miały klasę Normal (32) oraz dostęp do wszystkich 24 logicznych CPU. Użyto niezmienionego nadzorcy Windows Job Object, z atomowym JOB_LIST, kill-on-close i sprzątaniem potomków. Nie zastosowano profilu CPU z próby 08.

Natywny Lean: `C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe`, wersja 4.35.0, commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`. SHA256 obrazu: `ec7a472d1c12a09b0c0c718f7427c2be527b3f5f07810fdbe076c2507c7a91ea`. Ścieżkę, wersję i hash powiązano z narzędziem użytym do wcześniejszych dowodów.

## Nowe wykonania regresji

| Próba | Wynik | Czas unittest [s] | Limit nadzorcy [s] | Szczyt private [GiB] | Pozostałe procesy Job |
| --- | --- | ---: | ---: | ---: | ---: |
| Tylko test różnicowy | 1/1 PASS | 129,741 | 660 | 4,327 | 0 |
| Pełny aktualny zestaw | 180/180 PASS | 183,621 | 2400 | 5,084 | 0 |

Obie próby zachowały limit pamięci 6 GiB oraz oryginalny test różnicowy: 1547 przypadków i wewnętrzny timeout 600 s. Nie było błędów, niepowodzeń ani pominięć. W pełnym zestawie obserwowany czas testu różnicowego wynosił około 125,390 s; to pomiar próbkowany. Dla pojedynczej próby cały czas unittest 129,741 s stanowi bezpośrednią górną granicę czasu testu.

Każda próba otrzymała nową izolowaną kopię z historycznym README wymaganym przez niezmienione testy etapu 5. Przed wykonaniem sprawdzono wszystkie skopiowane wejścia; jedynym nadpisaniem treści było README. Po wykonaniu ponownie sprawdzono zakotwiczone pliki, kod i testy obu drzew oraz oba README. Rzeczywisty zbiór 180 kwalifikowanych nazw wyprowadzono z aktualnego kodu i niezależnie porównano z pełnym logiem, uwzględniając przeplatane komunikaty Fetching.

- [Wynik pojedynczej próby](../verification/stage8-single-09.json), [stderr](../local/stage8/close-09/single/process/stderr.log), [stdout](../local/stage8/close-09/single/process/stdout.log), [zasoby](../local/stage8/close-09/single/process/resource-report.json).
- [Wynik pełnej regresji](../verification/stage8-full-09.json), [stderr](../local/stage8/close-09/full/process/stderr.log), [stdout](../local/stage8/close-09/full/process/stdout.log), [zasoby](../local/stage8/close-09/full/process/resource-report.json).
- [Minutowa obserwacja hosta](../local/stage8/close-09/environment-before.json); rzeczywiste profile procesów i dalsze próbki są również zakotwiczone w raportach prób.

Sukces po ustąpieniu wcześniejszego obciążenia wspiera hipotezę jego wpływu na timeouty. Ten pomiar nie rozstrzyga jednej wyłącznej przyczyny; nie kontrolowano między innymi pamięci podręcznej systemu.

## Ponownie wykorzystane dowody i akceptacja

[Przegląd ponownego użycia](../verification/stage8-reuse-review-09.json) sprawdził 32 pełne inwentarze, 11 029 plików i hashe 133 raportów. Obejmuje kod, wersje zależności, natywne narzędzia, manifest z niezależną kotwicą SHA256, źródła, konfiguracje oraz dane o poprawkach. Końcowy recenzent ponownie sprawdził te tożsamości i powiązanie z wcześniejszym niezależnym audytem semantycznym.

Ponownie wykorzystano sześć pełnych dowodów źródło–odpowiedź dla 18 plików Chromium–Electron–Brave, dziewięć benchmarków grafowych do miliona węzłów z 27 pełnymi odpowiedziami i certyfikatami, pomiary indeksowania rzeczywistych oraz 10 000 syntetycznych źródeł, testy nadzorcy i drabinę Lean. Nie wykonywano ponownie pilota, benchmarków miliona węzłów ani kosztownych kompilacji tych dowodów. Zachowano dokładne bajty 78 historycznych plików oraz raporty final-06, retry-07 i retry-08.

[Sterownik regresji](../verification/stage8-close-09.py) i [sterownik agregacji](../verification/stage8-aggregate-09.py) mają [osobny przegląd regresji](../verification/stage8-close-tool-review-09.json) oraz [przegląd agregacji](../verification/stage8-aggregate-tool-review-09.json). Agregacja najpierw utrwaliła [kandydata](../verification/stage8-candidate-09.json), następnie związała jego dokładny hash z niezależnym przeglądem i ponownie sprawdziła dowody przed końcową oceną. Nie wystarczyło przepisanie pola statusu.

[Zasoby przeglądu](../verification/stage8-final-review-resources-09.json) zachowują również pierwsze nieudane sprawdzenie recenzenta, które błędnie wymagało opcjonalnego znacznika czasu pojedynczej próby. Poprawiony odczyt wykorzystał rzeczywisty czas całego testu, bez ponownego wykonywania testów. Końcowy przegląd trwał 18,119 s i zakończył z zerem procesów zadania.

Zakres gwarancji pozostaje taki sam: największy nowy dowód źródłowy obejmuje 18 rzeczywistych plików i 19 krawędzi, największy nowy zaakceptowany graf Lean ma 1000 węzłów. Próba 10 000 rzeczywiście osiągnęła limit 4 GiB. Milion węzłów dotyczy kontroli grafowej i certyfikatów Python. Ręcznie przyjęta specyfikacja mapowania pozostaje granicą zaufania opisaną w dokumentacji korpusu; dowód sprawdza jej wykonanie. Nie wykonywano wywołań LLM API ani odczytów kluczy.
