# Etap 5 — BLOCKED_PIN_CONFLICT

**Nie uzyskano `STAGE5_PASS`; etap 5 nie jest ukończony.** Ujawniono konflikt
istotnego wejścia, dla którego polecenie wymaga `BLOCKED_PIN_CONFLICT`.
Nie podmieniono snapshotu, locka, wymagań ani kryteriów sukcesu.

Checkpoint etapu 4 już istniał i został zweryfikowany:
`e4984110743131d04ad984eaaa48d33d72867336`. Przodek `3184813` i wszystkie
96 plików śledzonych na początku są zachowane. Początkowy katalog roboczy
był czysty. Nie wykonano push ani zmian globalnej konfiguracji Git.

## Zamrożony kontrakt i konflikt

Przed implementacją zapisano [stage5-contract.md](stage5-contract.md):
całe polecenie, wszystkie bramy G1–G8 i odzyskany kontrakt zapytania.
SHA-256, także zapisany w kodzie i raportach:

```text
5c323f4e9c2ae8d3bb498cd2b267e57ba8d4e76d09e2673c5d46979d3f44161d
```

| Tożsamość | Commit Chromium | Root tree |
| --- | --- | --- |
| Inwentarz podany w poleceniu | `1ab171af2976555a2b12b9bca8b984c204962ba8` | `9e5b002b0ce384a82f6cb836fd3abaebab8a7da6` |
| Zaakceptowana baza i rzeczywista kontrola Git/bajtów | `27cec857a08a0ee0e1b41f5eb18c07467a0ce093` | `25131300fa459906dedb84bf592a8537b7848771` |

Kotwicę odczytano z `git show e498411...:corpus.lock.json`, nie z pakietu
producenta. Potwierdzają ją bieżący lock, kod korpusu/parsera, ekstrakcja
i raporty etapów 2–4. Audyt rzeczywistych obiektów Git oraz wszystkich
wybranych bajtów potwierdził drugą parę. To diagnostyka bazy, **nie** milczący
wybór zastępczego pinu etapu 5. Nie pobierano innego korpusu.

## Zakres i dotychczasowa gwarancja

Dla potwierdzonej bazy `27cec857...` wybór to wszystkie zwykłe śledzone
`.mojom` głównego repozytorium, tryby `100644`/`100755`, również pliki bez
importów. Symlinki, gitlinki i DEPS nie są rozwijane. To nie całe Chromium.
Ścieżki są tożsamościami Git bez normalizacji Windows. W wybranym inwentarzu
wszystkie są ASCII; dotychczasowa specyfikacja źródeł używa ścisłego UTF-8.
Pełne reguły komentarzy, literałów, atrybutów, rozwiązywania, duplikatów
i unresolved pozostają w zamrożonym kontrakcie, bez nowego formalnego dowodu.

Regresja: **1864 węzły, 4419 krawędzi, 213 izolowanych węzłów, 477 wyników**
dla `mojo/public/mojom/base/time.mojom`, włącznie z korzeniem. Krawędź biegnie
importer → importowany. Są to obserwacje bazy, nie liczebności sprzecznego
commita `1ab171af...` i nie definicja zakresu.

Źródłowa diagnostyka objęła 1864 ścieżki i **6 946 142 bajty**. Niezależny
oczekiwany SHA-256 manifestu to
`1e6fe63490e2007c56b088194f0c2acb61abc834aeefb4edb2bbfe6399bc2e4a`.
Pełny receipt zawiera ścieżki, tryby, OID, długości i SHA-256 obliczone
ponownie z uchwyconych `bytes`. Oba przebiegi dały identyczne pełne
**468 948 bajtów receipt**. To nie regeneracja kanonicznej odpowiedzi etapu 5.

Ponownie, świeżo sprawdzono tylko bazową instancję grafową:
`ChromiumFast.accepted`, `ChromiumFast.erased_accepted`, `ChromiumFast.exact`.
Zachowane są `RepoProof.fastCheck_refines` i `RepoProof.fastCheck_exact`.
Audyty używają wyłącznie dopuszczonych `propext`, `Classical.choice`,
`Quot.sound`; nie są wolne od aksjomatów. **Nie dodano nowych deklaracji Lean
etapu 5.** Nie powstał sound/complete most źródło–graf, eksport bajtów źródeł
do Lean, dowód dekodowania wyniku ani kompozycja źródło–odpowiedź.

## Wykonana implementacja częściowa

