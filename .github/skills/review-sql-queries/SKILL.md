---
name: review-sql-queries
description: "Review zapytań SQL w RetailDW (mssql): identyfikacja błędów agregacji (COUNT vs SUM, AVG ze średnich, JOINy), weryfikacja logiki biznesowej, porównanie wyników na bazie, propozycja poprawek z komentarzami. Use when: sprawdzenie poprawności SQL, liczby nie zgadzają się z oczekiwaniem, wątpliwości czy widok lub tabela faktów to właściwe źródło, błędy w agregacji danych."
argument-hint: "wklej SQL lub dołącz plik .sql z zapytaniem, opcjonalnie: co powinno robić"
user-invocable: true
disable-model-invocation: false
---

# Review Zapytań SQL — RetailDW

## Cel

Dostarczyć **drugą parę oczu** dla zapytań SQL — systematycznie sprawdzić logikę, zweryfikować wyniki na bazie danych, wskazać błędy z wyjaśnieniami i zaproponować poprawne SQL z komentarzami edukacyjnymi.

---

## Kiedy Używać

| Scenariusz | Przykład | Tryb |
|-----------|---------|------|
| **Wątpliwości co do logiki** | "Jest SELECT COUNT(*) na agregacji — czy to OK?" | Analiza statyczna |
| **Liczby nie zgadzają się** | "Powinno być 3703 transakcji, ale wychodzi 5" | Test na bazie + diagnostyka |
| **Przed wysłaniem do biznesu** | "Sprawdzisz ten raport zanim wyślę do zespołu sprzedaży?" | Pełny review (wszystkie kroki) |
| **Nowy widok (CREATE VIEW)** | "Czy ten widok poprawnie liczy sprzedaż netto?" | Analiza logiki + test |

---

## Procedura (4 kroki)

### **Krok 0: Ustal zakres**

Jeśli nie jest klarowne, zapytaj:
- Co to zapytanie powinno robić? (opisz biznesowo)
- Jaka jest oczekiwana liczba wierszy / zakres danych?
- Czy to SELECT do raportowania, czy CREATE VIEW do warstwy?
- Czy muszę sprawdzić to na bazie czy wystarczy analiza kodu?

**→ Idź do Kroku 1 (analiza statyczna) — zawsze.**

---

### **Krok 1: Analiza Statyczna (bez bazy)**

Przeczytaj SQL i identyfikuj potencjalne błędy:

#### Typowe błędy do szukania:

| Błąd | Sygnatura | Czemu to źle | Poprawka |
|------|-----------|-------------|---------|
| **COUNT(\*) na agregacji** | `COUNT(*) OVER (PARTITION BY ...)` lub `COUNT(*) GROUP BY` | Liczy wiersze, nie obiekty biznesowe | `SUM(istniejąca_metryka)` lub `COUNT(DISTINCT klucz)` |
| **AVG(metryka_zagregowana)** | `AVG(AvgBasketValue)` — średnia ze średnich | Ignoruje wagi, daje fałszywy wynik | `SUM(licznik) / SUM(mianownik)` |
| **JOIN bez ON** | `... FROM t1, t2 WHERE ...` zamiast `FROM t1 JOIN t2 ON` | Cartesian product, wyniki się mnożą | Dodaj `ON` klauzulę |
| **DISTINCT w złym miejscu** | `SELECT DISTINCT *, SUM(...)` | DISTINCT ignoruje agregaty | Przenieś DISTINCT do GROUP BY |
| **Nie uwzględnia NULL** | `SUM(kolumna)` gdy kolumna może być NULL | Wiersze z NULL są ignorowane | Sprawdź czy to zamierzone, `COALESCE(kolumna, 0)` |
| **Wśród tygodni/lat** | `... GROUP BY Year, IsoWeek` | Rok kalendarzowy ≠ rok ISO | Użyj `IsoYear` razem z `IsoWeek` |

#### Źródła metryk

Zawsze sprawdź [docs/slownik-metryk.md](../../../docs/slownik-metryk.md):
- Czy ta metryka jest zdefiniowana?
- Jakie są jej składniki (licznik, mianownik)?
- Jakie źródło (FactSales, FactReturns, etc.)?

