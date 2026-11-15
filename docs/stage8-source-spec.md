# Źródła, resolver i granica zaufania etapu 8

Specyfikacja operacyjna:
`SourceBytes byte import projection v2 + contextual exact prefix resolver v8.2`.
Zachowujemy [projekcję bajtową v2](stage5-source-spec-v2.md): pełne surowe bajty,
UTF-8, automat komentarzy/napisów/importów, porządek i duplikaty zdarzeń,
brak wartościowania warunków atrybutów. Nie jest to pełna semantyka Mojom.
Nowe źródła nie otrzymują automatycznie gwarancji konkretnego dowodu Chromium.

Manifest wejściowy `stage8-corpus-v1` zawiera origin (`real` albo
`synthetic-fixture`), repozytoria z URL/commit/tree, zakres prefiksów i pełną
listę `.mojom` (ścieżka/blob/SHA-256), konfiguracje i reguły resolvera.
Lokalizacje checkoutów są osobną konfiguracją, nie częścią tożsamości źródeł.
Wiele wersji projektu ma różne trójki tożsamości, nawet przy identycznej treści.

Przy capture sprawdzamy drzewo przypiętego commitu, pełną listę zwykłych
śledzonych `.mojom` w zadanych prefiksach i dokładne blob IDs. Czytamy źródła
z obiektów Git, **nie niezacommitowane bufory/worktree**. Zmieniony worktree
nie zmienia zapytania o poprzedni commit. Nowa wersja wymaga nowego manifestu.
Symlinki i gitlinki nie są źródłami Mojom i nie są rozwijane automatycznie.
Brak wymaganego obiektu lub pliku blokuje capture. Każdy blob porównujemy
z SHA-256 zakotwiczonym w manifeście. Konfiguracji nie wykonujemy przez eval/exec.

Reguła jest krotką: ID, `(repo_id, commit)` importera, dokładny prefiks importu,
cel `(repo_id, commit)` lub jawne external, prefiks ścieżki docelowej i ID
konfiguracji pochodzenia. Rozwiązanie to zastąpienie prefiksu, bez normalizacji.
Musi pasować dokładnie jedna reguła. Dwa pasujące prefiksy są błędem, a nie
wyborem najdłuższego lub pierwszego. Nie istnieje domyślne wyszukiwanie po nazwie,
fallback do własnego repozytorium ani poprawianie wielkości liter lub `..`.
Cel wewnętrzny musi istnieć dokładnie w deklarowanej wersji i uniwersum.
External jest dozwolone wyłącznie przy jawnej regule; zdarzenie pozostaje w bazie.

`evidence` wiąże regułę z przypiętymi bajtami konfiguracji. **Nie wyprowadzamy
automatycznie semantyki reguły z dowolnego GN/DEPS**. Akceptacja mapowania
manifestu pozostaje ręczną, audytowaną częścią specyfikacji. To kolejna przyczyna,
dla której samo działanie resolvera i indeksu nie stanowi formalnego source-to-answer.

Tabele DuckDB i Parquet:

| Tabela | Treść |
| --- | --- |
| files | Pełna lista, także pliki izolowane; lokalny ID, repo_id, commit, path, blob, hash |
| repositories | Wersje, URL-e, drzewa i zadeklarowany zakres |
| events | Importer, pozycja zdarzenia, literalny import, hash całego źródła |
| resolutions | Każde zdarzenie, ID reguły, cel lub external |
| edges | Unikalne pary lokalnych ID importer→importowany |
| external | Pełne jawnie wyłączone zdarzenia |
| configs | Tożsamości konfiguracji reguł |
| metadata | Cały manifest, jego kotwica, specyfikacja i wersje/hashe ekstraktora i narzędzi |

Brakujące/niejednoznaczne rozstrzygnięcia kończą prepare z błędem. Nie są
cicho usuwanymi krawędziami w przyjętym indeksie; diagnoza pozostaje błędem CLI.
Nie ma aktualizacji przyrostowych: zmiana źródła, commitu, reguł, specyfikacji
lub narzędzi unieważnia cały snapshot. Zapytanie ponownie odtwarza capture
z niezależnej kotwicy manifestu podanej przez wywołującego i porównuje wszystkie
wiersze z DB oraz Parquet. Sam opis/hash zapisany w cache nie ustanawia zaufania.
Zaufany caller ma przechowywać oczekiwany hash poza nieufnym cache; obliczenie
nowego hasha z podmienionego manifestu nie jest akceptacją poprzedniej kotwicy.

