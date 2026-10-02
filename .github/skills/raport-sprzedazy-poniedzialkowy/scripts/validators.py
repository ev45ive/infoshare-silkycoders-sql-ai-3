"""
Walidacja okresu raportu i danych w bazie.
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pyodbc

logger = logging.getLogger(__name__)


def parse_week_input(week_input: str) -> Optional[Tuple[int, int]]:
    """
    Parsuje wejście użytkownika: numer tygodnia ISO lub datę.
    
    Zwraca: (iso_year, iso_week) lub None jeśli błędny format.
    """
    week_input = week_input.strip()
    
    # Format ISO: 2026-W38
    if "-W" in week_input:
        try:
            year_str, week_str = week_input.split("-W")
            iso_year = int(year_str)
            iso_week = int(week_str)
            if 1 <= iso_week <= 53:
                return (iso_year, iso_week)
        except ValueError:
            pass
    
    # Format data: YYYY-MM-DD
    if "-" in week_input and week_input.count("-") == 2:
        try:
            date_obj = datetime.strptime(week_input, "%Y-%m-%d")
            iso_year, iso_week, _ = date_obj.isocalendar()
            return (iso_year, iso_week)
        except ValueError:
            pass
    
    # Słowo kluczowe: "7days" (ostatnie 7 dni)
    if week_input.lower() == "7days":
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        iso_year, iso_week, _ = seven_days_ago.isocalendar()
        return (iso_year, iso_week)
    
    logger.error(f"Nie mogę sparsować okresu: {week_input}")
    return None


def validate_period_in_dimdate(
    connection_string: str,
    iso_year: int,
    iso_week: int
) -> Tuple[bool, str]:
    """
    Sprawdza czy tydzień ISO istnieje w DimDate z pełnymi 7 dniami.
    
    Zwraca: (is_valid, message)
    """
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) as day_count, MIN(Date) as start_date, MAX(Date) as end_date
        FROM [dbo].[DimDate]
        WHERE IsoYear = ? AND IsoWeek = ?
        """
        
        cursor.execute(query, (iso_year, iso_week))
        row = cursor.fetchone()
        day_count, start_date, end_date = row
        
        conn.close()
        
        if day_count == 0:
            return False, f"Tydzień {iso_year}-W{iso_week} nie istnieje w DimDate"
        elif day_count < 7:
            return False, f"Tydzień {iso_year}-W{iso_week} ma tylko {day_count} dni (oczekiwane 7)"
        else:
            return True, f"✅ Tydzień {iso_year}-W{iso_week} ({start_date} — {end_date}): pełny"
    
    except Exception as e:
        return False, f"Błąd walidacji okresu: {e}"


def validate_data_coverage(
    connection_string: str,
    iso_year: int,
    iso_week: int
) -> Tuple[bool, str]:
    """
    Sprawdza czy FactSales ma dane za cały tydzień.
    
    Zwraca: (is_complete, message)
    """
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(DISTINCT d.Date) as days_with_data
        FROM [dbo].[FactSales] f
        JOIN [dbo].[DimDate] d ON d.DateKey = f.DateKey
        WHERE d.IsoYear = ? AND d.IsoWeek = ?
        """
        
        cursor.execute(query, (iso_year, iso_week))
        row = cursor.fetchone()
        days_with_data = row[0] if row else 0
        
        conn.close()
        
        if days_with_data == 0:
            return False, f"⚠️  RAPORT NIEGOTOWY — brak danych sprzedażowych za tydzień {iso_year}-W{iso_week}"
        elif days_with_data < 7:
            return False, f"⚠️  RAPORT NIEKOMPLETNY — dane za {days_with_data}/7 dni"
        else:
            return True, f"✅ Dane kompletne za wszystkie 7 dni"
    
    except Exception as e:
        return False, f"Błąd sprawdzenia danych: {e}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    test_input = "2026-W38"
    result = parse_week_input(test_input)
    print(f"Parsed: {test_input} -> {result}")
