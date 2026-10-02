# Słownik Pól ETL — Szybka Referentka

## src.SalesRaw — Warstwa: Dane Surowe (CSV)

**Cechy:** NVARCHAR wszędzie, brak typów

| Kolumna | Typ | Co To | Uwagi |
|---------|-----|-------|-------|
| `TransactionNo` | nvarchar | Unikalny ID paragonu | Powtarza się wiele razy (LINE ITEMS) |
| `LineNumber` | nvarchar | Numer linii w paragonie | 1, 2, 3... |
| `SalesDate` | nvarchar | Data sprzedaży (naleŻy konwertować) | FORMAT: YYYY-MM-DD |
| `StoreCode` | nvarchar | Kod sklepu | "S001", "S002", "WEB" |
| `SKU` | nvarchar | Kod produktu | Łączy z DimProduct |
| `Quantity` | nvarchar | Ilość (trzeba konwertować na INT) | Może być NULL |
| `UnitPrice` | nvarchar | Cena za jednostkę (trzeba na DECIMAL) | Może być NULL → Problem! |
| `DiscountAmount` | nvarchar | Rabat na linię (trzeba na DECIMAL) | Może być NULL |
| `SourceFile` | nvarchar | Z jakiego pliku CSV | "POS_20260817.csv", "WEB_20260817.csv" |
| `ExtractedAt` | datetime | Kiedy plik załadowano | Czas ETL, nie sprzedaży |

**Kluczowe Kontrole:**
- ✓ `UnitPrice` czy `Quantity` NIE SĄ NULL → Inaczej nie można obliczyć brutto
- ✓ `SalesDate` parsuje się do DATE → Inaczej znowu błąd w konwersji
- ✓ `SourceFile` jest poprawnie przypisany → Ponad plik == zagrożenie duplikatu

---

## stg.Sales — Warstwa: Dane Wstawione (Po TRY_CAST)

**Cechy:** Typy już konwertowane, walidacja się odbył, ale jeszcze bez lookup wymiarów

| Kolumna | Typ | Co To | Różnica od src |
|---------|-----|-------|-----------------|
| `SalesDate` | date | Zkonwertowana data | ✓ Teraz DATE, było nvarchar |
| `Quantity` | int | Zkonwertowana ilość | ✓ Teraz INT, było nvarchar |
| `UnitPrice` | decimal | Zkonwertowana cena | ✓ Teraz DECIMAL, było nvarchar |
| `DiscountAmount` | decimal | Zkonwertowany rabat | ✓ Teraz DECIMAL, było nvarchar |
| `TransactionNo`, `LineNumber`, `StoreCode`, `SKU` | varchar | Są nadal jako tekst | (lookup wymiarów dopiero w dbo) |

**Kluczowe Kontrole:**
- ✓ COUNT(stg) == COUNT(src) → Czy wszystkie wiersze przeszły?
- ✓ SUM(brutto w stg) == SUM(brutto w src) → Czy wartości się zgadzają?
- ✓ Czy brakuje wierszy gdzie Quantity czy UnitPrice to NULL? (TRY_CAST → NULL jeśli konwersja się nie powiedziała)

---

## dbo.FactSales — Warstwa: Fakty (Final, z Wymiarami)

**Cechy:** Wciąż ta sama liczba wierszy, ale z surrogate keys + obliczone Netto

| Kolumna | Typ | Co To |
|---------|-----|-------|
| `DateKey` | int | Lookup na DimDate (np. 20260817) |
| `ProductKey` | int | Lookup na DimProduct |
| `StoreKey` | int | Lookup na DimStore |
| `TransactionNo` | nvarchar | Original TxNo z src |
| `LineNumber` | int | Linia w paragonie |
| `Quantity` | int | Jako w stg |
| `UnitPrice` | decimal | Jako w stg |
| `DiscountAmount` | decimal | Jako w stg |
| `GrossAmount` | decimal | = Quantity * UnitPrice - DiscountAmount (obliczone) |
| `NetAmount` | decimal | = GrossAmount / 1.23 (VAT 23%) |
| `UnitCost` | decimal | Koszt artykułu (ze DimProduct) |
| `LoadId` | int | Którego laodu to pochodzi (tracking) |

**Kluczowe Kontrole:**
- ✓ COUNT(dbo) == COUNT(stg) == COUNT(src) → Czy wszystkie wiersze
- ✓ SUM(GrossAmount w dbo) == SUM(brutto w stg) → Czy lookup wymiarów nie zmienił wartości
- ✓ NetAmount = GrossAmount / 1.23 (dokładnie) → Czy VAT się obliczył
- ✓ `LoadId` jest zawsze > 0 → Każdy wiersz musi być przypisany do ładowania

---

## dbo.DimDate — Wymiar: Daty (Calendar)

**Cechy:** Jedna linia = jeden dzień, zawiera metadane kalendarza

| Kolumna | Format | Przykład | Użycie |
|---------|--------|---------|--------|
| `DateKey` | int (YYYYMMDD) | 20260817 | Klucz do FactSales.DateKey |
| `Date` | date | 2026-08-17 | Czytanie ludzie |
| `Year` | int | 2026 | WHERE clause |
| `Month` | int | 8 | WHERE clause |
| `MonthName` | varchar | August | Raporty |
| `YearMonth` | varchar | 2026-08 | Agregacja do miesiąca |
| `DayOfWeek` | int | 2 (Monday=1) | Grupowanie po dniach tygodnia |
| `DayName` | varchar | Monday | Raporty |
| `IsWeekend` | bit | 0 | Filtr weekend vs robocze |
| `IsoYear` | int | 2026 | ISO-8601 (dla przychodu) |
| `IsoWeek` | int | 33 | ISO-8601 (dla przychodu) |
| `YearWeek` | varchar | 2026-W33 | ISO format (dla przychodu) |

