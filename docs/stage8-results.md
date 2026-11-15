# Wyniki etapu 8

**STAGE8_CORPUS_BLOCKED**. Silnik i pomiary syntetyczne działają, ale nie
ustanowiono wymaganego rzeczywistego pilota trzech połączonych projektów.
Nie ogłaszamy STAGE8_PASS ani formalnego source-to-answer dla nowych źródeł.

Baza to `9d590b5b7538fb20f1061ef31e266f1ee9f221e8`; na początku HEAD odpowiadał
dokładnie tej bazie i drzewo było czyste. Praca jest na gałęzi
`codex/stage8-multirepo`. Nie cofnięto zmian i nie wykonano push.
Historyczne pliki są zachowane, z jawnym wyjątkiem głównego README.

## Co wykonano i czego nie wykonano

| Część | Stan i granica |
| --- | --- |
| Rzeczywisty korpus | CORPUS_BLOCKED; 0 przyjętych projektów i 0 zaakceptowanych połączeń pilota |
| Rozpoznanie | 8 kandydatur Git; pełny skan 153 Mojom w 3 projektach, 631 537 B, 125 importów, wszystkie własne |
| Silnik | Kontekstowy resolver wersji, pełny source capture IO, DuckDB/Parquet, odwrotny CSR, pełne odpowiedzi i certyfikaty |
| Source IO fixture | 3 jawnie sztuczne repozytoria Git, 4 źródła, 4 zdarzenia, 3 krawędzie cyklu między repozytoriami, 1 external |
| Formalny pilot źródłowy | NOT_RUN_CORPUS_BLOCKED; brak wymaganych 6 rzeczywistych korzeni i 3 rzeczywistych source-to-answer proofów |
| Nowy ogólny most Lean źródło→kontekstowy resolver→graf | NOT_IMPLEMENTED; działa Python source IO, nie formalny most |
| Lean grafowy | Trzy świeże dowody dla 64 syntetycznych węzłów, pełny audyt i maska całej odpowiedzi |
| Skalowanie 10K, 100K, 1M | Wszystkie dziewięć wariantów GRAPH_PASS; graf + niezależny checker Python, **bez Lean i bez źródeł** |
| Soufflé/Magic Sets | Osobny mały eksperyment: 256 węzłów, te same fakty i korzenie, wszystkie pełne wyniki zgodne |

Wybór i wersje rzeczywistych kandydatów oraz konkretne przeszkody opisuje
[rozpoznanie](stage8-reconnaissance.md). [Manifest wyboru](../verification/stage8-corpus.json)
zawiera kotwice hashy raportów. Ich HEAD nie są łączone jako spójny korpus.
Same zależności DEPS/GN, kopie protokołów i komunikacja IPC nie są importami plików.

Przykład **wyłącznie syntetyczny**: pytanie o `(a, commit-A, local/a.mojom)`
zwraca trzy tożsamości `a@commit-A:local/a.mojom`,
`b@commit-B:local/shared.mojom`, `c@commit-C:local/shared.mojom`.
Izolowany plik `a:local/isolated.mojom` nie trafia do tego wyniku. Import
`external/no.mojom` pozostaje zdarzeniem zewnętrznym. Nie ma analogicznego
przyjętego przykładu na rzeczywistych repozytoriach. Pełne commity i odpowiedzi
są w fixture_queries końcowego raportu i `local/stage8/final-02/fixture-query-*`.

## Skalowanie na syntetycznych grafach

Seed 808. Rodziny: długi łańcuch; moduły po 100 węzłów z kontrolowanymi mostami;
8-cykle z rozgałęzieniami i 10% izolowanych węzłów. Trzy logiczne repozytoria
generatora nie oznaczają trzech rzeczywistych projektów. Korzenie deterministyczne:
0, N/2 i N−1. Każde wyszukiwanie wykonano trzy razy na przygotowanym indeksie.
Porównano wszystkie 27 pełnych list i całe certyfikaty, nie próbki/hashy.
Niezależny DFS jest liniowy; na indukowanym prefiksie do 64 węzłów użyto też
niezależnego punktu stałego. Nie utworzono miliona małych plików.

Poniższe pomiary pochodzą z final-02. Czas wariantu obejmuje uruchomienie procesu,
przygotowanie, bazę, odczyt, trzy korzenie, powtórzenia i zapis pełnych artefaktów.
Mediana zapytania jest dla największej odpowiedzi, korzenia 0, bez budowy indeksu.

