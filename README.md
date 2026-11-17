# Repo Proof Lab — etap 9

## Pilotaż Fineract R2

Do wyszukiwania literałów w Apache Fineract użyj
`scripts/fineract_r2.py query-verified`. Polecenie publikuje pełną odpowiedź
dopiero po porównaniu z przypiętymi obiektami Git. Gwarancja R2 dotyczy tej
odpowiedzi i jest odrębna od dowodów Lean dla grafów Mojom.
[Uruchomienie i ograniczenia](docs/fineract-r2-usage.md) ·
[Wyniki](docs/fineract-r2-results.md) ·
[Lokalna pamięć projektu](docs/project-memory-usage.md)

## Korpus Mojom

Etap 9 dodaje kontekstowy korpus **1251 rzeczywistych plików Chromium–Electron–Brave**,
4 188 752 bajty źródeł i 3286 krawędzi, w tym 13 między projektami.
[Kontrakt](docs/stage9-contract.md), [specyfikacja](docs/stage9-source-spec.md),
[publiczne CLI](docs/stage9-usage.md), [wyniki i ograniczenia](docs/stage9-results.md)
oraz [maszynowy status wszystkich bramek](verification/stage9-status.json).
Liczebność zaindeksowanego korpusu sama nie ustanawia pełnego dowodu:
największy rzeczywiście przyjęty zakres formalny wskazuje raport wyników.
Korpus dotyczy Chromium upstream oraz wybranych, audytowanych celów Electron i Brave;
nie całych grafów aplikacji po poprawkach. Dwa wyjścia generatorów GN są jawnymi
granicami źródłowego zakresu. Odtwarzanie wymaga ignorowanych lokalnych danych,
zależności i natywnego toolchain; zwykły czysty klon nie został sprawdzony.

Potwierdzone zamknięcie etapu 8 to **STAGE8_PASS**, commit `160860c`:
18 rzeczywistych plików trzech projektów i sześć dowodów źródło–odpowiedź;
1000 syntetycznych węzłów z zaakceptowanym dowodem grafowym Lean;
milion syntetycznych węzłów z kontrolą grafową i certyfikatami Python.
1864 pliki Chromium opisane dalej są osobnym historycznym wynikiem źródłowym.

## Historyczna ścieżka etapów 1–8

Etap 8 dodaje osobny [silnik wielu repozytoriów i benchmarki](docs/stage8-usage.md).
Stan rzeczywistego pilota i poziomy weryfikacji opisuje [uzupełnienie etapu 8](docs/stage8-completion.md).
Zachowano [historyczne wyniki etapu 8](docs/stage8-results.md).
Dotychczasowy formalnie sprawdzony korpus i interfejs Claude pozostają opisane poniżej.

Projekt odpowiada na pytanie, które pliki importują dokładnie wskazany plik
Mojom bezpośrednio lub przez łańcuch importów. Pełna odpowiedź obejmuje także
sam korzeń. Obsługiwane są wszystkie 1864 pliki wybranego korpusu Chromium,
zawierającego 4419 krawędzi importów. Etap 7 dodaje interpretację pytania
po polsku lub angielsku przez Claude i lokalną walidację przed uruchomieniem
dotychczasowego dowodu. [Instrukcja etapu 7](docs/stage7-usage.md),
[kontrakt](docs/stage7-contract.md) i [wyniki](docs/stage7-results.md).
Lean dowodzi wyniku dla wybranego korzenia; nie poprawności interpretacji
języka naturalnego. SDK Anthropic jest opcjonalną zależnością etapu 7.

## Gwarancja

Dla każdego zapytania powstaje nowy certyfikat i dowód Lean. Kernel sprawdza
akceptację certyfikatu, pełną listę wyników i jej powiązanie ze źródłami.
Warstwa źródło–graf korzysta z wcześniej przyjętego dowodu etapu 5 v2,
zakotwiczonego w commicie `7cbad10af87dc97bae4b23603921441aa899f7b0`.
Każde użycie ponownie kontroluje jego zależności i rzeczywiste bajty źródeł.

