# Etap 2 — ekstrakcja Mojom i pierwsze zapytanie

9 listopada 2026. Zapytanie o `mojo/public/mojom/base/time.mojom` ma wynik
**477 plików**, wraz z korzeniem, i status `complete_for_declared_scope`.
Cały zadeklarowany zakres `S` został przetworzony: nie było potrzeby
wykluczania plików testowych ani zmiany kontraktu. Ten status jest wynikiem
przetestowanej implementacji; nie stanowi formalnego dowodu ekstrakcji.

## Zachowany stan i dane

Przed zmianami utrwalono etap 1 lokalnym commitem
`376fe37f5872fad1f30896813b6b53e6b71e599a`, z istniejącą tożsamością autora
Git. Zapis wymagał uprawnień do `.git`; różnicę właściciela obejściowo
rozstrzygnięto opcją `git -c safe.directory=<dokładny katalog projektu>`
wyłącznie dla tego wywołania. Nie ustawiano fikcyjnego autora ani globalnej
konfiguracji. Niczego nie publikowano.

Odtworzono stan bazowy: 30 testów Python, sześć twierdzeń Lean bez aksjomatów,
kontrole manipulacji i pełna weryfikacja korpusu offline. Raporty:
`verification/stage2-baseline.json` i `stage2-corpus-baseline.json`.
Nie znaleziono obowiązujących `AGENTS.md` w projekcie ani jego przodkach.
Sprawdzony interpreter to Python 3.12.14; Git ma wersję 2.55.0.windows.2.

Lokalizacja korpusu nadal pochodzi z `local/corpus.json`, a niezależne
oczekiwania pochodzą z `corpus.lock.json`. Nie zmieniono commitu Chromium:

```text
27cec857a08a0ee0e1b41f5eb18c07467a0ce093
```

SHA-256 istniejącego manifestu pozostaje:

```text
1e6fe63490e2007c56b088194f0c2acb61abc834aeefb4edb2bbfe6399bc2e4a
```

Zweryfikowano pełne 564 613 wpisów metadanych Git, w tym 1 864 zwykłe pliki
`.mojom` o łącznej długości 6 946 142 oryginalnych bajtów. Ponownie sprawdzono
także trzy materializowane pliki referencyjne etapu 1. Nie pobierano całego
Chromium, DEPS ani zawartości gitlinków, nie uruchamiano budowania i hooków.

## Parser i ekstrakcja

Wybrano **niezmodyfikowany parser Chromium z przypiętego commitu**, aby
sprawdzać składnię całych plików, także po ostatnim imporcie. Zależności to
minimalny zestaw 14 oryginalnych plików, razem 244 585 bajtów, w tym PLY 3.11
i trzy pliki licencyjne. Są w `vendor/chromium`; `vendor/mojom-parser.lock.json`
zawiera ścieżki źródłowe, OID Git, SHA-256, długości oraz pochodzenie.
Adapter i skrypt kontroli uwierzytelniają także sam lock przed użyciem.
Szczegóły odtwarzania i licencji: [vendor/README.md](../vendor/README.md).

Adapter osobno zachowuje oryginalne tokeny. Pole `ast.Import.import_filename`
w upstream normalizuje ścieżkę przez `os.path.normpath`; **nie używamy tego
pola do rozwiązywania importów**. Surowy literał jest dekodowany bez
normalizacji i sprawdzany według niezmienionego kontraktu. Nie ewaluujemy
warunków importów i nie przeszukujemy dodatkowych katalogów kompilacji.

Pochodzenie każdej deklaracji obejmuje ścieżkę importera, OID bloba,
oryginalny literał z cudzysłowami, zakres deklaracji wraz z atrybutami,
zakres słowa `import` i literału oraz rozstrzygnięty cel, status i przyczynę.
Zakresy są półotwartymi offsetami **bajtów UTF-8**, a nie indeksami znaków.
Wiersze i kolumny bajtowe zaczynają się od 1. Weryfikowane są oryginalne
wycinki literału, słowa kluczowego, atrybutów i końcowego średnika. CRLF i
Unicode pozostają bez zmiany oryginalnych bajtów.

