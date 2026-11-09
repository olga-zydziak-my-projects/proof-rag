# Repo Proof Lab — etap 1

Prototyp wyszukiwania zależności w grafie, certyfikatu wyniku i niezależnego
checkera. Etap 1 dodaje zamrożony, częściowy korpus Chromium, deterministyczny
manifest oraz [kontrakt zapytania o importy Mojom](docs/query-contract.md).

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
- Python, Git, parser manifestu i przyszła ekstrakcja Mojom nie mają dowodu
  zgodności z Lean. Nie zaimplementowano jeszcze ekstraktora grafu Chromium.
  Przyjęcie certyfikatu przez Python nie uruchamia Lean dla tej instancji.

Szczegóły pomiarów i kontroli: [wyniki etapu 1](docs/stage1-results.md).
Formalny rdzeń: [formal/README.md](formal/README.md).

## Testy i demonstracja

Python 3.10+, Git (sprawdzono 2.55.0.windows.2), Lean 4.35.0.
Kod Python nie wymaga dodatkowych bibliotek. PowerShell w katalogu projektu:

```powershell
$py = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$lean = 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe'
& $py scripts/check.py --lean $lean
```

Raport `verification/latest.json` zawiera wyniki testów, wersję Lean, audyt
sześciu twierdzeń, demo manipulacji i skróty kodu. Testy obejmują wszystkie
512 grafów skierowanych o trzech węzłach, po trzy korzenie: 1 536 przypadków.

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

Zaimplementować ekstraktor spełniający kontrakt, z diagnostyką każdej deklaracji
i statusem `unresolved` dla nieobsługiwanych przypadków. Następnie osobno
zmierzyć ekstrakcję, wyszukiwanie, certyfikowanie i sprawdzanie na rzeczywistym
grafie. Soufflé i Magic Sets pozostają kandydatami do późniejszego porównania.
