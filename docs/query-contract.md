# Pierwsze zapytanie: zależności przez deklaracje importów Mojom

Wersja kontraktu: `mojom-import-dependents-v1`. Repozytorium źródłowe to
`https://github.com/chromium/chromium`, commit
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`. Kontrakt określa przyszłą
ekstrakcję i znaczenie wyniku; etap 1 nie zawiera formalnie zweryfikowanego
parsera ani dowodu zgodności ekstraktora z kodem Chromium.

## Zakres i wynik

Niech `S` oznacza wszystkie zwykłe, śledzone pliki o ścieżkach kończących się
dokładnie na `.mojom` w drzewie wskazanego commitu głównego repozytorium.
Tryby `100644` i `100755` oznaczają zwykłe pliki. Dowiązania `120000`, gitlinki
`160000` oraz zawartość zewnętrznych repozytoriów DEPS nie należą do `S`.
Ścieżki są identyfikatorami z drzewa Git, z ukośnikiem `/` i rozróżnieniem
wielkości liter. Zawartość pliku oznacza oryginalne bajty obiektu Git.

Dla `r ∈ S` wynik to zbiór:

```text
R(r) = {v ∈ S | istnieje ścieżka importów v → … → r,
                 której wszystkie wierzchołki należą do S}
```

Ścieżka długości zero jest dozwolona: wynik zawsze zawiera wskazany plik `r`.
To celowy wybór zgodny z istniejącym certyfikatem
`reverse_reachability_including_root`. Cykle i pętle są dozwolone. Duplikaty
deklaracji dają jedną krawędź grafu, z zachowaniem wszystkich lokalizacji
deklaracji jako danych pochodzenia. Kolejność listy wynikowej nie ma znaczenia
matematycznego; zapis wyników powinien sortować ścieżki.

## Co tworzy krawędź

Krawędź `Import(a, b)` biegnie od importera do importowanego pliku. Powstaje
z poprawnej, kompletnej deklaracji importu na poziomie pliku, zakończonej
średnikiem, której literał ścieżki rozwiązuje się jednoznacznie do `b ∈ S`.
Deklaracje poprzedzają definicje; opcjonalna deklaracja modułu poprzedza
importy. Składnia importu w przypiętym parserze to
`attribute_section IMPORT STRING_LITERAL SEMI`, gdzie sekcja atrybutów może
być pusta. Źródła dekodujemy jako UTF-8 w trybie ścisłym; błąd dekodowania
lub nieobsługiwany BOM daje `unresolved`. Nie normalizujemy tekstu ani
końców linii. Są to reguły kontraktu oparte na
[przypiętym parserze Chromium](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/mojom/mojom/parse/parser.py).
Ekstraktor musi rozpoznawać tokeny języka, komentarze, literały i zagnieżdżenia;
samo wyszukanie napisu `import` lub wyrażenie regularne na liniach nie jest
specyfikacją parsera. Napis przypominający import w komentarzu albo innym
literale nie tworzy krawędzi.

Importy z atrybutami warunkowymi wchodzą do relacji bez oceny warunków.
Relacja oznacza obecność deklaracji w zamrożonym tekście, niezależnie od
ustawień GN, systemu operacyjnego i wybranego wariantu kompilacji. Nie jest
to graf importów konkretnego zbudowanego programu. Komentarze liniowe
`// …` i blokowe `/* … */` są pomijane zgodnie z regułami leksykalnymi;
niedomknięty komentarz lub literał jest błędem ekstrakcji.
Przypięty [lexer Chromium](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/mojom/mojom/parse/lexer.py)
oddziela tokeny komentarzy od tokenów literałów. Jego pełne reguły literałów
dopuszczają więcej zapisów niż przyjęty niżej podzbiór ścieżek.

## Rozwiązywanie ścieżek

