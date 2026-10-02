# Procedura Interaktywna — Ścieżka po Kroku

## Czy To Naprawdę Anomalia?

**Przed** zalewem się w analizę, odpowiedz na 3 pytania:

1. **Czy metryka jest poprawnie obliczana?**
   - Sprawdź formułę w [slownik-metryk.md](../../docs/slownik-metryk.md)
   - Czy VAT jest inkludowany / ekskludowany poprawnie?
   - Czy okres się zgadza (pełny miesiąc czy część)?

2. **Czy porównujesz to samo do tego samo?**
   - Ten sam kanał? (ONLINE ≠ STORE)
   - Ten sam harmonogram? (podatek zmienia się co roku)
   - Czy dane są w tej samej walucie?

3. **Czy źródło danych jest godne zaufania?**
   - Pochodzi ze słownika merytorycz czy to właśnie liczymy?
   - Czy to wczorajsza liczba czy dziś obliczona?

---

## Faza 1: Rozmowa Początkowa (5-10 min)

### Pytania dla Ciebie

Zanim sformułuję plan, odpowiedz zwięźle:

```
📋 CONTEXT
- Metryka: ________ (np. "sprzedaż netto sierpień 2026")
- Okres: ________ (dzień/tydzień/miesiąc/rok)
- Kanał: ________ (STORE / ONLINE / wszystkie)
- Gdzie znalazłeś anomalię? (raport/dashboard/sms od szefa?)

🔢 LICZBY
- Oczekiwana wartość: ________ PLN
- Zaobserwowana wartość: ________ PLN
- Różnica: ________ PLN lub ________ %

📌 CO JUŻ WIESZ?
- Czy problem jest na poziomie dnia czy tygodnia?
- Czy dotyczy jednego kanału czy wszystkich?
- Czy znasz przybliżony dzień gdy się pojawiło?

💭 HIPOTEZY (min. 2-3)
1. ________ (np. "Zduplikowana sprzedaż POS")
2. ________ (np. "Brakujące zapisy w danym dniu")
3. ________ (np. "Błąd konwersji VAT na określonym dniu")
```

→ **Gotowy? Pokaż mi te odpowiedzi. Zatwierdzę założenia i proponuję kolejny krok.**

---

## Faza 2: Rozbój Anomalii — Zawęź Zakres (10-15 min)

Jeśli anomalia jest szeroka (cały miesiąc), musimy znaleźć "układ molekuł":

### Jeśli anomalia dotyczy całego **miesiąca**:
```sql
-- Rozbij dzień po dniu
SELECT Date, SUM(NetAmount) AS SprzedazNetto, COUNT(DISTINCT TransactionNo) AS Paragony
FROM dbo.FactSales
WHERE Year = 2026 AND Month = 8
GROUP BY Date
ORDER BY Date
```
→ Szukamy dnia(dni) które są 30-50% wyższe od średniej

### Jeśli anomalia dotyczy **kanału** na całym poziomie:
```sql
-- Rozbij kanał po kanale, dzień po dniu
SELECT Channel, Date, SUM(NetAmount)
FROM dbo.FactSales
GROUP BY Channel, Date
ORDER BY Channel, Date
```
→ Szukamy tego czy problem jest globalny czy lokalny

### Jeśli masz już **konkretny dzień**:
→ Przejdź do Fazy 3: Śledzenie Źródła

---

## Faza 3: Śledzenie Źródła (15-20 min)

Po znalezieniu anomalnego dnia (lub kilku dni), śledzisz źródło:

### Krok 3a: Porównaj Wiersze Między Warstwami

```sql
-- src.SalesRaw
SELECT COUNT(*) FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'
-- Wynik: X wierszy

-- stg.Sales  
SELECT COUNT(*) FROM stg.Sales
WHERE SalesDate = '2026-08-17'
-- Wynik: X wierszy (powinno być identyczne)

-- dbo.FactSales
SELECT COUNT(*) FROM dbo.FactSales
WHERE DateKey = '20260817'
-- Wynik: X wierszy (powinno być identyczne)
```

**Jeśli liczby się zgadzają** → przejdź do 3b  
**Jeśli się różnią** → błąd w transformacji (rzadko w RetailDW)

### Krok 3b: Sprawdź Sumy Brutto Między Warstwami

