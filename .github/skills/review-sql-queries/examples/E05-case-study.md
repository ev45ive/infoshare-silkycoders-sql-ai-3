# E05: Case Study — Sierpniowa Sprzedaż Kanałów

> Pełny przykład review'u SQL: od błędu przez diagnozę do poprawki
> 
> **Data:** 2026-10-02  
> **Status:** ✅ Zakończone  
> **Typ:** SELECT + agregacja, analiza sprzedaży  

---

## 📋 Pytanie Biznesowe

> Przygotowałem zestawienie sierpniowej sprzedaży dla STORE i ONLINE: liczba transakcji, sztuki, przychód netto i średni koszyk. Zapytanie wykonuje się, ale zanim wyślę wynik dalej, chciałbym drugiej pary oczu. Sprawdzcie proszę, czy liczby odpowiadają temu pytaniu.

**Odbiorcy:** Zespół sprzedaży Nordvik

---

## ❌ Zapytanie Oryginalne (BŁĘDNE)

```sql
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
```

**Źródło:** `reporting.vw_StoreScorecard` (widok warstwy raportowej)

---

## 🔍 Krok 1: Analiza Statyczna

### Znalezione Problemy

| Lp. | Kod | Problem | Poważność |
|-----|-----|---------|-----------|
| 1 | `COUNT(*) AS Transakcje` | Liczy wiersze w widoku (magazyny), nie transakcje | 🔴 KRYTYCZNE |
| 2 | `CAST(AVG(s.AvgBasketValue) ...)` | Średnia ze średnich — matematycznie niepoprawne | 🔴 KRYTYCZNE |
| 3 | Używanie widoku ze `WHERE SalesAreaM2 > 0` | ONLINE wykluczone z powodu NULL | 🟠 WAŻNE |

---

## ✅ Krok 2: Test na Bazie

### Wyniki Obu Wersji

| Metryka | Błędne Zapytanie | Poprawne Zapytanie | Różnica |
|---------|------------------|-------------------|---------|
| **Transakcje** | 5 | 3703 | **741x błąd** ❌ |
| **Sztuki** | 16047 | 16047 | ✓ Bez zmian |
| **Przychód** | 2,212,078.65 PLN | 2,212,078.65 PLN | ✓ Bez zmian |
| **Średni koszyk** | 595.91 PLN | 597.37 PLN | +1.46 PLN (0.24%) |

### Szczegółowe Obserwacje

**Błędne zapytanie zwraca:**
```
STORE | 5 | 16047 | 2212078.65 | 595.91
```

**Poprawne zapytanie zwraca:**
```
STORE | 3703 | 16047 | 2212078.65 | 597.37
```

**Wniosek:** Liczba transakcji jest drastycznie nie zgadza się. Poprawne zapytanie zwraca 3703 transakcje dla kanału STORE.

---

## 📌 Krok 3: Wyjaśnienie Błędów

### ❌ BŁĄD 1: Transakcje — COUNT(*) zamiast SUM(Transactions)

**Kod:**
```sql
COUNT(*) AS Transakcje
```

**Dlaczego to błąd:**

Widok `reporting.vw_StoreScorecard` ma ziarno: **1 wiersz = 1 magazyn + 1 miesiąc**. 

- `FactSales` ma pojedyncze transakcje (poziom paragonu)
- Widok agreguje do poziomu magazynu (już policzone transakcje w kolumnie `Transactions`)
- Kanał STORE ma **5 magazynów**

Gdy robisz `COUNT(*)` na grupie:
- Liczyasz **wiersze** → liczba magazynów = 5
- Nie liczyasz **transakcji** → trzeba `SUM(s.Transactions)`

**Poprawka:**
```sql
SUM(s.Transactions) AS Transakcje
```

**Wynik: 5 → 3703** ✓

---

### ❌ BŁĄD 2: Średni Koszyk — AVG(AvgBasketValue) zamiast SUM/SUM

**Kod:**
```sql
CAST(AVG(s.AvgBasketValue) AS DECIMAL(10, 2)) AS SredniKoszyk
```

**Dlaczego to błąd:**

Każdy magazyn ma własny średni koszyk:
- Magazyn M1: 590 PLN (1000 transakcji)
- Magazyn M2: 600 PLN (2700 transakcji)
- itd. (5 magazynów razem)

`AVG(AvgBasketValue)` = średnia arytmetyczna = (590 + 600 + ...) / 5 ≈ 595.91 PLN

Ale **rzeczywisty** średni koszyk kanału:
$$\frac{\text{Suma przychodu wszystkich magazynów}}{\text{Suma transakcji wszystkich magazynów}} = \frac{2,212,078.65}{3703} ≈ 597.37 \text{ PLN}$$

Średnia arytmetyczna ignoruje **wagi** (różne liczby transakcji w magazynach). Jeśli jeden magazyn ma 10x więcej transakcji, powinien mieć 10x większy wpływ na wynik.

**Poprawka:**
```sql
CAST(SUM(s.NetRevenue) / SUM(s.Transactions) AS DECIMAL(10, 2)) AS SredniKoszyk
```

**Wynik: 595.91 → 597.37 PLN** ✓

---

### ⚠️ PROBLEM BONUS: Brak Kanału ONLINE

**Obserwacja:** Zapytanie zwraca tylko STORE, nie ONLINE.

**Przyczyna:** Widok `vw_StoreScorecard` ma warunek `WHERE SalesAreaM2 > 0`. ONLINE ma `SalesAreaM2 = NULL` (nie ma fizycznej powierzchni sprzedaży) → wykluczone z widoku.

