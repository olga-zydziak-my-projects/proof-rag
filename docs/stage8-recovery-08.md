# Domknięcie walidacji etapu 8, próby 07 i 08

**STAGE8_INCOMPLETE**. Jedna obowiązkowa kontrola pozostaje niezaliczona, historyczny test różnicowy Lean z limitem 600 s. [Pełny przebieg 06](stage8-run-06.md) zachowuje 179 zaliczonych wyników i jeden timeout w zbiorze 180 aktualnych testów. Dokładny zbiór kwalifikowanych identyfikatorów został ponownie wyprowadzony z bieżącego kodu i porównany z pełnym logiem, z obsługą dwóch wyników przeplatanych komunikatami Fetching.

## Próby odzyskania

| Próba | Zakres | Profil CPU | Limit testu | Wynik | Pozostałe procesy zadania |
| --- | --- | --- | ---: | --- | ---: |
| 06 | Pełne 180 testów | Standardowy | 600 s | 179 PASS i 1 timeout | 0 |
| 07 | Tylko niezaliczony test | Standardowy | 600 s | Timeout | 0 |
| 08 | Tylko niezaliczony test | 4 logiczne CPU i AboveNormal | 600 s | Timeout | 0 |

Powtórki zachowały identyczny kod silnika i testów, identyczną kopię z historycznym README oraz oryginalny test_lean_export.py z bazowego commitu. Limit pamięci wynosił 6 GiB, limit nadzorcy pojedynczej powtórki 660 s. Profil 08 został zapisany przed wykonaniem. Natywny Job Object narzucił maskę 0x55 dla procesorów 0/2/4/6 oraz klasę 0x8000. Krótki proces i jego potomek potwierdzili dziedziczenie, a obserwacja uruchomionego Lean potwierdziła ten sam profil. Znaczenie pól opisuje [dokumentacja Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information).

Dodatkowy sterownik eksperymentu ma osobny hash i niezależny przegląd. Jego działanie obejmuje konfigurację własnego Job Object przed utworzeniem procesu. Kod src/scripts/tests/formal zachowuje tożsamość z zamrożeniem 08. Aktualna ścieżka i hash obrazu Lean zostały związane z narzędziem użytym do sześciu dowodów źródłowych.

## Końcowy audyt

[Przegląd końcowy 08](../verification/stage8-final-review-08.json) zachowuje dokładnie jedną blokującą uwagę dotyczącą regresji. Ponownie sprawdzono pełne inwentarze artefaktów, kotwice wejściowe, surowe bajty 78 historycznych plików, kod i README kopii regresyjnej oraz źródła wszystkich 18 plików. Semantyczny audyt sześciu dowodów i 27 odpowiedzi grafowych z przebiegu 06 został wykorzystany po potwierdzeniu niezmienności wszystkich artefaktów.

Sześć pełnych dowodów źródło–odpowiedź pozostaje ważnych. Każda odpowiedź przekracza granice repozytoriów. Największy nowy korpus źródłowy obejmuje 18 rzeczywistych plików, 42 268 bajtów i 19 krawędzi. Największy nowy graf z zaakceptowanym dowodem Lean ma 1000 węzłów. Próba 10 000 rzeczywiście osiągnęła limit 4 GiB. Największy graf sprawdzony w Pythonie ma milion węzłów i 1 012 499 krawędzi. Pomiar indeksowania objął również 10 000 syntetycznych źródeł Git.

Bieżący stan wszystkich bramek i granice weryfikacji zawiera [raport zbiorczy 08](../verification/stage8-status-08.json). Historyczne 179 zaliczonych testów z przebiegu 05 pozostaje wynikiem ówczesnego kodu. Warunkiem przyznania STAGE8_PASS pozostaje zaliczenie pełnej regresji bieżącego zamrożenia.

## Artefakty i odtworzenie

- [Powtórka 07](../verification/stage8-regression-retry-07.json).
- [Powtórka 08](../verification/stage8-regression-retry-08.json).
- [Jawny profil 08](../verification/stage8-regression-retry-08-config.json).
- [Sterownik profilu](../verification/stage8-retry-08-driver.py).
- [Tożsamość rzeczywistego narzędzia](../verification/stage8-regression-retry-08-tool-identity.json).
- [Końcowe sprawdzenie źródeł i niezmienności](../verification/stage8-handoff-check-08.json).

Pełne polecenie ponowienia znajduje się w [raporcie 06](stage8-run-06.md). Wybierz nowy katalog i nowy plik raportu. Domyślna kontrola zwraca sukces dopiero dla całego etapu. Dalsze zamknięcie wymaga zaliczenia testu różnicowego w zachowanym budżecie 600 s.
