# Sprawdzenie wniosków Claude’a na sześciu nowych pytaniach

19 listopada 2026 · Apache Fineract i Electron · Claude Sonnet 5.5

**W zwykłych zapytaniach bramka przepuściła wszystkie 8 w pełni poprawnych szkiców oraz wszystkie 3 z błędnym dopowiedzeniem.** Przy kontrolowanych podmianach wniosku z tymi samymi cytatami wykryła obie sprzeczności. W tej próbie nie poprawiła jakości odpowiedzi wydanych przez zwykłe CLI.

Oba tryby dostały te same sześć pytań. Każde zadano dwukrotnie w każdym trybie. Kolejność trybów dla każdego pytania odwrócono w drugim powtórzeniu. Każde z 24 żądań uruchamiało osobny proces CLI. Repozytoria, commity i gotowe indeksy były wspólne dla obu trybów. Próby odbywały się kolejno. Systemowa pamięć podręczna pozostawała aktywna.

## Wyniki z punktu widzenia użytkownika

| Miara | Bez dodatkowej bramki | Z bramką |
|---|---:|---:|
| Pełna poprawność wśród wszystkich żądań | 10 z 12 | 8 z 12 |
| Opublikowane odpowiedzi | 11 z 12 | 11 z 12 |
| Czas do zakończenia żądania, mediana ze wszystkich prób | 13,17 s | 20,14 s |
| Czas pełnej odpowiedzi, mediana dla 10 par zakończonych publikacją w obu trybach | 13,17 s | 20,14 s |
| Szacunkowy koszt 12 żądań | 0,3304 USD | 0,4927 USD |

Mediana różnicy czasów w obrębie 10 par zakończonych publikacją wyniosła 5,06 s. Po ograniczeniu do 8 par, w których obie odpowiedzi były w pełni poprawne, mediana różnicy wyniosła 5,06 s. Pomiar biegnie od uruchomienia procesu do jego końca. Obejmuje pobranie wersji, wyszukiwanie, generowanie i wydanie odpowiedzi. Wiersz obejmujący wszystkie żądania uwzględnia również błędy i odmowy.

## Poprawność według pytania

| Temat | Bez bramki, w pełni poprawne / próby | Z bramką, w pełni poprawne / próby |
|---|---:|---:|
| Fineract · wyjątek przy usuwaniu starych zdarzeń | 0 z 2 | 0 z 2 |
| Fineract · pomijanie błędów zlecenia stałego | 2 z 2 | 2 z 2 |
| Fineract · domyślne ponowienia odczytu kontekstu najemcy | 2 z 2 | 2 z 2 |
| Electron · okno dla menu bez fokusu | 2 z 2 | 1 z 2 |
| Electron · wejście procesu pomocniczego | 2 z 2 | 2 z 2 |
| Electron · dane raportu awarii | 2 z 2 | 1 z 2 |

Pytania i kryteria oceny zostały ustalone przed wywołaniami. Dwaj agenci Codex, po jednym na repozytorium, porównali tekst i werdykt ze swoim wcześniej przygotowanym wzorcem z kodu. Teksty miały losowe identyfikatory, a oceniający nie znali trybu ani decyzji bramki. Sprawdzono osobno, czy cytaty publikowane przez CLI zgadzają się z plikami w Git.

## Co zmieniła bramka w otrzymanym szkicu

Bramka otrzymała 11 szkiców w 12 żądaniach. Rozpoczęła poprawę w 0 przypadkach. Tabela śledzi ten sam szkic od jego pierwszej oceny do wyniku dla użytkownika.

| Szkic przed oceną | Wynik dla użytkownika | Liczba |
|---|---|---:|
| poprawny | poprawny | 8 |
| częściowo poprawny | częściowo poprawny | 3 |

W obu powtórzeniach Fineracta Claude prawidłowo opisał obsługę wyjątku przy czyszczeniu zdarzeń. Rozszerzył jednak wynik pojedynczej metody na cały krok lub zadanie. Kod i test potwierdzają tylko, że ta metoda zwraca FINISHED. W jednej odpowiedzi Electrona prawidłowo rozpoznał obie wartości metadanych, ale dodał, że flaga uploadToServer wpływa wyłącznie na wymóg podania adresu. Implementacja natywna przekazuje tę flagę również do SetCollectStatsConsent. Wszystkie trzy szkice opublikowano w niezmienionej postaci. W podstawowym trybie błąd dotyczący całego zadania Fineracta pojawił się raz. Oba tryby generowały tekst od początku, więc różnicy między 10 a 8 w pełni poprawnymi odpowiedziami nie można przypisać działaniu bramki.

## Cztery dodatkowe próby z tymi samymi cytatami

Dla jednego pytania z każdego repozytorium przygotowano poprawny i błędny wniosek z tymi samymi autentycznymi cytatami. Recenzent nie dostał etykiety ani wzorcowej odpowiedzi. Obie poprawne wersje przeszły od razu. Bramka wskazała sprzeczność w obu błędnych wersjach. W Electronie poprawiona odpowiedź prawidłowo rozróżnia konfigurację potoków od dostępu do wejścia procesu. W Finerakcie poprawa zakończyła się statusem BLOCKED, ponieważ zabrakło wymaganego dowodu miejsca wywołania metody.

## Błędy i odmowy w zwykłym CLI

| Próba | Pytanie | Tryb | Status | Przyczyna |
|---:|---|---|---|---|
| 3 | Electron · okno dla menu bez fokusu | z bramką | ERROR | Windows odmówił przeniesienia katalogu z wynikiem wyszukiwania do miejsca publikacji. |
| 8 | Fineract · wyjątek przy usuwaniu starych zdarzeń | bez bramki | ERROR | Windows odmówił przeniesienia katalogu monitoringu do katalogu logu. |

## Zakres wniosków

Badanie dotyczy sześciu konkretnych pytań i dwóch wersji kodu. Powtórzenia służą do obserwacji zmienności na tych samych pytaniach. Własny czas Claude’a i jego wybór narzędzi mogą się zmienić między zapytaniami. Prób kontrolnych nie doliczono do trafności ani czasu zwykłych zapytań CLI.

Szacowany koszt całego testu to 0,9165 USD, w tym 0,0934 USD za cztery odrębne próby kontrolne. Wyliczenie opiera się na tokenach zgłoszonych przez API. [Cennik Anthropic](https://platform.claude.com/docs/en/about-claude/pricing).

Pełne brzmienie pytań, wzorce, przypięte wersje i zakresy w Git, kolejność, indywidualne czasy, anonimowe oceny oraz decyzje recenzenta znajdują się w [raporcie danych](../verification/qa-gate-eval-02.json).