**Kluczowe Kontrole:**
- ✓ DateKey zawsze YYYYMMDD (np. 20260817 = 17 sierpnia 2026)
- ✓ Jeśli szukasz daty w FactSales, JOIN na `dd.Date = '2026-08-17'` **LUB** `fs.DateKey = 20260817`
- ✓ ISO tygodnie (IsoWeek) nie pokrywają się z miesiącami! (PU pojawi się w poprzednim ISO roku)

---

## dbo.DimStore — Wymiar: Sklepy

| Kolumna | Typ | Co To | Wartości |
|---------|-----|-------|----------|
| `StoreKey` | int | Surrogate key | 1, 2, 3, ... |
| `StoreCode` | varchar | Original code z src | "S001", "S002", "S003", "S004", "S005", "WEB" |
| `StoreName` | varchar | Czytelna nazwa | "Store 1", "Store 2", "Online" |
| `Channel` | varchar | Kanał sprzedaży | "STORE" lub "ONLINE" |
| `SalesAreaM2` | decimal | Metraż sklepu | NULL dla ONLINE |

**Kluczowe Kontrole:**
- ✓ ONLINE zawsze: StoreCode="WEB", Channel="ONLINE"
- ✓ STORE zawsze: StoreCode=S00X, Channel="STORE"
- ✓ 5 sklepów stacjonarnych + 1 ONLINE = 6 rekordy razem

---

## dbo.DimProduct — Wymiar: Produkty

| Kolumna | Typ | Co To |
|---------|-----|-------|
| `ProductKey` | int | Surrogate key |
| `SKU` | varchar | Original SKU z src |
| `ProductName` | varchar | Czytelna nazwa produktu |
| `Category` | varchar | Kategoria produktu |
| `UnitCost` | decimal | Koszt artykułu (dla marża) |

**Kluczowe Kontrole:**
- ✓ SKU jest unikalny (jeden SKU = jeden ProductKey)
- ✓ UnitCost jest zawsze >= 0

---

## dbo.FactReturns — Fakt: Zwroty

| Kolumna | Typ | Co To | Uwagi |
|---------|-----|-------|-------|
| `DateKey` | int | Data zwrotu (YYYYMMDD) | Join na DimDate |
| `ProductKey` | int | Produkt zwracany | Join na DimProduct |
| `StoreKey` | int | Gdzie zwrócono | Join na DimStore |
| `ReturnAmount` | decimal | Kwota zwrotu (z VAT!) | **⚠️ To brutto, zawiera 23% VAT** |
| `LoadId` | int | Tracking |

**Kluczowe Kontrole:**
- ✓ ReturnAmount zawsze zawiera VAT (23%)
- ✓ Aby policzyć "netto zwroty", dziel przez 1.23 ← **Ważne!**
- ✓ "Sprzedaż po zwrotach" = SUM(FactSales.NetAmount) - SUM(FactReturns.ReturnAmount / 1.23)

---

## dbo.LoadLog — Log: Załadowań ETL

| Kolumna | Typ | Co To |
|---------|-----|-------|
| `LoadId` | int | ID tego załadowania |
| `PackageName` | varchar | Nazwa procedury SSIS (np. etl.LoadSales) |
| `FinishedAt` | datetime | Kiedy się skończyło |
| `Status` | varchar | SUCCEEDED, FAILED, RUNNING |
| `RowsRead` | int | Ile wierszy ze źródła |
| `RowsLoaded` | int | Ile zaakceptowanych |
| `RowsRejected` | int | Ile odrzuconych (problemy w konwersji) |
| `ErrorMessage` | varchar | Opis błędu (jeśli Status ≠ SUCCEEDED) |

**Kluczowe Kontrole:**
- ✓ `RowsRejected` == 0 → Wszystko przeszło bez problemów
- ✓ `RowsRead` == `RowsLoaded` → Nie ubyło danych
- ✓ `Status` == 'SUCCEEDED' → Nie było przerwań

---

## Szybkie Sprawdzenia — Diagnoza

| Problem | Gdzie Szukać | Co Sprawdzić |
|---------|--------------|-------------|
| Brakuje wierszy | src vs stg vs dbo | Czy COUNT się zgadza na każdej warstwie? |
| Brakuje pieniędzy | src vs stg vs dbo | Czy SUM(brutto) się zgadza? |
| Brakuje parametru | src.Sales[Column] | Czy kolumna jest NULL w src? |
| Duplikaty | src.SalesRaw | Czy TransactionNo pojawia się 2+ razy? |
| VAT źle | dbo.FactSales | Czy NetAmount = GrossAmount / 1.23? |
| Datum źle | dbo.DimDate | Czy DateKey odpowiada dacie? |
| Kanał źle | dbo.DimStore | Czy Channel jest poprawnie przypisany? |

---

## Porada: Czytanie Łączności

```sql
-- Typowy join:
SELECT SUM(fs.NetAmount) AS SprzedazNetto
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
INNER JOIN dbo.DimStore ds ON fs.StoreKey = ds.StoreKey
WHERE dd.Year = 2026 AND dd.Month = 8
    AND ds.Channel = 'STORE'
```

**Czyta się jako:**
- Zacznij od `FactSales` (fakty)
- Lookup `DimDate` by pobrać datę (fs.DateKey)
- Lookup `DimStore` by pobrać kanał (fs.StoreKey)
- Filtruj August 2026, tylko STORE
- Zsumuj netto

**Zasada:** Zawsze zaczynaj od **Facts**, potem dodawaj **Dimensions** (1-to-Many)
