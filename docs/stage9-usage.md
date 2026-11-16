# Odtwarzanie i publiczne CLI etapu 9

Wymagane są natywne Windows Python 3.12.14, Git 2.55.0.windows.2, Lean 4.35.0
i istniejące przypięte zależności `requirements-stage8.txt` w `local/stage8-deps`.
Nie dodano zależności. API modeli i klucze nie są potrzebne.

Zwykły klon nie zawiera ignorowanych obiektów Git ani toolchain i historycznych
artefaktów etapu 8 wymaganych do sprawdzenia zgodności pinów/poprawek. Odtwarzanie
samego czystego klonu **nie zostało sprawdzone**. Polecenia poniżej wymagają tych
lokalnych danych; ich brak kończy się błędem. Rekonstrukcję starego korpusu
opisuje `stage8-connected-corpus.md`. Wszystkie nowe duże artefakty są w `local/stage9`.

```powershell
$py = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$lean = 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe'
$env:PYTHONPATH = 'src;local/stage8-deps;scripts'
$env:GIT_NO_LAZY_FETCH = '1'
$manifest = 'verification/stage9-manifest.json'
# Ta kotwica pochodzi z zamrożenia i niezależnego przeglądu, poza proof cache.
$trustedManifest = '49e019318b6ca51cd70806f5816a06616dfcd3693337f564a5431018ad652299'
$locations = 'local/stage9/acquire-03/data/locations.json'
```

Pozyskanie brakujących źródeł z oficjalnych serwerów, maksymalnie cztery odczyty
HTTP, po sprawdzeniu obciążenia hosta:

```powershell
& $py -B scripts/stage8_supervise.py --config verification/stage9-config.json `
  --run-dir local/stage9/acquire-new/process --artifact-root local/stage9/acquire-new `
  -- $py -B scripts/stage9_recon.py --run-dir local/stage9/acquire-new/data `
  --reuse local/stage9/acquire-03/data
```

`--reuse` jest opcjonalne i kopiuje cache/obiekty bez modyfikowania oryginału.
Wybrane moduły i piny są stałe. Rekonstrukcja drzew i blobów sprawdza Git IDs.
`stage9_freeze.py` tworzy manifest i deterministyczne korzenie przed pomiarami;
nie uruchamiaj go w istniejącym katalogu przebiegu ani w celu zmiany korzeni po błędzie.

Przygotowanie całej warstwy źródeł (bez cache dowodu), automatycznie pod nadzorem:

```powershell
$prepared = 'local/stage9/user-prepare-new/work'
& $py -B scripts/stage9.py prepare --manifest $manifest --manifest-sha256 $trustedManifest `
  --locations $locations --lean $lean --run-dir $prepared
if ($LASTEXITCODE -ne 0) { throw 'Przygotowanie nie zostało przyjęte' }
# Zachowaj tę kotwicę po własnym rzeczywistym, udanym wykonaniu; nie wyliczaj jej
# ponownie z nieufnego/podmienionego cache zamiast weryfikacji poprzedniej kotwicy.
$trustedPreparation = (Get-FileHash "$prepared/prepare.json" -Algorithm SHA256).Hash.ToLower()
```

Zapytanie o pełną tożsamość. Katalog musi być nowy:

```powershell
& $py -B scripts/stage9.py query --manifest $manifest --manifest-sha256 $trustedManifest `
  --locations $locations --lean $lean --prepared-dir $prepared --prepared-sha256 $trustedPreparation `
  --repo-id chromium --context upstream --commit 3927f129b801f969d4abdb1458d55174cc062723 `
  --path url/mojom/url.mojom --run-dir local/stage9/user-query-new/work
if ($LASTEXITCODE -ne 0) { throw 'Zapytanie nie zostało przyjęte; nie odczytuj wcześniejszego wyniku' }
Get-Content local/stage9/user-query-new/work/answer.json -Raw
```

Pełna lista jest w `answer.json` dopiero po świeżych dowodach QueryGraph/QueryAnswer,
pełnym ponownym sprawdzeniu źródeł/cache i `PROCESS_PASS` nadzorcy z zerem potomków.
Worker zapisuje kandydatów z `formally_verified=false`. Błąd/timeout/limit nie
publikuje zweryfikowanej odpowiedzi. `query.json`, logi i receipt wskazują przyczynę.
Wewnętrzne `--worker` nie jest ścieżką wydającą zaakceptowaną odpowiedź.

Każdy przebieg ma osobny katalog nadrzędny (`.../user-query-new/`): limit 20 GiB
obejmuje work, control, eksporty, moduły, logi, bazy, odpowiedzi i pliki tymczasowe.
Wejściowe repozytoria, wcześniejsze dowody i koordynator są poza tym pomiarem.
Pomiar pamięci obejmuje nadzorcę i procesy Job Object; współdzielone RSS mogą
być policzone wielokrotnie. Profil Normal i wszystkie logiczne CPU są zachowane.

Trzy powtórzenia sześciu zamrożonych korzeni oraz pełna regresja:

```powershell
& $py -B scripts/stage9_run.py queries --prepared-dir $prepared --prepared-sha256 $trustedPreparation --lean $lean `
  --locations $locations --run-dir local/stage9/queries-new
# View powstaje przed procesem unittest. Nowy proces odczyta TEMP/TMP dopiero,
# gdy katalog już istnieje; dzięki temu także fixture testów obejmuje limit dysku.
$env:TEMP = [IO.Path]::GetFullPath('local/stage9/regression-new/view')
$env:TMP = $env:TEMP
& $py -B scripts/stage9_run.py regression --lean $lean --run-dir local/stage9/regression-new
& $py -B scripts/stage9_run.py status --prepared-dir $prepared --prepared-sha256 $trustedPreparation --lean $lean `
  --locations $locations --candidate
```

Końcowy status wymaga niezależnego przeglądu dokładnego dossier kandydata,
potem ponownego `status` bez `--candidate`. Historyczne wyniki 18 plików,
1000 syntetycznych węzłów Lean, miliona węzłów Python oraz 1864 plików Chromium
pozostają odrębnymi gwarancjami. Bieżące wykonanie opisuje `stage9-results.md`.
Ustawienia TEMP/TMP powyżej dotyczą procesu PowerShell używanego do regresji;
po wykonaniu przywróć poprzednie wartości albo zakończ tę powłokę.

Dokładne małe sterowniki pomiarów pomocniczych są wersjonowane w
`verification/stage9-control-tools/`. Ich bajty odpowiadają wykonanym lokalnym
kopiom wskazanym w raportach `profiler_code_path` i `profiler_code_sha256`.
`profile_sources.py` rozdziela IO/projekcję/indeks, `profile_search.py` mierzy
czysty BFS, a `profile_publication.py` profiluje koordynator osobnego rzeczywistego
query. Wymagają lokalnych danych i wyników przebiegów wskazanych w ich kodzie.
Pierwsze dwa uruchamiano przez `stage8_supervise.py`, odpowiednio pod profilem
przygotowania i zapytania; trzeci wywołuje publiczny CLI z jego nadzorcą.