| Węzły | Rodzina | Krawędzie | Czas wariantu [s] | Mediana root=0 [s] | Szczyt RSS [MiB] | Szczyt private [MiB] |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 10 000 | chain | 9999 | 0,786 | 0,005510 | 152,3 | 893,9 |
| 10 000 | modular | 9999 | 0,792 | 0,005502 | 151,0 | 886,2 |
| 10 000 | cycles | 10124 | 0,794 | 0,005492 | 151,0 | 859,8 |
| 100 000 | chain | 99999 | 1,578 | 0,056857 | 220,2 | 923,7 |
| 100 000 | modular | 99999 | 1,577 | 0,050974 | 218,9 | 926,9 |
| 100 000 | cycles | 101249 | 1,574 | 0,043434 | 231,2 | 948,0 |
| 1 000 000 | chain | 999999 | 10,632 | 0,504933 | 773,3 | 1571,8 |
| 1 000 000 | modular | 999999 | 10,638 | 0,524609 | 787,9 | 1571,0 |
| 1 000 000 | cycles | 1012499 | 10,104 | 0,447790 | 742,5 | 1505,0 |

Są to pojedyncze budowy indeksu, a nie mediany trzech budów. Wszystkie trzy
próbki, mediany i zakresy zapytań, czasy osobnych faz przygotowania, budowy/odczytu
indeksu, generowania i kontroli certyfikatu, niezależnego DFS i pełnego zapisu,
rozmiary DB/temp/artefaktów oraz rozkłady logicznych repozytoriów są w
[raporcie final-02](../verification/stage8-final-02.json). Przykładowo modular 1M
ma 9999 mostów między logicznymi repozytoriami; jego pozostałe krawędzie są wewnętrzne.
Nie wymagano identyczności binarnego DuckDB. Powtórne eksporty Parquet faktów
były bajtowo identyczne; odpowiedź i certyfikat źródłowego fixture także.

Największy sprawdzony zbiór to **1M syntetycznych węzłów**, w rodzinie cycles
1 012 499 krawędzi. Jego poziom to GRAPH_PASS_PYTHON_CERTIFICATE.
Największy świeży dowód Lean tego etapu obejmuje **64 syntetyczne węzły**;
nie jest to nowy dowód źródłowy. Formalnie zaakceptowany korpus Chromium z
poprzednich etapów pozostaje oddzielnym wynikiem 1864 rzeczywistych plików.

## Narzędzia i zasoby

Python 3.12.14, Git 2.55.0.windows.2, DuckDB 2.0.0, PyArrow 26.0.1,
NumPy 2.5.4, psutil 7.2.2. Lean 4.35.0,
commit `eb6cafb7290e8bd5f2937522d8d804f58f02bafc`, ze sprawdzeniem hasha programu
przed/po. Reachability i Checker kompilowano świeżo, jeden proces Lean naraz.
Nie użyto projektowych `.olean` ani konkretnego dowodu Chromium jako dowodu
nowych grafów. Aksjomaty były odczytane rygorystycznie; brak sorry/admit/native_decide.

Przed pomiarami: fizyczny RAM 33 752 997 888 B (około 31,4 GiB), dostępny
9 923 039 232 B; wolny dysk 337 882 193 920 B. Zamrożono 4 GiB pamięci drzewa,
8 GiB artefaktów i 600 s na wariant; DuckDB 512 MB, temp 2 GB i jeden wątek,
Arrow CPU/IO po jednym wątku. Zostawiono zapas dla Windows/IDE.

RSS i private to równoczesne sumy monitora i drzewa workera, próbkowane co
żądane 0,1 s; raport podaje rzeczywiste przerwy. RSS może podwójnie liczyć
współdzielone strony. Private jest miarą commit procesu, **nie użyciem dysku**.
Pomiar obejmuje pamięć poza menedżerem DuckDB. Nie jest ścisłym pomiarem
chwil między próbkami ani całej pamięci Windows. Nie nazywamy przebiegów cold.
Kontrolowane testy małego limitu faktycznie dały TIMEOUT i RESOURCE_LIMIT;
nie zaliczano ich jako benchmarków. W dziewięciu właściwych wariantach limitów
nie osiągnięto i nie zwiększano ich automatycznie.

## Opcjonalne Soufflé

Natywnego Soufflé nie było. Dostępny WSL Ubuntu-24.04 pozwolił rozpakować oficjalny
pakiet 2.5 po porównaniu SHA-512, bez systemowej instalacji. Przebiegi były
interpreterem, bez kompilacji analizowanych projektów. Wyjściowy program Datalog
i skrypt tego osobnego eksperymentu zamrożono przed jego wykonaniem; hashe
przed/po są zgodne. Nie zmieniono kodu silnika używanego przez final-02.

Na 256-węzłowym łańcuchu oba warianty sprawdziły korzenie 0/128/255 i pełne
385 par `(root,node)`. Trzy próby na wariant:

