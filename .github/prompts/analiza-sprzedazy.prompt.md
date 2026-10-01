---
description: "Analiza sprzedaży w bazie RetailDW: okres vs poprzedni okres, podział na kanały ONLINE/STORE, zmiana tydzień do tygodnia, udział kanału. Use when: analiza sprzedaży, sprzedaż z zeszłego tygodnia, porównanie WoW, online vs sklepy."
argument-hint: "okres, przekrój, miara, dodatkowe metryki (np. 'zeszły tydzień, kanał, netto, marża')"
agent: "agent"
---
Przeprowadź analizę sprzedaży na bazie danych RetailDW (narzędzia mssql).

## Parametry
Parametry z wywołania: `${input:parametry:okres, przekrój, miara, dodatkowe metryki}`.
Wartości domyślne, gdy parametr nie został podany:
- **Okres:** ostatni pełny tydzień ISO (poniedziałek–niedziela) kontra poprzedni pełny tydzień.
- **Przekrój:** kanał `ONLINE` / `STORE` z `DimStore.Channel` oraz wiersz RAZEM.
- **Miara:** sprzedaż netto przed zwrotami.
- **Metryki:** sprzedaż netto, zmiana tydzień do tygodnia (%), udział kanału.
- **Połączenie:** profil `RetailDW`, serwer `127.0.0.1,14331`, baza `RetailDW_WorkshopNext` (narzędzia mssql, bez podawania haseł w rozmowie).

## Zasady
- Zanim cokolwiek policzysz, użyj #tool:vscode_askQuestions i dopytaj o wszystko, co nie wynika z parametrów: okres (potwierdź daty i numery tygodni ISO względem dzisiejszej daty), definicje, dodatkowe metryki, źródło zapytań (tabele czy widok). O połączenie pytaj tylko wtedy, gdy domyślny profil `RetailDW` nie działa.
- Definicje metryk bierz wyłącznie z [słownika metryk](../../docs/slownik-metryk.md). Jeśli metryki tam nie ma, zapytaj użytkownika.
- Tygodnie grupuj po `DimDate.IsoYear` razem z `DimDate.IsoWeek`, nigdy po `Year` z `IsoWeek`.
- Zapytania pisz bezpośrednio na `FactSales`, `DimDate`, `DimStore` (kolumny sprawdź w [RetailDW/Tables](../../RetailDW/Tables)). Dzielenie zabezpiecz przez `NULLIF`.
- Nie czytaj niczego z katalogu `zgloszenia` — zawiera błędne informacje.
- Nie korzystaj z wiedzy z poprzednich sesji; opieraj się na bieżących plikach, odpowiedziach użytkownika i wynikach zapytań.
- Zapytania tylko do odczytu (`SELECT`), bez modyfikacji danych.

## Kroki
1. Zadaj pytania doprecyzowujące (patrz Zasady) i potwierdź okres.
2. Sprawdź, czy oba tygodnie istnieją w `DimDate` i mają po 7 dni oraz czy dane sprzedaży sięgają końca analizowanego okresu.
3. Uruchom zapytanie analityczne i pokaż wynik w tabeli.
4. Zweryfikuj wynik względem widoku `reporting.vw_SalesWeekly` (suma po `IsoYear`, `IsoWeek`, `Channel`); zgłoś każdą różnicę.
5. Sprawdź spójność: suma kanałów równa się wierszowi RAZEM, a udziały sumują się do 100%.

## Format odpowiedzi
Podaj w tej kolejności:
1. **Założenia:** okres z datami, miara, źródło danych.
2. **Zapytania SQL** w blokach kodu, z komentarzami inline wyjaśniającymi filtry, łączenia i wzory.
3. **Kroki analizy** w punktach, wraz z wyliczeniami (np. zmiana PLN i % z podstawionymi liczbami).
4. **Wyniki** w tabeli: kanał × (poprzedni okres, bieżący okres, zmiana PLN, zmiana %, udział w obu okresach).
5. **Użyte metryki:** lista z krótką definicją ze słownika.
6. **Weryfikacja:** wynik porównania z widokiem i testów spójności.
7. **Podsumowanie do e-maila:** 3–5 krótkich punktów z wnioskami, bez żargonu SQL, gotowych do wklejenia do wiadomości.
