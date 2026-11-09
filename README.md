# Repo Proof Lab — etap 2

Prototyp wyszukiwania zależności w grafie, certyfikatu wyniku i niezależnego
checkera. Zamrożony korpus Chromium ma deterministyczny manifest,
[kontrakt zapytania o importy Mojom](docs/query-contract.md), pełną ekstrakcję
składniową i pierwsze zapytanie o `mojo/public/mojom/base/time.mojom`.

## Stan i granica gwarancji

- Generator zwraca korzeń oraz wszystkie węzły mające ścieżkę importów do niego.
- Osobny checker nie wywołuje wyszukiwania generatora. Kontroluje rodziców,
  malejące rangi oraz domknięcie po wszystkich krawędziach grafu.
- Sześć twierdzeń Lean dowodzi dokładności wyniku **względem dostarczonego grafu**.
  Audyt nie wykazuje zależności od aksjomatów; znaczenie twierdzeń zachowano.
- Korpus zawiera kompletne metadane drzewa wskazanego commitu oraz oryginalne
  bajty 1 864 zwykłych plików `.mojom` i trzech plików referencyjnych parsera.
  To nie jest pełna lokalna kopia Chromium. DEPS, gitlinki i dowiązania nie są
  rozwijane. Nie uruchamiano budowania ani hooków Chromium.
- Przypięty, niezmodyfikowany parser Chromium i PLY 3.11 sprawdzają całe pliki.
  Ekstrakcja zachowuje oryginalne literały, lokalizacje bajtowe UTF-8,
  atrybuty, duplikaty i jawne statusy wszystkich plików oraz deklaracji.
- Graf ma 1 864 węzły i 4 419 krawędzi. Dla `time.mojom` zaakceptowano wynik
  477 plików, włącznie z korzeniem. Cztery deklaracje poza zakresem nie
  tworzą krawędzi; nie ma przypadków `unresolved` w przypiętym korpusie.
- Weryfikacja instancji ponownie sprawdza źródła, odtwarza graf i porównuje
  także pochodzenie oraz wyświetlany wynik. Oczekiwany commit i manifest
  pochodzą z niezależnego locka, a korzeń z jawnego argumentu wywołania.
- Python, Git, parser manifestu i ekstrakcja Mojom nie mają dowodu zgodności
  z Lean. Ponowne uruchomienie tego samego parsera wykrywa podmianę danych,
  lecz nie jest niezależnym dowodem poprawności parsera. Przyjęcie certyfikatu
  przez Python nie uruchamia Lean dla tej instancji.

Szczegóły: [wyniki etapu 2](docs/stage2-results.md),
[granica formalnej gwarancji](docs/stage2-formal-boundary.md),
[wyniki etapu 1](docs/stage1-results.md) i [formalny rdzeń](formal/README.md).

## Testy i demonstracja

Python 3.10+, Git (sprawdzono 2.55.0.windows.2), Lean 4.35.0.
Nie trzeba instalować dodatkowych pakietów. Mały runtime parsera z licencjami
jest w [vendor](vendor/README.md). Uruchamiaj z kopii repozytorium;
dystrybucja wheel nie jest częścią tego etapu. PowerShell w katalogu projektu:

```powershell
$py = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$lean = 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe'
& $py scripts/check.py --lean $lean
```

Raport `verification/latest.json` zawiera wyniki testów, wersję Lean, audyt
sześciu twierdzeń, demo manipulacji i skróty kodu. Testy obejmują wszystkie
512 grafów skierowanych o trzech węzłach, po trzy korzenie: 1 536 przypadków.

## Zapytanie Mojom i weryfikacja od źródeł

Po ustawieniu `$py` jak powyżej, z istniejącym `local/corpus.json` i zaufanym
`corpus.lock.json` z tego repozytorium:

```powershell
$root = 'mojo/public/mojom/base/time.mojom'
& $py scripts/mojom_experiment.py run --root $root `
  --artifact-dir local/stage2 --report verification/stage2-run.json
& $py scripts/mojom_experiment.py verify --root $root `
  --artifact-dir local/stage2 --report verification/stage2-verify.json
& $py scripts/mojom_experiment.py tamper --root $root `
  --artifact-dir local/stage2 --report verification/stage2-tampering.json

# Powtórzenie offline i porównanie rzeczywistych bajtów wszystkich artefaktów:
& $py scripts/mojom_experiment.py run --root $root `
  --artifact-dir local/stage2-repeat --report verification/stage2-repeat.json
& $py scripts/mojom_experiment.py compare --first local/stage2 `
  --second local/stage2-repeat --report verification/stage2-determinism.json