| Wariant | Mediana pełnego czasu WSL [s] | Zakres [s] | Maks. RSS Linux [KiB] |
| --- | ---: | --- | ---: |
| Bez Magic Sets | 2,313615 | 2,134348–2,321438 | 12800 |
| Z Magic Sets | 2,125840 | 2,016817–2,133958 | 11932 |

Pełny czas obejmuje start WSL, import, obliczenie i zapis. Przygotowanie faktów
jest mierzone oddzielnie; profiler zachowuje loadtime, runtime i savetime
poszczególnych relacji. Linux `/usr/bin/time -v` mierzy pamięć, a ulimit/timeout
ograniczają adresy 1 GiB, CPU 60 s i wall 65 s. Windows psutil nie jest tu użyty
do przypisywania pamięci procesom Linux. Nie wnioskujemy o przyspieszeniu na
dużej skali z różnicy około 0,19 s zdominowanej kosztem WSL.
[Zwięzły raport](../verification/stage8-souffle.json) odsyła do pełnych profili.

## Historia kontroli, ograniczenia i następny krok

Pierwszy smoke 10K zakończył się GRAPH_PASS, ale był wcześniejszą wersją kodu,
z łącznym wyszukiwaniem i świadkami oraz innym odczytem Arrow; jego 56,45 s
nie służy do porównania wydajności finalnej wersji. Review rozdzielił faktyczne
generowanie certyfikatu od pomiaru wyszukiwania, poprawił wyścig znikającego
pliku temp w monitorze, zakres dysku Lean i przypisanie repozytoriów w modular.
Pierwsze 18 HTTP 429 pobierania źródeł usunięto pojedynczym sekwencyjnym retry.

Final-01 zaliczył niezależne części i 151 testów z CORPUS_BLOCKED. Po jego
zakończeniu dodano osobne liczby projektów i wersji w odpowiedzi źródłowej.
Dlatego wykonano pełny nowy final-02, zamiast przedstawiać stary raport jako
dowód aktualnego kodu. Pierwotne raporty i logi pozostają zachowane.

Źródłowe mapowania manifestu są ręcznie akceptowaną specyfikacją; ich evidence
kontroluje bajty konfiguracji, nie dowodzi wyprowadzenia z dowolnego systemu
budowania. Brak aktualizacji przyrostowych: zmiana tożsamości unieważnia cały
snapshot. Brak nowego formalnego mostu źródłowego pozostaje osobnym,
nieukończonym elementem. Zanim powstanie rzeczywisty formalny pilot, trzeba
znaleźć poprawnie powiązaną trójkę, przypiąć zgodne wersje i udowodnić ten most.

Dokładne komendy finalne:

```powershell
$env:PYTHONPATH = 'src;local/stage8-deps'
& $py scripts/check_stage8.py --run-dir local/stage8/final-02 `
  --report verification/stage8-final-02.json --lean $lean
& $py examples/stage8-souffle/reproduce.py local/stage8/souffle-01
```

Nazwy katalogów są już zajęte; dla powtórzenia użyj nowych. Instalację,
przygotowanie i zapytania opisuje [instrukcja](stage8-usage.md).
Duże dane i logi są w ignorowanym `local/stage8`; manifesty, seedy i zwięzłe
raporty są wersjonowane. Żadnych płatnych wywołań etapu 7 nie wykonywano.

Końcowy final-02: **STAGE8_CORPUS_BLOCKED**, `independent_parts_pass=true`.
Regresja zaliczyła **151 testów**, 0 błędów, 0 niepowodzeń, 0 pominięć;
w tym 21 zachowanych testów offline etapu 7, 10 nowych testów etapu 8 oraz
historyczne 1547 przypadków różnicowych Python–Lean. Tożsamości kodu/testów,
konfiguracji i manifestu pozostały zgodne przed/po. Kod regresji był identyczny
z bieżącym drzewem; jedyny override izolowanej kopii to historyczny README.
Wszystkie dziewięć wariantów i kontrolowane testy limitów przeszły wymagane
kontrole. Żaden sukces syntetyczny nie został awansowany na STAGE8_PILOT_PASS.

Niezależny [końcowy przegląd](stage8-review.md) zaakceptował dostarczenie w tym
ograniczonym zakresie. Zweryfikował ponownie całe 27 list i certyfikatów,
wszystkie małe dowody, dane rozpoznania i sześć odpowiedzi Soufflé.
[Tożsamości narzędzi](../verification/stage8-tools.json) oraz
[maszynowy zapis przeglądu](../verification/stage8-review.json) zachowują
powiązanie z końcowym kodem. Nie oznacza to ukończenia brakującego mostu
źródłowego ani rzeczywistego pilota.