Gwarancja dotyczy `SourceBytes byte import projection v2` dla Chromium
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`, tree
`25131300fa459906dedb84bf592a8537b7848771`. Atrybuty warunkowe importów
pozostają niewartościowane. Formalny zakres obejmuje tekstowe importy w tym
snapshotcie. Ocena wpływu zmiany na działanie programu wymaga dalszej analizy.

Niezależny audyt odczytuje wszystkie dane eksportu i dopuszcza wyłącznie
zamkniętą postać deklaracji oraz kompletnych dowodów. Raporty aksjomatów muszą
być kompletne i jednoznaczne. Dopuszczone aksjomaty to `propext`,
`Classical.choice`, `Quot.sound`. Awaria kontroli blokuje wydanie nowej
zweryfikowanej odpowiedzi.

Założenia obejmują kernel i SDK Lean, uczciwe API systemu i procesów,
mechanizmy Git i odporność hashy na kolizje. Python, serializacja, wyświetlanie
oraz identyfikacja źródeł są audytowanymi granicami IO. Przebieg wymaga
zaufanego lokalnego katalogu wykonania, bez wrogiego współbieżnego zapisu.
Pełny opis zawierają [granica zaufania](docs/stage5-trust-boundary-v2.md),
[specyfikacja bajtowa](docs/stage5-source-spec-v2.md) i
[kontrakt etapu 6](docs/stage6-contract.md).

## Wymagania i dane lokalne

Potrzebne są Python 3.10+, Git oraz Lean 4.35.0 zgodny z przygotowanymi
modułami dowodu. Pomiary procesów w obecnym przebiegu wymagają Windows.
Runtime przypiętego parsera jest w `vendor/`. Polecenia uruchamiaj z katalogu
repozytorium, zachowując historię Git i commit kotwicy.

Zwykły klon zawiera kod, testy, dokumentację i raporty. Do uruchomienia etapu 6
potrzebne są dodatkowo wyłączone z Git dane lokalne

- `local/corpus.json` wskazujący korpus i przypięty commit.
- Oryginalne bajty korpusu, metadane Git i manifest zgodne z `corpus.lock.json`.
- Artefakty ekstrakcji etapu 2 w `local/stage2`.
- Przyjęty przebieg `local/stage5-v2/full-03`, wraz z pełnym zestawem źródeł
  i skompilowanych modułów `.olean` odpowiadających zapisanej kotwicy.

Przeniesienie tych danych wymaga dostosowania konfiguracji korpusu i zachowania
sprawdzanych tożsamości. Samowystarczalność nowego klonu pozostaje niewykazana.
Sposób pozyskiwania korpusu opisują `scripts/prepare_corpus.py --help` oraz
[historyczne wyniki etapu 2](docs/stage2-results.md).

## Przygotowanie i zapytanie

W PowerShell ustaw `$py` i `$lean` na dostępne lokalnie programy. Poniższy
przykład zakłada, że są osiągalne przez `PATH` oraz że wymagane dane już istnieją.
Każdy katalog wyjściowy musi mieć nową nazwę.

```powershell
$py = (Get-Command python).Source
$lean = (Get-Command lean).Source
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')

& $py scripts/stage6.py prepare --cache-dir local/stage6/my-prepared-proof `
  --source-run local/stage5-v2/full-03

& $py scripts/stage6.py query --cache-dir local/stage6/my-prepared-proof `
  --root 'mojo/public/mojom/base/values.mojom' `
  --run-dir local/stage6/my-values-query --lean $lean
```

Korzeń musi być dokładną ścieżką z korpusu z `/` i prawidłową wielkością liter.
Wynik znajduje się w `answer.json` i `answer.txt`. Sukces wymaga kodu 0
oraz `STAGE6_QUERY_PASS` w `query-report.json`. Przygotowanie kopiuje i sprawdza
wcześniejszy dowód źródłowy. Zapytanie wykonuje świeżą kontrolę swojego dowodu.

## Weryfikacja i aktualny przegląd

```powershell
$env:REPO_PROOF_LEAN = $lean
& $py scripts/check_stage6.py --lean $lean `
  --run-dir local/stage6/reproduce-new `
  --report verification/stage6-reproduce-new.json
```

Pełne regresje w tym poleceniu uruchamiają aktualny kod i testy w odizolowanej
kopii z historycznym README. Zachowane testy preflight etapu 5 wymagają jego
dawnych bajtów. Tożsamość kodu i testów jest sprawdzana przed i po wykonaniu,
a wyjątek dokumentacyjny jest jawnie zapisany w raporcie. Bezpośrednie
uruchomienie całej historycznej suity w bieżącym drzewie zgłasza dwa konflikty
z aktualizacją README.

`STAGE6_CHECKS_PASS` oznacza zaliczenie automatycznych kontroli. Końcowe
zatwierdzenie wymaga także przeglądu rzeczywiście sprawdzonego kodu.
Wynik tego audytu zapisano w [przeglądzie VS](docs/stage6-vs-review.md)
i [podsumowaniu maszynowym](verification/stage6-vs-review.json).
Świeży przebieg ma [raport run-04](verification/stage6-vs-audit-run-04.json).
Raporty historyczne zachowano, w tym
[run-01](verification/stage6-vs-audit-run-01.json),
[wyniki etapu 6](docs/stage6-results.md) i
[wyniki etapu 5 v2](docs/stage5-results-v2.md).
Szczegółowe użycie i ograniczenia opisuje [instrukcja etapu 6](docs/stage6-usage.md).
