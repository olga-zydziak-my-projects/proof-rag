# Pytania o pliki testowe po polsku

## Pierwszy pomiar z 18 listopada 2026

Oba warianty poprawnie rozpoznały wszystkie 16 pytań. Bezpośrednie API kosztowało
0,0007753 USD, a DSPy 0,0012857 USD. Do dalszego testowania tej operacji wybrałbym
bezpośrednie API. W tym zbiorze dało tę samą trafność z niższym kosztem i krótszą
odpowiedzią w nowym procesie.

| Miara | Bezpośredni Claude | DSPy |
| --- | ---: | ---: |
| Poprawne decyzje | 16/16 | 16/16 |
| Błędnie wydane listy | 0 | 0 |
| Pełne listy zgodne z R2 | 8/8 | 8/8 |
| Tokeny wejścia / wyjścia | 7213 / 108 | 10 237 / 524 |
| Koszt według `usage` i cennika | 0,0007753 USD | 0,0012857 USD |
| Pełna odpowiedź, mediana i zakres | 2,306 s (2,238–2,514 s) | 7,029 s (6,726–7,478 s) |
| Generacja przez API, mediana i zakres | 0,731 s (0,684–0,994 s) | 0,784 s (0,729–1,277 s) |
| Liczenie tokenów przez API, mediana i zakres | 0,272 s (0,249–0,289 s) | 0,273 s (0,245–0,409 s) |
| Lokalny odczyt i filtrowanie, mediana i zakres | 5,72 ms (4,28–7,35 ms) | 6,33 ms (4,77–7,70 ms) |

Wykonano 32 próby generacji za łącznie 0,002061 USD. Nie było pomyłek,
także przy zakazie pokazywania testów (P13). Lokalne czasy obejmują osiem
żądań listy w każdym wariancie. Czas pełnej odpowiedzi obejmuje uruchomienie
procesu, import zależności, liczenie tokenów, generację i obsługę CLI.
To pojedynczy pomiar dla małego zestawu i uruchomień w świeżych procesach.

Wersje z pomiaru to Python 3.12.10, `anthropic` 2.8.0, DSPy 3.2.1 i LiteLLM
1.110.0. Raport zawiera odpowiedzi dostawcy z użyciem tokenów, decyzje,
zachowanie CLI i SHA-256 plików kodu, pytań i artefaktów R2. Pomiar oparto
na zmianach względem `c561d972292540c633338d7d7f11b63d0b2ea4af`.
[Pełny zapis pierwszego pomiaru](../verification/project-memory-intent-first.json)

Zaliczono 35 testów bez klucza, w tym 25 dotychczasowych i 10 nowych. Atrapy
pokryły m.in. błędny format, timeout, brak aktywnego wyniku, zmianę artefaktów
i zatrzymanie przed wywołaniem poza rezerwą. Osobno sprawdzono błędny format
w zainstalowanym DSPy za pomocą lokalnej atrapy i zatrzymanie serii bez klucza.

## Metoda

Zamrożony zestaw obejmuje osiem próśb o pełną listę testów, cztery pytania
niejednoznaczne i cztery jawnie wykraczające poza dostępną operację. Niejasny
cel oznacza `clarify`. Prośba o wynik uruchomienia, treść plików, samą liczbę
lub listę po wykluczeniu testów oznacza `unsupported`. Tylko `show_test_paths`
uruchamia odczyt aktywnego wyniku i lokalne filtrowanie po `src/test/`.
[Zamrożone pytania](../verification/project-memory-intent-questions.json)

Oba warianty użyły potwierdzonego przez Models API `claude-haiku-5-5`,
identycznych zasad i trzech przykładów spoza zestawu, limitu 96 tokenów
wyjścia, wyłączonego trybu thinking i domyślnego próbkowania. Bezpośredni
wariant prosi o samą etykietę. DSPy używa jednej sygnatury `question → decision`,
`Predict` i `ChatAdapter`. W obu wariantach wysyłkę obsługuje ten sam oficjalny
SDK Anthropic. Warstwa DSPy formatuje wejście i interpretuje wyjście.
Wyłączono cache aplikacji, ponowienia i wywołania zapasowe. Kolejność wariantów
odwracano co pytanie. [Model](https://platform.claude.com/docs/en/models/haiku-5-5/overview),
[DSPy 3.2.1](https://dspy.ai/3.2.1/api/adapters/ChatAdapter/)

Każde pytanie uruchamiało osobny proces CLI. Oba warianty miały to samo
przypisanie rozmów. W tymczasowej bazie rozmowa A wskazywała `LoanTransaction`
(294 ścieżki testowe z 718), a B `BigDecimal` (570 z 1362). Porównanie obejmowało
literał, licznik i całą uporządkowaną listę. Do API trafiały pytanie i instrukcja.

Przed uruchomieniem serii zaplanowano 32 próby ze wspólnego limitu 1 USD.
Przed każdą próbą rezerwowano 0,008432 USD według wyższej stawki modelu dla
16 384 tokenów wejścia i 96 wyjścia. Suma rezerw wynosiła najwyżej 0,269824 USD.
Bezpłatny `count_tokens` sprawdzał każde gotowe wejście z zapasem `2 × szacunek + 2048`.
Odpowiedzi rozliczano z pola `usage` według opublikowanych stawek dla długości
wejścia. Dla nieznanego użycia narzędzie zachowuje rezerwę. [Cennik](https://platform.claude.com/docs/en/about-claude/pricing),
[Liczenie tokenów](https://platform.claude.com/docs/en/build-with-claude/token-counting)

## Odtworzenie

Użyj działającego `$projectPython` z [instrukcji pamięci](project-memory-usage.md).
Uruchom z głównego katalogu projektu z kluczem `ANTHROPIC_API_KEY` już
dostępnym w środowisku. Wykonanie skryptu rozpoczyna nową płatną serię.

```powershell
& $projectPython -B -X utf8 -m pip install -r requirements-project-memory-intent.txt 'litellm==1.110.0'
& $projectPython -B -X utf8 scripts/evaluate_project_memory_intent.py `
  --run-dir local/project-memory-intent/repro-01
```

Jeśli opublikowane katalogi są w innych miejscach, użyj `--loan-result` i
`--decimal-result`. Skrypt tworzy nowe `report.json` w podanym katalogu i
zapisuje każdą próbę oraz osobno decyzję i obserwowane zachowanie CLI.
