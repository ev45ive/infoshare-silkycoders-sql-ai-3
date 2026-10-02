# Tryb 3 — Przekroje (kanał / kategoria / sklep / SKU)

## Kiedy stosować

- "Porównaj sprzedaż kurtek męskich i damskich"
- "Pokaż wynik per sklep"
- "Który model/SKU sprzedaje się najlepiej"

## Podejście: zacznij szeroko, potem drąż

1. **Najpierw uruchom Tryb 2** (trend/porównanie) na poziomie, o który pytał użytkownik (np. Department+Category).
2. **Potem zaproponuj głębszy poziom** (`#tool:vscode_askQuestions`), jeśli wynik to uzasadnia (duża rozbieżność między elementami przekroju, albo użytkownik chce wiedzieć "dlaczego").

## Pytania doprecyzowujące (`#tool:vscode_askQuestions`)

1. **Wymiar przekroju:** kanał (`DimStore.Channel`), kategoria (`DimProduct.Category` + `Department`), sklep (`DimStore.StoreName`), model (`DimProduct.StyleCode`), SKU pełne (rozmiar/kolor).
2. **Poziom szczegółowości:** Department+Category (najwyższy) → StyleCode (model) → SKU (najniższy, rozmiar/kolor). Domyślnie zacznij od Department+Category.
3. **Agregacja czy per sklep:** czy pokazać zsumowane dla sieci, czy rozbite po każdym sklepie osobno + RAZEM.
4. **Identyfikacja produktu, gdy użytkownik opisuje słownie** (np. "kurtki damskie"): sprawdź `DimProduct.Department`/`Category` zapytaniem eksploracyjnym zamiast zgadywać nazwę:
   ```sql
   SELECT DISTINCT Department, Category FROM dbo.DimProduct
   WHERE Category LIKE '%<fraza>%' OR StyleName LIKE '%<fraza>%';
   ```

## Szablon SQL — Porównanie dwóch grup (np. Department) w dwóch okresach, z tempem i cenami

```sql
WITH sprzedaz_razem AS (
    SELECT
        dd.IsoWeek,
        dp.Department,
        CAST(SUM(fs.NetAmount) AS DECIMAL(12, 2)) AS SprzedazNetto_PLN,
        CAST(SUM(fs.Quantity) AS INT) AS Sztuki
    FROM dbo.FactSales fs
    INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
    INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
      AND dp.Category = @Category AND dp.Department IN (@Dept1, @Dept2)
    GROUP BY dd.IsoWeek, dp.Department
)
SELECT
    IsoWeek, Department, SprzedazNetto_PLN, Sztuki,
    CAST(SprzedazNetto_PLN / NULLIF(Sztuki, 0) AS DECIMAL(10, 2)) AS CenaAvg_PLN_za_sztuke
FROM sprzedaz_razem
ORDER BY IsoWeek, Department;
```

## Szablon SQL — Przekrój per sklep + RAZEM

```sql
WITH sprzedaz_detalicznie AS (
    SELECT
        dd.IsoWeek,
        ds.Channel,
        ds.StoreName,
        CAST(SUM(fs.NetAmount) AS DECIMAL(12, 2)) AS SprzedazNetto_PLN,
        CAST(SUM(fs.Quantity) AS INT) AS Sztuki
    FROM dbo.FactSales fs
    INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
    INNER JOIN dbo.DimStore ds ON fs.StoreKey = ds.StoreKey
    INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
      AND dp.Category = @Category
    GROUP BY dd.IsoWeek, ds.Channel, ds.StoreName
)
SELECT IsoWeek, Channel, StoreName, SprzedazNetto_PLN, Sztuki
FROM sprzedaz_detalicznie
ORDER BY IsoWeek, Channel, StoreName;
```

## Szablon SQL — Ranking kategorii wg zmiany (do znalezienia, co odstaje)

```sql
WITH kategorie_okresy AS (
    SELECT
        dp.Category,
        dd.IsoWeek,
        CAST(SUM(fs.NetAmount) AS DECIMAL(12, 2)) AS Netto_PLN,
        CAST(SUM(fs.Quantity) AS INT) AS Sztuki
    FROM dbo.FactSales fs
    INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
    INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
    GROUP BY dp.Category, dd.IsoWeek
)
SELECT
    Category,
    MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN Netto_PLN END) AS Poprzedni_Netto,
    MAX(CASE WHEN IsoWeek = @TydzienBiezacy THEN Netto_PLN END) AS Biezacy_Netto,
    CAST(
        (MAX(CASE WHEN IsoWeek = @TydzienBiezacy THEN Netto_PLN END) -
         MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN Netto_PLN END)) /
        NULLIF(MAX(CASE WHEN IsoWeek = @TydzienPoprzedni THEN Netto_PLN END), 0) * 100.0
        AS DECIMAL(6, 2)
    ) AS Zmiana_Proc
FROM kategorie_okresy
GROUP BY Category
ORDER BY Zmiana_Proc ASC;
```

> Uwaga: nie agreguj bezpośrednio na wyniku agregatu w tym samym `SELECT` (błąd "Cannot perform an aggregate function on an expression containing an aggregate or a subquery") — dlatego dane są najpierw zebrane w CTE (`kategorie_okresy`), a dopiero potem przestawiane przez `MAX(CASE WHEN ...)`.

## Kiedy przejść do drill-down (głębszy poziom)

Zaproponuj (`#tool:vscode_askQuestions`) zejście niżej, gdy:
- Zmiana na poziomie Category jest duża, ale chcesz wiedzieć, czy dotyczy wszystkich modeli czy jednego (`StyleCode`).
- Wynik per sklep pokazuje duże rozbieżności między lokalizacjami (jeden sklep odstaje).
- Użytkownik pyta "dlaczego" — to sygnał do przejścia w stronę Trybu 4.

## Format odpowiedzi

Jak w Trybie 2, plus dodatkowa tabela przekroju (wymiar w wierszach, okresy/metryki w kolumnach). Jeśli porównujesz dwie grupy (np. MEN vs WOMEN), zestaw je obok siebie w jednej tabeli dla czytelności.
