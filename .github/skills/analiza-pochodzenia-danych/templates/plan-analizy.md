# Plan Analizy Pochodzenia Danych — Szablon do Wypełnienia

**Data:** ________________  
**Osoba:** ________________  

---

## 📌 PROBLEM

### Co się stało?
```
Metryka: ________________________
Okres: ________________________
Kanał: ________________________
```

### Liczby
```
Oczekiwana wartość: ________________________ PLN
Zaobserwowana wartość: ________________________ PLN
Różnica: ________________________ PLN (_____ %)
```

### Gdzie znalazłeś anomalię?
```
[ ] Raport biznesowy
[ ] Dashboard
[ ] Zgłoszenie z zespołu
[ ] Inne: ________________________
```

---

## 💭 HIPOTEZY (Min. 2-3)

1. **Hipoteza 1:** ________________________
   - Co jeśli: ________________________
   - Jak byś to zweryfikował: ________________________

2. **Hipoteza 2:** ________________________
   - Co jeśli: ________________________
   - Jak byś to zweryfikował: ________________________

3. **Hipoteza 3:** ________________________
   - Co jeśli: ________________________
   - Jak byś to zweryfikował: ________________________

---

## 📋 PLAN — Faza 1: Zaważ Zakres (10-15 min)

### Pytanie do Sprawdzenia
```
[ ] Czy problem jest w całym miesiącu czy konkretnym dniu?
[ ] Czy problem dotyczy wszystkich kanałów czy jednego?
[ ] Czy to się powtarza w poprzednich miesiącach?
```

### Query do Uruchomienia
```sql
-- [Wklej SQL template z references/szablon-sql.md nr 1 lub 2]

```

### Założenia
- Szukamy anomalii > 30% od średniej
- Anomalia musi być reprezentatywna dla problemu
- Porównujemy z rozsądnym benchmarkiem (ostatni miesiąc / rok)

### Kiedy Gotowy → Przejdź do Fazy 2

---

## 🔧 PLAN — Faza 2: Porównanie Wierszy ETL (5-10 min)

### Pytanie do Sprawdzenia
```
Czy liczba wierszy jest konsystentna między warstwami?
src.SalesRaw ==? stg.Sales ==? dbo.FactSales
```

### Query do Uruchomienia
```sql
-- [Wklej SQL template z references/szablon-sql.md nr 3]

```

### Założenia
- Jeśli liczby się różnią → transformacja straciła dane
- Każdy rekord z src musi przejść do stg do dbo
- Jeśli są różnice → najpierw sprawdz stg.Sales czy nie ma NULL

### Oczekiwany Wynik
```
src.SalesRaw: ____________ wierszy
stg.Sales: ____________ wierszy
dbo.FactSales: ____________ wierszy
STATUS: ✓ OK / ✗ PROBLEM
```

### Kiedy Gotowy → Przejdź do Fazy 3

---

## 💰 PLAN — Faza 3: Porównanie Sum Brutto (5-10 min)

### Pytanie do Sprawdzenia
```
Czy sumy brutto są konsystentne między warstwami?
src brutto ==? stg brutto ==? dbo brutto ==? dbo netto / 1.23
```

### Query do Uruchomienia
```sql
-- [Wklej SQL template z references/szablon-sql.md nr 4]

```

### Założenia
- Brutto zawsze = Quantity * UnitPrice - DiscountAmount
- Netto zawsze = Brutto / 1.23
- Jeśli sumy się różnią → brakuje danych lub błędy w konwersji

### Oczekiwany Wynik
```
src.SalesRaw brutto: ____________ PLN
stg.Sales brutto: ____________ PLN
dbo.FactSales brutto: ____________ PLN
dbo.FactSales netto: ____________ PLN
dbo.FactSales netto (brutto/1.23): ____________ PLN

ZGODNOŚĆ: ✓ OK / ✗ PROBLEM
RÓŻNICA: ____________ PLN (powinna być 0)
```

### Kiedy Gotowy → Przejdź do Fazy 4

---

## 📂 PLAN — Faza 4: Identyfikacja Pliku Źródłowego (5-10 min)

### Pytanie do Sprawdzenia
```
Które pliki CSV zawierają dane dla tego okresu?
Czy któreś są podejrzanie identyczne (duplikat)?
```

### Query do Uruchomienia
```sql
-- [Wklej SQL template z references/szablon-sql.md nr 5]

```