```

W `local/stage2` zapisują się deterministyczne `extraction.json`, `graph.json`,
`certificate.json` i `query.json`. Plik `query.json` zawiera wszystkie wyniki
i przykładowe ścieżki. `extraction.json` zawiera każdy plik `S`, każdą znalezioną
deklarację, jej pochodzenie, półotwarte zakresy `[byte_start, byte_end)` oraz
wiersz i kolumnę **bajtową**, liczone od 1. Czasy i daty trafiają wyłącznie
do oddzielnych raportów `verification/`.

`verify` nie uruchamia generatora ani jego wyszukiwania. Odtwarza graf z
ponownie zweryfikowanego korpusu i porównuje całą zawartość grafu, pochodzenie,
diagnostykę i wynik. Nie wystarcza skrót dostarczony przez generator. Jego
oczekiwania pochodzą z `--config`, `--lock` i `--root`, nigdy z certyfikatu.
Zachowuj te wejścia niezależnie od pakietu otrzymanego do sprawdzenia.

Kod zakończenia: 0 oznacza zakończoną kontrolę / odpowiedź kompletną w
zadeklarowanym zakresie; 3 oznacza uczciwe `unresolved`; 2 oznacza odrzucone
wejście, podmianę albo niepoprawny certyfikat. Przy `unresolved` zachowywany
jest wynik dla częściowego grafu z jawnym brakiem kompletności źródłowej.
Wystarczy problem w dowolnym pliku `S`, także poza składową korzenia.
Parser zgłasza pierwszą przeszkodę składniową w danym pliku; raport zachowuje
wszystkie pliki z problemami oraz wszystkie wykryte diagnostyki rozstrzygnięć.

Demo pokazuje usunięcie wyniku, dodanie fałszywego wyniku oraz usunięcie
rzeczywistej krawędzi przed wygenerowaniem nowego certyfikatu. Ten ostatni
certyfikat przechodzi checker dla zmienionego grafu, a warstwa źródłowa
odrzuca podmieniony graf po jego ponownym odtworzeniu.

## Mały przykład grafowy

```powershell
$env:PYTHONPATH = 'src'
& $py -m repo_proof demo --graph examples/graph.json --root core
& $py -m repo_proof query --graph examples/graph.json --root core --out local/certificate.json
& $py -m repo_proof verify --graph examples/graph.json --root core --certificate local/certificate.json
```

Oczekiwany wynik: `app`, `controller`, `core`, `service`. `isolated`, `cycle_a`
i `cycle_b` pozostają poza wynikiem. `verify` zwraca kod 0 przy akceptacji i 2
przy odrzuceniu. Graf ma dokładnie pola `nodes` i `edges`; `[A, B]` oznacza
import z A do B. Duplikaty węzłów i krawędzi są odrzucane.

## Przygotowanie i ponowne sprawdzenie korpusu

Korpus jest poza repozytorium narzędzia. Pierwsze polecenie zapisuje jego
lokalizację w ignorowanym pliku `local/corpus.json`:

```powershell
& $py scripts/prepare_corpus.py prepare `
  --data-dir 'C:\Users\User\Documents\Codex\2026-11-08\nie\outputs\chromium-corpus-27cec857a08a' `
  --report verification/corpus-first.json

# Ponowne użycie konfiguracji, metadanych i sprawdzonych blobów:
& $py scripts/prepare_corpus.py prepare --report verification/corpus-repeat.json

# Wyłącznie lokalny odczyt; automatyczne pobieranie Git jest wyłączone:
& $py scripts/prepare_corpus.py verify --report verification/corpus-offline.json
```

Na innym komputerze wybierz własny katalog poza repozytorium. Commit jest
zapisany na stałe w kodzie i `corpus.lock.json`:
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`. Nie ma zastępowania go gałęzią
`main`. Błąd pobrania daje kod 2 i jawny status `unresolved`.

Przygotowanie używa bare Git: `fetch --depth=1 --filter=blob:none`, następnie
zbiorczego pobrania wyłącznie brakujących wybranych blobów. Bez checkoutu,
zmiany końców linii, rekursji submodułów i zależności DEPS. Ponowne uruchomienie
sprawdza bajty, zamiast ufać samej obecności plików. Uszkodzone kopie blobów
może odbudować z lokalnego Git, a brakujące obiekty Git pobiera ponownie.

W katalogu korpusu powstają:

- `manifest.json`: kanoniczny JSON, bez czasu uruchomienia i ścieżki komputera;
  każdy wpis zawiera ścieżkę, tryb, typ Git, kategorię, OID i status dostępności.
  Treść opublikowana w korpusie ma dodatkowo długość i SHA-256.
- `tree.entries.z`: pełne rekurencyjne wyjście `git ls-tree -r -t -z`.
  Obejmuje katalogi; OID katalogu głównego zapisano osobno w manifeście.
- `blobs/<pierwsze 2 znaki OID>/<pozostałe znaki>`: oryginalne bajty;
  ścieżki Git pozostają w manifeście, bez odwzorowania ich na ścieżki Windows.
- `git/`: częściowa baza obiektów; jej obecność nie oznacza pełnej kopii źródeł.
- `state.json`: stan operacji, oddzielony od deterministycznego manifestu.

Statusy `not_selected`, `link_not_materialized`, `external_not_fetched` i
`metadata_only` opisują zadeklarowany zakres publikacji danych. Nie twierdzą,
że dany OID na pewno nie znajduje się przypadkiem w wewnętrznym cache Git.

Obsługiwany jest jeden proces zapisujący dany korpus. Zapisy są atomowe przez
`.part`; przerwanie nie publikuje nowego kompletnego manifestu. Po przerwaniu
uruchom ponownie `prepare`; gotowe, poprawne bloby zostaną wykorzystane.
Niekompletnego transportowego packa Git nie uznaje się za zweryfikowane dane.
Po twardym zabiciu procesu może zostać porzucony plik `git/objects/pack/tmp_pack_*`;
nie jest używany przez weryfikację, a jego rozmiar wlicza się do pomiaru miejsca.
Zapisany wcześniej manifest dla tego samego commitu zachowuje ważność tylko
wtedy, gdy pełne `verify` nadal przechodzi; samo `state.json` nie jest dowodem.

Testowe `--stop-after-blobs N` przerywa po N nowych zapisach; nie zmienia
wyboru źródeł ani formatu manifestu. Testy sprawdzają także awarię transportu,
wznowienie, porzucony `.part`, uszkodzone skróty i pominięte wpisy.

## Następny krok

Rozwinąć dowód związku oryginalnych bajtów, parsowania, relacji importów i
implementacji checkera z twierdzeniem Lean. Powtarzalne pomiary z etapu 2
stanowią punkt odniesienia dla późniejszych eksperymentów; Soufflé, Magic Sets
i LLM nie zostały dodane.
