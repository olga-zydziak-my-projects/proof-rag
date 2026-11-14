# Zapytania o dowolny plik w korpusie Mojom

Etap 6 udostępnia przygotowanie sprawdzonego korpusu i osobne zapytania o jego
pliki. Zakres to ten sam snapshot Chromium i ta sama specyfikacja importów co
w etapie 5. Nie rozszerza to wyniku na inne języki, konfiguracje kompilacji
ani wpływ zmian na zachowanie programu.

## Przygotowanie

Uruchamiaj polecenia z katalogu projektu. Ustaw ścieżki do istniejącego Pythona
i Lean 4.35.0, na przykład:

```powershell
$py = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$lean = 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe'

& $py scripts/stage6.py prepare --cache-dir local/stage6/my-prepared-proof `
  --source-run local/stage5-v2/full-03
```

Katalog docelowy musi być nowy. Potrzebne są wcześniejszy korpus, konfiguracja
`local/corpus.json`, artefakty etapu 2 oraz zaakceptowany przebieg etapu 5.
To nie jest samowystarczalny pakiet. Nie jest potrzebne ponowne pobieranie
Chromium ani instalowanie nowych pakietów Pythona.

Przygotowanie kopiuje dokładne moduły dowodu z etapu 5, sprawdzając ich
tożsamość względem raportu utrwalonego w commicie `7cbad10`. Czyta także
rzeczywiste źródła i porównuje wszystkie bajty wyeksportowane do Lean.
Jest to ponowne użycie wcześniej przyjętego dowodu źródłowego, nie jego
świeża kompilacja. Koszt historycznego zbudowania tego dowodu pozostaje
opisany w raporcie etapu 5.

## Nowe zapytanie

```powershell
& $py scripts/stage6.py query --cache-dir local/stage6/my-prepared-proof `
  --root 'mojo/public/mojom/base/values.mojom' `
  --run-dir local/stage6/my-values-query --lean $lean
```

Wybierz dowolną dokładną ścieżkę z 1864 wybranych plików. Używaj ścieżki
repozytorium z `/` i zachowaj wielkość liter. Program nie zgaduje nazwy,
nie normalizuje ścieżki Windows i odrzuca pliki spoza wybranego uniwersum.

Pytanie zawsze znaczy: wszystkie wybrane pliki, które importują korzeń
bezpośrednio lub przez łańcuch importów, włącznie z samym korzeniem.
Liczba wyników zależy od pliku i nie jest ograniczona warunkiem 477.

Każde zapytanie ponownie sprawdza snapshot, cały przygotowany zestaw modułów
i ich niezależną kotwicę. Tworzy własny certyfikat oraz nowy plik Lean,
który kernel musi świeżo przyjąć. Niezależny audyt odczytuje rzeczywiste
literały tego pliku i porównuje pełne dane zapytania. Dowód konkretnej
odpowiedzi nie jest współdzielony między różnymi korzeniami.

W nowym katalogu zapytania znajdują się:

- `answer.json`: pełna lista, korzeń/ID, pin, zakres i tożsamości danych;
- `answer.txt`: pełna lista i metadane w postaci tekstowej;
- `query-report.json`: status, dowód wykonania, audyty aksjomatów i pomiary;
- `certificate.json`, `lean/QueryProof.lean`, `lean/QueryProof.olean` i logi.

Sukces to kod 0 oraz `STAGE6_QUERY_PASS` w raporcie. Samo istnienie certyfikatu
lub `.olean` nie wystarcza. Kod 2 oznacza odrzucenie; po niepowodzeniu nowa
odpowiedź nie jest promowana jako udana. Zachowane diagnostyczne wyniki
częściowe mają końcówkę `.failed`. Program nie nadpisuje istniejących przebiegów.

## Pełna kontrola etapu

```powershell
& $py scripts/check_stage6.py --lean $lean `
  --run-dir local/stage6/reproduce-01 `
  --report verification/stage6-reproduce-01.json
```

Polecenie przygotowuje nowy cache, świeżo dowodzi 12 różnych zapytań,
porównuje pełne wyniki z niezależnym punktem stałym, powtarza jedno zapytanie,
sprawdza deterministyczne bajty, ataki na prywatnych kopiach, błędny korzeń
przez publiczne CLI oraz pełne regresje. `STAGE6_CHECKS_PASS` oznacza przejście
tych kontroli. Końcowy `STAGE6_PASS` wymaga także niezależnego przeglądu
zgodnego z rzeczywiście uruchomionym kodem i końcowego raportu etapu.

Nie modyfikuj kodu podczas przebiegu: zmiana jest wykrywana i odrzuca wynik.
Zmiana źródeł, specyfikacji lub importowanych dowodów wymaga ponownego
ustanowienia odpowiedniej gwarancji; przeliczenie lokalnego manifestu cache
nie autoryzuje takiej zmiany.

## Granica gwarancji

Twierdzenie dotyczy `SourceBytes byte import projection v2`. Pełny parser
Mojom nadal wykonuje kontrolę operacyjną. Dowody korzystają ze standardowych
`propext`, `Classical.choice`, `Quot.sound`. Ufamy kernelowi i przypiętemu SDK
Lean, poprawności mechanizmów Git, odporności hashy na kolizje oraz opisanej
granicy IO Pythona i systemu operacyjnego. Kontrola wersji i niezmienności
pliku Lean nie jest niezależnym dowodem pochodzenia całego SDK.

Kontrole cache nie chronią przed napastnikiem kontrolującym system, pamięć
procesu weryfikatora lub niezależną kotwicę. Nie są dowodem serializacji,
renderera, całej gramatyki Mojom ani dowolnego interfejsu wyświetlania.
Przebieg zakłada prywatny, zaufany katalog wykonania bez wrogiego równoległego
zapisu do importowanych plików. Kontrole przed i po użyciu wykrywają trwałe
podmiany; nie dowodzą braku krótkiej podmiany i przywrócenia bajtów pomiędzy
kontrolami. Obsługa aktywnie wrogiego współbieżnego zapisującego wymagałaby
dodatkowej blokady zapisu lub izolowanego niezmiennego snapshotu importów.
