# Rozpoznanie rzeczywistych repozytoriów

Werdykt: **STAGE8_CORPUS_BLOCKED** dla zbadanych kandydatów. Nie jest to dowód,
że w całym ekosystemie nie istnieje odpowiedni korpus. Nie połączyliśmy arbitralnie
HEAD projektów w rzekomo spójną wersję. Zamrożony manifest wyboru ma pusty zbiór
przyjętych repozytoriów i żadnych zaakceptowanych połączeń.

[Metadane kandydatów](../verification/stage8-discovery.json) zawierają pełne
URL-e, commity, drzewa, źródła konfiguracji i hashe pobranych plików.
[Pełne inwentarze](../verification/stage8-inventories.json) i
[skan całych źródeł](../verification/stage8-candidate-scan.json) są dowodami
rozpoznania, **nie manifestem spójnego korpusu pilota**.

| Kandydat | Przypięty commit (skrót; pełne SHA w raporcie) | Wynik |
| --- | --- | --- |
| Chromium | 27cec857a08a | Zachowany korpus etapów 5–7; nie rozszerzano jego gwarancji |
| chromiumos/platform2 | c2c6eedd4d40 | 96 Mojom, 110 importów, wszystkie wewnętrzne |
| chromiumos/platform/libchrome | 26299852898b | 50 Mojom, 10 importów, wszystkie wewnętrzne |
| chromiumos/third_party/libcamera | 6273963b7290 | 7 Mojom, 5 importów własnego core; odłączony od dwóch powyższych |
| crosvm/crosvm | 4f5fefd86b75 | Pełny inwentarz: 1580 wpisów, zero Mojom |
| chromiumos/platform/camera | 47fda3a408a8 | 2237 wpisów, zero Mojom; README opisuje wkład vendorów/partnerów |
| chromiumos/platform2/system_api | dfe5a85e26a5 | 253 wpisy, zero Mojom; read-only gsubtree platform2 |
| chromiumos/manifest | 88b086eddddc | Dane rozpoznania; default.xml odsyła do full.xml i gałęzi, nie ustala przyjętej trójki |

Przeczytano pełne bajty wszystkich **153 plików Mojom**, razem **631 537 B**,
w trzech kandydaturach zawierających Mojom. Wszystkie **125 zdarzeń importów**
rozwiązują się po dosłownej ścieżce we własnym repozytorium. Nie ma nawet
kandydatury literalnego importu wychodzącego poza własną pełną listę źródeł.
Nie powstaje połączony graf trzech projektów ani wymagane dwie pary połączeń.
W efekcie nie ma uczciwego przykładu rzeczywistej odpowiedzi wielorepozytoryjnej.

Weryfikowano m.in.:

- Przypięty `platform2/common-mk/mojom_bindings_generator.gni`: reguły
  `mojo_root`, input roots i import paths są konfiguracją generowania. Sama
  zależność `libchrome/libmojo` nie dowodzi importu pliku między repozytoriami.
- `platform2/diagnostics/.../cros_healthd_probe.mojom` i
  `federated/mojom/federated_service.mojom`: komentarze jawnie opisują kopie
  protokołów w Chromium i różne katalogi bazowe. To nie import oryginalnego pliku.
- `camera/common/BUILD.gn` i całe camera Mojom: źródła są w platform2;
  nie należy wydzielać ich jako sztucznego trzeciego repozytorium.
- Libchrome zawiera źródła pochodzące z Chromium. Pochodzenie/mirror nie jest
  dowodem połączenia Mojom ani podstawą do liczenia dwóch niezależnych projektów.
- Libcamera używa Mojom do IPA, ale jego pięć importów dotyczy wyłącznie
  `include/libcamera/ipa/core.mojom` we własnym projekcie. Pełny skan platform2
  i libchrome nie wykazał importów przychodzących do libcamera.

Pierwszy skan pobierania otrzymał **18 HTTP 429**. Zachowano
[raport początkowy](../verification/stage8-candidate-scan-initial.json).
Jedno sekwencyjne ponowienie pobrało brakujące pliki, wykorzystując pozostałe
lokalne kopie; finalny skan nie ma błędów. Pełny zdalny inventory Chromium
przekroczył jawny limit 8 MB odpowiedzi — nie zwiększano limitu. Istniejący
lokalny korpus Chromium i jego historyczne dowody są zachowane oddzielnie.

Odtworzenie pobiera wyłącznie dane, bez hooków/buildów/wykonywania konfiguracji:

```powershell
& $py scripts/stage8_discover.py local/stage8/discovery-new
& $py scripts/stage8_inventory.py local/stage8/discovery-new local/stage8/inventory-new
& $py scripts/stage8_scan_candidates.py local/stage8/discovery-new local/stage8/inventory-new local/stage8/sources-new
```

`discover` jest narzędziem rozpoznania bieżących HEAD, więc jego kolejne
uruchomienie może wskazać inne wersje. Dokładne odtworzenie tej oceny korzysta
z **wersjonowanego discovery.json** i zapisanych w nim pełnych commitów, a nie
z nowych HEAD. Inwentarze i skan używają wyłącznie tych przypiętych commitów.

Następny krok: znaleźć rzeczywisty trzeci projekt z udokumentowanym importem
i regułą rozwiązywania oraz manifestem zgodnych wersji. Dopiero potem zamrozić
przyjęty korpus i zbudować nowy formalny most źródłowy; obecny dowód Chromium
tego obowiązku nie zastępuje.
