---
name: analiza-sprzedazy
description: "Analiza sprzedaży w hurtowni RetailDW (mssql): pojedynczy okres, porównanie okresów/trend WoW/MoM, przekroje po kanałach/kategoriach/sklepach/SKU, diagnoza anomalii (brak towaru vs brak popytu). Use when: analiza sprzedaży, sprzedaż z zeszłego tygodnia, porównanie WoW/MoM, trend sprzedaży, podział na kanały lub kategorie, dlaczego sprzedaż spadła/wzrosła."
argument-hint: "opisz co chcesz: okres, przekrój, miara, kategoria/produkt — albo zostaw puste, zapytam o tryb"
user-invocable: true
disable-model-invocation: false
---

# Analiza Sprzedaży — RetailDW

## Cel

Doprowadzić analityka od pytania biznesowego do liczby i wyjaśnienia, pracując na `FactSales`, `DimDate`, `DimStore`, `DimProduct` w `RetailDW`. Skill ma 4 tryby — od najprostszego do diagnostyki anomalii.

---

## Krok 0: Wybierz tryb

Jeśli użytkownik nie wskazał jasno trybu w zapytaniu, zapytaj `#tool:vscode_askQuestions`:

- **Tryb 1 — Prosta analiza okresu**: jeden okres (lub okres vs poprzedni), podział kanał + RAZEM. Najczęstszy przypadek ("sprzedaż za zeszły tydzień").
- **Tryb 2 — Porównanie okresów / Trend**: WoW, MoM, trend N tygodni/miesięcy, lub własny zakres dat.
- **Tryb 3 — Przekroje**: dodatkowy podział po kategorii/department/stylu/SKU/sklepie, zaczynając od trendu (tryb 2), potem drążenie w głąb wymiarów.
- **Tryb 4 — Analiza anomalii**: diagnoza *dlaczego* sprzedaż się zmieniła (brak towaru vs brak popytu vs błąd danych) — wywoływana ręcznie LUB proponowana, gdy tryb 2/3 wykryje zmianę > 15%.

Jeśli zapytanie użytkownika już jednoznacznie wskazuje tryb (np. "pokaż trend od W30" → tryb 2/3, "dlaczego spadła sprzedaż kurtek" → tryb 4), pomiń pytanie o tryb i przejdź od razu do właściwej sekcji — ale nadal dopytaj o szczegóły specyficzne dla tego trybu.

---

## Zasady wspólne (wszystkie tryby)

- **Połączenie:** profil `RetailDW`, serwer `127.0.0.1,14331`, baza `RetailDW_WorkshopNext` (narzędzia mssql, bez haseł w rozmowie). O połączenie pytaj tylko gdy domyślne nie działa.
- **Definicje metryk** wyłącznie z [docs/slownik-metryk.md](../../../docs/slownik-metryk.md). Jeśli metryki tam nie ma, zapytaj użytkownika.
- **Tygodnie** grupuj po `DimDate.IsoYear` razem z `DimDate.IsoWeek`, nigdy po `Year` z `IsoWeek`.
- Zapytania pisz bezpośrednio na `FactSales`, `DimDate`, `DimStore`, `DimProduct` (kolumny sprawdź w [RetailDW/Tables](../../../RetailDW/Tables)). Dzielenie zabezpiecz przez `NULLIF`.
- **Nie czytaj** `zgloszenia/`, `.specstory/`, `notatki/`, `RetailDW/Scripts/`, `docs/ai-sessions/` — poza zakresem (patrz AGENTS.md).
- Nie korzystaj z wiedzy z poprzednich sesji; opieraj się na bieżących plikach, odpowiedziach użytkownika i wynikach zapytań.
- Zapytania tylko do odczytu (`SELECT`), bez modyfikacji danych.
- Przed policzeniem czegokolwiek sprawdź, czy analizowane tygodnie/miesiące istnieją w `DimDate` w pełni (np. tydzień ma 7 dni) i czy dane sprzedaży sięgają końca okresu — brak danych zgłoś użytkownikowi zamiast zgadywać.
- Każdy wynik agregujący po tygodniach/kanałach zweryfikuj względem `reporting.vw_SalesWeekly` i sprawdź spójność: suma części = RAZEM, udziały sumują się do 100%.

---

## Tryb 1 — Prosta analiza okresu

### Parametry
Wartości domyślne, gdy parametr nie został podany:
- **Okres:** ostatni pełny tydzień ISO (poniedziałek–niedziela) kontra poprzedni pełny tydzień.
- **Przekrój:** kanał `ONLINE` / `STORE` z `DimStore.Channel` oraz wiersz RAZEM.
- **Miara:** sprzedaż netto przed zwrotami.
- **Metryki:** sprzedaż netto, zmiana tydzień do tygodnia (%), udział kanału.

### Zasady dodatkowe
Zanim cokolwiek policzysz, użyj `#tool:vscode_askQuestions` i dopytaj o wszystko, co nie wynika z parametrów: okres (potwierdź daty i numery tygodni ISO względem dzisiejszej daty), definicje, dodatkowe metryki, źródło zapytań (tabele czy widok).