Jeśli metryka **nie ma** w słowniku → zaproponuj definicję i zapytaj użytkownika.

**→ Wypisz znalezione problemy jako lista (bez działań na bazie jeszcze).**

---

### **Krok 2: Test na Bazie (jeśli potrzeba)**

Jeśli znalazłeś potencjalne błędy **lub** użytkownik chce weryfikacji, wykonaj:

1. **Połączenie:** Użyj domyślnego profilu `RetailDW` (serwer `127.0.0.1,14331`, baza `RetailDW_WorkshopNext`)
2. **Uruchom zapytanie **błędne** (oryginalne):**
   ```
   SELECT ... FROM ... WHERE ...
   ```
3. **Uruchom zapytanie poprawione** (z poprawkami z Kroku 1):
   ```
   SELECT ... FROM ... WHERE ... (ze zmianami)
   ```
4. **Porównaj wyniki** side-by-side:
   - Ile wierszy każde zwraca?
   - Jakie są wartości kluczowych kolumn?
   - Czy różnice pokrywają się z teorią (np. COUNT(*) = 5 zamiast 3703)?

**OUTPUT:** Tablica porównawcza (patrz [./templates/porownanie-wynikow.md](./templates/porownanie-wynikow.md))

---

### **Krok 3: Wyjaśnienie Błędów**

Dla każdego znalezionego problemu:

1. **Co się stało?** — Konkretna linijka kodu
2. **Dlaczego to błąd?** — Wyjaśnienie z przykładami
3. **Jaka jest różnica w wyniku?** — Porównanie liczb (step 2)
4. **Jak to naprawić?** — Poprawka w SQL

**FORMAT:** Dla każdego błędu:

```markdown
### ❌ BŁĄD [N]: [NAZWA]

**Kod:**
```sql
PROBLEM LINE HERE
```

**Dlaczego to błąd:**
[Wyjaśnienie + przykład numeryczny jeśli możliwe]

**Poprawka:**
```sql
CORRECTED LINE HERE
```
```

---

### **Krok 4: Propozycja Poprawnego SQL**

Napisz **kompletne, poprawne SQL** z:

1. **Strukturą blokową** — komentarze oddzielające krok logiczny:
   ```sql
   -- BLOK 1: Przyłączenie wymiarów
   -- (opis czemu te wymiary)
   
   SELECT ...
   FROM FactSales AS fs
   INNER JOIN DimStore AS st ON st.StoreKey = fs.StoreKey
   
   -- BLOK 2: Filtr czasowy
   WHERE dd.YearMonth = '2026-08'
   
   -- BLOK 3: Agregacja
   GROUP BY st.Channel
   ORDER BY st.Channel;
   ```

2. **Komentarze inline** przy kluczowych elementach:
   ```sql
   COUNT(DISTINCT fs.TransactionNo) AS Transakcje  -- Liczy każdą transakcję raz
   CAST(SUM(fs.NetAmount) / COUNT(DISTINCT fs.TransactionNo) AS DECIMAL(10, 2)) AS SredniKoszyk -- Przychód kanału / liczba transakcji kanału
   ```

3. **Nagłówek z kontekstem:**
   ```sql
   -- Sierpień 2026: Porównanie kanałów sprzedaży
   -- Metryki: transakcje, sztuki, przychód netto, średni koszyk
   -- Źródło: FactSales (level transakcji) + DimStore, DimDate
   -- Poprawki względem wersji oryginalne: SUM(Transactions) zamiast COUNT(*), itp.
   ```

**OUTPUT:** Plik `.sql` gotowy do wysłania lub dalszego użytku (patrz [./templates/sql-poprawny.sql](./templates/sql-poprawny.sql))

---

### **Krok 5: Raport Finalny (opcjonalnie)**

Jeśli zapytanie idzie do odbiorcy biznesowego, przygotuj:

1. **Checklist przed wysłaniem** (patrz [./templates/checklist-review.md](./templates/checklist-review.md)):
   - [ ] Liczby są sensowne biznesowo?
   - [ ] Brak wyników dla ONLINE/STORE — czy to oczekiwane czy błąd?
   - [ ] Metryki zgadzają się ze słownikiem?
   - [ ] Są wątpliwości o dodatkowych wymiarach (per sklep, kategoria)?

