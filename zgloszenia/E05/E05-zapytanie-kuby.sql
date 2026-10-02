-- Sierpien 2026: porownanie kanalow sprzedazy
-- Jedna linia na kanal dla zespolu sprzedazy.
SELECT s.Channel AS Kanal,
       COUNT(*) AS Transakcje,
       SUM(s.Units) AS Sztuki,
       SUM(s.NetRevenue) AS Przychod,
       CAST(AVG(s.AvgBasketValue) AS DECIMAL(10, 2)) AS SredniKoszyk
FROM reporting.vw_StoreScorecard AS s
WHERE s.YearMonth = '2026-08'
GROUP BY s.Channel
ORDER BY s.Channel;
