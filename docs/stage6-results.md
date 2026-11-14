# Etap 6 — STAGE6_PASS

Etap zakończony 11 listopada 2026. Narzędzie przyjmuje dowolny jawny korzeń
z dotychczasowego korpusu Mojom. Ponownie używa zaakceptowanego dowodu
źródło–graf i świeżo sprawdza w kernelu Lean dowód każdej nowej odpowiedzi.
Zakres, snapshot i specyfikacja źródłowa pozostały niezmienione.

Końcowy przebieg `local/stage6/full-03` zakończył się kodem 0 i statusem
`STAGE6_CHECKS_PASS`; niezależny przegląd uzyskał `PASS`. Razem zamykają
wymagania [kontraktu](stage6-contract.md) i dają `STAGE6_PASS`.

- [Końcowa ocena etapu](../verification/stage6-final.json).
- [Pełny przebieg i pomiary](../verification/stage6-checks-03.json).
- [Niezależny przegląd](stage6-review.md) oraz [jego tożsamości plików](../verification/stage6-review-final.json).
- [Instrukcja przygotowania i zapytań](stage6-usage.md).
- [Niezależne pełne oczekiwane listy](../verification/stage6-query-selection.json).

## Co się zmieniło

Ukończony etap 5 zapisano przed pracą w lokalnym commicie
`7cbad10af87dc97bae4b23603921441aa899f7b0`. Zachowano 149 śledzonych plików
oraz historię etapów 3–5. Nowe moduły,
testy i dokumenty są dodatkami; istniejących plików etapu 5 nie zmieniano.
Nie wykonano push ani zmian globalnej konfiguracji Git. Zmiany etapu 6
pozostają w katalogu roboczym; HEAD wskazuje checkpoint etapu 5.
Historyczna lista etapu 5 zawierała także `docs.zip`, `scripts.zip`, `src.zip`
i `tests.zip`. Nie ma ich pod tymi ścieżkami w końcowym katalogu. Początkowy
inwentarz etapu 6 obejmował pliki śledzone, więc nie ustala chwili zniknięcia
archiwów; nie deklarujemy ich zachowania ani przyczyny braku. Źródła projektu
i dowody wymagane do wykonania etapu są dostępne i sprawdzone.

`scripts/stage6.py prepare` tworzy nowy przygotowany zestaw z 41 modułów
przebiegu etapu 5. Oczekiwane tożsamości odczytuje z raportu utrwalonego
w powyższym commicie, z wyłączonymi Git replacement overlays. Sprawdza
rzeczywisty snapshot, zachowany kod ekstrakcji/specyfikację i pełne bajty
wyeksportowane do Lean. Manifest cache nie wybiera własnej kotwicy.

`scripts/stage6.py query` przyjmuje dokładną ścieżkę `--root`. Ponownie
sprawdza źródła i cache, tworzy certyfikat dla tego korzenia, generuje
`QueryProof.lean`, niezależnie odczytuje jego rzeczywiste dane, a następnie
uruchamia nowy proces Lean. Po przyjęciu dowodu zapisuje pełne JSON i tekst,
ponownie sprawdza ich treść i dopiero wtedy kończy sukcesem.

Każdy katalog zapytania jest nowy. Błędny korzeń daje kod 2. Awaria dowodu
lub zapisu raportu nie pozostawia nowej odpowiedzi oznaczonej jako udana;
częściowe odpowiedzi są wycofywane do nazw `.failed`. Ten przypadek ma
osobny test z wymuszonym błędem końcowego zapisu raportu.

## Gwarancja formalna

`ChromiumSource.source_bound` nie zależy od korzenia. Nowy moduł odnosi się
do dokładnie tego samego `ChromiumFast.graph` i mapowania `SourceNames`.
Dla każdego korzenia kernel przyjmuje świeże:

- `QueryProof.accepted` i `erased_accepted`;
- `answer_checked` i `paths_unique`;
- `source_to_answer`, przez istniejące `AnswerBinding.source_to_answer`.

Pełna lista to `resultIDs.map SourceNames.names`. Sprawdzane są wszyscy
świadkowie, rzeczywiste wskazania krawędzi, domknięcie całego grafu oraz
zgodność członkostwa listy i certyfikatu. Nie występuje warunek 477 dla
nowych zapytań. Niezależny audyt sprawdza pełne tabele, typy, korzeń,
sekwencję ID, dekodowanie, importy i sygnatury twierdzeń, także ich możliwe
osłabienie przez dodatkowe przesłanki lub zmianę rozwiązywania nazw.

