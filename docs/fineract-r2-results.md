# Fineract R2 — wyniki przebiegu

Przebieg `run-02` zweryfikował **64 pełne odpowiedzi dla 48 różnych literałów**.
Wszystkie 24 historyczne uruchomienia zachowały identyczne rozpakowane bajty
JSONL z archiwów R1. Osobne zestawy rozwojowy i końcowy przeszły po 20/20,
również w przypadkach bez trafień. Wykonano **32 testy**. Wśród nich było
15 istniejących testów CLI i korpusu oraz 17 testów R2. Ostateczny status
wylicza skrypt z raportu, zachowanych artefaktów i obu niezależnych przeglądów.
[Bramki akceptacji](../verification/fineract-r2/gates.json) ·
[Raport maszynowy](../verification/fineract-r2/run.json) ·
[Kontrakt i hashe list](fineract-r2-contract.json) ·
[Uruchomienie w PowerShell](fineract-r2-usage.md)

## Zakres i kontrole

Weryfikator w każdym zapytaniu odczytał przypięty commit
`d63beed7ccfeadaffa0c7842b1011bc88451376f` i drzewo
`04e7b93943ea30b4557d651fd0e6ef6e98f61c0d`. Zakres obejmował
8 635 zwykłych ścieżek i 8 609 unikalnych blobów. Inwentarz zawierał dwa
wyłączone dowiązania i zero gitlinków. Zestaw końcowy pozostał zamrożony
przed pierwszą oceną. Kolejność i rzeczywiste komendy są w raporcie maszynowym.
[Lista rozwojowa](../verification/fineract-r2/development.json) ·
[Lista końcowa](../verification/fineract-r2/final.json)

Po usunięciu jednego wpisu `Nee` z kopii indeksu fixture samodzielne
wyszukiwanie R1 zakończyło się kodem 0 i zwróciło 0 zamiast 3 trafień.
R2 dla tej samej kopii zwróciło **`MISMATCH` (2)** i nie utworzyło katalogu
odpowiedzi. Testy objęły też zmienione bajty i mapowania indeksu, pominięte
i dodatkowe ścieżki, błędny pierwszy offset i wiersz, błędne piny, brakujący
obiekt Git, uszkodzony JSONL, timeout, przerwanie i istniejący katalog.
Kontrole timeoutu i przerwania kończą z zerem procesów w nadzorowanym zadaniu.

## Pomiary

Budowa indeksu trwała **9,69 s** w funkcji budującej i **10,34 s** dla pełnego
CLI. Indeks miał **159 535 104 B** i SHA-256 identyczny z indeksem R1.
Szczyt próbkowanego RSS podczas budowy wyniósł **245,8 MiB**. W 64
wywołaniach zapytań pełny czas CLI miał medianę **1,131 s**, zakres
**1,007–1,286 s** i maksimum próbkowanego RSS **135,5 MiB**.
Cały przebieg z logami i indeksem zajmował **198 591 551 B**. Budowa i każde
zapytanie zakończyły nadzór z zerową liczbą pozostałych procesów.

Poniższe czasy to mediana [minimum–maksimum] w milisekundach z trzech
osobnych wywołań na literał. Wyszukiwanie obejmuje zapis roboczego JSONL.
Skan Git obejmuje ponowny odczyt całego zakresu i wyznaczenie oczekiwanych
trafień. Pełny czas CLI obejmuje także uruchomienie, nadzór i sprzątanie.

