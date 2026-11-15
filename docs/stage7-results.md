# Wyniki etapu 7 — 15 listopada 2026

Stan bazowy: `683ec76b021349cf5b911aabf77f01e07fc6828f`. Praca użytkownika
nie wymagała rozwiązywania konfliktów; historia i kotwice etapów 1–6 zostały
zachowane. Główny README jest jawnym wyjątkiem dokumentacyjnym.

## Rzeczywiste Claude API

Użyto bezpośredniego Messages API, modelu `claude-haiku-5-5`, effort `medium`,
oficjalnego Python SDK `anthropic==2.8.0`, promptu `stage7-v1`.
`output_config.format` wymusza ścisły JSON Schema; dodatkowa lokalna walidacja
kontroluje pola, wartości, dosłowne odwołanie i korpus. Nie użyto narzędzi LLM,
drugiego wywołania do opisania wyników, OpenAI API ani tokena GitHub.

Klucz był dostępny w środowisku procesu. Odczyt zmiennej użytkownika Windows
w tej sesji nie wykazał wartości; dostępność procesu wystarczyła do rzeczywistych
żądań. Wartości klucza nie wypisywano ani nie zapisano w projekcie.

Pierwszy zestaw 32 pytań PL/EN zamrożono przed wywołaniami. SHA-256 zestawu:
`831838e271932dd3f4b30e59c724c78ed70b01ef331c74f34092e616f42ceb7c`.
[Pytania](../verification/stage7-questions.json),
[oryginalne odpowiedzi i raport](../verification/stage7-live-01.json).

| Ocena | Wynik | Znaczenie |
| --- | --- | --- |
| Pierwsza ocena Claude i początkowej aplikacji | 31/32, 96,875% | Jeden błąd kierunku; kryterium zatrzymania niewspieranych pytań niespełnione |
| Replay tych samych odpowiedzi przez finalny resolver | 32/32 | Ocena po poprawce lokalnej, bez nowych żądań |
| Osiem dodatkowych pytań przez rzeczywiste API | 8/8 finalnych decyzji | Lokalna bramka zatrzymała dwa błędy kierunku Claude |

Oryginalny eksperyment ma zachowany status `STAGE7_FAILED`. Model zinterpretował
„Co importuje mojo/public/mojom/base/time.mojom?” w przeciwnym kierunku.
Po tym wyniku dodano zachowawczą lokalną bramkę jawnych pytań o kierunek
przeciwny i wyłącznie bezpośrednich importerów. Nie zmieniono promptu ani
zapisanych odpowiedzi. Osiem dodatkowych pytań zamrożono przed tą poprawką w
[osobnym zestawie](../verification/stage7-holdout.json).

Na dodatkowych pytaniach Claude popełnił dwa podobne błędy, które aplikacja
zatrzymała. Surowa skuteczność modelu wynosi zatem 37/40, 92,5% na łącznym
materiale. Decyzje finalnej aplikacji to 32/32 w replayu i 8/8 w nowych
wywołaniach. Replay jest jawnie oceną po poprawce, a nie niezależną oceną
generalizacji. Nie wynika z tego ogólna gwarancja rozumienia języka.

Wykonano łącznie **40 fizycznych żądań**, przy `max_retries=0`.
Pierwsza część: 19 871 tokenów wejścia, 2234 wyjścia, suma czasów wywołań
52,440 s. Dodatkowa część: 5028 wejścia, 480 wyjścia, 10,771 s.
Łącznie: **24 899 tokenów wejścia, 2714 wyjścia, 63,211 s** czasu wywołań.
Surowe odpowiedzi zachowują pełne dane `usage` i rzeczywisty model odpowiedzi.

## Dowody i regresje

Pierwsza wersja wykonała trzy rzeczywiste przebiegi pytanie → API → plan →
CLI etapu 6 → świeży kernel Lean → pełna odpowiedź. Całe listy zgadzały się
z niezależnym synchronicznym punktem stałym:

| Korzeń | Wyniki |
| --- | ---: |
| `mojo/public/mojom/base/time.mojom` | 477 |
| `mojo/public/mojom/base/values.mojom` | 240 |
| `ash/public/mojom/accelerator_actions.mojom` | 5 |

