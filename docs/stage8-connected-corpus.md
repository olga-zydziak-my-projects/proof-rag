# Przypięty korpus trzech projektów

Przyjęty zakres zawiera 18 rzeczywistych plików Mojom, 42 268 bajtów źródeł
i 19 unikalnych krawędzi. Dwa pełne cele GN Electron i pełny cel Mojom AI Chat
Brave korzystają z tego samego commitu Chromium. Zakres zamrożono przed
wyborem korzeni zapytań. Wyniki dowodów i końcowych pomiarów są raportowane
oddzielnie przez runner etapu 8.

| Projekt | Wydanie | Commit | Pliki Mojom |
| --- | --- | --- | ---: |
| Electron | v38.1.2 | `d60ae179985685d75d238ee33e17c15a7b53d703` | 2 |
| Brave Core | v1.82.166 | `38bf45887ca5336841cddb4200e6deee32ce45a8` | 6 |
| Chromium | 140.0.7339.133 | `3927f129b801f969d4abdb1458d55174cc062723` | 10 |

Electron DEPS przypina Chromium 140.0.7339.133. Brave package.json przypina
ten sam tag w `brave/chromium`. Przypięte odpowiedzi metadanych potwierdzają,
że mirror Brave i oficjalne Chromium mają identyczny commit i drzewo
`9126a9192eb20fda7cc2e0f5a6b5163dfae53b4b`. Oryginalny obiekt commitu oraz
`chrome/VERSION` są dodatkowo sprawdzane lokalnie. Mirror ustanawia tożsamość
zależności Brave. Trzema projektami korpusu są Electron, Brave Core i Chromium.

## Zamrożony zakres

Przyjęto wszystkie źródła dwóch zadeklarowanych celów GN Electron
`//electron/shell/common:plugin` i
`//electron/shell/common:web_contents_utility`. Są to odpowiednio
`shell/common/plugin.mojom` i `shell/common/web_contents_utility.mojom`.
W Brave przyjęto cały katalog `components/ai_chat/core/common/mojom/`
oraz wszystkie sześć źródeł celu `mojom_component("mojom")` z jego BUILD.gn.
Następnie algorytm domknięcia dołącza każdy wymagany import, aż nie pozostanie
żaden brakujący cel. Wszystkie importy przyjętego zakresu mają cele wewnętrzne.

Chromium obejmuje `content/public/common/webplugininfo.mojom`,
`mojo/public/mojom/base/{big_buffer,string16,time,unguessable_token,values}.mojom`,
`third_party/blink/public/mojom/permissions/permission_status.mojom`,
`third_party/blink/public/mojom/tokens/tokens.mojom`
oraz `url/mojom/{origin,url}.mojom`.

Przykładowe połączenia są odczytane z pełnych oryginalnych blobów Git.

| Importer | Deklarowany import | Cel |
| --- | --- | --- |
| Electron `shell/common/plugin.mojom` | `content/public/common/webplugininfo.mojom` | Chromium, ten sam literalny plik |
| Electron `shell/common/plugin.mojom` | `url/mojom/url.mojom` | Chromium, ten sam literalny plik |
| Electron `shell/common/web_contents_utility.mojom` | `url/mojom/origin.mojom` | Chromium, ten sam literalny plik |
| Brave `components/ai_chat/core/common/mojom/ai_chat.mojom` | `mojo/public/mojom/base/time.mojom` | Chromium, ten sam literalny plik |
| Brave `components/ai_chat/core/common/mojom/ai_chat.mojom` | `url/mojom/url.mojom` | Chromium, ten sam literalny plik |
| Brave `components/ai_chat/core/common/mojom/settings_helper.mojom` | `brave/components/ai_chat/core/common/mojom/ai_chat.mojom` | Brave, usunięty prefiks montowania `brave/` |

Pełne commity, ścieżki, blob IDs, SHA-256, reguły i konfiguracje zawiera
[manifest korpusu](../verification/stage8-connected-corpus-manifest-04.json).
Jego kotwica wynosi
`ca113f50946345eacd8905d48fb2367dd0a95886bbb72631d4ec6cb344d204e1`.
Ten wariant ma jawne zakończenia LF, zgodne z atrybutami Git. Poprzedni
wariant roboczy oraz raporty wcześniejszych prób pozostają zachowane.

