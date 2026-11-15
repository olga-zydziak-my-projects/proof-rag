# Kontrakt etapu 7

Etap 7 dodaje jednorazową interpretację pytania PL/EN przez bezpośrednie
Anthropic Messages API. Domyślny model to `claude-haiku-5-5`, effort `medium`.
Zmiana modelu lub effort wymaga jawnej konfiguracji. Nie ma fallbacku.

Model otrzymuje wyłącznie stały opis operacji i pytanie, bez korpusu, narzędzi
i uprawnień wykonawczych. Zwraca dokładnie `operation` oraz `file_reference`.
Operacje: `reverse_importers`, `needs_clarification`, `unsupported`.
Odwołanie jest dosłownym fragmentem pytania lub null. Ścisły schemat API
uzupełnia lokalna kontrola JSON, duplikatów pól, typów i pochodzenia nazwy.
Rozstrzyganie nazw korzysta z ponownie sprawdzonego korpusu etapu 6.
Dokładne ścieżki i jednoznaczne nazwy są akceptowane; niejednoznaczność
zwraca kandydatów. Nie poprawiamy literówek, wielkości liter ani `..`.

Zakres: wszyscy bezpośredni i pośredni importerzy wraz z korzeniem w
przypiętym korpusie 1864 plików Mojom i 4419 importów. Kierunek przeciwny,
wyłącznie bezpośredni importerzy, zachowanie i wpływ zmian są niewspierane.
Granica języka naturalnego jest omylna i oceniana eksperymentalnie.
Lokalna zachowawcza bramka blokuje także jawne sformułowania o przeciwnym
kierunku (`Co importuje X?`, `Które pliki importuje X?`, `What does X import?`)
oraz wyłącznie bezpośrednich importerach. Bramka może tylko zatrzymać plan;
nie przekształca decyzji modelu w operację obsługiwaną. Nie jest kompletnym
parserem języka naturalnego.

Etap 6 działa przez osobny proces z listą argumentów, bez powłoki.
Wymagane są exit code 0, `STAGE6_QUERY_PASS`, zgodny korzeń, tożsamość
cache oraz zgodność całych odpowiedzi JSON i tekstowej z certyfikatem,
zachowanym grafem i hashami raportu. Wynik polski jest deterministyczny,
zawiera pełną listę oraz odnośnik do raportu. Nie ma drugiego wywołania LLM.

Formalna gwarancja dotyczy wyniku dla wybranego korzenia i specyfikacji
`SourceBytes byte import projection v2`. Nie dowodzi poprawności interpretacji
pytania przez Claude. Obowiązują założenia IO i zaufanego lokalnego katalogu
etapu 6. Wcześniejszy dowód źródłowy jest ponownie używany, a dowód zapytania
jest świeżo sprawdzany przez kernel Lean 4.35.0.

Limity: 8000 bajtów UTF-8 wejścia, 1024 tokeny wyjścia, timeout API 60 s,
timeout procesu etapu 6 2100 s. SDK `max_retries=0`; jedno żądanie na pytanie.
Ocena ma wspólny licznik maksymalnie 40 żądań. Błąd sieci, limit, odmowa,
brak tekstu, obcięcie, błędny format lub awaria dowodu blokują wydanie wyniku.
Treści wyjątków SDK nie są zapisywane, aby nie ujawnić danych uwierzytelnienia.

Zestaw oceny jest zamrożony w `verification/stage7-questions.json` przed
wywołaniami API; wymagamy co najmniej 90% trafności oraz poprawnego zatrzymania
wszystkich niejednoznacznych i niewspieranych przypadków. Trzy różne korzenie
wymagają rzeczywistych dowodów i porównania pełnych list z niezależnym punktem
stałym. Atrapy w testach jednostkowych sprawdzają obsługę, nie model ani Lean.

Zachowujemy historyczne pliki etapów 1–6; zmiana głównego README jest jawnym
wyjątkiem dokumentacyjnym. Regresje uruchamiają aktualny kod i testy w istniejącym
mechanizmie izolowanej kopii z historycznym README i kontrolą ich tożsamości.