Audyty czterech jawnie drukowanych twierdzeń każdego zapytania zawierają
wyłącznie dopuszczone `propext`, `Classical.choice`, `Quot.sound`. Nie dodano
nowych aksjomatów ani `sorry`, `admit`, `native_decide` czy obejścia VM.
Nie nazywamy wyniku wolnym od aksjomatów.

Warstwa źródłowa jest **ponownie użytym dowodem etapu 5**, nie świeżą
kompilacją źródeł. Każdy dowód nowego zapytania jest świeży. Zaakceptowane
`.olean` cache są sprawdzane względem niezależnego commita przed i po użyciu.
Nie ma tu dowodu pełnego parsera Mojom, serializacji, Git ani systemu IO;
formalna relacja pozostaje `SourceBytes byte import projection v2`.

## Rzeczywiste zapytania i pomiary

Korpus nadal zawiera 1864 węzły, 4419 krawędzi i 213 izolowanych węzłów.
Wynik obejmuje korzeń. Pełne oczekiwane listy policzył osobny skrypt przez
punkt stały, bez importowania generatora, checkera ani eksportera projektu.
Policzył też rozmiary odpowiedzi dla wszystkich 1864 korzeni. Kernelowo
sprawdzono poniższych 12 reprezentantów, a nie wszystkie 1864 zapytania.

| Korzeń | Wyniki | Całe zapytanie | Wywołanie nowego procesu dowodowego |
| --- | ---: | ---: | ---: |
| `mojo/public/mojom/base/time.mojom` | 477 | 73,295 s | 49,347 s |
| `android_webview/common/mojom/renderer.mojom` | 1 | 28,241 s | 6,488 s |
| `android_webview/common/mojom/frame.mojom` | 1 | 28,385 s | 6,423 s |
| `ash/public/mojom/accelerator_configuration.mojom` | 2 | 29,409 s | 6,397 s |
| `ash/style/mojom/color_scheme.mojom` | 2 | 28,140 s | 6,573 s |
| `ash/public/mojom/accelerator_actions.mojom` | 5 | 29,374 s | 6,935 s |
| `cc/mojom/render_frame_metadata.mojom` | 10 | 28,729 s | 7,042 s |
| `chromeos/ash/experiences/arc/mojom/gfx.mojom` | 20 | 30,402 s | 7,469 s |
| `third_party/blink/public/mojom/blob/serialized_blob.mojom` | 50 | 30,596 s | 8,996 s |
| `url/mojom/scheme_host_port.mojom` | 100 | 33,343 s | 11,114 s |
| `mojo/public/mojom/base/values.mojom` | 240 | 42,167 s | 20,961 s |
| `mojo/public/mojom/base/unguessable_token.mojom` | 423 | 59,708 s | 36,988 s |

Mediana całego zapytania wyniosła **29,906 s**, zakres **28,140–73,295 s**.
To po jednej obserwacji na różny korzeń, nie stabilny benchmark ani gwarancja
opóźnienia. Każde zapytanie ponownie wykonuje kontrolę źródeł i pełny parser.
Czas wywołania procesu dowodowego zawiera importy, elaborację, kernel oraz
obsługę procesu/logów; nie jest samym czasem redukcji kernela.

Przygotowanie: **17,585 s** na snapshot i parser oraz **4,122 s** na
uwierzytelnienie, skopiowanie i audyt wcześniejszego dowodu. To razem około
21,707 s; nie obejmuje historycznego kosztu stworzenia dowodu źródłowego.
85 plików payloadu cache zajmuje **617 408 631 B**, poza małym manifestem.
Źródła 12 nowych modułów zajmują łącznie **1 897 902 B**, ich `.olean`
**23 924 936 B**; `.olean` zawierają dane, kod i dowody.

Najwyższe natywne szczyty pojedynczego nowego procesu Lean:
`PeakWorkingSetSize` **4 095 283 200 B** (rezydentna pamięć) i
`PeakPagefileUsage` **5 920 841 728 B** (commit procesu, nie zapis na dysk).
Żądany interwał oczekiwania wynosi 20 ms; scheduler może go wydłużyć.
Odczyt po zakończeniu z otwartym uchwytem powiódł się dla każdego procesu,
więc natywne liczniki obejmują całe życie tych procesów. Nie obejmują dzieci.

