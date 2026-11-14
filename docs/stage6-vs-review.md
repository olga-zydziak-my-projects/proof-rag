# Końcowy przegląd VS etapu 6

Werdykt **STAGE6_CONFIRMED**. Data przeglądu 15 listopada 2026.

## Zmiany i zakres

Audytor stosuje zamkniętą, niezależną gramatykę całego modułu eksportu.
Kontroluje konteksty deklaracji, kompletne instrukcje dowodów i koniec pliku.
Wcześniejsze niezależne porównania korzenia, grafu, świadków, rang,
wskazań krawędzi i całej listy wyników pozostają obowiązkowe.
Eksporter pozostaje odrębną implementacją.

Osobny parser etapu 6 wymaga dokładnie jednego pełnego raportu dla każdego
z czterech drukowanych twierdzeń, w tym `erased_accepted`. Odrzuca brak,
duplikaty, sprzeczności, błędną składnię, nieznane wpisy i niedopuszczone
aksjomaty. Kontrola następuje przed promocją odpowiedzi. Zachowano
historyczny parser etapu 4 oraz wszystkie pliki etapów 1–5.

Nie wykazano błędnej historycznej odpowiedzi. Dotychczasowe CLI samo
generowało dowód w zaufanym katalogu. Ustalono luki w pokryciu audytu tekstu
i logów. Dodane testy awarii procesu używają jawnych atrap, a świeże zapytania
akceptacyjne rzeczywiście uruchamiają Lean.

## Warunki regresji

Run-03 na aktualnym drzewie wykonał 120 testów, z czego 118 przeszło,
a dwa zakończyły się niepowodzeniem z powodu wymagania historycznych bajtów
README w testach etapu 5. Nie było pominięć ani błędów wykonania testów.
[Raport run-03](../verification/stage6-vs-audit-run-03.json) zachowuje rzeczywisty
status FAILED i kompletne logi. Historyczne testy i ich kontrola zachowania
plików pozostały bez zmian.

Końcowy run-04 wykonuje pełny zestaw testów w odizolowanej kopii aktualnego kodu,
testów, formalnych modułów i danych etapu 2. Jedyna zamiana treści to
historyczny README, odczytany z commitu e498411 i sprawdzony względem
zamrożonego baseline etapu 5. Tożsamości aktualnego kodu i testów są
porównywane bajtowo przed i po wykonaniu. README głównego drzewa pozostaje
aktualny. Szczegóły kopii i obie tożsamości README zapisano w raporcie.

## Faktycznie wykonane kontrole

- Pełna regresja zaliczyła 120 testów, z 0 pominięciami,
  0 błędów i 0 niepowodzeń. Zachowany test różnicowy obejmuje
  1547 przypadków Python–Lean.
- Sprawdzono 12 różnych korzeni. Każdy pełny wynik porównano
  z niezależnym obliczeniem punktu stałego. Dla każdego powstał świeży dowód
  zapytania przy ponownym użyciu zakotwiczonego dowodu źródłowego etapu 5.
- Powtórzone zapytanie dało identyczne bajty certyfikatu, pliku Lean,
  `answer.json` oraz `answer.txt`.
- Odrzucono 28 podmian rzeczywistych danych.
  Ukierunkowane testy obejmują dodatkowe `run_tac pure ()`, zmienione dowody,
  brakujące, powtórzone i sprzeczne raporty oraz odmowę promocji odpowiedzi.
- Dodatkowo odrzucono 7 podmian rzeczywistego eksportu i logu pierwszego korzenia.
  Kontrole obejmują dopisane taktyki, zamieniony dowód oraz błędne raporty
  aksjomatów. [Raport nowych kontroli](../verification/stage6-vs-hardening-04.json)
- Publiczne CLI wykonało przygotowanie oraz poprawne zapytanie o `values.mojom`,
  z pełnym porównaniem 240 ścieżek. Sprawdzono też odrzucenie błędnego korzenia.
- Zachowano 148 historycznych plików. Jawny wyjątek dotyczy
  wymaganego przez użytkownika README. Raport zawiera dawną i nową tożsamość.
  Baseline pozostał bez zmian, a kotwica etapu 5 pozostała przodkiem HEAD.

Wyniki są w [run-04](../verification/stage6-vs-audit-run-04.json),
[raporcie publicznego CLI](../verification/stage6-vs-public-cli-04.json)
i [podsumowaniu przeglądu](../verification/stage6-vs-review.json).
Pełne SHA-256 przejrzanych plików oraz całego sprawdzonego kodu są zapisane
w podsumowaniu maszynowym. Bramki obliczono z raportów i aktualnych bajtów.
Zaliczenie testów stanowi jedną z bramek końcowego zatwierdzenia.

## Niezależny przegląd i zachowanie historii

Agent `/root/final_review`, który nie implementował zmian, przejrzał cały diff
kodu, testów i README. Własny przebieg zaliczył 35 testów etapu 6 bez pominięć.
Zgłoszony konflikt baseline README usunięto przez jawny wyjątek dokumentacyjny.
Agent ponownie sprawdził poprawkę i tożsamości końcowych plików, wydając PASS.
Dodatkowy przegląd gramatyki odrzucił wstawienie `run_tac pure ()` w każdym
z 474 punktów syntetycznego modułu.

Historyczny [run-01](../verification/stage6-vs-audit-run-01.json) pozostaje
wynikiem wcześniejszej wersji kodu. [run-02](../verification/stage6-vs-audit-run-02.json)
odrzucono po zmianie kodu checkera podczas pierwszego zapytania, bez wydania
odpowiedzi. Końcową podstawą akceptacji jest odrębny run-04.
Wcześniejsze przeglądy i raporty zachowano.

## Ograniczenia

Zakres pozostaje przypiętym korpusem Chromium i specyfikacją
`SourceBytes byte import projection v2`. Założenia obejmują kernel i SDK Lean,
aksjomaty `propext`, `Classical.choice`, `Quot.sound`, uczciwe IO systemu,
Git i odporność hashy. Wykonanie wymaga zaufanego katalogu lokalnego.
Obrona przed aktywnie wrogim współbieżnym zapisem pozostaje poza gwarancją.

Wymagane lokalne źródła i zaakceptowane moduły dowodu są wyłączone z Git.
Samowystarczalność zwykłego klonu pozostaje niewykazana. Integracja LLM
będzie osobnym etapem. Instrukcje uruchomienia zawiera [README](../README.md),
a szczegóły założeń [granica zaufania](stage5-trust-boundary-v2.md).
