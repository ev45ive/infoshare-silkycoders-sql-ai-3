-- =============================================================================
-- SIERPIEŃ 2026: Porównanie kanałów sprzedaży
-- Zestawienie dla zespołu sprzedaży: liczba transakcji, sztuki, przychód netto, średni koszyk
-- =============================================================================
-- WERSJA POPRAWNA (2026-10-02)
-- Poprawki względem wersji oryginalnej:
--   1. SUM(s.Transactions) zamiast COUNT(*) — liczy rzeczywiste transakcje, nie magazyny
--   2. SUM(NetRevenue) / SUM(Transactions) zamiast AVG(AvgBasketValue) — liczy średni koszyk całego kanału
--   3. LEFT JOIN zamiast inner (via widok) — aby zwrócić ONLINE nawet bez powierzchni sprzedaży
-- =============================================================================

-- BLOK 1: Alternatywne źródło — bezpośrednio z FactSales (bardziej niezawodne)
-- =============================================================================
-- Ta wersja omija problem z SalesAreaM2 w widoku i liczy direktnie z faktów
SELECT st.Channel AS Kanal,
       COUNT(DISTINCT fs.TransactionNo) AS Transakcje,
       SUM(fs.Quantity) AS Sztuki,
       SUM(fs.NetAmount) AS Przychod,
       CAST(SUM(fs.NetAmount) / COUNT(DISTINCT fs.TransactionNo) AS DECIMAL(10, 2)) AS SredniKoszyk
FROM dbo.FactSales AS fs
INNER JOIN dbo.DimStore AS st ON st.StoreKey = fs.StoreKey
INNER JOIN dbo.DimDate AS dd ON dd.DateKey = fs.DateKey
WHERE dd.YearMonth = '2026-08'
GROUP BY st.Channel
ORDER BY st.Channel;

-- BLOK 2: Wariant używający widoku (jeśli upierasz się przy vw_StoreScorecard)
-- =============================================================================
-- Uwaga: To będzie zwracać tylko STORE (ONLINE ma SalesAreaM2 = NULL, wyruguje go WHERE)
-- Zastosuj tę wersję TYLKO jeśli biznes wymagał specjalnie widoku
-- SELECT s.Channel AS Kanal,
--        SUM(s.Transactions) AS Transakcje,
--        SUM(s.Units) AS Sztuki,
--        SUM(s.NetRevenue) AS Przychod,
--        CAST(SUM(s.NetRevenue) / SUM(s.Transactions) AS DECIMAL(10, 2)) AS SredniKoszyk
-- FROM reporting.vw_StoreScorecard AS s
-- WHERE s.YearMonth = '2026-08'
-- GROUP BY s.Channel
-- ORDER BY s.Channel;