Cały końcowy driver trwał **682,166 s**: przygotowanie, 12 zapytań, powtórzenie,
ataki, negatywne CLI i regresje. Zegar nie obejmuje startu/importów Pythona,
końcowego zapisu raportu, niezależnego przeglądu ani redakcji dokumentów.
Nie wyliczamy speedupu względem około 27 minut etapu 5, który świeżo budował
źródłową warstwę dowodową i wykonywał inny zestaw obowiązków.

## Powtarzalność, ataki i regresje

Drugie świeże zapytanie o `accelerator_configuration.mojom` dało identyczne
pełne bajty `certificate.json`, `QueryProof.lean`, `answer.json` i `answer.txt`.
Dodatkowe końcowe uruchomienie publicznego CLI o `color_scheme.mojom`
zwróciło dwie ścieżki w **28,541 s**; jego cztery kanoniczne artefakty są
identyczne z odpowiednim zapytaniem pełnego przebiegu.

Wykonano **28 odrzuconych podmian na rzeczywistych danych**, m.in. zamianę
certyfikatu, dowodu i odpowiedzi między korzeniami o tej samej liczebności,
brak/duplikat/zamianę ścieżki, błędny korzeń i typ metadanych, zmianę commita,
podmianę cache z przeliczeniem własnych hashy oraz dodanie modułu mogącego
przesłonić import. Prywatna kopia cache służyła do mutacji; baza pozostała
niezmieniona. Są to odrzucenia na granicy IO/checkera/audytu, nie twierdzenie,
że kernel odrzucił każdą z tych podmian.

Pełny zestaw: **115 testów, 114 zaliczonych i 1 pominięty**. System odmówił
utworzenia fizycznego symlinka/junction w teście; oddzielny test odrzucenia
atrybutu reparse point przeszedł. Zachowano 85 wcześniejszych testów i
**1547 porównań Python–Lean**. Ten test przechwytuje wyjście Lean wewnętrznie;
liczba wynika z zachowanego kodu: 512 × 3 + 9 + 2. Rzeczywisty graf nie ma
cykli; cykle pozostają pokryte testami syntetycznymi. Zgodność programów
jest dowodem testowym, nie formalnym twierdzeniem ich równoważności.

`full-01` zachowano jako nieudany przebieg: brak katalogu pomocniczego logu
Lean, zero zaakceptowanych zapytań. Wczesne `cli-smoke-01` odrzuciło ścieżkę
pakietu Lean; jawny `--root` i prywatny katalog procesu rozwiązały problem.
`full-02` zachowano jako nieudane końcowe raportowanie: wszystkie jego
dowody i 113 testów przeszły, ale driver błędnie oczekiwał napisu `1547`
w logu unittest. Dodano dwa testy raportowania i wykonano pełny `full-03`.
Tylko `full-03` jest końcowym zaakceptowanym przebiegiem kontroli etapu.

## Granice i dalsze użycie

Pozostaje jeden przypięty korpus i jedna specyfikacja zależności. Nie ma
integracji LLM, nowych języków ani analizy zachowania programu. Reguły
komentarzy, napisów, atrybutów i importów poza zakresem są takie jak w etapie 5.

Ufamy wskazanemu SDK/kernelowi Lean, standardowym aksjomatom, kotwicy Git,
odporności hashy i opisanej warstwie IO. Katalog wykonania jest prywatny
i nie jest wrogo modyfikowany podczas odczytów. Kontrole przed/po wykrywają
trwałe podmiany, ale nie dowodzą braku krótkiej podmiany i przywrócenia
bajtów pomiędzy kontrolami. Wrogi współbieżny zapis wymagałby dalszej izolacji
lub blokad plików. Uczciwie odróżniamy te założenia od twierdzeń Lean.

Polecenia do pojedynczych zapytań i pełnego odtworzenia są w
[instrukcji etapu 6](stage6-usage.md). Pełny wynik przykładowego nowego
zapytania: [values.mojom — 240 ścieżek](../local/stage6/full-03/query-deep/answer.json).
