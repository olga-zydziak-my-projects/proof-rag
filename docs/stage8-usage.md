# Użycie etapu 8 w PowerShell

Zwykły projekt i etap 7 nie wymagają nowych bibliotek. Opcjonalne zależności:
DuckDB 2.0.0, PyArrow 26.0.1, NumPy 2.5.4, psutil 7.2.2. Użyto Python 3.12.14
oraz Git 2.55.0.windows.2.
Nie zmieniano pyproject.toml ani .gitignore.

```powershell
$py = 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$lean = 'C:\Users\User\Documents\Codex\2026-11-08\nie\work\toolchains\lean-4.35.0-windows\bin\lean.exe'
& $py -m pip install --target local/stage8-deps -r requirements-stage8.txt
$env:PYTHONPATH = "src;local/stage8-deps"
& $py -m unittest discover -s tests -p test_stage8.py -v
```

Klucze API i SDK Anthropic nie są potrzebne. Nie uruchamiaj ponownie płatnej
oceny etapu 7. Nowe testy są offline; integracja poniżej tworzy jawnie
syntetyczne lokalne repozytoria, a nie zastępuje zablokowanego pilota.

Pełny zestaw niezależnych części, w nowym katalogu i z nowym raportem:

```powershell
& $py scripts/check_stage8.py --run-dir local/stage8/reproduce-new `
  --report verification/stage8-reproduce-new.json --lean $lean
```

Obejmuje dziewięć benchmarków, kontrolowane TIMEOUT/RESOURCE_LIMIT,
przygotowanie źródłowego fixture i pięć zapytań (w tym powtórzenie), trzy
świeże dowody grafowe Lean oraz historyczne regresje. Nie korzysta z sieci.
Status końcowy pozostaje CORPUS_BLOCKED, jeżeli niezależne części przejdą;
kod 0 tego narzędzia oznacza zaliczenie **niezależnych części**, nie STAGE8_PASS.

Duże benchmarki zawsze uruchamiaj przez supervisor:

```powershell
& $py scripts/stage8_supervise.py `
  --config verification/stage8-benchmark-config.json --run-dir local/stage8/one-new `
  -- $py scripts/stage8.py benchmark --nodes 1000000 --family modular `
  --run-dir local/stage8/one-new/work
```

Sam subcommand `benchmark` jest workerem i nie wymusza limitu całego drzewa;
kanoniczne pomiary wymagają wrappera. `resource-report.json` zawiera czas,
RSS/private, dysk, limit i rzeczywisty odstęp próbek; `work/benchmark.json`
zawiera fazy, trzy próbki wyszukiwania na korzeń, medianę i zakres, cały poziom
weryfikacji i tożsamości artefaktów. Certyfikaty i pełne odpowiedzi są w Parquet.

Źródłowe CLI wymaga manifestu `stage8-corpus-v1`, jego **niezależnie zaufanego**
SHA-256 i mapy lokalizacji `[{repo_id,commit,directory}, ...]`:

```powershell
& $py scripts/stage8.py prepare --manifest $manifest --manifest-sha256 $trustedHash `
  --locations $locations --run-dir local/stage8/my-index
& $py scripts/stage8.py query --manifest $manifest --manifest-sha256 $trustedHash `
  --locations $locations --index-dir local/stage8/my-index `
  --repo-id $repo --commit $commit --path 'local/shared.mojom' `
  --run-dir local/stage8/my-query
```

Realny manifest wyboru `verification/stage8-corpus.json` jest **raportem blokady**,
nie gotowym korpusem do prepare. Przykładowy działający manifest źródłowy znajduje
się po checku w `local/stage8/final-02/synthetic-source-fixture/manifest.json`;
jest jednoznacznie oznaczony `synthetic-fixture`. Odpowiedź źródłowego CLI ma
`formally_verified=false` i poziom GRAPH_PASS_WITH_PYTHON_SOURCE_IO.
Nowy korpus nie ma formalnego dowodu źródło–odpowiedź.

Opcjonalny, osobno zamrożony eksperyment Soufflé:

```powershell
& $py examples/stage8-souffle/reproduce.py local/stage8/souffle-new
```

Wymaga WSL Ubuntu-24.04, `/usr/bin/time`, timeout i lokalnego programu
`local/stage8/souffle-tool/extracted/usr/bin/souffle`. Użyto oficjalnego
[pakietu 2.5](https://github.com/souffle-lang/souffle/releases/tag/2.5)
`x86_64-ubuntu-2404-souffle-2.5-Linux.deb`, porównanego z SHA-512 z tego samego
wydania. `dpkg-deb -x` wyłącznie rozpakował go lokalnie; nie instalował pakietu
ani skryptów systemowych. WSL interpreter działa z jednym wątkiem, limitem
adresowym 1 GiB, CPU 60 s i wall 65 s. Fakty i program są identyczne dla obu
wariantów, wyniki pełne; profiler zachowuje osobno loadtime/runtime/savetime.

Nie kontrolujemy cache OS. Wersjonowane raporty są zwięzłe; duże źródła, bazy,
certyfikaty i pełne logi pozostają w ignorowanym `local/`. Dotychczasowe dane
Chromium potrzebne do regresji są takie same jak w etapach 5–7.
