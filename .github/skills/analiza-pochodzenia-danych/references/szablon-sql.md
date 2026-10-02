# Szablony SQL — Copy-Paste Ready

## 1. Rozbój Anomalii: Dzień po Dniu

```sql
-- Rozbij sprzedaż sierpień po dniach
-- Szukamy której dnia są 30-50% wyższe od średniej

SELECT 
    dd.Date AS Data,
    DATENAME(weekday, dd.Date) AS DzienTygodnia,
    SUM(fs.NetAmount) AS SprzedazNetto,
    COUNT(DISTINCT fs.TransactionNo) AS Paragony,
    COUNT(*) AS Pozycje,
    ROUND(SUM(fs.NetAmount) / COUNT(DISTINCT fs.TransactionNo), 2) AS KoszzykNetto,
    ROUND(100.0 * SUM(fs.NetAmount) / (SELECT SUM(NetAmount) FROM dbo.FactSales WHERE Year = 2026 AND Month = 8), 1) AS ProcentMiesiaca
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Year = 2026 AND dd.Month = 8
GROUP BY dd.Date, DATENAME(weekday, dd.Date)
ORDER BY dd.Date
```

**Co czytać:**
- `SprzedazNetto` — całkowita sprzedaż netto na dzień
- `Paragony` — liczba unikalnych transakcji
- `Pozycje` — liczba linii w koszyku
- `KoszzykNetto` — średnia wartość paragonu (netto)
- Jeśli `KoszzykNetto` jest 50-100% wyższy niż inne dni → **anomalia w wartości**
- Jeśli `Paragony` normalne ale `Pozycje` wysoka → **anomalia w ilościach/zwracanych przedmiotach**

---

## 2. Rozbój po Kanałach: Który Kanał Sprawca?

```sql
-- Rozbij anomalię przez kanały
SELECT 
    ds.Channel AS Kanal,
    SUM(fs.NetAmount) AS SprzedazNetto,
    COUNT(DISTINCT fs.TransactionNo) AS Paragony,
    COUNT(*) AS Pozycje
FROM dbo.FactSales fs
INNER JOIN dbo.DimStore ds ON fs.StoreKey = ds.StoreKey
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Date = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ
GROUP BY ROLLUP(ds.Channel)  -- ROLLUP daje razem na końcu
ORDER BY KANAL DESC
```

**Co czytać:**
- Czy anomalia jest w STORE czy ONLINE czy obu?
- To zawęża problem do konkretnych plików CSV

---

## 3. Porównanie Wierszy na Każdej Warstwie ETL

```sql
-- Czy liczba wierszy jest konsystentna między warstwami?
SELECT 'src.SalesRaw' AS Warstwa, COUNT(*) AS Wiersze
FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ

UNION ALL

SELECT 'stg.Sales', COUNT(*)
FROM stg.Sales
WHERE SalesDate = '2026-08-17'

UNION ALL

SELECT 'dbo.FactSales', COUNT(*)
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Date = '2026-08-17'
```

**Co czytać:**
- Jeśli wszystkie warstwa mają tę samą liczbę wierszy → `✓ OK`
- Jeśli się różnią → `✗ Błąd w transformacji`

---

## 4. Porównanie Sum Brutto na Każdej Warstwie

```sql
-- Czy sumy pieniędzy się zgadzają między warstwami?
SELECT 
    'src.SalesRaw' AS Warstwa,
    COUNT(*) AS Wiersze,
    SUM(TRY_CAST(Quantity AS DECIMAL(10,2)) * TRY_CAST(UnitPrice AS DECIMAL(10,2))
        - ISNULL(TRY_CAST(DiscountAmount AS DECIMAL(10,2)), 0)) AS Brutto
FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ

UNION ALL

SELECT 'stg.Sales', COUNT(*), SUM(Quantity * UnitPrice - DiscountAmount)
FROM stg.Sales
WHERE SalesDate = '2026-08-17'

UNION ALL

SELECT 'dbo.FactSales (brutto)', COUNT(*), SUM(GrossAmount)
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Date = '2026-08-17'

UNION ALL

SELECT 'dbo.FactSales (netto)', COUNT(*), SUM(NetAmount)
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Date = '2026-08-17'
```

**Co czytać:**
- `src` brutto powinno = `stg` brutto powinno = `dbo` brutto
- Netto zawsze = Brutto / 1.23
- Jeśli src ≠ stg → **Błąd w TRY_CAST (NULL values w kolumnie)**
- Jeśli stg ≠ dbo → **Błąd w lookup wymiarów**

---

## 5. Identyfikacja Pliku Źródłowego — Które CSV?

```sql
-- Która plik zawiera ile wierszy i jaką kwotę?
SELECT 
    r.SourceFile AS Plik,
    COUNT(*) AS Wiersze,
    SUM(TRY_CAST(r.Quantity AS DECIMAL) * TRY_CAST(r.UnitPrice AS DECIMAL)
        - ISNULL(TRY_CAST(r.DiscountAmount AS DECIMAL), 0)) AS Brutto,
    COUNT(DISTINCT r.TransactionNo) AS UnikalneTransakcje,
    MIN(TRY_CAST(r.SalesDate AS DATE)) AS OdDaty,
    MAX(TRY_CAST(r.SalesDate AS DATE)) AS DoDaty
FROM src.SalesRaw r
WHERE TRY_CAST(r.SalesDate AS DATE) = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ
GROUP BY r.SourceFile
ORDER BY r.SourceFile
```

