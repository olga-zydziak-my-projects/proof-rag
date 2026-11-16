# Wyniki etapu 9

Końcowe rozstrzygnięcie wylicza [raport bramek](../verification/stage9-status.json).
Kod zamrożono w [inwentarzu](../verification/stage9-code-freeze.json); zwykłe pola
PASS nie zastępują kontroli artefaktów. [Kontrakt](stage9-contract.md),
[korpus](stage9-corpus.md), [specyfikacja](stage9-source-spec.md),
[CLI](stage9-usage.md) i [przeglądy](stage9-review.md) opisują dokładny zakres.

## Rzeczywisty korpus i pełny dowód

Przyjęty zakres ma trzy projekty i trzy przypięte wersje: Chromium 1243 pliki,
Electron 2, Brave 6; razem **1251 rzeczywistych plików**, 1251 unikalnych treści,
4 188 752 bajty oraz 3286 unikalnych krawędzi. 13 krawędzi przekracza projekty.
Nie ma dodatkowych wariantów podnoszących próg plików. Są cztery jawne zdarzenia
do dwóch plików generowanych przez GN, nieobecnych w Git. Nie wyłączono żadnego
trudnego, commitowanego importu. Pełny audyt poprawek i nakładek oraz kontekst
upstream opisuje raport korpusu. Wspólna składowa trzech projektów ma 1149 plików.

Największa nowa pełna ścieżka źródło–odpowiedź obejmuje **wszystkie 1251 źródeł
i cały graf**, także pliki spoza konkretnej odpowiedzi. Świeżo skompilowano 168
modułów, w tym wszystkie 157 grup źródeł, pełną tabelę nazw i równość grafu.
Każde z sześciu różnych zapytań wykonano trzy razy; wszystkie 18 pełnych list
zgadza się z niezależnym DFS i ma własny świeży kernel QueryGraph/QueryAnswer.
Cztery korzenie mają odpowiedzi wieloprojektowe, jeden obejmuje wszystkie trzy
projekty. Przyjęto wyłącznie propext, Classical.choice i Quot.sound; pełne
raporty aksjomatów i cała dozwolona składnia eksportów są ponownie audytowane.

[Przygotowanie](../verification/stage9-preparation.json) zakończyło się
`SOURCE_LAYER_PASS`. Niezależnie zachowana kotwica receipt wynosi
`e9a1ce003e44ac1de5ce2faddcce4d18ff5f0a39da1bfaa5a2bcd315c06e473b`.
Nowe query sprawdza pełne źródła, manifest, reguły, kod, zależności, Python,
toolchain Lean, Git, wszystkie artefakty cache, DB/Parquet i raporty aksjomatów
przed świeżym dowodem oraz po nim. Nie importuje niezakotwiczonego pola PASS.

## Koszty przygotowania i IO

Pełny przebieg **bez cache dowodu** `prepare-03` trwał 1585,178 s we workerze
i 1585,986 s pod nadzorcą, przy limicie 3600 s. Cache systemu operacyjnego
nie był kontrolowany; przebieg nie jest nazywany cold.

| Faza rzeczywistego przygotowania | Sekundy |
| --- | ---: |
| Pełna tożsamość środowiska na początku | 23,590 |
| Odczyt/audyt/ekstrakcja źródeł | 5,871 |
| Zapis indeksu DuckDB/Parquet | 0,250 |
| Eksport i pełne audyty proof | 3,257 |
| Świeża formalna warstwa, wszystkie moduły | 1528,083 |

Pozostały czas obejmuje końcowy ponowny audyt, capture i tożsamość środowiska.
Tabela nie przypisuje tego narzutu pojedynczemu niezmierzonemu timerowi.
Wstrzykiwalność pełnych tożsamości zajęła 134,609 s, dane grafu 6,458 s,
a zbiorczy dowód źródeł i całego grafu 14,610 s.