`repo_proof.stage5_preflight` i publiczny `scripts/stage5_preflight.py`
sprawdzają zamrożony kontrakt, zachowanie bazy, kotwicę z historii Git,
konfigurację producenta i diagnostycznie bajty bazy. Kod nie ma gałęzi
`STAGE5_PASS`, opcji zastępczego pinu ani obejścia G3. Nawet same zgodne
piny nie wystarczyłyby do przyjęcia brakującego dowodu źródłowego.

Kod 3 oznacza BLOCKED, kod 2 błąd wejścia/kontroli. Powstaje diagnostyka
`success=false`, `answer_released=false`, bez nowej koperty lub odpowiedzi
oznaczonej jako sukces. Nie wdrożono jeszcze renderera, walidatora faktycznie
wydawanej listy ani źródłowej instancji Lean. Stan G3 pozostaje
`STAGE5_BLOCKED__SOURCE_PROOF` z powodu nieuzgodnionej przesłanki pinu i braku
nowego dowodu. Nie uznano audytów Python za zamknięcie tej bramy.

## Mechaniczny wynik bram

| Brama | Status | Powód |
| --- | --- | --- |
| G1 | PASS | Historia, 96 bazowych plików i istniejące regresje zachowane |
| G2 | BLOCKED | `BLOCKED_PIN_CONFLICT`; audyt bajtów dotyczy tylko innego, zaakceptowanego pinu bazy |
| G3 | BLOCKED | Nie ma kernelowego mostu źródłowego dla pełnej instancji |
| G4 | BLOCKED | Grafowa dokładność zachowana, ale brak kompozycji ze źródłami i dekodowaniem |
| G5 | BLOCKED | Nie wydano ani nie udowodniono nowej odpowiedzi |
| G6 | BLOCKED | Regresje przeszły; pełne ataki A–L nowej ścieżki nie zostały wykonane |
| G7 | BLOCKED | Odtworzono blokadę, nie pomyślną pełną ścieżkę i kanoniczną odpowiedź |
| G8 | PASS | Brak nowego skrótu zaufania i nieuprawnionej deklaracji sukcesu |

## Testy i ataki

Końcowo przeszło **78 testów**: wcześniejsze 71, pięć nowych testów kontroli
wstępnej i dwa testy wyłączności logów. Zachowano 1547 porównań Python–Lean,
cykle, izolowane węzły, korzeń, rangi z przerwami i wcześniejsze pozytywne
fixture legalnego formatowania. Porównania programów pozostają testami.

Nowy test publicznego CLI odrzuca producenta z manifestem, którego hash
i liczebność zgadzają się z jego własnym plikiem, ale pin nie zgadza się
z niezależną kotwicą. Oczekiwanego manifestu nie generuje się z fixture.
To test granicy metadanych, nie pełnego alternatywnego snapshotu Git.
Sprawdzono także błędny JSON, zamrożenie wymagań, odmowę nadpisania runu
i logów oraz rozdzielenie dwóch katalogów wynikowych.

Zachowana demonstracja rzeczywiście usuwa krawędź przed regeneracją
certyfikatu: checker Python przyjmuje zmieniony graf z **473 wynikami**,
a odtworzenie grafu ze źródeł odrzuca podmianę. To wynik wcześniejszej warstwy
źródłowej, nie odrzucenie źródeł przez kernel. Nowych ataków na kanoniczną
i ludzką odpowiedź nie wykonano, bo nie powstała taka odpowiedź. Nie jest
to zaliczenie testu jej wiązania. Wszystkie wymagane A–L mają w
[stage5-tampering.json](../verification/stage5-tampering.json) jawny stan
`NOT_RUN_BLOCKED`, z oddzielonymi pomocniczymi obserwacjami C i E.

## Pomiary — wyłącznie diagnostyka

| Zakres końcowego przebiegu | Czas |
| --- | ---: |
| Audyt rzeczywistych bajtów pod pinem bazy | 5,059925 s |
| Cały proces zablokowanej kontroli wstępnej | 5,233713 s |
| Suma procesów kompilacji modułów ogólnych | 3,981262 s |
| Świeży proces bazowego dowodu grafowego | 10,076402 s |
| Cały proces 78 testów | 124,468 s |
| Zablokowany driver wraz z regresjami i bazowym tamper demo | 167,175037 s |
| Nowa walidacja semantyki / generacja / instancja źródłowa / walidacja odpowiedzi / pomyślna cała ścieżka | **nie wykonano** |