**Co czytać:**
- Jeśli 2 pliki mają identyczne Wiersze + Brutto → **Potencjalny duplikat (np. _RETRY)**
- Patrz na nazwy plików — jeśli widzisz `_RETRY` czy `_BACKUP` → wyjaśniam why

---

## 6. Szukanie Duplikatów: TransactionNo Się Powtarza?

```sql
-- Czy TransactionNo pojawia się więcej niż raz?
-- (To wskaż istnienie duplikat rekordu / zduplikowany plik)

SELECT 
    TransactionNo,
    COUNT(*) AS IleRazy,
    STRING_AGG(SourceFile, ', ') AS Pliki
FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ
GROUP BY TransactionNo
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
```

**Co czytać:**
- Jeśli jest wynik → Duplikaty znalezione
- `IleRazy` = ile razy się powtarza
- `Pliki` = które CSV zawierają duplikaty
- Jeśli `IleRazy = 2` i oba z _RETRY pliku → definitywnie duplikat

---

## 7. Pełna Zawartość Anomalnego Dnia — Gdzie Szukać

```sql
-- Pokaż mi dokładnie jakie transakcje są na anomalnym dniu
SELECT TOP 20  -- ZMIEŃ NA 100+ jeśli chcesz całość
    r.SourceFile,
    r.TransactionNo,
    r.LineNumber,
    r.SalesDate,
    r.Quantity,
    r.UnitPrice,
    r.DiscountAmount,
    TRY_CAST(r.Quantity AS DECIMAL) * TRY_CAST(r.UnitPrice AS DECIMAL)
        - ISNULL(TRY_CAST(r.DiscountAmount AS DECIMAL), 0) AS Brutto
FROM src.SalesRaw r
WHERE TRY_CAST(r.SalesDate AS DATE) = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ
ORDER BY r.SourceFile, r.TransactionNo, r.LineNumber
```

**Co czytać:**
- Wizualne przejrzenie rekordu po rekordzie
- Czy wartości wyglądają normalnie (Quantity > 0, UnitPrice > 0)?
- Czy są NULLy w kolumnach krytycznych?

---

## 8. Weryfikacja VAT: Czy Netto = Brutto / 1.23?

```sql
-- Czy konwersja VAT jest spójna?
SELECT TOP 20
    fs.TransactionNo,
    fs.GrossAmount,
    fs.NetAmount,
    ROUND(fs.GrossAmount / 1.23, 2) AS NettoTeoria,
    fs.NetAmount - ROUND(fs.GrossAmount / 1.23, 2) AS Roznica
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
WHERE dd.Date = '2026-08-17'  -- ZMIEŃ NA ANOMALNY DZIEŃ
    AND ABS(fs.NetAmount - ROUND(fs.GrossAmount / 1.23, 2)) > 0.01  -- Szukamy różnic > 1 grosz
ORDER BY ABS(Roznica) DESC
```

**Co czytać:**
- Jeśli `Roznica` ≠ 0 → błąd w obliczeniu Netto
- Zwykle wszystkie różnice = 0 (zaokrąglenie)
- Jeśli są większe różnice → **Anomalia w formuł Netto**

---

## 9. Historia LoadLog — Kiedy To Załadowano?

```sql
-- Kiedy dane zostały załadowane do hurtowni?
SELECT 
    LoadId,
    PackageName,
    FinishedAt,
    Status,
    RowsRead,
    RowsLoaded,
    RowsRejected
FROM dbo.LoadLog
WHERE PackageName LIKE '%Sales%'  -- Szukamy Sale load'u
ORDER BY FinishedAt DESC
```

**Co czytać:**
- `Status` powinno być SUCCEEDED
- `RowsRejected` powinno być 0 (jeśli > 0 → dane miały problemy)
- `FinishedAt` mówi Ci kiedy ETL ran

---

## Zsumowanie: Przebieg Analityki

1. 📊 Rozbój anomalii (Query 1 lub 2) → Znajdź anomalny dzień/kanał
2. 📈 Porównanie wierszy (Query 3) → Czy liczby się zgadzają?
3. 💰 Porównanie sum (Query 4) → Czy pieniądze się zgadzają?
4. 📂 Identyfikacja pliku (Query 5) → Które CSV są podejrzane?
5. 🔍 Szukanie duplikatów (Query 6) → Czy TransactionNo się powtarza?
6. 👁️ Przegląd surowych danych (Query 7) → Czy wartości wyglądają ok?
7. ✅ Weryfikacja VAT (Query 8) → Czy netto = brutto / 1.23?
8. 📅 Historia LoadLog (Query 9) → Kiedy to załadowano?

**Jeśli wciąż nie wiesz:** Porzuć najnowsze dane i zrepetyuj na poprzednim miesiącu — czy problem tam też istnieje?
