-- =============================================================================
-- [NAZWA RAPORTU / ANALIZA]
-- =============================================================================
-- Kontekst:
--   Cel:    [Opisz co to zapytanie powinno zwrócić biznesowo]
--   Okres:  [Jaki zakres czasowy]
--   Źródło: [Jakie tabele i dlaczego te akurat]
--   Metryki: [Jakie metryki i czy są w slownik-metryk.md]
--
-- Poprawki względem wersji oryginalne:
--   1. [Problem 1] - [Poprawka 1]
--   2. [Problem 2] - [Poprawka 2]
--   3. [itd.]
-- =============================================================================

-- BLOK 1: Przyłączenie wymiarów
-- (Rozjaśnienie: FactSales to poziom transakcji, przyłączamy wymiary by mieć kontekst)
SELECT st.Channel AS Kanal,
       COUNT(DISTINCT fs.TransactionNo) AS Transakcje,  -- COUNT DISTINCT — każda transakcja raz, nie po sztuce
       SUM(fs.Quantity) AS Sztuki,
       SUM(fs.NetAmount) AS Przychod,
       CAST(SUM(fs.NetAmount) / COUNT(DISTINCT fs.TransactionNo) AS DECIMAL(10, 2)) AS SredniKoszyk
       -- Średni koszyk = suma przychodu kanału / suma transakcji kanału
       -- (nie: AVG(AvgBasketValue) — to byłoby średnia ze średnich)

FROM dbo.FactSales AS fs
INNER JOIN dbo.DimStore AS st ON st.StoreKey = fs.StoreKey  -- Dołącz wymiar sklepu (kanał, lokalizacja)
INNER JOIN dbo.DimDate AS dd ON dd.DateKey = fs.DateKey    -- Dołącz wymiar daty (YearMonth, tydzień, etc.)

-- BLOK 2: Filtr czasowy
-- (Ograniczenie do okresu zainteresowania — upewnij się że data kolumny i format się zgadzają)
WHERE dd.YearMonth = '2026-08'
-- Alternatywnie: WHERE dd.IsoYear = 2026 AND dd.IsoWeek = 34

-- BLOK 3: Agregacja i sortowanie
-- (Grupowanie po kanałach — każdy kanał w osobnym wierszu)
GROUP BY st.Channel
ORDER BY st.Channel;

-- =============================================================================
-- NOTATKI DLA ODBIORCY (usuń w ostatecznej wersji)
-- =============================================================================
-- ✅ Założenia przyjęte:
--    - Pytanie biznesowe: [opisz]
--    - Okresy: pełne miesiące [wymień]
--    - Kanały: ONLINE i STORE (z DimStore.Channel)
--    - Sprzedaż netto (bez VAT)
--    - Liczba transakcji: DISTINCT TransactionNo (przed agregacją)
--
-- ❓ Otwarte pytania do biznesu:
--    - Czy sprzedaż powinna być netto czy brutto po zwrotach?
--    - Czy chcecie widzieć podział per sklep czy per kanał razem?
--    - Dlaczego brak danych ONLINE w sierpniu? (czy to anomalia?)
--
-- 📚 Słownik metryk: docs/slownik-metryk.md
-- 🗂️  Tabele: RetailDW/Tables/dbo.FactSales.sql, dbo.DimStore.sql, dbo.DimDate.sql