Kontrakt używa jawnie ustalonego pojedynczego korzenia: katalogu głównego
zamrożonego repozytorium. Import `"mojo/public/mojom/base/string16.mojom"`
wskazuje tę samą ścieżkę w drzewie Git, niezależnie od katalogu importera.
Nie przeszukujemy systemu plików komputera, bieżącego katalogu, katalogów
wyników kompilacji ani repozytoriów DEPS. Nie stosujemy niejawnego fallbacku
do ścieżki względnej wobec importera.
To jawny wybór eksperymentu: narzędzia budowania Chromium mają również
konfigurowalne katalogi importów i katalog wynikowy, co widać w
[generatorze wiązań](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/tools/bindings/mojom_bindings_generator.py).

Obsługiwany literał ścieżki zawiera kanoniczną ścieżkę repozytoryjną:
niepuste segmenty rozdzielone `/`, bez początkowego `/`, segmentów `.` lub
`..`, odwrotnych ukośników, sekwencji ucieczki, bajtów NUL oraz prefiksów
dysku lub schematu URL. Inny zapis wymaga rozszerzenia kontraktu albo daje
status `unresolved`; nie jest automatycznie normalizowany regułami Windows.
Nieprawidłowa lub niejednoznaczna ścieżka nie znika z raportu.

## Przykład z przypiętych źródeł

Pierwszy proponowany korzeń to `mojo/public/mojom/base/time.mojom`.
Rzeczywisty plik
[`mojo/public/mojom/base/file_info.mojom`](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/mojo/public/mojom/base/file_info.mojom)
importuje ten korzeń bezpośrednio w linii 7. Należy więc do wyniku wraz
z samym korzeniem. Obiekt Git pliku ma identyfikator
`c10e953809bee580680b84839ed02274d76b2de7`.

Istnieje też ścieżka o dwóch krawędziach:

```text
services/network/public/mojom/url_loader.mojom
  → services/network/public/mojom/url_response_head.mojom
  → mojo/public/mojom/base/time.mojom
```

