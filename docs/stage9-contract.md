# Kontrakt etapu 9

Baza: `160860c`, czyste drzewo; gałąź `codex/stage9-real-corpus`.
Etap wymaga co najmniej 1000 rzeczywistych, odrębnych plików trzech projektów,
pełnego formalnego powiązania całego zadeklarowanego korpusu z grafem,
sześciu różnych zapytań (minimum trzy między projektami, jedno obejmujące
wszystkie trzy), pełnej zgodności każdej listy z niezależnym obliczeniem,
świeżego dowodu każdego zapytania, publicznego CLI, testów odrzuceń,
pełnej regresji oraz dwóch niezależnych przeglądów bez uwag blokujących.

Zakres zamraża `verification/stage9-scope-policy.json`, przed wyborem korzeni
i właściwymi pomiarami. Wybieramy całe wymienione moduły źródłowe Chromium,
także ich pliki testowe, pełne dwa cele Electron i cel AI Chat Brave oraz
domknięcie importów commitowanych źródeł. Nie przycinamy list do 1000.
Jawne wyjątki to dokładnie dwa wyjścia generatorów GN, nieobecne w Git.
Wszystkie ich zdarzenia pozostają w danych i w formalnym resolverze external.
Korpus nie jest domknięty względem źródeł generowanych podczas builda.

Tożsamość obejmuje projekt, commit, kontekst i ścieżkę. Chromium ma kontekst
upstream. Importy wybranych celów Electron/Brave mogą mapować do upstream
wyłącznie po audycie równości efektywnych bajtów ich całego domknięcia.
Pozostałe pliki upstream nie otrzymują gwarancji dla patched aplikacji.
Manifest i kotwica są osobne od lokalizacji obiektów Git.

Operacja `reverse_importers` zwraca korzeń i wszystkich jego bezpośrednich
oraz pośrednich importerów **w zamrożonym zakresie**. Domknięcie zależności
nie zapewnia uwzględnienia importerów spoza zakresu. Wynik nie dowodzi wpływu
zmiany na zachowanie programu. Ręcznie przyjęte mapowanie GN/mount/context
pozostaje jawną granicą zaufania.

Źródła, manifest, reguły, generator, dependencies, narzędzia i wszystkie
przygotowane artefakty są ponownie sprawdzane przy użyciu dowodu.
Niezależnie przechowywany hash receipt wskazuje wcześniejsze rzeczywiste
wykonanie kernela; sam hash lub pole PASS bez tego wykonania nie wystarcza.
Nowe zapytanie kompiluje własny graf, certyfikat, maskę i twierdzenie odpowiedzi.
Audyt obejmuje cały eksport i wszystkie pełne raporty aksjomatów.
Dozwolone są tylko `propext`, `Classical.choice`, `Quot.sound`.
Nie dopuszczamy sorry/admit/native_decide ani nowych założeń.

Profil `verification/stage9-config.json`: jedno ciężkie zadanie, Windows
Python/Lean, Normal, 6 GiB całego nadzorowanego drzewa, przygotowanie 3600 s,
zapytanie 600 s, regresja 2400 s, historyczny timeout różnicowy nadal 600 s,
20 GiB całego osobnego katalogu przebiegu. Nadzorca Job Object sprząta potomków.
Cache systemu nie jest kontrolowany. Nie podnosimy limitów po porażce.
Próby rozpoznawcze i nieudane przebiegi pozostają zachowane.

Status jest koniunkcją dwunastu bramek zlecenia, wyliczaną z raportów.
TIMEOUT/RESOURCE_LIMIT/niepełne dowody nie są PASS. Bez wszystkich bramek
status wynosi `STAGE9_INCOMPLETE` z listą braków. Budżet LLM API: zero.
