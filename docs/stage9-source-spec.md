# Specyfikacja źródeł etapu 9

Obowiązuje SourceBytes byte import projection v2: kompletne surowe bajty,
UTF-8, sprawdzony automat komentarzy/napisów/importów, kolejność i duplikaty
zdarzeń, bez wartościowania atrybutów warunkowych. Nie jest to pełna semantyka
Mojom ani wykonanie GN/DEPS.

Manifest `stage9-context-corpus-v1` zawiera źródłowy manifest v8, dokładny
rejestr kontekstów, kopię zamrożonej polityki i niezależną kotwicę zaakceptowanego
małego korpusu. Tożsamość Lean `Contextual.Identity.repository` przechowuje
`project@context`; pozostałe pola przechowują pełny commit i ścieżkę w bajtach.
Żaden dozwolony identyfikator projektu ani kontekstu nie zawiera `@`.
Pełna tożsamość występuje w każdej odpowiedzi. Warianty nie podnoszą progu plików.

Resolver stosuje rozłączne literalne prefiksy; musi pasować dokładnie jedna
reguła. Etap 9 jawnie dopuszcza także prefiks pełnej nazwy `.mojom`, przy
zachowaniu formalnej semantyki zastąpienia prefiksu z etapu 8. Poprzednie CLI
nie włącza tego trybu. Nie ma fallback, wyboru najdłuższego prefiksu ani
normalizacji ścieżek. Pełne rozstrzygnięcia sprawdzane są dodatkowo względem
przyjętej specyfikacji mountów. Wyjątki external to dwa dokładne literaly
z polityki; mają dedykowane reguły z konfiguracją własnego GN.

Wszystkie pliki manifestu są odczytywane z oryginalnych obiektów Git w batch,
z kontrolą pełnej enumeracji zakresu i hashy. Pełne źródła mieszczą się w kilku
MB; pozostają w pamięci podczas audytu. Większe dowody dzielimy na moduły po
osiem plików. Każdy moduł przechowuje pełne bajty i świadków przejść; kernel
sprawdza każdą część. Wspólna warstwa zawiera wstrzykiwalność nazw dowiedzioną
przez sprawdzoną odwrotność, wszystkie pliki oraz obustronną równość pełnego grafu.

Audyt niezależnego parsera v8 czyta wszystkie dane i komendy źródłowe po
bezstratnym złożeniu faktycznie zapisanych shardów. Nowa otoczka, odwrotność,
składanie zakresów i końcowy dowód mają zamkniętą składnię. Graf jest niezależnie
parsowany w całości. Query importuje sprawdzoną warstwę i świeżo dowodzi
certyfikatu, pełnej maski oraz `Contextual.answer_exact` dla całego payloadu.

Ponowne użycie sprawdza pełne inwentarze kodu, specyfikacji, Python runtime,
lokalnych zależności i toolchain Lean; executable i wersję Git; każde źródło,
każdy wiersz DuckDB/Parquet, każdy plik eksportu/olean i pełne raporty aksjomatów.
Punktem zaufania pozostaje rzeczywiście zaakceptowany receipt z przygotowania
oraz jego niezależna kotwica. IO, Git/hash, system i ręcznie zaakceptowana
semantyka mapowania są granicami operacyjnymi. Zakładamy zaufany lokalny katalog
bez wrogiego współbieżnego zapisu, jak w etapie 8.