## Poprawki i nakładki

Audyt obejmuje kompletny przypięty inwentarz `patches/` obu projektów,
225 plików `.patch` Electron i 644 Brave, oraz cały inwentarz
`chromium_src/` Brave liczący 2780 wpisów. Kompletność każdego poddrzewa
jest sprawdzana przez odtworzenie binarnej postaci wszystkich drzew Git
i porównanie ich identyfikatorów z oryginalnym commitem. Każdy pobrany
plik poprawki musi mieć oryginalny Git blob ID.

Ścieżki zmieniane przez poprawki są ustalane ze wszystkich nagłówków
`diff --git`, z uwzględnieniem starej i nowej ścieżki oraz mapowania
podrepozytorium. Mapowanie Electron pochodzi z `patches/config.json`.
W Brave zachowano sterowniki `util.js`, `gitPatcher.js`, `applyPatches.js`
i synchronizacji. Audyt obejmuje także przechowywaną poprawkę TFLite,
której przypięty `util.js` nie aktywuje. Sprawdzenie nakładek obejmuje
efektywne ścieżki Chromium oraz `electron/` i `brave/` importerów.

Żaden z 18 przyjętych plików nie jest zmieniany przez te poprawki lub
nakładki. Przypięty parser Brave dodaje zmiany AST dla odpowiadającego
ścieżką pliku `chromium_src/`. Pełny inwentarz wyklucza taką nakładkę dla
każdego przyjętego pliku. Dzięki temu oryginalne bajty przyjętych źródeł
odpowiadają obu analizowanym kontekstom.

Pierwszy zbadany zakres Electron API odrzucono. Pełne domknięcie
`shell/common/api/api.mojom` sięga
`services/network/public/mojom/url_response_head.mojom`, zmienianego przez
`feat_expose_raw_response_headers_from_urlloader.patch` Electron.
Zachowano `recon-api.json`, `candidate-api-manifest.json` i
`scope-api-freeze.json` w katalogu rozpoznania. Wybór dwóch innych kompletnych
celów GN usuwa ten konflikt przy zachowaniu rzeczywistych importów.

## Granica specyfikacji i odtwarzanie

Przypięte konfiguracje montowania i literalne prefiksy ustanawiają ręcznie
przyjętą specyfikację resolvera. Audyt niezależnie wylicza oczekiwane pełne
krotki reguł z importów źródłowych i tej specyfikacji. Podmiana prefiksu,
wersji, celu lub odwołania do konfiguracji jest odrzucana. Pełna lista
wymaganych konfiguracji jest niezależnie wiązana z oryginalnymi blobami Git.
Semantyka całego GN i DEPS pozostaje poza tym twierdzeniem.

Źródła i metadane pozostają w
`local/stage8/connected-recon-01`. Repozytoria zawierają oryginalne obiekty
commitów, wszystkie drzewa przodków wybranych ścieżek i wymagane bloby.
Capture działa offline z `GIT_NO_LAZY_FETCH=1`. Niekompletny zbiór obiektów
blokuje weryfikację. Pobieranie nie wykonuje checkoutów, hooków ani buildów.

```powershell
& $py scripts/stage8_connected_recon.py local/stage8/connected-recon-01 `
  --download-patches --electron-common-targets
$env:PYTHONPATH = 'src;local/stage8-deps'
& $py scripts/stage8_materialize_candidate.py local/stage8/connected-recon-01
& $py -m unittest discover -s tests -p test_stage8_corpus_audit.py -v
```

Publiczne odczyty mają cache, limit odpowiedzi 16 MB, 45 sekund na odczyt,
maksymalnie trzy próby i najwyżej cztery równoczesne pobrania. Przy limitach
inwentarza GitHub odczyt jest dzielony na kompletne poddrzewa. Ogólny skrypt
`stage8_inventory.py` obsługuje również pełną enumerację lokalnych obiektów
Git i podział zbyt dużych odpowiedzi Gitiles. `stage8_discover.py` przyjmuje
listę kandydatów JSON przez `--candidates`, a `stage8_scan_candidates.py`
domyślnie analizuje wszystkich zinwentaryzowanych kandydatów i pozwala ich
ograniczyć przez powtarzalny argument `--repo`.
