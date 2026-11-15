# Przebieg etapu 8 final-06

**STAGE8_INCOMPLETE**. Korpus, most formalny, sześć rzeczywistych dowodów, skalowanie, indeksowanie i nadzorca przeszły. Historyczny test różnicowy Lean przekroczył oryginalny limit 600 s przy wysokim równoległym obciążeniu WSL. Wykonano 180 testów z jednym błędem timeout i bez pominięć.

## Stan kodu i historia

Początek pracy odpowiadał `d0af2aecc6baf0ec870f51de6ab62d586bc5805d`, gałęzi `codex/stage8-multirepo` i czystemu drzewu. Kod przed i po przebiegu jest identyczny z [przeglądem 08](../verification/stage8-code-review-08.json). Zachowano dokładne surowe bajty 78 historycznych plików. Osobna kontrola porównuje treść Git z uwzględnieniem istniejących LF/CRLF. Jedynym jawnym nadpisaniem treści w kopii regresji pozostaje historyczne README.

## Naprawy i sprawdzenie

- Nadzorca tworzy zawieszony proces atomowo w Windows Job Object przez JOB_LIST. Po wyjściu rodzica kończy pozostałych potomków, czeka na zakończenie i zamyka uchwyty. Kill-on-close obejmuje awarię monitora i śmierć przed ResumeThread. Zakończenie używa uchwytów procesu i Job Object. Końcowy limit artefaktów obejmuje sam raport. Dwanaście rzeczywistych testów obejmuje trzy pokolenia, szybkie wyjście rodzica, awarie, przerwanie i limity.
- Capture buduje mapę metadanych raz, odczytuje źródła przez trwałe cat-file --batch i utrzymuje pojedynczy blob w pamięci. Fakty są przechowywane na dysku i zapisywane partiami. Pełne źródła, drzewa, hashe, konfiguracje i rozstrzygnięcia są ponownie kontrolowane przy zapytaniu. Prefiksy zachowują wcześniejszą semantykę startswith.
- Kontrakt przywraca sześć pełnych rzeczywistych dowodów i minimum trzy odpowiedzi między repozytoriami. [Poprzedni kontrakt](stage8-contract-before-correction.md) pozostaje zachowany.
- ContextualSourceBinding łączy pełne bajty ze skanerem, niezależnym resolverem, obustronną zgodnością grafu, certyfikatem i pełnymi tożsamościami odpowiedzi. Zamknięty parser audytuje całą dozwoloną postać eksportu. Nowe zależności, źródła i zapytania są kompilowane świeżo w prywatnym LEAN_PATH.
- Bramka wymaga pełnej macierzy benchmarków, dowodów, porównań odpowiedzi, negatywnych testów i tożsamości kodu. Po kontroli semantycznej utrwala pełny inwentarz artefaktów i porównuje go ponownie przed akceptacją. Usunięcie, dodanie i podmiana pliku blokują akceptację. Parser wyników testów rozpoznaje dokładne kwalifikowane nazwy z LF, CRLF i CR.

```powershell
$env:PYTHONPATH = 'src;local/stage8-deps'
& $py -m unittest discover -s tests -p "test_stage8*.py" -v
```

Zestaw etapu 8 zawiera 39 testów. Dawny nadzorca zwracał PROCESS_PASS z żywym dzieckiem i wnukiem. Aktualny test test_fast_root_exit_drains_child_and_grandchild sprawdza zakończenie obu i samodzielne sprzątanie.

## Korpus

| Projekt | Wydanie | Commit | Pliki |
| --- | --- | --- | ---: |
| Chromium | 140.0.7339.133 | `3927f129b801f969d4abdb1458d55174cc062723` | 10 |
| Electron | v38.1.2 | `d60ae179985685d75d238ee33e17c15a7b53d703` | 2 |
| Brave Core | v1.82.166 | `38bf45887ca5336841cddb4200e6deee32ce45a8` | 6 |

Zakres obejmuje pełne cele GN Electron plugin i web_contents_utility, pełny cel Mojom AI Chat Brave oraz wszystkie ich importy. Łącznie ma 18 plików, 42 268 bajtów i 19 krawędzi. Zakres zamrożono przed wyborem korzeni. Historyczne wydania przypinają dokładnie ten sam Chromium.

