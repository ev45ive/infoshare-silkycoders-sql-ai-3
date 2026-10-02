/*
    Stock availability: for a given day, store and category, the share of SKUs
    that had stock left at the close of trading.

    Built from the stock feed, so a day only appears for a store that actually
    reported that day.
    
    WARNING: This view calculates UNWEIGHTED availability (average per category).
    If you aggregate this for a whole period, large categories have the same weight
    as small categories. For example:
      - Jackets (24% of catalog): 97.5% availability
      - Dresses (3% of catalog): 100% availability
    Result from this view: (97.5 + 100) / 2 = 98.75% (unweighted)
    
    If you need WEIGHTED availability (actual inventory %), query FactInventoryDaily directly:
      SELECT CAST(100.0 * SUM(CASE WHEN StockQuantity > 0 THEN 1 ELSE 0 END) / COUNT(*)
             AS DECIMAL(5,2)) FROM dbo.FactInventoryDaily
    That will give ~99.2% (weighted by catalog size).
    
    Always specify which method you used when reporting availability.
*/
CREATE VIEW [reporting].[vw_StockAvailability]
AS
SELECT  d.[Date]        AS [SnapshotDate],
        d.[YearMonth],
        d.[YearWeek],
        st.[StoreCode],
        st.[StoreName],
        p.[Department],
        p.[Category],
        COUNT(*)                                                    AS [SkuCount],
        SUM(CASE WHEN i.[StockQuantity] > 0 THEN 1 ELSE 0 END)      AS [SkuInStock],
        CAST(100.0 * SUM(CASE WHEN i.[StockQuantity] > 0 THEN 1 ELSE 0 END) / COUNT(*)
             AS DECIMAL (5, 2))                                     AS [AvailabilityPct],
        SUM(i.[StockQuantity])                                      AS [StockQuantity]
FROM    [dbo].[FactInventoryDaily] AS i
JOIN    [dbo].[DimDate]            AS d  ON d.[DateKey]    = i.[DateKey]
JOIN    [dbo].[DimStore]           AS st ON st.[StoreKey]  = i.[StoreKey]
JOIN    [dbo].[DimProduct]         AS p  ON p.[ProductKey] = i.[ProductKey]
GROUP BY d.[Date], d.[YearMonth], d.[YearWeek],
         st.[StoreCode], st.[StoreName], p.[Department], p.[Category];
