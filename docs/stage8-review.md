# Niezależny przegląd etapu 8

Werdykt recenzenta `/root/stage8_review`: **PASS dla dostarczenia ze statusem
STAGE8_CORPUS_BLOCKED**. Nie jest to STAGE8_PASS ani zatwierdzenie nowego
formalnego mostu źródłowego.

Recenzent nie implementował zmian i nie zmieniał plików. Niezależnie uruchomił
10 testów offline, a po final-02 sprawdził:

- Aktualne tożsamości kodu, manifestu i konfiguracji, regresję 151 testów bez
  pominięć oraz zachowany test różnicowy 1547 przypadków.
- Pełne 27 list Parquet i całe certyfikaty dziewięciu wariantów, także 1M,
  z niezależnym DFS. Nie regenerował przy tym grafów producentem.
- Wszystkie trzy dowody Lean64: rzeczywiste `.lean/.olean`, bajty zależności,
  zamknięty audyt eksportu i rygorystyczne raporty aksjomatów.
- Sześć plików Soufflé answer.csv: każdy zawiera 385 unikalnych i dokładnie
  poprawnych par `(root,node)`; hashe kodu i binarium pozostały zgodne.
- Wszystkie 153 pełne źródła kandydatów i kompletność względem inwentarzy:
  631537 B, 125 importów, wszystkie wewnętrzne. Potwierdził przeszkodę korpusu.
- Wszystkie dziewięć wierszy czasu/RSS/private dokumentacji względem raportu.

W przeglądzie wstępnym zgłosił i sprawdził poprawki: wyścig usunięcia tempfile
w supervisorze i cleanup potomków; oddzielne generowanie certyfikatu;
wspólny limit dysku Lean; modularne przypisanie repozytoriów; wersję i hash Lean.
Nie znaleziono pozostałych blokujących usterek w dostarczonym zakresie.

Pozostałe braki są jawne: nie wybrano prawdziwej połączonej trójki; nie wykonano
wymaganych zapytań rzeczywistego pilota; nowy ogólny most Lean źródła→resolver→graf
jest NOT_IMPLEMENTED. Mapowania manifestu są ręcznie zaakceptowaną specyfikacją.
Milion węzłów oznacza syntetyczny GRAPH_PASS z Pythonem, a nie milion plików
sprawdzonych źródłowo przez Lean. Kolejny krok wymaga rzeczywistych połączeń,
spójnych pinów i formalizacji nowego mostu.

W końcowej kontroli recenzent nie wykonywał sieci ani wywołań API.
Zapis hashy jest w `verification/stage8-review.json`.

Nowe lokalne pliki `.gitattributes` zachowują dokładne bajty wyłącznie raportów
etapu 8 i przykładu Datalog. Dzięki temu hashe manifestu nie zmieniają się przy
konwersji CRLF/LF przez Git. Historyczny główny `.gitattributes` i raporty
wcześniejszych etapów pozostają bez zmian.