```sql
-- src.SalesRaw (brutto)
SELECT SUM(TRY_CAST(Quantity AS DECIMAL) * TRY_CAST(UnitPrice AS DECIMAL) 
           - ISNULL(TRY_CAST(DiscountAmount AS DECIMAL), 0)) AS Brutto
FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'

-- stg.Sales (brutto)
SELECT SUM(Quantity * UnitPrice - DiscountAmount) AS Brutto
FROM stg.Sales
WHERE SalesDate = '2026-08-17'

-- dbo.FactSales (brutto)
SELECT SUM(GrossAmount) AS Brutto
FROM dbo.FactSales
WHERE DateKey = '20260817'
```

**Jeśli wszystkie trzy sumy się zgadzają:**  
→ Problem nie w ETL transformacji  
→ Przejdź do 3c: Szukaj duplikatów w źródle

**Jeśli nie zgadzają się:**  
→ Błąd w konwersji między warstwami  
→ Szukaj NULL w kolumnach krytycznych w stg.Sales

### Krok 3c: Identyfikuj Źródło — Które Pliki?

```sql
SELECT 
    r.SourceFile,
    COUNT(*) AS Wiersze,
    SUM(TRY_CAST(r.Quantity AS DECIMAL) * TRY_CAST(r.UnitPrice AS DECIMAL)
        - ISNULL(TRY_CAST(r.DiscountAmount AS DECIMAL), 0)) AS Brutto
FROM src.SalesRaw r
WHERE TRY_CAST(r.SalesDate AS DATE) = '2026-08-17'
GROUP BY r.SourceFile
ORDER BY r.SourceFile
```

**To pokaże CI wiele do każdego pliku CSV zawiera:**  
- Czy pewne pliki są identyczne? (Wskaźnik duplikatu)
- Czy wiersze sum są logiczne?

### Krok 3d: Szukaj Duplikatów w Wierszach

```sql
-- Czy TransactionNo się powtarza?
SELECT TransactionNo, COUNT(*) AS CzyDuplikat
FROM src.SalesRaw
WHERE TRY_CAST(SalesDate AS DATE) = '2026-08-17'
GROUP BY TransactionNo
HAVING COUNT(*) > 1
ORDER BY CzyDuplikat DESC
```

**Jeśli są duplikaty:**  
- Która kolumna różni się? (LineNumber? Product?)
- Czy wszystkie kolumny są identyczne? (FULL DUPLIKAT = może z _RETRY pliku)

---

## Faza 4: Potwierdzenie Hipotezy (5 min)

Po znalezieniu podejrzanego pliku / duplikatu / NULL:

**Sformułuj precyzyjnie:**
```
ROOT CAUSE: ____________________________________
(np. "POS_20260817_RETRY.csv zawiera dokładny duplikat POS_20260817.csv")

SKALA: ____________________________________
- Ile wierszy: X
- Ile PLN brutto: Y
- Ile PLN netto (Y/1.23): Z
- Czy to wyjaśnia różnicę anomalii?

ŁATWA NAPRAWA?: (TAK / NIE / WYMAGA DYSKUSJI)
```

→ **Gotowy? Pokaż mi te odpowiedzi. Tworzę końcowy raport.**

---

## Faza 5: Raport Końcowy (5 min)

Dokumentuję w formie:

```markdown
## Anomalia: [Nazwa]
**Data:** [Data]  
**Metryka:** [Metryka]  
**Różnica:** [Liczby]

## Root Cause
[Wysoko-poziomowe wyjaśnienie]

## Dowód (SQL + Wyniki)
```

Wysyłam raport do Team i koordynuję dalsze kroki (czy trzeba czyszczenia danych).

---

## Checklist — Jak Wiesz Że Skończyłeś?

- [ ] Anomalia ma nazwę (data/kanał/metryka)
- [ ] Root cause jest zidentyfikowany i zweryfikowany na bazie
- [ ] SQL query jest łatwością do powielenia (comentarze + gotowe)
- [ ] Rozumiesz skalę problemu (liczba wierszy, PLN, % do metryk)
- [ ] Wiesz czy to jednorazowy incident czy systematyczny problem
- [ ] Znasz następne kroki (korekta danych? Zmiana ETL? Just inform team?)
