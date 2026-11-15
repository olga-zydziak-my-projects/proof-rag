# Użycie etapu 7

Wymagane są Python 3.10+, Git, Lean 4.35.0 oraz wszystkie lokalne dane etapu 6:
oryginalny korpus i jego metadane Git, `local/corpus.json`, ekstrakcja
`local/stage2`, zakotwiczony przebieg `local/stage5-v2/full-03` i przygotowany
cache etapu 6. Zwykły klon nie zawiera tych lokalnych danych.

Zainstaluj sprawdzony SDK do swojego środowiska Python:

```powershell
& $py -m pip install -r requirements-stage7.txt
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
```

Użyto `anthropic==2.8.0`. W lokalnej walidacji pakiety zainstalowano opcjonalnie
przez `--target local/stage7-deps` i dodano ten katalog do `PYTHONPATH`.
Dotychczasowe funkcje nie importują SDK i nie wymagają klucza.

Klucz aplikacja czyta wyłącznie ze środowiska procesu `ANTHROPIC_API_KEY`.
Po zapisaniu zmiennej użytkownika Windows uruchom nowy terminal lub przekaż
ją do bieżącego procesu, bez wypisywania wartości:

```powershell
if (-not $env:ANTHROPIC_API_KEY) {
  $env:ANTHROPIC_API_KEY = [Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY', 'User')
}
[bool]$env:ANTHROPIC_API_KEY
```

Przygotowanie cache opisuje instrukcja etapu 6. Każdy katalog przebiegu musi być nowy.

```powershell
& $py scripts/stage7.py `
  --question 'Które pliki importują mojo/public/mojom/base/time.mojom bezpośrednio lub pośrednio?' `
  --model claude-haiku-5-5 --effort medium `
  --cache-dir local/stage6/my-prepared-proof `
  --run-dir local/stage7/my-time-query --lean $lean
```

`report.json` zawiera decyzję i status. `api.json` zachowuje odpowiedź API,
zużycie tokenów, model, effort, wersję promptu, SDK i czas. Katalog `stage6/`
zawiera pełne artefakty dowodowe. `answer.txt` etapu 7 powstaje dopiero po
akceptacji i zawiera pełną listę. Nie wysyłaj do API pytań z sekretami.

Przy `needs_clarification` wybierz spośród `candidates` i uruchom nowe pytanie
z pełną ścieżką. `not_found` nie uruchamia dowodu. `unsupported` oznacza zakres
poza kontraktem. Błędy i brak zweryfikowanego wyniku zwracają kod 2;
`STAGE7_QUERY_PASS` zwraca kod 0. Status pojedynczego zapytania nie jest
globalnym statusem akceptacji etapu.

```powershell
& $py -m unittest discover -s tests -p test_stage7.py -v
& $py scripts/evaluate_stage7.py `
  --cache-dir local/stage6/my-prepared-proof `
  --run-dir local/stage7/my-live-evaluation --lean $lean
```

Ocena zapisuje `evaluation.json` po każdym przypadku, zatrzymuje serię przy
braku dostępu/autoryzacji modelu i wykorzystuje odpowiedzi tej samej oceny
do trzech pełnych przebiegów bez dodatkowych wywołań API. Interpretacja,
pytanie, plan oraz dowód zachowują wspólne identyfikatory przypadków.

Końcowa kontrola bieżącego eksperymentu używa zapisanych 32 odpowiedzi,
ośmiu dodatkowych, wcześniej zamrożonych pytań, trzech nowych dowodów
i pełnej regresji. To jawny replay po poprawce lokalnego resolvera;
nie nowa niezależna ocena Claude na 32 pytaniach. Oryginalne wyniki pozostają
zachowane. Łączny budżet obu części wynosi 40 żądań, bez ponowień.

```powershell
& $py scripts/check_stage7.py `
  --evaluation local/stage7/my-live-evaluation/evaluation.json `
  --cache-dir local/stage6/my-prepared-proof `
  --run-dir local/stage7/my-final-checks --lean $lean `
  --report verification/stage7-my-final-checks.json
```

Nie uruchamiaj ponownie części online w ramach wyczerpanego budżetu
tego samego eksperymentu. Nowy eksperyment wymaga osobnego zestawu i budżetu.

Konfigurację API sprawdzono w oficjalnej dokumentacji Anthropic:
[structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs),
[effort](https://platform.claude.com/docs/en/build-with-claude/effort),
[Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview).
Używamy `messages.create`, `output_config.format` z `type=json_schema`
i `output_config.effort`. Bloki czytamy według typu, nie pozycji.