| Literał | Ścieżki | Wyszukiwanie | Skan Git | Porównanie | Publikacja | Pełny CLI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Loan` | 3 218 | 100,6 [99,2–108,6] | 612,9 [593,8–618,4] | 11,6 [11,3–12,2] | 4,1 [3,4–4,2] | 1170,6 [1145,5–1192,6] |
| `loan` | 3 613 | 111,0 [110,1–121,2] | 616,0 [592,6–670,8] | 12,9 [12,8–14,1] | 4,7 [4,3–4,9] | 1172,3 [1170,5–1202,5] |
| `LoanTransaction` | 718 | 52,3 [50,0–52,6] | 651,3 [627,0–668,4] | 3,0 [2,8–3,1] | 3,0 [2,5–4,2] | 1131,7 [1077,2–1148,5] |
| `BigDecimal` | 1 362 | 51,9 [49,6–54,0] | 593,7 [591,8–601,7] | 5,2 [5,1–5,3] | 3,5 [3,0–5,0] | 1055,1 [1047,6–1085,5] |
| `org.apache.fineract` | 7 347 | 113,9 [113,1–118,5] | 613,0 [605,9–637,7] | 28,4 [27,7–29,7] | 4,8 [4,1–5,0] | 1162,6 [1155,8–1181,0] |
| `tenant_id` | 7 | 29,8 [29,0–31,3] | 641,7 [635,8–701,2] | 0,3 [0,3–0,4] | 3,6 [2,8–5,3] | 1098,7 [1083,9–1162,8] |
| `.` | 8 575 | 137,2 [132,2–142,6] | 600,2 [594,1–603,9] | 30,7 [29,5–31,2] | 4,2 [4,2–4,6] | 1188,7 [1185,5–1256,4] |
| `R1_ABSENCE_SENTINEL_9F807CD3` | 0 | 17,0 [16,8–17,8] | 618,4 [603,0–619,7] | 0,2 [0,2–0,2] | 3,7 [3,0–3,8] | 1065,1 [1028,6–1098,2] |

Dla `Loan` mediana porównywalnej fazy od otwarcia indeksu do ustalenia trafień
w blobach wyniosła 114,6 ms w powtórzeniach R1 i 74,2 ms w R2. Są to osobne
przebiegi na tej samej implementacji wyszukiwania i bez czyszczenia pamięci
podręcznej systemu plików. Literały krótsze niż trzy znaki skanują wszystkie
bloby w indeksie. Niezależny odczyt Git obejmuje wszystkie bloby przy każdym
zapytaniu, niezależnie od długości literału.

Pomiar wykonano z priorytetem Normal, sekwencyjnie, w Windows z Pythonem
3.12.14, Git 2.55.0.windows.2, SQLite 3.53.1 i psutil 7.2.2. Nadzorca
próbkował RSS i pamięć prywatną procesu kontrolera oraz członków Windows
Job Object. Sumowanie RSS może dwukrotnie uwzględnić współdzielone strony.
Konfiguracja przewidywała 300 s na budowę, 60 s na zapytanie, 2 GiB na
pamięć nadzorowanego drzewa i 4 GiB na artefakty. Pamięć i rozmiary były
sprawdzane próbkowo. Limitów nie podnoszono.

## Artefakty i odtworzenie

Pełne logi, odpowiedzi, potwierdzenia i indeks są w ignorowanym
`local/fineract-r2/run-02`. Śledzony raport zawiera skróty SHA-256
kontraktu, zestawów, kodu, testów, lokalnych plików psutil, użytych plików
wykonywalnych i wyników, a także komendy i kody zakończenia. Historyczne
artefakty R1 zachowano bajt w bajt w bazie
`c4842d788d11cfa1459c8ab4ad68c78f5bd2b456`.

Wstępny fixture pokazał błąd dostępu Windows przy usuwaniu skopiowanego
obiektu tylko do odczytu. Kontrola tworzy teraz kopię bez tego obiektu.
`run-01` zatrzymał się przed budową, ponieważ parser logów pominął dwa testy
korpusu, których komunikaty pojawiły się pomiędzy nazwą testu a `ok`.
Rzeczywiste wyniki testów i raport tamtej próby zachowano w
`local/fineract-r2/run-01` oraz `local/fineract-r2/run-01-summary.json`.
Żaden z tych przebiegów nie odpytał końcowego zestawu.

Do ponownego wyliczenia bramek zapisanego przebiegu użyj tych samych lokalnych
artefaktów i zależności. Przeglądy są powiązane z tym konkretnym raportem.

```powershell
& $pilotPython -B scripts/check_fineract_r2.py `
  --report verification/fineract-r2/run.json `
  --reviews verification/fineract-r2/reviews.json `
  --out local/fineract-r2/gates-recheck.json
```

[Niezależne przeglądy](../verification/fineract-r2/reviews.json)