Rozpoznawcze profilowanie starej ścieżki dla tego samego korpusu zmierzyło
51,950 s osobnych odczytów Git i 0,303 s batch. Generowanie monolitu miało
1,440 s, a dawny pełny audyt 228,262 s. Nowy audyt indeksuje granice deklaracji
raz, nadal konsumując cały eksport i odrzucając duplikaty/braki. Eksport wraz
z jego audytami w rzeczywistym przygotowaniu zajmuje 3,257 s. Surowe źródła
mają tylko 4,19 MB; nie wprowadzano złożonego streamingu ich kilku kopii w RAM.
Podział dowodów i sprawdzona odwrotność nazw rozwiązują większe koszty Lean.

[Osobny profil źródeł](../verification/stage9-source-profile.json) porównuje
wszystkie pliki, krawędzie i fakty z przygotowanym indeksem oraz nieinstrumentowanym
capture. Zwykły capture miał 2,697 s; cProfile 4,815 s: Git metadata/config
1,491 s, batch blob read 0,243 s, projekcja 2,533 s, resolver 0,179 s, inne
kontrole/setup 0,370 s. Audyt wspólnego kontekstu miał 1,500 s, zapis indeksu
0,140 s. Instrumentacja dodaje narzut; tych czasów nie sumujemy z pierwszym
przygotowaniem ani nie przedstawiamy jako czystego czasu bez profilera.

Pozyskanie źródeł ma [osobne raporty prób](../verification/stage9-attempts.json).
Pierwsze pobranie modułów trwało 204,928 s, następne uzupełnienie 25,839 s;
obie próby zakończyły się błędem rozpoznania i są zachowane. Ostateczna próba
ponownie użyła 1202 blobów modułów i ukończyła 1251 źródeł w 16,817 s.
Piny, kompletne drzewa i bloby uwierzytelniono niezależnie przed akceptacją.

## Odpowiedzi: trzy powtórzenia każdego korzenia

Pełna latencja obejmuje start CLI, obie kontrole ponownego użycia, świeży Lean
i finalną publikację. [Pełne próbki](../verification/stage9-measurements.json)
są oddzielne od [pomiarów samego BFS](../verification/stage9-search-profile.json).
BFS używa wcześniej przygotowanego CSR; jego budowa miała 0,000253 s.
Każda lista z profilu BFS jest porównana w całości z DFS i rzeczywistą przyjętą
odpowiedzią. Nie jest samodzielnie nazywana formalnie zweryfikowaną odpowiedzią.

| Korzeń (commit i kontekst w queries.json) | Wyniki | Projekty | Pełna mediana [s] | Zakres [s] | BFS mediana [µs] | BFS zakres [µs] |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| url/mojom/url.mojom | 264 | 3 | 63,059 | 62,554–63,064 | 205,6 | 194,3–222,9 |
| mojo/public/mojom/base/values.mojom | 157 | 2 | 60,058 | 59,549–60,080 | 118,6 | 116,8–121,7 |
| content/public/common/webplugininfo.mojom | 2 | 2 | 56,044 | 55,547–57,057 | 5,5 | 5,0–8,6 |
| Brave: components/ai_chat/core/common/mojom/customization_settings.mojom | 1 | 1 | 56,050 | 56,025–63,167 | 4,4 | 4,1–6,0 |
| third_party/blink/public/mojom/shared_storage/shared_storage_worklet_service.mojom | 3 | 1 | 67,656 | 65,166–86,005 | 6,2 | 5,3–8,9 |
| mojo/public/mojom/base/unguessable_token.mojom | 372 | 2 | 81,771 | 79,347–91,726 | 666,8 | 655,1–676,6 |

Nie skracano zakresu źródłowego dla odpowiedzi jednoelementowej. Koszt kontroli
całego korpusu pozostaje również w takim przypadku. Osobny
[profil publikacji](../verification/stage9-publication-profile.json) wykonał
dodatkowe rzeczywiste query ze świeżym, nieinstrumentowanym workerem. Koordynator
finalizacji (zapis/pełny readback/porównanie/atomowa publikacja) miał 0,005377 s.
Ta instrumentowana próba nie wchodzi do 18 próbek powyżej.