Nieobecne pomiary mają w JSON `null`, nie zero. Nie jest to pomiar pomyślnego
pipeline'u etapu 5. Nie twierdzimy, że etap 5 cokolwiek przyspieszył.
Historyczne **749,257 → 1,550 s** pozostaje sumą kontroli liści i wstawienia
lematów, a **9,992150 s** pojedynczą obserwacją świeżego procesu etapu 4
po kompilacji modułów ogólnych. Pełny czas etapu 3 i jego szczyt pamięci
są nieznane; artefakty etapu 4 wzrosły. Nie uruchamiano drogiego dowodu 3.

Przed diagnostycznym dowodem zbudowano `Reachability`, `Checker`,
`ProofTiming`, `FastChecker`; ich `.olean` oraz biblioteki Std/Lean SDK
4.35.0 były prekompilowanymi importami procesu instancji. Samą bazową
instancję sprawdzono ze źródła do nowego pliku w runie, bez importu jej
gotowego `.olean`. Nie jest to nowa instancja źródłowa etapu 5.

Windows odnotował dla kontroli snapshotu szczyt `PeakWorkingSetSize`
**1 363 828 736 B** i `PeakPagefileUsage` **1 358 282 752 B**; dla bazowego
dowodu grafowego **1 510 305 792 B** i **2 867 310 592 B**. Working set obejmuje
rezydentne strony procesu, także współdzielone; drugi licznik to commit,
nie bajty I/O. Odczytywano natywne liczniki szczytu między żądanymi
oczekiwaniami 20 ms i po zakończeniu. Końcowe odczyty się powiodły, więc
obejmują całe życie danego procesu, bez jego dzieci. Scheduler może wydłużyć
interwał. Zegar obejmuje otwarcie logów, Popen i wait; dekodowanie logów jest
poza nim. Rozmiary źródeł i artefaktów oraz hashe zapisano w evidence.

Pierwszą diagnostykę z 76 testami zachowano w `stage5-checks.json`; jej
oryginalny driver w `local/stage5/run-01/executor-original.py` ma zgodny hash.
Następnie poprawiono lokalizację i wyłączność logów, dodano dwa testy i
wykonano końcowy `run-02`. Nie jest to powtarzany benchmark. Równość pełnych
bajtów obu receipt dotyczy tylko danych diagnostycznych, nie odpowiedzi.

## Odtworzenie i pliki

Z katalogu projektu, z `$py` i `$lean` jak w instrukcjach etapu 4:

```powershell
& $py scripts/check_stage5.py --lean $lean `
  --run-dir local/stage5/recheck-03 `
  --report local/stage5/recheck-03-report.json
# Oczekiwany wynik: BLOCKED_PIN_CONFLICT, niezerowy kod 3.
```

To jedno polecenie odtwarza **blokadę i diagnostykę**, nie pomyślną ścieżkę
wymaganą przez G7. Samą odmowę odtwarza
`scripts/stage5_preflight.py --run-dir <nowy katalog>`. Istniejące katalogi,
raporty i logi nie są nadpisywane. Pomiar wymaga Windows; nie dodano pakietów.

- [Końcowy raw report](../verification/stage5-final-checks.json).
- [Evidence, hashe i równość receipt](../verification/stage5-evidence.json).
- [Pełny receipt bazy](../verification/stage5-source-receipt.json).
- [Inwentarz stanu początkowego](../verification/stage5-baseline.json).
- [Granica zaufania](stage5-trust-boundary.md).

Korpus jest zewnętrzny, pod ścieżką
`C:/Users/User/Documents/Codex/2026-11-08/nie/outputs/chromium-corpus-27cec857a08a`.
Potrzebne są jego materializowane bloby, manifest, listing drzewa i obiekty
Git, konfiguracja `local/corpus.json` oraz `local/stage2`. To nie jest
samowystarczalny bundle ani pełny checkout Chromium. Nie utworzono procedury
podstawiającej drugi pin pod dotychczasowy eksperyment.

Najpierw potrzebne jest autorytatywne rozstrzygnięcie konfliktu pinu.
**Samo uzgodnienie nie zamknie G3–G7**: nadal trzeba wykonać niezależną
specyfikację bajtów Mojom i kernelowy sound/complete most dla wszystkich
plików, pełne mapowanie/dekodowanie, kompozycję, rzeczywistą kopertę i
renderer, ataki oraz pomyślny pełny przebieg. Nie dodano aksjomatu poprawności
parsera ani integracji LLM, Soufflé lub Magic Sets. Pozostałe założenia
Git/hash/OS/I/O/Python/Lean są jawnie oddzielone od dowodów.