### Kroki
1. Zadaj pytania doprecyzowujące i potwierdź okres.
2. Sprawdź, czy oba okresy istnieją w `DimDate` i mają pełną liczbę dni oraz czy dane sprzedaży sięgają końca analizowanego okresu.
3. Uruchom zapytanie analityczne i pokaż wynik w tabeli.
4. Zweryfikuj wynik względem `reporting.vw_SalesWeekly` (suma po `IsoYear`, `IsoWeek`, `Channel`); zgłoś każdą różnicę.
5. Sprawdź spójność: suma kanałów równa się wierszowi RAZEM, a udziały sumują się do 100%.
6. Jeśli zmiana WoW przekracza **15%** w dowolnym kierunku, zapytaj użytkownika (`#tool:vscode_askQuestions`), czy chce przejść do **Trybu 4 (Analiza anomalii)**.

### Format odpowiedzi
1. **Założenia:** okres z datami, miara, źródło danych.
2. **Zapytania SQL** w blokach kodu, z komentarzami inline wyjaśniającymi filtry, łączenia i wzory.
3. **Kroki analizy** w punktach, wraz z wyliczeniami (zmiana PLN i % z podstawionymi liczbami).
4. **Wyniki** w tabeli: kanał × (poprzedni okres, bieżący okres, zmiana PLN, zmiana %, udział w obu okresach).
5. **Użyte metryki:** lista z krótką definicją ze słownika.
6. **Weryfikacja:** wynik porównania z widokiem i testów spójności.
7. **Podsumowanie do e-maila:** 3–5 krótkich punktów z wnioskami, bez żargonu SQL.
8. **Otwarte pytania i sugestie:** nierozstrzygnięte kwestie i propozycje dalszych analiz.

---

## Tryb 2 — Porównanie okresów / Trend

Dla trendu lub porównania więcej niż dwóch okresów. Zapytaj `#tool:vscode_askQuestions` o:
- Typ porównania: WoW (tydzień do tygodnia), MoM (miesiąc do miesiąca), trend N tygodni/miesięcy, czy własny zakres dat.
- Liczbę okresów wstecz (np. "trend od W30").
- Czy uwzględnić konkretny produkt/kategorię, czy całą sieć.

Pełna procedura, szablony SQL i warunki wejścia w drill-down: [tryb2-trend-porownanie.md](./references/tryb2-trend-porownanie.md).

---

## Tryb 3 — Przekroje (kanał / kategoria / sklep / SKU)

Zacznij od trendu (Tryb 2), potem zaproponuj głębsze drążenie. Zapytaj `#tool:vscode_askQuestions` o poziom szczegółowości: Department+Category, StyleCode (model), czy pełne SKU (rozmiar/kolor), oraz czy per sklep czy zagregowane.

Pełna procedura i szablony SQL: [tryb3-przekroje.md](./references/tryb3-przekroje.md).

---

## Tryb 4 — Analiza anomalii (brak towaru vs brak popytu vs błąd danych)

Wywoływana ręcznie przez użytkownika, albo proponowana przez Tryb 1/2/3 po wykryciu zmiany > 15%. **Nigdy nie wchodź w ten tryb automatycznie bez potwierdzenia użytkownika** (`#tool:vscode_askQuestions`).

Zawiera testy rozróżniające niedobór zapasów od spadku popytu (tempo konsumpcji zapasów, zwroty, aktywność SKU) oraz wskazówki, kiedy problem jest raczej techniczny (ETL/jakość danych) niż biznesowy.

Pełna procedura, hipotezy i szablony SQL: [tryb4-anomalie.md](./references/tryb4-anomalie.md).

**Jeśli wyniki wskazują na problem techniczny** (liczby się nie zgadzają między warstwami, podejrzane duplikaty, braki w ETL) — zatrzymaj się i zaproponuj użytkownikowi przejście do skilla `analiza-pochodzenia-danych`, który ma dedykowaną procedurę śledzenia danych przez warstwy `src → stg → dbo`. Nie próbuj diagnozować ETL w tym skillu.

---

## Checklist — czy skończyłeś analizę?

- [ ] Tryb został potwierdzony z użytkownikiem (lub jednoznacznie wynikał z zapytania)
- [ ] Okres/zakres dat zweryfikowany w `DimDate` (pełne tygodnie/miesiące, dane sięgają końca okresu)
- [ ] Metryki użyte zgodnie ze słownikiem metryk, z podanym źródłem
- [ ] Wynik zweryfikowany względem `reporting.vw_SalesWeekly` (gdy dotyczy)
- [ ] Test spójności: suma części = RAZEM, udziały = 100%
- [ ] Jeśli zmiana > 15% — użytkownik zapytany o przejście do Trybu 4
- [ ] Odpowiedź zawiera: założenia, SQL, kroki analizy, wyniki w tabeli, metryki, weryfikację, podsumowanie do e-maila, otwarte pytania
