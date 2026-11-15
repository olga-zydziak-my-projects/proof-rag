# Kontrakt etapu 8

Baza: `9d590b5b7538fb20f1061ef31e266f1ee9f221e8`. Gałąź:
`codex/stage8-multirepo`. Etapy 1–7, ich dane, dowody i baseline pozostają
zachowane; jedyny wyjątek modyfikacji istniejącego pliku to główny README.
Nie wykonujemy LLM API, odczytu kluczy ani publikacji.

Operacja pozostaje `reverse_importers`: wszyscy bezpośredni i pośredni
importerzy, wraz z korzeniem. Tożsamość pliku jest trójką
`(repo_id, commit, repo_relative_path)`. Kolejność źródłowej odpowiedzi to
porządek leksykograficzny tych trójek. Projekty i wersje liczymy osobno.

Osobne poziomy i bramki:

| Status/poziom | Warunek |
| --- | --- |
| `INDEX_IO_CHECKED` | Cały manifest, źródła Git, ekstrakcja i lokalny indeks zgodne w Pythonie |
| `GRAPH_PASS_WITH_PYTHON_SOURCE_IO` | Pełny wynik oraz certyfikat grafowy, dodatkowo ponowne sprawdzenie źródłowego indeksu przez Python; **bez formalnego source-to-answer** |
| `GRAPH_PASS` benchmarku | Pełne wyniki zgodne z niezależnym DFS; checker pełnego certyfikatu sprawdza rodziców, rangi i domknięcie |
| `LEAN_GRAPH_PASS` | Świeży kernel sprawdził graf, certyfikat i maskę całej odpowiedzi; brak twierdzenia o nowych źródłach |
| `STAGE8_PILOT_PASS` | Co najmniej 3 rzeczywiste, spójnie przypięte i połączone projekty, pochodzenie krawędzi, 6 korzeni, 3 pełne source-to-answer Lean, w tym 2 przekraczające repozytoria, wymagane odrzucenia |
| `STAGE8_PASS` | Pilot PASS oraz wszystkie trzy rozmiary GRAPH_PASS, regresje, przegląd i niezmienny kod |
| `STAGE8_PARTIAL` | Pilot PASS, lecz niezaliczone wymagane skalowanie |
| `STAGE8_CORPUS_BLOCKED` | Nie ustalono wymaganego rzeczywistego korpusu; syntetyczne sukcesy nie podnoszą tego statusu |
| `STAGE8_FAILED` | Niepowodzenie poprawności lub końcowych kontroli |

W tej implementacji pilot jest zablokowany. **Nie wdrożono ani nie zaakceptowano
formalnego mostu wielu repozytoriów źródło–odpowiedź**. Nie korzystamy z dowodu
Chromium jako dowodu nowych źródeł. Implementacja źródłowa jest sprawdzanym
operacyjnie fundamentem do dalszego etapu; brak tej formalizacji jest jawny.

Każdy przebieg otrzymuje nowy katalog. Błędy, brak plików lub repozytoriów,
niejednoznaczność, konflikt wersji i niezgodność indeksu blokują odpowiedź.
Nie powstaje pozornie formalnie zweryfikowany pusty wynik. Świadome wyłączenia
muszą być regułami manifestu przed zapytaniem i pozostają zdarzeniami zewnętrznymi.

Zamrożone parametry pomiarów są w `verification/stage8-benchmark-config.json`:
10K/100K/1M, trzy rodziny, seed 808, 3 korzenie i 3 powtórzenia każdego
wyszukiwania. Jeden wariant naraz, DuckDB 512 MB, jeden wątek, temp 2 GB;
limit nadzorowanego drzewa 4 GiB, artefaktów wariantu 8 GiB i czasu 600 s.
Nie podnosimy limitów po niepowodzeniu. `TIMEOUT` i `RESOURCE_LIMIT` nie są PASS.

Monitor próbkowany obejmuje siebie, worker i jego potomków. RSS sumuje strony
współdzielone wielokrotnie; równolegle mierzy private bytes. Nie jest to pomiar
całego Windows ani pamięci oddzielnego koordynatora. Raport zachowuje maksymalną
rzeczywistą przerwę między próbkami; krótkie skoki między próbkami są ograniczeniem.
Dla Lean limit dysku obejmuje wspólny katalog źródeł, modułów i logów.
Przebiegi nie są nazywane cold: cache systemu operacyjnego nie jest kontrolowany.

Soufflé jest oddzielnym, opcjonalnym eksperymentem. WSL wymaga natywnych limitów
i pomiaru Linux; liczniki potomków Windows nie mierzą uczciwie procesów Linux.
Zamrożenie i hashe programu Datalog oraz jego skryptu są zapisane osobno.

Podstawy doboru i interpretacji ustawień:
[DuckDB tuning](https://duckdb.org/docs/current/guides/performance/how_to_tune_workloads),
[DuckDB OOM](https://duckdb.org/docs/current/guides/performance/oom),
[Soufflé Magic Sets](https://souffle-lang.github.io/magicset).
Limit menedżera DuckDB nie zastępuje pomiaru pamięci całego procesu.
