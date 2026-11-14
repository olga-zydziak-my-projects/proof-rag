# Etap 6 — wiele zapytań na sprawdzonym korpusie

Zatwierdzony zakres: użytkownik wybiera dowolny plik z dotychczasowego korpusu
Mojom; każde zapytanie dostaje własny dowód i pełną odpowiedź. Bez zmiany
snapshotu, semantyki importów, zakresu plików ani włączania LLM.

Baza: ukończony etap 5 v2, commit projektu
`7cbad10af87dc97bae4b23603921441aa899f7b0`. Chromium pozostaje przypięte do
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`, tree
`25131300fa459906dedb84bf592a8537b7848771`. Formalna relacja pozostaje
`SourceBytes byte import projection v2`, z granicą IO opisaną w etapie 5.

## Wymagania

1. Zachować wcześniejsze źródła, dowody, raporty i wyniki. Nowe katalogi
   wyników są tworzone wyłącznie bez nadpisywania istniejących. Nie publikować.
2. Jawny argument korzenia akceptuje dowolną dokładną ścieżkę w wybranym
   uniwersum. Nieznana ścieżka jest odrzucana, bez normalizacji lub zgadywania.
   Semantyka nadal obejmuje korzeń i wszystkich jego pośrednich importerów.
3. Przygotować wielokrotnie używaną warstwę źródło–graf z zaakceptowanego
   przebiegu etapu 5. Pochodzenie i tożsamości dowodów muszą mieć niezależną
   kotwicę w zapisanym commicie, nie w samoopisującym się cache.
4. Przy każdym użyciu zweryfikować snapshot, specyfikację, mapowanie, graf
   oraz wszystkie importowane zależności. Wykrywać brak, dodatkowy moduł,
   zmianę i podmianę danych. Użycie wcześniejszego `.olean` jest jawnie
   ponownym użyciem sprawdzonego dowodu, nie świeżą kompilacją źródeł.
5. Dla każdego nowego korzenia wygenerować certyfikat i świeżo sprawdzić
   przez kernel jego akceptację, pełne dekodowanie odpowiedzi i kompozycję
   ze źródłami. Nie używać poprzedniego dowodu odpowiedzi dla nowego korzenia.
   Brak `sorry`, `admit`, `native_decide`, nowych aksjomatów lub obejść VM.
   Dopuszczone aksjomaty pozostają `propext`, `Classical.choice`, `Quot.sound`.
6. Niezależny audyt porównuje rzeczywiste dane nowego źródła Lean, korzeń,
   świadków, wskazania krawędzi i całą listę odpowiedzi. Wynik JSON i tekst
   mają pełne metadane i listę oraz kontrolę po zapisaniu. Awaria nie wydaje
   nowej odpowiedzi oznaczonej jako zweryfikowana.
7. Sprawdzić co najmniej dziesięć różnych rzeczywistych korzeni: wcześniejszy
   wynik 477, plik izolowany i różne wielkości wyników. Niezależny punkt stały
   ustala pełne oczekiwane listy. Dodatkowe testy obejmują cykle i błędne korzenie,
   podmiany między zapytaniami, zmianę cache oraz metadanych odpowiedzi.
8. Zachować wszystkie wcześniejsze regresje, wykonać nowe testy i niezależny
   przegląd. Dla identycznego zapytania powtórzyć generowanie i porównać bajty.
9. Zmierzyć osobno przygotowanie przez ponowne użycie dowodu, kontrolę
   snapshotu, kontrolę cache, generowanie, świeży proces dowodowy zapytania,
   zapis odpowiedzi i całe zapytanie. Nie utożsamiać tego z historycznym
   świeżym przebiegiem 27 minut, który wykonywał inne obowiązki i regresje.

## Kryterium zakończenia

`STAGE6_PASS` wymaga wszystkich punktów powyżej, poprawnych pełnych wyników
dla wybranych zapytań, wykazanych odrzuceń podmian i końcowego raportu z
poleceniami odtworzenia. Liczby 1864/4419 opisują zachowany snapshot;
liczba 477 jest regresją jednego korzenia, nigdy warunkiem innych odpowiedzi.
Gwarancja pozostaje względna wobec jawnej specyfikacji bajtowej i założeń IO.