Indeks odwrotny CSR jest odtwarzany przy odczycie snapshotu. BFS bez świadków
jest bazowym wyszukiwaniem. Osobny przebieg BFS generuje rodziców i rangi.
Niezależny DFS buduje własną strukturę dict-of-arrays. Checker nie wyszukuje:
sprawdza korzeń, wszystkie oryginalne krawędzie rodziców, spadek rang i pełne
domknięcie po wszystkich krawędziach. To daje poprawność i kompletność względem
przekazanego grafu; checker Python nie jest formalnie zweryfikowany.

Mały eksport regresyjny Lean dopuszcza do 64 węzłów i 128 krawędzi. Nowy
eksport blokowy używa `FastChecker` i ma osobną drabinę pomiarową powyżej 64.
Zamknięty niezależny
parser porównuje cały eksport: liczby, korzeń, wszystkie krawędzie, świadków,
pełną listę odpowiedzi i dokładną postać dowodów. Kernel sprawdza `accepted`,
`exact` i `answer_mask`. Raport aksjomatów musi zawierać dokładnie trzy kompletne
rekordy; dopuszczone są jedynie propext, Classical.choice i Quot.sound.
Reachability i Checker są świeżo kompilowane w prywatnym LEAN_PATH, bez użycia
projektowych `.olean` z cache. Nie ma nowych aksjomatów, sorry/admit ani VM proof.

Wersja początkowa etapu 8 nie zawierała twierdzenia źródło→resolver→graf→odpowiedź.
Uzupełnienie opisane poniżej wprowadza ogólne twierdzenie i nowy eksport.
Git, hashe, ekstrakcja/resolver Python, DuckDB/Parquet, serializacja i renderer
są kontrolowanymi granicami IO, a nie twierdzeniami Lean. Przyjmujemy uczciwy
system, Git/kernel i zaufany lokalny katalog bez wrogiego współbieżnego zapisu.

## Implementacja uzupełniająca z 15 listopada 2026

Zakres v8.2 zachowuje semantykę prefiksów ścieżek. Prefiks kończący się `/`
wybiera całe poddrzewo. Prefiksy nazw plików są rozwijane na podstawie pełnej
listy ich katalogu nadrzędnego, z jednokrotnym odczytem każdego takiego katalogu.
Pusty prefiks wybiera całe repozytorium. Enumeracja używa literalnych
pathspec Git i odtwarza pełną listę zadeklarowanego zakresu. Pozwala to czytać
przypięte obiekty częściowego repozytorium bez pobierania obcych poddrzew.

Capture tworzy mapę metadanych raz. Jeden trwały `git cat-file --batch` na
repozytorium odczytuje pojedyncze bloby. Skaner uruchamia te same przejścia
bajtowe bez alokowania świadków dowodowych. Zdarzenia, rozstrzygnięcia i external
są sekwencjami na dysku. Zapis i porównanie faktów używają partii 4096 wierszy.
Przygotowanie i zapytanie zachowują pełne ponowne sprawdzenie treści.
Pliki tymczasowe produkcyjnej ścieżki mieszczą się w katalogu artefaktów.
Manifest, tabela tożsamości i unikalne krawędzie pozostają w pamięci.

`formal/ContextualSourceBinding.lean` definiuje kontekstowy resolver na regułach,
niezależnie od tabeli krawędzi. Twierdzenia `target_iff`, `source_exact` i
`answer_exact` łączą skaner bajtowy, obustronną zgodność grafu, certyfikat oraz
pełne tożsamości odpowiedzi. `check_sources` wykonuje świeżą kompilację zależności,
źródeł i zapytania, audyt całej dozwolonej składni eksportu oraz raportów aksjomatów.
Przyjęcie reguł mapowania pozostaje ręczną specyfikacją opartą na przypiętych danych.
Bieżący wynik konkretnych przebiegów opisuje nowy raport uzupełniający.
