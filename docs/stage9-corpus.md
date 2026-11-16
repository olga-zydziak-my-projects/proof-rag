# Korpus i konteksty etapu 9

Zamrożony [manifest](../verification/stage9-manifest.json) ma SHA256
`49e019318b6ca51cd70806f5816a06616dfcd3693337f564a5431018ad652299`.
Osobna [kotwica](../verification/stage9-manifest-anchor.json) i
[niezależny przegląd](../verification/stage9-corpus-review.json) wiążą kompletne
inwentarze z oryginalnymi commitami, drzewami i blobami Git. Lokalne lokalizacje
nie są częścią tożsamości. Nie zmieniano wersji zaakceptowanych w etapie 8.

| Projekt | Commit | Drzewo | Pliki |
| --- | --- | --- | ---: |
| Chromium 140.0.7339.133 | `3927f129b801f969d4abdb1458d55174cc062723` | `9126a9192eb20fda7cc2e0f5a6b5163dfae53b4b` | 1243 |
| Electron v38.1.2 | `d60ae179985685d75d238ee33e17c15a7b53d703` | `fa2587baa940913befc5d539afef827a695dfb73` | 2 |
| Brave Core v1.82.166 | `38bf45887ca5336841cddb4200e6deee32ce45a8` | `21f15cb35a06c819d080872a0c404a771a76efc1` | 6 |

Pochodzenie: oficjalne repozytoria [Chromium](https://github.com/chromium/chromium),
[Electron](https://github.com/electron/electron) i [Brave Core](https://github.com/brave/brave-core).
Metadane Chromium pochodzą także z oficjalnego Gitiles. Electron DEPS i Brave
package.json przypinają ten sam Chromium; mirror Brave wskazuje identyczny commit/tree.
Przypięty `chrome/VERSION` wiąże wersję z rzeczywistym obiektem commitu.

Wybrano wszystkie commitowane `.mojom` w kompletnych modułach `components`,
`content`, `device`, `gpu`, `media`, `mojo/public/mojom`, `printing`, `services`,
`third_party/blink/public/mojom`, `ui`, `url/mojom`, łącznie 1202 pliki.
Dołączono 41 wymaganych źródeł Chromium spoza modułów przez najmniejsze domknięcie
importów oraz niezmienione kompletne cele GN Electron plugin/web_contents_utility
i sześć źródeł celu Brave AI Chat. Nie wycinano plików testowych lub izolowanych
ani nie dopasowywano liczby do 1000. Zachowano 96 składowych grafu; wspólna
składowa trzech projektów zawiera 1149 plików. Nie dodano sztucznych połączeń.

Razem: trzy projekty, trzy przypięte wersje, 1251 odrębnych rzeczywistych plików,
1251 unikalnych treści, 4 188 752 bajty, 3286 krawędzi: 3273 wewnątrz projektów
i 13 między projektami. Są trzy jawne konteksty, 1251 rekordów kontekstowych
i zero dodatkowych wariantów tego samego pliku.

Wszystkie 225 poprawek Electron, 644 Brave oraz pełne 2780 wpisów overlay
Brave sprawdzono ponownie dla rozszerzonego zakresu. Przegląd zawiera kompletne
listy przecięć upstream: 14 ścieżek patch Electron, 2 Brave i 16 nakładek.
Te pliki mają wyłącznie kontekst **upstream**. Nie są utożsamiane z efektywnymi
wariantami w aplikacjach. Wybrane cele Electron/Brave mają wspólne pełne
18-plikowe domknięcie, bez jakiegokolwiek przecięcia z poprawkami/nakładkami.
Wyłącznie dla tych importów przyjęto audytowaną równość efektywnych bajtów.

Dwa wyjścia builda (`runtime_feature.mojom`, `origin_trial_feature.mojom`)
nie występują w Git. Ich własne BUILD.gn, generatory i szablony są przypiętymi
konfiguracjami; cztery pełne zdarzenia importów zachowano jako external.
[Osobny przegląd granicy](../verification/stage9-generated-boundary-review.json)
potwierdza konkretne deklaracje `$root_gen_dir`. Nie ma innych zdarzeń external.
Nie jest to domknięcie względem wszystkich źródeł generowanych przez build.

Regułę modułów zapisano przed pozyskaniem danych, a politykę i manifest przed
wyborem zapytań. Zamrożona deterministyczna reguła wybrała odpowiedzi o rozmiarach
264,157,2,1,3,372. Pierwsza obejmuje wszystkie trzy projekty, cztery z sześciu
przekraczają granice projektów. Te liczności pochodzą z niezależnego DFS i nie
ustanawiają jeszcze akceptacji formalnej: każdy pełny wynik wymaga własnego Lean.