Końcowa kontrola ponawia te trzy dowody na zamrożonym finalnym kodzie,
wykorzystując dokładnie powiązane autentyczne odpowiedzi API z pierwszej oceny.
Nie nalicza dodatkowych wywołań modelu. Pełne listy, certyfikaty, źródła Lean,
logi i raporty są w `local/stage7/final-01/full-01` do `full-03`.
Dowód źródłowy jest ponownie używany z cache
`local/stage6/vs-public-cli-04/prepared`; dowody zapytań są świeże.

21 testów offline etapu 7 przeszło także w niezależnym uruchomieniu recenzenta.
Obejmują one schema/JSON, duplikaty pól, pochodzenie odwołania i granice nazwy,
nazwy dokładne/jednoznaczne/niejednoznaczne/nieistniejące, brak korekt ścieżek,
lokalną bramkę zakresu, odmowy i obcięcia, brak tekstu, błędy i limit API,
zachowanie metadanych błędnej odpowiedzi, timeout/awarię procesu oraz
odmowę wydania podmienionej pełnej odpowiedzi. Atrapy są wyłącznie testami
obsługi kodu, a nie dowodem działania Claude lub Lean.

Pierwszy przebieg regresji zaliczył 136 testów, ale końcowa kontrola tożsamości
odrzuciła go, ponieważ README i testy zostały zmienione podczas wykonania.
Nie traktujemy go jako finalnej regresji. Zachowano
[raport odrzucenia](../verification/stage7-initial-regression.json) i lokalne logi.
Końcowa regresja używa istniejącej izolowanej kopii z historycznym README;
aktualny kod i testy muszą być identyczne przed i po wykonaniu.

## Ograniczenia i odtworzenie

Lean dowodzi pełnego wyniku dla zaakceptowanego korzenia w przypiętym
korpusie i relacji `SourceBytes byte import projection v2`. Nie dowodzi
poprawności interpretacji pytania. Lokalna bramka jest skończonym zbiorem
reguł obronnych i nie eliminuje wszystkich możliwych błędów semantycznych LLM.
Wymagane są zaufany katalog lokalny, zachowane dane korpusu i moduły dowodu
etapu 5. Zwykły klon nadal nie jest samowystarczalny.

Polecenia instalacji, pytań i walidacji opisuje [instrukcja](stage7-usage.md).
Końcowy eksperyment wykonano przez `scripts/check_stage7.py` z
`--evaluation local/stage7/live-01/evaluation.json`,
`--run-dir local/stage7/final-01` oraz
`--report verification/stage7-final-01.json`.
Wyczerpano budżet online tego eksperymentu; nie wykonuj dalszych wywołań jako
jego części. Projekt zapisujemy lokalnie w Git, bez deklarowania publikacji.

Końcowy status: **STAGE7_PASS**.
[Raport końcowy](../verification/stage7-final-01.json) zaliczył wszystkie bramki:
32/32 decyzji replayu, 8/8 nowych pytań, limit 40 żądań, trzy pełne dowody,
niezmieniony kod podczas kontroli i zachowanie historycznych plików.
Finalna regresja: **141 testów, 0 błędów, 0 niepowodzeń, 0 pominięć**, 167,128 s.
Obejmuje zachowany test różnicowy 1547 przypadków Python–Lean.
Tożsamości kodu i testów kopii regresyjnej oraz drzewa głównego są zgodne.

Trzy końcowe przebiegi mają `STAGE7_QUERY_PASS` i `STAGE6_QUERY_PASS`, z
pełną zgodnością wszystkich 477, 240 i 5 ścieżek z niezależnym obliczeniem.
Zachowane raporty dowodów:
[time](../verification/stage7-query-01.json),
[values](../verification/stage7-query-02.json),
[accelerator_actions](../verification/stage7-query-03.json).
Nie pominięto żadnego wymaganego testu. Pierwotne niepowodzenia opisane wyżej
pozostają częścią historii eksperymentu; finalne zaliczenie dotyczy poprawionej
aplikacji, nie nieomylności Claude.

Niezależny recenzent `/root/stage7_review` zatwierdził finalny kod i raporty:
PASS. Samodzielnie zaliczył 21 testów offline, ponownie sprawdził korpus,
pełne odpowiedzi i ich zgodność z niezależnym obliczeniem oraz tożsamości
raportów i aktualnego kodu. Nie wykonywał dodatkowych żądań API.
[Zapis przeglądu](../verification/stage7-review.json).