## Zasoby, odrzucenia i granice

Przygotowanie osiągnęło 4,2365 GiB sumy private w nadzorowanym drzewie, przy
limicie 6 GiB; RSS wyniosło 3 289 604 096 bajtów. Katalog przygotowania po
publikacji ma 443 821 003 bajty, poniżej 20 GiB. Natywny Windows, Normal i pełna
afiniczność pozostały zachowane. Nadzorca obejmuje siebie i Job Object z
potomkami, z atomowym przypisaniem i kill-on-close. Współdzielone RSS mogą być
policzone kilkakrotnie; krótkie skoki pomiędzy próbkami są ograniczeniem pomiaru.
Dysk oznacza wskazany cały katalog przebiegu; źródła i przygotowany cache są
osobnymi wejściami kolejnych query. Proces koordynujący jest poza pomiarem Job.

Nowe testy obejmują źródłowe bajty, brak pliku/importu, projekt/commit/kontekst,
reguły/manifest, niejednoznaczność, całą odpowiedź, certyfikat, eksport,
aksjomaty, cache, zależności/narzędzia, bytecode, agregację i publikację po
TIMEOUT/RESOURCE_LIMIT. Modyfikacje są wyłącznie na fixture lub kopiach.
Nie zmieniono żadnego historycznego testu, jego timeoutu ani historycznych raportów.
Wynik pełnej regresji i dokładne nazwy publikuje `verification/stage9-regression.json`.

Wcześniejsze próby przygotowania 01/02 świadomie przerwano dla konkretnych
poprawek synchronizacji Windows i niezależnej kotwicy runnera. Nie są PASS,
nie użyto ich jako cache, a ich Job reports potwierdzają sprzątanie potomków.
Nie podnoszono limitów i nie zmieniano korzeni. Nie zatrzymywano zadań użytkownika
ani nie zmieniano WSL, limitów systemowych lub priorytetów innych procesów.

Pełna [regresja](../verification/stage9-regression.json) zaliczyła **205/205**
odkrytych, kwalifikowanych nazw: wszystkie 180 historycznych oraz 25 nowych.
Nie było błędów, niepowodzeń ani pominięć. Czas unittest wyniósł 209,139 s,
sam nadzór 231,180 s, cała próba z końcowymi kontrolami 237,335 s, poniżej 2400 s. Wewnętrzny timeout
historycznego testu różnicowego nadal wynosi 600 s. Szczyt private drzewa regresji
wyniósł 5 455 605 760 bajtów (około 5,081 GiB), poniżej 6 GiB; po sprzątaniu
pozostało zero procesów Job. To największy zaobserwowany szczyt private etapu.
TEMP/TMP procesu unittest wskazywały nowy katalog view, więc fixture mieszczą się
w mierzonym katalogu regresji. Kod i testy obu drzew oraz oba warianty README
sprawdzono po wykonaniu. README fixture jest jedynym nadpisaniem istniejącej
treści kopii; lokalne, niezmienione zależności skopiowano jako dodatkowe wejście.

Gwarancja dotyczy zamrożonych źródeł i przyjętego mapowania, bez pełnej semantyki
GN/Mojom, bez build-generated closure i bez tezy o zachowaniu programu lub
importerach spoza zakresu. Ręczna akceptacja mapowania i kontrolowane IO są
granicami zaufania. Odtwarzanie zwykłego czystego klonu nie zostało sprawdzone.
Historyczne 1864 pliki Chromium, 1000 syntetycznych węzłów Lean i milion węzłów
Python są osobnymi wynikami. Milionowych benchmarków nie powtarzano: silnik
grafowy nie zmienił się. Nie deklarujemy gotowości na miliony rzeczywistych plików.
Projekt nie wykonywał LLM API ani nie odczytywał kluczy API.
