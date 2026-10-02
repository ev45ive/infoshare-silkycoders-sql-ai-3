"""
Budowanie zapytań SQL dla raportu sprzedaży.
Dynamicznie tworzy SELECT dla aktualnego tygodnia, poprzedniego, i YoY.
"""

import logging
from typing import Tuple, Dict, Any
from datetime import datetime, timedelta
import pyodbc

logger = logging.getLogger(__name__)


def get_week_dates(iso_year: int, iso_week: int) -> Tuple[str, str]:
    """
    Zwraca daty początkową i końcową dla tygodnia ISO.
    
    Zwraca: (start_date_str, end_date_str) w formacie 'YYYY-MM-DD'
    """
    # Konstruujemy datę pierwszego dnia tygodnia ISO
    jan4 = datetime(iso_year, 1, 4)
    week_one_monday = jan4 - timedelta(days=jan4.weekday())
    target_monday = week_one_monday + timedelta(weeks=(iso_week - 1))
    target_sunday = target_monday + timedelta(days=6)
    
    return target_monday.strftime("%Y-%m-%d"), target_sunday.strftime("%Y-%m-%d")


def build_sales_query(
    iso_year: int,
    iso_week: int,
    include_category: bool = False
) -> str:
    """
    Buduje SQL dla sprzedaży danego tygodnia po kanałach (i opcjonalnie kategoriach).
    
    Zwraca: SELECT z Group By Channel (+ Department, Category jeśli include_category=True)
    """
    start_date, end_date = get_week_dates(iso_year, iso_week)
    
    if include_category:
        group_by = "st.Channel, p.Department, p.Category"
        select_fields = "st.Channel, p.Department, p.Category,"
    else:
        group_by = "st.Channel"
        select_fields = "st.Channel,"
    
    query = f"""
    SELECT
        {select_fields}
        SUM(f.NetAmount) AS NetAmount,
        SUM(f.Quantity) AS Quantity,
        COUNT(DISTINCT f.TransactionNo) AS Transactions
    FROM [dbo].[FactSales] AS f
    JOIN [dbo].[DimDate] AS d ON d.DateKey = f.DateKey
    JOIN [dbo].[DimStore] AS st ON st.StoreKey = f.StoreKey
    JOIN [dbo].[DimProduct] AS p ON p.ProductKey = f.ProductKey
    WHERE d.Date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY {group_by}
    ORDER BY 1
    """
    
    return query


def build_all_queries(iso_year: int, iso_week: int) -> Dict[str, str]:
    """
    Buduje wszystkie potrzebne zapytania dla raportu.
    
    Zwraca:
    {
        'current': SQL dla aktualnego tygodnia,
        'prev_week': SQL dla W-1,
        'yoy': SQL dla tego samego zakresu dat rok temu,
        'current_detail': SQL z kategoriami dla bieżącego tygodnia
    }
    """
    
    # Poprzedni tydzień
    if iso_week > 1:
        prev_week = iso_week - 1
        prev_year = iso_year
    else:
        prev_week = 52
        prev_year = iso_year - 1
    
    # Daty dla YoY (same daty, rok wcześniej)
    start_date, end_date = get_week_dates(iso_year, iso_week)
    
    # Parse dates i przesuń rok wstecz
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    yoy_start = start_dt.replace(year=start_dt.year - 1).strftime("%Y-%m-%d")
    yoy_end = end_dt.replace(year=end_dt.year - 1).strftime("%Y-%m-%d")
    
    # YoY query
    yoy_query = f"""
    SELECT
        st.Channel,
        SUM(f.NetAmount) AS NetAmount,
        SUM(f.Quantity) AS Quantity,
        COUNT(DISTINCT f.TransactionNo) AS Transactions
    FROM [dbo].[FactSales] AS f
    JOIN [dbo].[DimDate] AS d ON d.DateKey = f.DateKey
    JOIN [dbo].[DimStore] AS st ON st.StoreKey = f.StoreKey
    WHERE d.Date BETWEEN '{yoy_start}' AND '{yoy_end}'
    GROUP BY st.Channel
    ORDER BY 1
    """
    
    return {
        'current': build_sales_query(iso_year, iso_week, include_category=False),
        'prev_week': build_sales_query(prev_year, prev_week, include_category=False),
        'yoy': yoy_query,
        'current_detail': build_sales_query(iso_year, iso_week, include_category=True),
    }


def execute_queries(
    connection_string: str,
    queries: Dict[str, str]
) -> Dict[str, Any]:
    """
    Uruchamia wszystkie zapytania i zwraca wyniki.
    
    Zwraca: słownik z wynikami każdego zapytania (lista słowników)
    """
    results = {}
    
    try:
        conn = pyodbc.connect(connection_string)
        conn.execute("SET NOCOUNT ON")
        
        for key, query in queries.items():
            logger.debug(f"Uruchamiam zapytanie: {key}")
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Pobranie wyników jako lista słowników
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            results[key] = rows
            
            logger.info(f"✅ {key}: {len(rows)} wierszy")
        
        conn.close()
        return results
    
    except Exception as e:
        logger.error(f"Błąd egzekucji SQL: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Test
    queries = build_all_queries(2026, 38)
    print("\n=== Current Week Query ===")
    print(queries['current'])
    print("\n=== Previous Week Query ===")
    print(queries['prev_week'])
    print("\n=== YoY Query ===")
    print(queries['yoy'])
