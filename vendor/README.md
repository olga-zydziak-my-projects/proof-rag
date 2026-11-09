# Przypięty parser Mojom i PLY

`chromium/` zawiera wyłącznie 14 niezmodyfikowanych plików potrzebnych do
uruchomienia parsera, PLY oraz zachowania licencji. Źródło to
`https://github.com/chromium/chromium`, commit
`27cec857a08a0ee0e1b41f5eb18c07467a0ce093`. PLY ma wersję 3.11 zgodnie z
`chromium/third_party/ply/README.chromium`. Licencje zachowano w `LICENSE`,
`mojo/public/LICENSE` oraz `third_party/ply/LICENSE` pod katalogiem `chromium`.

`mojom-parser.lock.json` zapisuje pochodzenie, OID Git, SHA-256 i długość
każdego oryginalnego pliku. Łączna długość to 244 585 bajtów. Adapter ma
przypięty SHA-256 tego locka; sprawdza również pochodzenie zaimportowanych
modułów, żeby nie korzystać z przypadkowej instalacji `mojom` lub `ply`.
Oryginalny układ ścieżek pozwala używać upstreamowego `fileutil.py` bez zmian.

Weryfikacja offline z katalogu projektu:

```powershell
python scripts/vendor_mojom_parser.py --check
```

Opcjonalne odtworzenie dokładnie tych plików z przypiętych adresów i hashy:

```powershell
python scripts/vendor_mojom_parser.py --download
```

To pobiera tylko ten niewielki zestaw, nie checkout Chromium ani DEPS.
Normalne parsowanie i testy nie korzystają z sieci ani nie zapisują tablic PLY.
Adapter używa układu repozytorium; przenośna dystrybucja wheel nie jest
częścią tego etapu.

Pełne `Parse` sprawdza także składnię po ostatnim imporcie. Tokeny oryginalnego
lexera służą do lokalizacji deklaracji i literałów w oryginalnych bajtach UTF-8.
Nie używamy pola `ast.Import.import_filename` do rozwiązywania ścieżek:
upstream normalizuje je przez `os.path.normpath`. Adapter zachowuje surowy
token i niezależnie dekoduje sam literał, a warstwa ekstrakcji stosuje kontrakt
kanonicznych ścieżek. Atrybuty warunkowe pozostają bez ewaluacji warunków.

Przy błędzie pełnego parsowania można zachować kompletne importy leksykalnego
nagłówka oznaczone jako częściowe. Nie oznaczają one poprawności reszty pliku.
Każdy taki plik wymusza `unresolved` dla całego zakresu. Testy parsera i
kontrola hashy nie są formalnym dowodem poprawności parsera ani ekstrakcji.