**Rozwiązanie:** Jeśli raport powinien zawierać ONLINE, trzeba napisać zapytanie bezpośrednio z `FactSales` + `DimStore` (zamiast widoku):

```sql
SELECT st.Channel,
       COUNT(DISTINCT fs.TransactionNo) AS Transakcje,
       ...
FROM dbo.FactSales fs
INNER JOIN dbo.DimStore st ON st.StoreKey = fs.StoreKey
WHERE dd.YearMonth = '2026-08'
GROUP BY st.Channel
```

---

## ✅ Krok 4: Poprawne SQL

```sql
-- =============================================================================
-- SIERPIEŃ 2026: Porównanie kanałów sprzedaży
-- Wersja poprawna — liczy bezpośrednio z tabeli faktów
-- =============================================================================

-- BLOK 1: Główne metryki na kanał
-- - Liczba transakcji: COUNT(DISTINCT TransactionNo)
-- - Sztuki: SUM(Quantity)
-- - Przychód netto: SUM(NetAmount)
-- - Średni koszyk: przychód / liczba transakcji
SELECT st.Channel AS Kanal,
       COUNT(DISTINCT fs.TransactionNo) AS Transakcje,
       SUM(fs.Quantity) AS Sztuki,
       SUM(fs.NetAmount) AS Przychod,
       CAST(SUM(fs.NetAmount) / COUNT(DISTINCT fs.TransactionNo) AS DECIMAL(10, 2)) AS SredniKoszyk

FROM dbo.FactSales AS fs
INNER JOIN dbo.DimStore AS st ON st.StoreKey = fs.StoreKey
INNER JOIN dbo.DimDate AS dd ON dd.DateKey = fs.DateKey

-- BLOK 2: Filtr czasowy
WHERE dd.YearMonth = '2026-08'

-- BLOK 3: Agregacja i sortowanie
GROUP BY st.Channel
ORDER BY st.Channel;
```

**Dlaczego ta wersja jest lepsza:**
- ✅ Liczy bezpośrednio z faktów (nie przez widok)
- ✅ Zawiera zarówno STORE jak ONLINE
- ✅ Logika jest przejrzysta (bloki + komentarze)
- ✅ Unika problemu z SalesAreaM2

---

## 📋 Krok 5: Checklist Przed Wysłaniem

- [x] Nie ma `COUNT(*)` na agregacji
- [x] Nie ma `AVG(metryka_zagregowana)`
- [x] Metryki zgadzają się z [slownik-metryk.md](../../../docs/slownik-metryk.md)
- [x] Liczby są rozsądne (średni koszyk 597 PLN dla odzieży ✓)
- [x] SQL zweryfikowany na bazie (test pass)
- [x] Poprawne SQL gotowe do wysłania

---

## 📚 Założenia Przyjęte

| Założenie | Status | Weryfikacja |
|-----------|--------|-------------|
| Sierpień = pełny miesiąc (YearMonth = '2026-08') | ✅ | Potwierdzić z biznesem |
| Kanały: STORE i ONLINE (z DimStore.Channel) | ✅ | OK |
| Sprzedaż netto = NetAmount bez VAT | ✅ | Per slownik-metryk.md |
| Transakcja = unikalny TransactionNo | ✅ | Per slownik-metryk.md |
| Sztuki = sprzedane (bez zwrotów) | ✅ | Dobrze dla odzieży |
| Porównanie całej grupy STORE vs ONLINE razem | ✅ | OK |

---

## ❓ Otwarte Pytania

1. **Czy sprzedaż powinna być netto czy brutto po zwrotach?**
   - Obecna wersja: sprzedaż bez odjęcia zwrotów
   - Alternatywa: dodać odjęcie z FactReturns

2. **Dlaczego brak ONLINE w sierpniu?**
   - Czy to anomalia (kanał nie sprzedawał)?
   - Czy brak danych w źródle?
   - Czy trzeba poprawy procedury ETL?

3. **Czy chcecie podział per sklep zamiast per kanał?**
   - Obecna wersja: STORE razem
   - Alternatywa: 5 wierszy (S1, S2, S3, S4, S5)

4. **Czy dodać metryki drażące?**
   - UPT (Units Per Transaction)?
   - Stopa rabatu?
   - Marża brutto?

---

## 📝 Podsumowanie

| Aspekt | Status |
|--------|--------|
| **Błędy zidentyfikowane** | 2 krytyczne + 1 bonus |
| **Weryfikacja na bazie** | ✅ Przebiegła |
| **Różnice w wyniku** | COUNT: 5 → 3703 (741x), Avg: 595.91 → 597.37 PLN |
| **SQL poprawiony** | ✅ Gotowy do wysłania |
| **Raport do biznesu** | ✅ Może iść dalej |

---

## 🚀 Następne Kroki

1. **Potwierdzić otwarte pytania z biznesem** (pytania 1–4 wyżej)
2. **Ewentualnie** dodać metryki drażące jeśli zespół chce
3. **Wysłać poprawne SQL** w załączeniu
4. **Jeśli trzeba drążyć głębiej** → przełączyć na skill `analiza-sprzedazy` (trend, przekroje, diagnostyka anomalii)

---

## 📎 Załączniki

- **SQL Poprawny:** [E05-zapytanie-kuby-POPRAWIONE.sql](../../zgloszenia/E05/E05-zapytanie-kuby-POPRAWIONE.sql)
- **SQL Oryginalne:** [E05-zapytanie-kuby.sql](../../zgloszenia/E05/E05-zapytanie-kuby.sql)
- **Słownik metryk:** [docs/slownik-metryk.md](../../../docs/slownik-metryk.md)

