# Formalny rdzeń osiągalności

`Reachability.lean` definiuje skierowany graf `Edge`, wierzchołek początkowy
`root`, osiągalność przez skończoną ścieżkę `Reach` i kandydacki zbiór `R`.
Ścieżka długości zero jest dozwolona, więc wynik obejmuje sam `root`.

Twierdzenie `RepoProof.exact_reachability` ma postać:

```text
Certificate Edge root R → ∀ v, (R v ↔ Reach Edge root v)
```

Certyfikat wymaga trzech osobnych obowiązków:

1. `root_mem`: `root` należy do `R`.
2. `sound`: każdy element `R` ma dowód osiągalności w podanym grafie.
3. `closed`: dla każdej krawędzi grafu wychodzącej z elementu `R`, jej koniec
   również należy do `R`.

Dowód kompletności jest indukcją po ścieżce. Nie wymaga skończoności grafu;
skończoność będzie potrzebna implementacji, która wylicza i sprawdza certyfikat.
`reachability_has_certificate` pokazuje, że warunki spełnia rzeczywisty zbiór
osiągalnych wierzchołków.

## Świadkowie rodziców i rangi

`soundness_from_ranked_witnesses` udowadnia obowiązek `sound` z warunków
lokalnych, odpowiadających certyfikatowi z rodzicami i rangami. Każdy element
`v` zbioru `R` musi być korzeniem albo posiadać rodzica `p`, dla którego:

- `p` należy do `R`;
- istnieje krawędź `Edge p v`;
- `rank p < rank v`, gdzie rangi są liczbami naturalnymi.

Silna indukcja po randze daje rzeczywistą ścieżkę od korzenia. Ścisły spadek
rangi wyklucza cykl wzajemnie uzasadniających się rodziców. Nie jest potrzebny
aksjomat wyboru: świadków dostarcza jawna alternatywa i kwantyfikator istnienia.
Ranga korzenia nie musi wynosić zero; twierdzenie tego nie wymaga.

`ranked_exact_reachability` łączy ten dowód z przynależnością korzenia i
domknięciem po wszystkich krawędziach. Otrzymujemy poprawność i kompletność
wyniku bez zakładania `sound` jako osobnego wejścia.

Jeżeli zapytanie dotyczy zależnych plików, `Edge` może oznaczać odwróconą
relację importów. Orientacja relacji musi być ustalona konsekwentnie przy
ekstrakcji, generowaniu świadków i sprawdzaniu certyfikatu.

## Co dokładnie jest objęte dowodem

Twierdzenie dowodzi poprawności i kompletności zbioru **względem podanego grafu**,
jeżeli wszystkie obowiązki certyfikatu zostaną udowodnione. Sam plik nie generuje
certyfikatów dla konkretnych danych. Pole `sound` jest obowiązkiem do sprawdzenia,
a nie zaufaną odpowiedzią silnika wyszukiwania.

Nie udowodniono tutaj:

- poprawności ani kompletności ekstrakcji grafu z kodu źródłowego;
- zgodności implementacji Python z definicjami Lean;
- poprawności parsera plików certyfikatu, hashy lub manifestu korpusu;
- własności semantycznych dowolnego programu ani osiągalności podczas wykonania;
- czasu działania, zużycia pamięci lub kompletności przerwanego wyszukiwania.

Weryfikacja `closed` musi obejmować wszystkie krawędzie wejściowego grafu.
Sprawdzenie tylko krawędzi odwiedzonych przez wyszukiwarkę nie spełnia tego
obowiązku. Weryfikacja `sound` wymaga rzeczywistych świadków lub dowodów; sama
lista wyników nie wystarcza.

## Założenia i kontrola pustych przypadków

`root_mem` wyklucza pusty zbiór wyników. `sound` wyklucza dodawanie wierzchołków
nieosiągalnych, a `closed` wyklucza pomijanie osiągalnych następców. Założenia
mogą być spełnione: dowodzi tego `reachability_has_certificate`.

Plik używa `Std`, bez Mathlib, `sorry`, własnych aksjomatów i `native_decide`.
Na końcu wypisuje zależności aksjomatyczne wszystkich sześciu twierdzeń.

## Uruchomienie

Z katalogu `formal`, po zainstalowaniu ustalonej wersji Lean 4:

```text
lean Reachability.lean
```

Docelowa wersja narzędzia dla tego projektu: Lean 4.35.0. Wynik kompilatora
i audytu aksjomatów należy sprawdzić w faktycznym uruchomieniu; sam ten opis
nie stanowi potwierdzenia, że uruchomienie się powiodło.