Electron plugin importuje content/public/common/webplugininfo.mojom oraz url/mojom/url.mojom z Chromium. Brave ai_chat importuje mojo/public/mojom/base/time.mojom i url/mojom/url.mojom. Wspólny rzeczywisty url.mojom łączy projekty. Pełne importery, literały, cele i konfiguracje zawiera [manifest LF](../verification/stage8-connected-corpus-manifest-04.json) z kotwicą `ca113f50946345eacd8905d48fb2367dd0a95886bbb72631d4ec6cb344d204e1`.

Audyt obejmuje 225 poprawek Electron, 644 Brave i 2780 wpisów nakładek Brave. Żaden przyjęty plik nie jest zmieniany w analizowanych kontekstach. Oryginalny zakres Electron API odrzucono, ponieważ jego domknięcie sięga do patchowanego url_response_head.mojom. Uzasadnienie i granice ręcznie przyjętej specyfikacji opisuje [rozpoznanie korpusu](stage8-connected-corpus.md). Lean dowodzi wykonania tej specyfikacji. Semantyka całego GN i DEPS pozostaje osobnym założeniem.

## Sześć rzeczywistych zapytań

Wszystkie korzenie pochodzą z przypiętego Chromium. Każdy przebieg obejmuje wszystkie 18 źródeł, świeży kernel i pełne porównanie odpowiedzi z niezależnym oracle.

| Korzeń | Liczba wyników | Projekty | Poziom |
| --- | ---: | ---: | --- |
| `url/mojom/url.mojom` | 7 | 3 | Pełny źródło–odpowiedź Lean |
| `content/public/common/webplugininfo.mojom` | 2 | 2 | Pełny źródło–odpowiedź Lean |
| `mojo/public/mojom/base/big_buffer.mojom` | 3 | 2 | Pełny źródło–odpowiedź Lean |
| `mojo/public/mojom/base/string16.mojom` | 2 | 2 | Pełny źródło–odpowiedź Lean |
| `mojo/public/mojom/base/time.mojom` | 3 | 2 | Pełny źródło–odpowiedź Lean |
| `mojo/public/mojom/base/unguessable_token.mojom` | 5 | 2 | Pełny źródło–odpowiedź Lean |

## Skalowanie grafów

Dane są syntetyczne. Wszystkie 27 pełnych list i certyfikatów porównano z niezależnym obliczeniem.

| Węzły | Rodzina | Krawędzie | Czas zadania [s] | RSS [MiB] | Private [MiB] |
| ---: | --- | ---: | ---: | ---: | ---: |
| 10000 | chain | 9999 | 2.400 | 166.0 | 897.0 |
| 10000 | modular | 9999 | 2.489 | 168.4 | 894.5 |
| 10000 | cycles | 10124 | 2.602 | 167.8 | 886.9 |
| 100000 | chain | 99999 | 4.960 | 240.1 | 944.0 |
| 100000 | modular | 99999 | 4.974 | 243.6 | 948.1 |
| 100000 | cycles | 101249 | 4.855 | 234.1 | 949.6 |
| 1000000 | chain | 999999 | 33.130 | 782.6 | 1581.1 |
| 1000000 | modular | 999999 | 35.035 | 782.3 | 1580.4 |
| 1000000 | cycles | 1012499 | 33.615 | 746.5 | 1539.0 |

Największy graf Python ma 1 000 000 węzłów i 1 012 499 krawędzi. Jego poziom to pełna kontrola grafowa i certyfikat Python. Pole legacy NOT_RUN_SIZE_BOUND_64 dotyczy zachowanej małej ścieżki eksportu benchmarku. Osobna drabina poniżej mierzy nową reprezentację blokową.

## Indeksowanie źródeł Git

| Pochodzenie | Pliki | Bajty źródeł | Capture [s] | Generowanie [s] |
| --- | ---: | ---: | ---: | ---: |
| synthetic-fixture | 10000 | 509967 | 3.916 | 55.913 |
| real | 18 | 42268 | 5.278 | 0.001 |