2. **Listy do dyskusji:**
   - **Assumptions:** Jakie założenia zostały przyjęte (okres, kanały, zaokrąglenie, etc.)
   - **Otwarte pytania:** Co wyjaśnia biznes (czy to anomalia czy normalnie?)

**OUTPUT:** Dokument w [./examples/](./examples/) dla referencji

---

## Kryteria Sukcesu

Skill uważam za **ukończony**, gdy:

- [ ] SQL **bez błędów agregacji** (COUNT/SUM/AVG używane prawidłowo)
- [ ] Wyniki **zweryfikowane na bazie** (test pass/fail)
- [ ] Każdy błąd **wyjaśniony** (nie tylko wskazany)
- [ ] Poprawne SQL **gotowe do użytku** (bloki + komentarze)
- [ ] **Założenia ujawnione** (co pytamy biznesu)

---

## Szablony i Materiały

| Materiał | Zawartość | Kiedy użyć |
|----------|-----------|-----------|
| [porownanie-wynikow.md](./templates/porownanie-wynikow.md) | Tablica błędne vs poprawne | Po Kroku 2 |
| [sql-poprawny.sql](./templates/sql-poprawny.sql) | Boilerplate z komentarzami | Po Kroku 4 |
| [checklist-review.md](./templates/checklist-review.md) | Do skopiowania w raport | Jeśli Krok 5 |
| [E05-case-study.md](./examples/E05-case-study.md) | Pełny przykład z liczbach | Dla inspiracji |

---

## Zasady (wszystko)

✅ **DO:**
- Zawsze sprawdź [docs/slownik-metryk.md](../../../docs/slownik-metryk.md) przed liczeniem czegokolwiek
- Eksplicitnie nazwij założenia (okres, kanały, metryka, źródło)
- Jeśli liczby wydają się dziwne → poproś o potwierdzenie
- Komentarze wyjaśniające — user ma nauczyć się z tego review'u

❌ **NIE:**
- Nie modyfikuj bazy (wszystko SELECT only, READONLY)
- Nie czytaj `zgloszenia/`, `notatki/`, `.specstory/`, `RetailDW/Scripts/` (poza scope)
- Nie zgaduj metryk — zawsze słownik albo pytaj użytkownika
- Nie wysyłaj raportów bez weryfikacji na bazie (chyba że user wyraźnie powie "tylko analiza kodu")

---

## Przykłady Invocacji

```
/ review-sql-queries

Wklej SQL + opis: "To jest zapytanie sierpniowej sprzedaży dla zespołu. Liczby wydają mi się dziwne."
```

```
/ review-sql-queries

[załączony plik E05-zapytanie-kuby.sql]

"Zanim wyślę to do biznesu, sprawdzisz mi czy nie ma błędów?"
```

```
/ review-sql-queries

CREATE VIEW reporting.vw_NewMetric AS
SELECT st.Channel, SUM(AVG(fs.NetAmount)) ...
FROM ...

"Nowy widok do raportu. Czy logika jest OK?"
```

---

## Następne Kroki po Review

- **SQL teraz OK?** → Kod gotów do deployment / wysłania do odbiorcy
- **Pytania otwarte?** → Przełącz na skill [analiza-sprzedazy](../analiza-sprzedazy/) jeśli to o samej analizie biznesowej, czy na zespół jeśli pytania biznesowe
- **Chcesz uogólnić?** → Zaproponuj nową metrykę do [docs/slownik-metryk.md](../../../docs/slownik-metryk.md) lub nowy widok do [RetailDW/Views/](../../../RetailDW/Views/)

---

## Powiązane Materiały

- [Słownik metryk](../../../docs/slownik-metryk.md) — definicje wszystkich miar
- [Struktura RetailDW](../../../RetailDW/Tables/) — schematy tabel
- Skill [analiza-sprzedazy](../analiza-sprzedazy/) — gdySQL już OK, ale pytanie biznesowe czeka