### Założenia
- Każdy dzień ma 1-3 pliki CSV (POS_YYYYMMDD.csv, WEB_YYYYMMDD.csv, ewentualnie _RETRY)
- Jeśli 2 pliki mają identyczne wiersze + brutto → duplikat
- Jeśli plik ma `_RETRY` → potrzebne sprawdzenie czy oryginalny był usunięty

### Oczekiwany Wynik
```
POS_YYYYMMDD.csv: ____________ wierszy, ____________ PLN
WEB_YYYYMMDD.csv: ____________ wierszy, ____________ PLN
[Ewentualnie _RETRY pliki]
STATUS: ✓ Normalne / ⚠️ Podejrzane (duplikaty?)
```

### Kiedy Gotowy → Przejdź do Fazy 5

---

## 🔍 PLAN — Faza 5: Szukanie Duplikatów (5-10 min)

### Pytanie do Sprawdzenia
```
Czy jakieś TransactionNo pojawiają się wielokrotnie?
To wskaź zduplikowanego rekordu / zduplikowanego pliku.
```

### Query do Uruchomienia
```sql
-- [Wklej SQL template z references/szablon-sql.md nr 6]

```

### Założenia
- Każdy TransactionNo powinien pojawić się dokładnie raz (+ jego line items)
- Jeśli pojawia się 2x → duplikat całego paragonu
- Jeśli pojawia się 3x+ → poważny problem (multiple retries?)

### Oczekiwany Wynik
```
DUPLIKATY ZNALEZIONE: ✓ Tak / ✗ Nie

Jeśli TAK:
- TransactionNo: ________________________
- IleRazy: ________________________
- Pliki: ________________________
```

### Kiedy Gotowy → Przejdź do Fazy 6

---

## 📊 PLAN — Faza 6: Potwierdzenie ROOT CAUSE (5 min)

### Sformułuj Precyzyjnie

```
ROOT CAUSE (zaproponowany):
________________________

SKALA PROBLEMU:
- Liczba wierszy: ________________________
- Kwota brutto: ________________________ PLN
- Kwota netto: ________________________ PLN (brutto / 1.23)
- Czy to wyjaśnia anomalię: ✓ TAK / ✗ NIE

EASY FIX?: 
[ ] TAK — Wystarczy usunąć duplikaty z src.SalesRaw
[ ] NIE — Wymaga dyskusji z zespołem
[ ] MAYBE — Mogę pokazać opcje
```

---

## ✅ WYNIKI I WNIOSKI

### Co Znaleźliśmy?
```
[Podsumowanie 2-3 zdania]
```

### SQL Query (do Udokumentowania)
```sql
-- [Finalne query które potwierdzą root cause]

```

### Dowód Numeryczny
```
Liczba 1: ____________
Liczba 2: ____________
Różnica: ____________
STATUS: ✓ Wyjaśnia anomalię
```

### Następne Kroki
```
[ ] Poinformować zespół o problemie
[ ] Zaplanować korekta danych
[ ] Zmienić proces ETL (deduplikacja?)
[ ] Archiwizować to zgłoszenie
[ ] Inne: ________________________
```

---

## 📌 NOTATKI

```
[Miejsce na notatki ad hoc, obserwacje, pytania, które pojawiły się podczas analizy]
```

---

## Checklist Ukończenia

- [ ] Anomalia ma jasną definicję (liczby, daty, kanały)
- [ ] Min. 2-3 hipotezy zostały sformułowane
- [ ] Plan zawiera min. 4 query do uruchomienia
- [ ] Wiersze się zgadzają między warstwami (src = stg = dbo)
- [ ] Sumy brutto się zgadzają między warstwami
- [ ] Zidentyfikowano źródło (pliki CSV)
- [ ] Sprawdzono duplikaty (TransactionNo)
- [ ] Root cause został potwierdzony na bazie
- [ ] Wiadomo ile to kosztuje (PLN)
- [ ] Wiadomo co robić dalej

---

## Zatwierdzenie

**Analizę przeprowadził:** ________________________  
**Data ukończenia:** ________________________  
**Zatwierdził (Lider analityki):** ________________________  
**Data zatwierdź:** ________________________

---

## Szybkie Linki

- 📖 [Procedura Interaktywna](../references/procedura-interaktywna.md)
- 🔧 [Szablony SQL](../references/szablon-sql.md)
- 📚 [Słownik Pól ETL](../references/slownik-etl-layers.md)
- 🏠 [Powrót do SKILL.md](../SKILL.md)