| Własność | Rzeczywisty wynik |
| --- | ---: |
| Pliki `S`, węzły grafu, końcowe statusy plików | 1 864 |
| Pliki zweryfikowane bajtowo i sparsowane w całości | 1 864 |
| Pliki `resolved` / `unresolved` | 1 864 / 0 |
| Deklaracje importów | 4 428 |
| Deklaracje `internal` | 4 424 |
| Deklaracje `outside_scope` | 4 |
| Deklaracje `unresolved` | 0 |
| Deklaracje z atrybutami | 69 |
| Unikalne krawędzie importer → importowany | 4 419 |
| Nadmiarowe deklaracje wewnętrzne wskutek duplikatów | 5 |
| Diagnostyki błędów | 0 |
| Wyniki zapytania, włącznie z korzeniem | 477 |

Wszystkie lokalizacje duplikatów zachowano. Cztery granice zakresu to:

- `chrome/services/file_util/public/mojom/document_analysis_service.mojom`,
  wiersz 9 → `chrome/services/file_util/public/mojom/safe_document_analyzer.mojom`.
- `third_party/blink/public/mojom/navigation/navigation_params.mojom`,
  wiersz 43 → `third_party/blink/public/mojom/runtime_feature_state/runtime_feature.mojom`.
- `third_party/blink/public/mojom/origin_trials/origin_trial_state_host.mojom`,
  wiersz 6 → ten sam cel `runtime_feature.mojom`.
- `third_party/blink/public/mojom/worker/worklet_global_scope_creation_params.mojom`,
  wiersz 10 → `third_party/blink/public/mojom/origin_trials/origin_trial_feature.mojom`.

Każdy cel ma kanoniczną ścieżkę, lecz brak dokładnie takiego śledzonego wpisu
w przypiętym drzewie Git. Są to rozstrzygnięte granice grafu indukowanego
przez `S`; ścieżki zapytania nie przechodzą przez te cele. Nie przypisujemy
im zawartości przez budowanie ani pobieranie dodatkowych źródeł.

## Związanie źródeł, grafu i wyniku

Artefakt ekstrakcji zawiera commit, SHA-256 manifestu, OID drzewa, niezmienioną
wersję kontraktu `mojom-import-dependents-v1`, wersję i hashe implementacji
ekstraktora, tożsamość parsera oraz identyfikator grafu. Ten ostatni używa
kanonicznego formatu dotychczasowego modułu `graph.py`:

```text
0b47a4e7333b12e42dc7571b1ab2720530868fa299a1f7ca75e3d9a6a08a440a
```

Identyfikator grafu nie jest hashem pliku `graph.json`: zapis pliku zawiera
również końcowy LF. Hashe rzeczywistych plików zapisano osobno w raportach.

Weryfikator instancji otrzymuje oczekiwany commit, manifest, kontrakt i korzeń
z niezależnych wejść. Ponownie enumeruje drzewo Git, sprawdza każdy
materializowany blob, wykonuje pełne parsowanie i porównuje rzeczywistą
zawartość grafu, całe pochodzenie, statusy i diagnostyki z dostarczonym
artefaktem. Sprawdza także osobny `graph.json` i wyświetlany `query.json`.
Dopiero dla odtworzonego grafu uruchamia dotychczasowy checker certyfikatu.
Nie wywołuje generatora ani jego wyszukiwania.

Potwierdzone ścieżki z kontraktu:

```text
mojo/public/mojom/base/file_info.mojom
  → mojo/public/mojom/base/time.mojom

services/network/public/mojom/url_loader.mojom
  → services/network/public/mojom/url_response_head.mojom
  → mojo/public/mojom/base/time.mojom
```

Wynik i certyfikat są w `local/stage2/query.json` oraz `certificate.json`.
Pełna ekstrakcja i graf są w tym samym katalogu. Weryfikacja źródłowa
zaakceptowała certyfikat i status `complete_for_declared_scope`. Niezależny
przegląd porównał wyniki z bezpośrednim odczytem AST i surowych tokenów oraz
osobnym obliczeniem punktu stałego, bez wywoływania generatora. Otrzymał te
same liczby, identyfikator grafu i 477 wyników. To kontrola implementacji,
nie drugi niezależnie dowiedziony parser ani formalny dowód ekstrakcji.

## Pomiary i odtwarzalność

W zakończonym uruchomieniu z `verification/stage2-run.json`:

| Faza | Czas ścienny |
| --- | ---: |
| Weryfikacja korpusu | 5,457 s |
| Parsowanie wszystkich plików i budowa grafu | 8,513 s |
| Wyszukiwanie i utworzenie certyfikatu | 0,011719 s |
| Checker certyfikatu grafowego | 0,010613 s |
| Pełna weryfikacja instancji od źródeł do wyniku | 17,125 s |

Ostatnia faza wykonuje ponownie weryfikację korpusu, ten sam parser i checker;
nie jest sumą tylko dwóch małych faz grafowych. Pierwsze parsowanie obejmuje
inicjalizację parsera. To pojedyncze rzeczywiste pomiary na tym komputerze,
bez deklaracji benchmarku całego agenta albo gwarancji czasu/pamięci.

Polecenia `run`, `verify`, `tamper` i powtórzenie `run` są opisane w
[README](../README.md). Nie wykonują operacji sieciowych. Dane korpusu
pozostają poza repozytorium, a duże artefakty w ignorowanym `local/`.
Daty i czasy są oddzielone od deterministycznych danych. Wynik porównania
wszystkich czterech plików po powtórzeniu jest w
`verification/stage2-determinism.json`; pełny raport odczytu zapisanej
instancji w `stage2-verify.json`.
Zbiorcze kontrole akceptacji, bieżące hashe kodu i artefaktów oraz powiązania
raportów są w `verification/stage2-summary.json`.

## Testy i granica formalnej gwarancji

Końcowa kontrola: **64 testy Python**, kontrola przypiętego runtime i sześć
twierdzeń Lean 4.35.0 bez aksjomatów. Dotychczasowe 1 536 kombinacji grafu
i korzenia nadal przechodzą. Nie zmieniono `formal/Reachability.lean`,
kontraktu zapytania, generatora ani checkera grafowego.

Testy obejmują komentarze i inne literały, atrybuty i duplikaty, zagnieżdżenia,
CRLF, Unicode, niezamknięte komentarze i literały, brak średnika, błędny ogon
pliku, niekanoniczne i różniące się wielkością liter ścieżki, granice gitlinków
i dowiązań, brakujące i uszkodzone źródła, podmianę manifestu, grafu,
pochodzenia, korzenia i wyświetlanego wyniku oraz usuwanie/dodawanie wyników.
Brak niepowiązanego pliku również blokuje kompletność źródłową.

Osobna demonstracja na rzeczywistym korpusie usuwa krawędź
`file_info.mojom → time.mojom` **przed** utworzeniem nowego certyfikatu.
Zmodyfikowany graf daje 473 wyniki zamiast 477. Checker grafowy przyjmuje
certyfikat dla zmienionego grafu. Weryfikator
instancji odrzuca go po odtworzeniu krawędzi ze źródeł. Raport:
`verification/stage2-tampering.json`.

Końcowy przegląd objął również jawny JSON `null` w wymaganych plikach grafu
i wyświetlanego wyniku. Prywatny sentinel odróżnia pominięty opcjonalny
argument API od dostarczonego `null`; takie pliki są odrzucane. Osobne
regresje API i CLI sprawdzają ten przypadek.

Jeśli w przyszłym korpusie plik nie przejdzie całego parsera, wszystkie
zachowane importy jego nagłówka mają status `unresolved` i nie tworzą
krawędzi. Każdy plik otrzymuje końcowy status; źródłowa kompletność całego `S`
jest zablokowana. Można zaakceptować certyfikat dla jawnie częściowego grafu,
lecz wynik źródłowy pozostaje `unresolved`. Parser zgłasza pierwszą przeszkodę
składniową na plik; nie deklarujemy wyliczenia wszystkich błędów po niej.

Formalnie sprawdzono sześć twierdzeń o warunkach certyfikatu grafu,
w szczególności `RepoProof.exact_dependents`. Nie dowiedziono poprawności
i kompletności parsera/adaptera, ekstrakcji, obsługi Git, serializacji ani
zgodności checkera Python z Lean. Ponowne uruchomienie tego samego parsera
wykrywa podmianę danych, lecz nie jego wspólny błąd systematyczny.
Założenia opisano w [przeglądzie formalnej granicy](stage2-formal-boundary.md).
Zapytanie dotyczy deklaracji importów, nie wpływu zmiany na zachowanie
programu. LLM, Soufflé i Magic Sets nie zostały dodane.
