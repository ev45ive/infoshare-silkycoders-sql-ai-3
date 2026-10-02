# Tryb 2 — Porównanie okresów / Trend

## Kiedy stosować

- "Pokaż trend sprzedaży od tygodnia X"
- "Porównaj ten miesiąc z poprzednim"
- "Jak zmieniała się sprzedaż w ostatnich N tygodniach"

## Pytania doprecyzowujące (`#tool:vscode_askQuestions`)

1. **Typ porównania:**
   - WoW — tydzień do tygodnia (dwa okresy)
   - MoM — miesiąc do miesiąca (dwa okresy)
   - Trend — N tygodni/miesięcy w szeregu czasowym
   - Własny zakres dat

2. **Zasięg:** ile okresów wstecz (np. "od W30" = 9 tygodni wstecz do bieżącego).

3. **Zakres produktowy:** cała sieć, czy konkretna kategoria/department/produkt (jeśli produkt — przejdź też przez pytania z Trybu 3 o identyfikację produktu).

4. **Miara:** domyślnie sprzedaż netto (`FactSales.NetAmount`) i sztuki (`FactSales.Quantity`) — potwierdź czy obie, czy tylko jedna.

## Kroki

1. Potwierdź okresy/zakres dat w `DimDate` (czy wszystkie tygodnie/miesiące są pełne, czy dane sięgają końca ostatniego okresu).
2. Uruchom zapytanie trendu — jeden wiersz na okres (`IsoYear`, `IsoWeek` lub `YearMonth`).
3. Dla porównania dwóch okresów (WoW/MoM) policz: zmianę PLN, zmianę %, i jeśli dotyczy — udziały kanałów.
4. Dla trendu N-okresowego: pokaż tabelę + krótki opis kierunku (rosnący/malejący/stabilny), zaznacz punkt zwrotny (peak/dołek) jeśli widoczny.
5. Zweryfikuj przeciw `reporting.vw_SalesWeekly` tam gdzie ma to zastosowanie.
6. **Próg anomalii:** jeśli ostatnia zmiana okres-do-okresu przekracza **15%**, zapytaj (`#tool:vscode_askQuestions`) czy użytkownik chce przejść do Trybu 4 (Analiza anomalii) lub Trybu 3 (drill-down po wymiarach).

## Szablon SQL — Trend N tygodni (jedna kategoria lub cała sieć)

```sql
-- Trend sprzedaży netto i sztuk po tygodniach ISO
-- Filtr produktowy jest opcjonalny (usuń WHERE dp.* dla całej sieci)
SELECT
    dd.IsoYear,
    dd.IsoWeek,
    dd.YearWeek,
    CAST(SUM(fs.NetAmount) AS DECIMAL(12, 2)) AS SprzedazNetto_PLN,
    CAST(SUM(fs.Quantity) AS INT) AS Sztuki
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
-- INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey  -- odkomentuj dla filtru produktowego
WHERE
    dd.IsoYear = @Rok
    AND dd.IsoWeek BETWEEN @TydzienOd AND @TydzienDo
    -- AND dp.Department = @Department
    -- AND dp.Category = @Category
GROUP BY dd.IsoYear, dd.IsoWeek, dd.YearWeek
ORDER BY dd.IsoWeek;
```

## Szablon SQL — Porównanie dwóch okresów (WoW/MoM) z kanałami

```sql
WITH podstawowe_dane AS (
    SELECT
        dd.IsoWeek,
        ds.[Channel],
        CAST(SUM(fs.NetAmount) AS DECIMAL(12, 2)) AS SprzedazNetto
    FROM dbo.FactSales fs
    INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
    INNER JOIN dbo.DimStore ds ON fs.StoreKey = ds.StoreKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
    GROUP BY dd.IsoWeek, ds.[Channel]
),
z_razem AS (
    SELECT * FROM podstawowe_dane
    UNION ALL
    SELECT IsoWeek, 'RAZEM', SUM(SprzedazNetto)
    FROM podstawowe_dane
    GROUP BY IsoWeek
)
SELECT
    Channel,
    MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN SprzedazNetto END) AS Poprzedni,
    MAX(CASE WHEN IsoWeek = @TydzienBiezacy THEN SprzedazNetto END) AS Biezacy,
    CAST(
        MAX(CASE WHEN IsoWeek = @TydzienBiezacy THEN SprzedazNetto END) -
        MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN SprzedazNetto END)
        AS DECIMAL(12, 2)
    ) AS ZmianaPln,
    CAST(
        (MAX(CASE WHEN IsoWeek = @TydzienBiezacy THEN SprzedazNetto END) -
         MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN SprzedazNetto END)) /
        NULLIF(MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN SprzedazNetto END), 0) * 100.0
        AS DECIMAL(6, 2)
    ) AS ZmianaProc
FROM z_razem
GROUP BY Channel
ORDER BY CASE WHEN Channel = 'RAZEM' THEN 0 ELSE 1 END, Channel;
```

**Uwaga o UNION ALL + ORDER BY:** SQL Server nie pozwala na `ORDER BY` z aliasem CASE bezpośrednio po `UNION ALL` bez owijki — użyj CTE jak powyżej (`z_razem`), albo dodaj kolumnę pomocniczą `SortOrder` przed sortowaniem.

## Format odpowiedzi (jak Tryb 1, z modyfikacją)

Zamiast jednej tabeli okres×kanał, pokaż:
1. **Założenia:** zakres dat/tygodni, miara, filtr produktowy (jeśli dotyczy).
2. **SQL** z komentarzami.
3. **Tabela trendu** (okres w wierszach, metryki w kolumnach) lub **tabela porównawcza** (jak w Trybie 1) dla dwóch okresów.
4. **Obserwacja kierunku:** rosnący/malejący/punkt zwrotny, z wyliczeniami.
5. **Metryki użyte**, **weryfikacja**, **podsumowanie do e-maila**, **otwarte pytania** — jak w Trybie 1.