Capture obejmuje pełne uniwersum Git, bloby, hashe, konfiguracje, skaner i resolver. Dziesięć tysięcy źródeł to syntetyczne pliki w lokalnym Git. Pomiar jest oddzielny od benchmarku tablic krawędzi.

## Drabina Lean

| Węzły | Wynik | Kompilacja i kernel [s] | Szczyt monitorowany [MiB] | Artefakty [B] |
| ---: | --- | ---: | ---: | ---: |
| 256 | LEAN_GRAPH_PASS | 9.973 | 2205.8 | 3534246 |
| 1000 | LEAN_GRAPH_PASS | 23.735 | 2375.8 | 12905168 |
| 10000 | RESOURCE_LIMIT | 97.217 | 4112.5 | 15241355 |

Wszystkie trzy próby rzeczywiście uruchomiono. Próba 10 000 osiągnęła zadeklarowany limit 4 GiB. Największy nowy graf z pełnym dowodem Lean ma 1000 węzłów. Największy nowy korpus z pełnym dowodem źródłowym ma 18 rzeczywistych plików. Historyczny dowód 1864 plików Chromium z wcześniejszych etapów zachowuje odrębną tożsamość.

## Regresja, przegląd i ograniczenia

Przebieg 06 wykonał 180 testów, bez pominięć, z jednym TimeoutExpired w historycznym test_differential. Test zachowuje oryginalny limit 600 s i 1547 przypadków. Limit całej regresji wynosił 2400 s i jawnie 6 GiB. Pozostałe próby zachowały 600 s, 4 GiB i 8 GiB artefaktów. Jeden kosztowny proces Lean działał naraz. Raporty pamięci sumują monitor i nadzorowane zadanie, z osobnymi RSS/private i rzeczywistymi odstępami próbkowania. Koordynator oraz cały Windows mają osobną pamięć.

Przebieg 03 zachowuje błąd limitu regresji 4 GiB i wcześniejsze zamrożenie kodu. Start 04 przerwano przed próbami z powodu kontroli starszych formatów tekstowych. Przebieg 05 zachowuje 179 zaliczonych testów i niezaliczoną agregację logów CRLF. Każda poprawka otrzymała nowe zamrożenie i nowe próby. Stare raporty pozostają historią.

Niezależny [przegląd artefaktów 06](../verification/stage8-independent-core-review-06.json) porównał źródła oddzielnym lexerem i domknięciem punktu stałego, wszystkie sześć odpowiedzi, całą dozwoloną postać eksportów, hashe modułów, raporty aksjomatów, dziewięć uniwersów grafowych oraz 27 pełnych odpowiedzi i certyfikatów. Jego pojedyncza blokująca uwaga dotyczy timeout regresji. Równoległy vmmemWSL dominował przy odczycie CPU bliskim 99%. Czasy są obserwacjami przy rzeczywistym obciążeniu.

## Odtworzenie

Wskaż Python i Lean zgodnie z [instrukcją](stage8-usage.md), zachowaj lokalne obiekty w local/stage8/connected-recon-01 i wybierz nowe nazwy katalogu oraz raportu.

```powershell
$env:PYTHONPATH = 'src;local/stage8-deps'
& $py scripts/check_stage8.py `
  --run-dir local/stage8/reproduce-new `
  --report verification/stage8-reproduce-new.json `
  --lean $lean `
  --manifest verification/stage8-connected-corpus-manifest-04.json `
  --manifest-sha256 ca113f50946345eacd8905d48fb2367dd0a95886bbb72631d4ec6cb344d204e1 `
  --locations local/stage8/connected-recon-01/locations.json `
  --corpus-evidence verification/stage8-connected-corpus-evidence-04.json `
  --review verification/stage8-code-review-08.json `
  --regression-memory-bytes 6442450944
```

Domyślny kod wyjścia oznacza wynik całego etapu. Tryb --independent-only jest jawnie ograniczony do części niezależnych. Obowiązkowy brak tego przebiegu to zaliczenie pełnej regresji bieżącego kodu z zachowanymi historycznymi testami.
