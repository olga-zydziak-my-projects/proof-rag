# Niezależne przeglądy etapu 9

Przeglądy wykonali odrębni agenci `/root/corpus_review` oraz
`/root/formal_review`. Własna kontrola implementatora nie jest liczona jako
niezależny audyt. Ich maszynowe raporty zachowują sprawdzone wejścia i hashe.

[Przegląd korpusu](../verification/stage9-corpus-review.json) potwierdza wszystkie
1251 źródeł, oryginalne obiekty commit/tree/blob, kompletne moduły, pełny graf,
zgodność wersji oraz kompletne przecięcia z poprawkami i nakładkami. Recenzent
obliczył własny graf z pełnych bajtów, używając skanera `source_bytes_v2.certificate`
oraz własnego rozstrzygania mountów i konstrukcji krawędzi.
Zweryfikował całe 18-plikowe domknięcie wspólne dla kontekstów aplikacji.
[Osobny raport](../verification/stage9-generated-boundary-review.json) uwierzytelnia
dwie granice generated oraz wszystkie cztery zdarzenia importów.

[Przegląd formalny i cache](../verification/stage9-formal-review.json) obejmuje
kod, zamknięte audytory, rzeczywiste testy i późniejszą kontrolę wykonania.
W trakcie implementacji wykryto i poprawiono następujące ryzyka:

- `-B` nadal odczytuje istniejące `.pyc`. CLI rozpoczyna właściwy proces z `-B`,
  `-S`, nowym pustym prefiksem bytecode i kontrolowanym PYTHONPATH.
- Same wersje zależności nie wskazują rzeczywiście importowanych bajtów.
  Wymuszono lokalny katalog, sprawdzenie `__file__` oraz pełne inwentarze runtime,
  zależności i narzędzi, w tym aktywny executable Lean i jego wersję/hash.
- Worker mógł pozostawić odpowiedź po timeout/limicie. Teraz zapisuje tylko
  kandydata; publikacja następuje po zakończeniu Job Object, pełnym odczycie
  kontrolnym i atomowej zmianie nazwy finalnej odpowiedzi.
- Nowe drzewa odwrotności, routing mastera i pełna lista odpowiedzi wymagają
  niezależnego odczytu danych. Dodano parser odwrotności, kontrolę rzeczywistego
  routingu i listy, obok pełnego audytu wszystkich shardów i grafu.
- Agregacja samych pól PASS mogła zaakceptować niepoprawne fixture.
  Agregacja ponawia kontrolę przygotowania, wszystkich 18 artefaktów zapytań,
  źródeł, certyfikatów, niezależnych list, raportów aksjomatów i profili zasobów.
- Runner pomiarów także musi otrzymać niezależną kotwicę przygotowania.
  Nie wylicza oczekiwanego hasha z nieufnego cache.
- Windows bootstrap musi czekać na proces właściwy. `spawnv(P_WAIT)` propaguje
  jego rzeczywisty kod wyjścia; test CLI sprawdza zakończenie i sprzątanie zadania.

Wstępne i pośrednie raporty nie są końcową akceptacją wykonania. Finalna bramka
wymaga przeglądu dokładnego dossier `verification/stage9-candidate.json` i jego
niezależnego hasha w raporcie recenzenta, a następnie ponownej kontroli przez
agregator. Aktualne rozstrzygnięcie zawiera `stage9-status.json`.