Pierwszą deklarację zawiera
[`url_loader.mojom`, linia 12](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/services/network/public/mojom/url_loader.mojom#L12)
(obiekt `47daa39be77716831401f3205b804352714a5ce7`), a drugą
[`url_response_head.mojom`, linia 7](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/services/network/public/mojom/url_response_head.mojom#L7)
(obiekt `2551c74d161edc11e3d4e95c858c144a063ae80a`). To przykładowi
bezpośredni i pośredni importerzy, a nie wyliczenie pełnego wyniku.

Rzeczywisty import warunkowy znajduje się w
[`chrome/common/renderer_configuration.mojom`, linie 12–13](https://github.com/chromium/chromium/blob/27cec857a08a0ee0e1b41f5eb18c07467a0ce093/chrome/common/renderer_configuration.mojom#L12):
atrybut `EnableIf=enable_request_header_integrity` poprzedza import
`services/network/public/mojom/http_request_headers.mojom`. Kontrakt zachowuje
tę krawędź bez oceny warunku. Obiekt pliku to
`b5631d2a8d915c9209ee9499cedad28b0b43e79a`.
Przykłady oraz referencyjne pliki parsera sprawdzono także w lokalnym
magazynie korpusu: identyfikatory Git i SHA-256 oryginalnych bajtów zgadzają
się z manifestem. Nie jest to walidacja składni całego korpusu ani pełne
wyliczenie grafu importów.

## Granice korpusu i niepełne dane

Każda rozpoznana deklaracja musi otrzymać jawny status rozstrzygnięcia:

- `internal`: kanoniczny cel należy do `S`; tworzy krawędź `Import`.
- `outside_scope`: kanoniczny cel nie należy do `S`, co potwierdza kompletne
  drzewo Git. Raport zachowuje importera, literał i przyczynę, np. gitlink,
  dowiązanie, brak śledzonego wpisu lub inny typ pliku. Cel nie jest dopisywany
  do `S`, a ścieżka zapytania nie może przechodzić przez taki cel.
- `unresolved`: nie można rozstrzygnąć ścieżki, składni albo przynależności
  do zakresu, lub nie można odczytać zweryfikowanej treści wymaganego pliku.

Znany import poza zakresem sam w sobie nie uniemożliwia dokładnej odpowiedzi
na powyższe zapytanie o graf indukowany przez `S`. Taka odpowiedź nie obejmuje
ścieżek wychodzących z `S` i powracających przez zewnętrzne repozytoria.
Jeżeli użytkownik oczekuje również takich ścieżek, potrzebny jest inny zakres
i nowe pobranie; obecny wynik nie jest odpowiedzią na rozszerzone zapytanie.

Brakujące bajty dla dowolnego pliku z `S`, niepełny manifest, błędny skrót,
nieobsługiwana składnia lub nierozstrzygnięta deklaracja powodują
`unresolved` dla zapytania o cały `S`. Błąd w pozornie niepowiązanym pliku
może ukryć import do korzenia. Nie wolno zawęzić kontroli do plików
odwiedzonych przez wyszukiwarkę. Można zachować wynik cząstkowy i przyczyny
błędu, ale nie przedstawiać go jako kompletnego. Korzeń spoza `S` jest
odrzucany jako `out_of_scope`; nie jest zastępowany podobną ścieżką.

Śledzone pliki wygenerowane, jeśli mają zwykły tryb Git i rozszerzenie
`.mojom`, należą do `S` tak samo jak inne pliki. Nieśledzone wyniki generatorów,
hooki, budowanie Chromium i pobieranie DEPS nie są częścią eksperymentu.
Błędna składnia nie oznacza pliku bez importów: musi być zgłoszona. Pełny
parser albo jawnie określony, odrzucający nieobsługiwane konstrukcje podzbiór
gramatyki musi poprzedzić deklarację dokładności ekstrakcji.

## Znaczenie statusu i granica formalnej gwarancji

Docelowy status `complete_for_declared_scope` wymaga kompletnego manifestu,
zgodności commitu i treści wszystkich plików `S`, zakończonej ekstrakcji bez
nierozstrzygnięć oraz przyjęcia certyfikatu przez niezależny checker.
Pozostaje on stwierdzeniem implementacji z udokumentowanymi założeniami
dotyczącymi ekstraktora. Nie jest dowodem formalnym parsera.

`RepoProof.exact_dependents` dowodzi dokładności względem dostarczonego
grafu przy trzech obowiązkach: korzeń należy do wyniku; każdy inny wynik
ma rodzica z oryginalną krawędzią `Import(v, parent)` i ściśle mniejszą rangą;
wynik jest domknięty po wszystkich odwróconych krawędziach. Dowód nie
ustanawia, że manifest albo graf wiernie opisują źródła. Checker Python nie
wywołuje wyszukiwania generatora, ale jego zgodność z Lean jest testowana,
a nie formalnie udowodniona.

Aby połączyć źródła z twierdzeniem o grafie, pozostają obowiązki:

1. Wykazać kompletność enumeracji drzewa wskazanego commitu, jednoznaczność
   ścieżek, klasyfikacji trybów i wyboru `S`, w tym wykluczenie gitlinków
   oraz dowiązań bez podążania za nimi.
2. Związać każde źródło z obiektem Git, oryginalnymi bajtami i manifestem;
   jawnie określić założenia kryptograficzne hashy oraz model zaufania do Git.
3. Określić gramatykę, leksykę, dekodowanie i rozwiązywanie ścieżek, a potem
   wykazać poprawność i kompletność ekstrakcji każdej deklaracji w każdym
   pliku `S`, włącznie z komentarzami i atrybutami.
4. Wykazać, że serializacja grafu zachowuje dokładnie relację `Import`,
   kierunek krawędzi i zbiór `S`, bez pominięć lub dodatkowych krawędzi.
5. Wykazać zgodność walidacji wejścia i checkera Python z obowiązkami
   `exact_dependents`, w tym naturalność rang i kontrolę wszystkich krawędzi.
6. Związać oczekiwany korzeń, wersję kontraktu, manifest, graf i certyfikat
   z jedną instancją zapytania; nie polegać wyłącznie na deklaracjach generatora.

Wynik opisuje zależność tekstowych deklaracji importów. Nie dowodzi, że zmiana
pliku wpłynie na zachowanie programu, że dany kod jest wykonywany ani że
konkretna konfiguracja kompilacji używa wszystkich znalezionych deklaracji.
