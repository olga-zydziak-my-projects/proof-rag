# Granica formalnej gwarancji po etapie 2

Niezależny przegląd objął kontrakt, przypięty parser, ekstrakcję i warstwę
wiążącą instancję ze źródłami. Nie zmienia znaczenia sześciu twierdzeń Lean.

## Co sprawdza każda warstwa

1. **Korpus.** Oczekiwany commit i SHA-256 manifestu pochodzą z wejścia
   niezależnego od generatora. Metadane manifestu porównuje się z pełnym
   drzewem Git, a opublikowane bajty z OID bloba, rozmiarem i SHA-256.
   Brak lub uszkodzenie treści daje diagnostykę; nie znika żaden węzeł `S`.
2. **Ekstrakcja.** Przypięty parser Chromium sprawdza cały plik. Adapter
   zachowuje oryginalny literał, a indeksy znaków przelicza na offsety
   oryginalnych bajtów UTF-8. Przed użyciem pochodzenia sprawdzane są
   odpowiednie wycinki bajtów. Krawędzie powstają tylko z deklaracji
   `internal` w plikach, które przeszły pełną kontrolę składni.
3. **Związanie instancji.** Weryfikacja ponownie odczytuje i sprawdza korpus,
   odtwarza ekstrakcję i porównuje rzeczywistą zawartość artefaktu z danymi
   użytymi przez certyfikat. Sam skrót deklarowany przez generator nie
   wystarcza. Korzeń i wersja kontraktu również są oczekiwanym wejściem.
4. **Certyfikat grafowy.** Dotychczasowy checker kontroluje przynależność
   korzenia, rodziców z rzeczywistą krawędzią importu, ściśle malejące rangi
   naturalne oraz domknięcie po wszystkich krawędziach grafu. Nie wykonuje
   wyszukiwania generatora.
5. **Lean.** `RepoProof.exact_dependents` dowodzi dokładności zbioru przy
   spełnieniu tych matematycznych obowiązków, względem dostarczonej relacji
   importów. Audyt sześciu twierdzeń nie wykazuje zależności od aksjomatów.
   Konkretne wywołanie checkera Python nie jest uruchomieniem kernela Lean
   nad certyfikatem tej instancji.

## Ważne rozstrzygnięcia przeglądu

Upstream `ast.Import` normalizuje ścieżkę przez `os.path.normpath`, co na
Windows naruszałoby kontrakt eksperymentu. Adapter nie używa tego pola do
rozwiązywania importu: zachowuje oryginalny token `STRING_LITERAL` i odmawia
rozstrzygnięcia sekwencji ucieczki oraz niekanonicznych ścieżek. Gramatyka
upstream pozostaje niezmodyfikowana.

Osobny odczyt bezpośrednio przez przypięte `Parse` i lexer, z pominięciem
adaptera i generatora projektu, potwierdził 1 864 poprawnie parsujące się
pliki, 4 428 deklaracji, 4 424 deklaracje wewnętrzne, cztery granice zakresu
i 4 419 unikalnych krawędzi. Wszystkie rzeczywiste literały importów tego
commitu są kanoniczne i bez sekwencji ucieczki. Niezależne obliczenie punktu
stałego przez rozszerzanie zbioru dało 477 wyników dla `time.mojom`.
To kontrola zgodności adaptera i wyszukiwania, a nie drugi parser ani dowód
poprawności użytej gramatyki. Skrót grafu w formacie projektu wyniósł:

```text
0b47a4e7333b12e42dc7571b1ab2720530868fa299a1f7ca75e3d9a6a08a440a
```

`outside_scope` jest rozstrzygniętą granicą grafu indukowanego przez `S`.
Nie pozwala przechodzić ścieżką przez wyłączony plik i powracać do `S`.
`unresolved` w dowolnym pliku blokuje kompletność całego źródłowego zapytania,
nawet jeśli plik wydaje się niezwiązany z korzeniem. Poprawny certyfikat
częściowego grafu potwierdza tylko wynik względem tego grafu.

Usunięcie prawdziwej krawędzi **przed** utworzeniem certyfikatu pokazuje
granicę checkera grafowego: może on zaakceptować wynik dla zmienionego
grafu. Ponowne odtworzenie grafu ze źródeł pozwala warstwie instancji wykryć
taką podmianę względem zweryfikowanego korpusu.

## Co pozostaje założeniem

Ponowne użycie tego samego parsera wykrywa podmianę danych, lecz nie wykrywa
wspólnego, systematycznego błędu parsera lub adaptera. Nadal nie ma dowodu
poprawności i kompletności ekstrakcji, zgodności serializacji/checkera Python
z Lean ani formalnej poprawności obsługi Git i manifestu. Ufamy także
odczytowi plików, wykonaniu Python i założeniom kryptograficznym hashy.
Wynik opisuje deklaracje importów; nie dowodzi wpływu zmiany na zachowanie
programu ani użycia deklaracji w wybranej konfiguracji kompilacji.
