# Etap 5 — granica zaufania i blokada

**Nie uzyskano gwarancji źródło–odpowiedź.** Bieżący status to
`BLOCKED_PIN_CONFLICT`, a formalny most źródłowy pozostaje niedostępny
(`STAGE5_BLOCKED__SOURCE_PROOF`, niepodjęty po niespełnieniu przesłanki pinu).

Zamrożony [kontrakt](stage5-contract.md), SHA-256:
`5c323f4e9c2ae8d3bb498cd2b267e57ba8d4e76d09e2673c5d46979d3f44161d`.

## Tożsamość wejścia

Podany inwentarz wskazuje:

```text
commit 1ab171af2976555a2b12b9bca8b984c204962ba8
tree   9e5b002b0ce384a82f6cb836fd3abaebab8a7da6
```

Zaakceptowany commit projektu `e4984110743131d04ad984eaaa48d33d72867336`,
jego `corpus.lock.json`, kod korpusu/parsera, artefakty ekstrakcji i raporty
etapów 2–4 dotyczą innej pary:

```text
commit 27cec857a08a0ee0e1b41f5eb18c07467a0ce093
tree   25131300fa459906dedb84bf592a8537b7848771
```

Drugą parę potwierdził odczyt obiektów Git i kontrola pełnego wybranego
inwentarza oraz materializowanych bajtów. To **diagnostyczne potwierdzenie
bazy**, nie wybór zastępczego snapshotu dla etapu 5. Nie pobierano nowego
korpusu, nie przepisano locka ani wymagań, nie wygenerowano oczekiwanego
manifestu z fixture ataku. Kotwica jest odczytywana z zaakceptowanej historii
Git, a nie ze sprawdzanego pakietu producenta.

## Cztery oddzielne obowiązki

| Warstwa | Co faktycznie wykonano | Czego nie wolno z tego wnioskować |
| --- | --- | --- |
| Snapshot | Zewnętrzny audyt kompletnego drzewa i wybranych bajtów pod pinem bazy; wykrycie konfliktu z podanym inwentarzem | Że wskazany w etapie 5 snapshot został uzgodniony lub zaakceptowany |
| Semantyka źródeł | Zachowano istniejącą specyfikację i testowany parser Mojom | Nie powstał kernelowy dowód poprawności i kompletności ekstrakcji |
| Graf | Ponownie sprawdzono bazową instancję `ChromiumFast` i istniejące twierdzenia | Grafowa dokładność nie jest twierdzeniem o źródłach |
| Wydana odpowiedź | Kontrola wstępna odmawia wydania nowej odpowiedzi i zwraca kod niepowodzenia | Nie udowodniono dekodowania, renderera, listy wynikowej ani dostarczenia odpowiedzi etapu 5 |

## Pozostają dowiedzione własności etapu 4

`RepoProof.fastCheck_refines` i `RepoProof.fastCheck_exact` oraz
`ChromiumFast.accepted`, `ChromiumFast.erased_accepted`, `ChromiumFast.exact`
dotyczą dokładności względem dostarczonego grafu. Audyty nadal dopuszczają
`propext`, `Classical.choice`, `Quot.sound`. Nie są to twierdzenia bez
aksjomatów. W etapie 5 nie dodano nowych deklaracji Lean ani aksjomatów,
nie użyto `sorry`, `admit`, `native_decide` czy wyniku VM jako dowodu.

Nie wprowadzono przesłanki „parser jest poprawny” pod pozorem zamknięcia
mostu. Równości policzone w Pythonie, zgodność dwóch ekstraktorów, hashe,
liczby plików i span źródłowy nie zastępują G3. Nie zdefiniowano relacji
źródłowej jako eksportowanego grafu ani akceptacji checkera.

## Audyt bajtów i I/O

Istniejący `load_snapshot` odczytuje manifest, porównuje go z niezależnym
oczekiwanym SHA-256, enumeruje przypięte drzewo Git i kontroluje wszystkie
wybrane bloby. Nowa diagnostyka zachowuje źródła jako odczytane `bytes`
i ponownie oblicza SHA-256 dla każdego wpisu receipt. Receipt obejmuje
wszystkie wybrane ścieżki, tryby, OID i długości. Nie korzysta z checkoutu
źródeł ani normalizacji ścieżek repozytorium przez Windows.

Pliki bez importów pozostają w wyborze. Zakres to zwykłe śledzone `.mojom`
o trybach `100644`/`100755`; symlinki, gitlinki i DEPS nie są rozwijane.
W rzeczywistym wybranym inwentarzu nie ma ścieżek nie-ASCII. Tekst źródłowy
w istniejącej specyfikacji ma ścisłe UTF-8, lecz nowa diagnostyka nie jest
formalnym walidatorem języka. Nie eksportowano bajtów źródeł do Lean i nie
wykonano wymaganej równości tego eksportu z snapshotem; G2/G3 pozostają
zablokowane. Nie ma późniejszego konsumenta, który wydaje na tej podstawie
odpowiedź. Nie twierdzimy, że rozwiązano TOCTOU całej przyszłej ścieżki
źródło–odpowiedź.

Zaufane pozostają implementacja Git i jego walidacji obiektów,
odporność SHA-1/SHA-256 na kolizje, OS i odczyt/zapis plików, Python,
narzędzia Lean oraz kernel z wymienionymi standardowymi aksjomatami.
Receipt i stdout diagnostyki to audytowana granica I/O, nie twierdzenia Lean.

## Bezpieczna odmowa

`stage5_preflight.py` nie ma gałęzi `STAGE5_PASS`. Nawet samo uzgodnienie
pinów nie zamknęłoby brakującego dowodu G3 ani bram G4–G7. Zwracany kod 3
oznacza blokadę; kod 2 — błąd wejścia lub kontroli. Każdy nowy katalog
diagnostyczny i jego logi są tworzone wyłącznie bez nadpisywania istniejących
plików. Nie powstaje payload ani ludzka odpowiedź oznaczona jako nowy sukces.
Stare CLI zachowują wcześniejsze działanie i zakres gwarancji; ich wyniki
nie stają się przez to odpowiedziami `STAGE5_PASS`.

Wyniki regresji bazy i scenariusz 473 wyników są opisane wyłącznie jako
regresje wcześniejszych warstw. Nie oznaczają wykonania wszystkich ataków
A–L na nieistniejącej jeszcze kompletnej ścieżce etapu 5. Konflikt wykrywa
audyt proweniencji, **nie kernel**.
