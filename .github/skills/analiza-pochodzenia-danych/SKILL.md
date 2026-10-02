---
name: analiza-pochodzenia-danych
description: "Verify data lineage and trace anomalies through ETL layers (src → stg → dbo) in RetailDW. Use when: finding root cause of metric discrepancies, validating data quality, isolating anomalous days/channels, identifying duplicate/missing records, debugging ETL failures. Iterative workflow with user to form hypotheses, generate SQL, and validate assumptions."
argument-hint: "Describe the data anomaly, metric affected, and initial hypothesis"
user-invocable: true
disable-model-invocation: true
---

# Analiza Pochodzenia Danych — Data Lineage Analysis

## Cel

Systematycznie śledzić dane od źródła do hurtowni, aby:
- 🔍 Znaleźć przyczynę anomalii (niespodziewane skoki/spadki metryk)
- ✅ Zweryfikować jakość danych na każdej warstwie ETL
- 📊 Izolować problem do konkretnego dnia/kanału/pliku/transakcji
- 🔄 Udokumentować decyzje i wnioski w pętli iteracyjnej

---

## Kiedy Stosować

✓ Metryka wynika nie zgadza się z danymi źródłowymi  
✓ Znalazłeś dzień/tydzień ze 100% wyższą sprzedażą niż zwykle  
✓ Liczba paragonów normalna, ale całkowita kwota zduplikowana  
✓ ETL zaraportował 0 błędów, ale dane wydają się dziwne  
✓ Chcesz udokumentować proces weryfikacji dla audytu  

---

## Procedura Interaktywna

### Faza 1: Zdefiniuj Problem (10 min)

1. **Wskaż metrykę anomalną**
   - Która metryka (sprzedaż netto, koszyk, paragony, zwroty)?
   - Jaki okres (dzień, tydzień, miesiąc)?
   - Jaki kanał (STORE, ONLINE, wszystkie)?

2. **Kwantyfikuj anomalię**
   - Wartość oczekiwana vs. zaobserwowana
   - Różnica procentowa / absolutna
   - Czy wpływa na inne okresy?

3. **Sformułuj wstępne hipotezy** (min. 2-3)
   - Zduplikowana sprzedaż w pliku?
   - Brakujące zapisy?
   - Błęd w konwersji VAT / walut?
   - Problem z datowaniem?

→ **Pokaż swoje założenia — zatwierdzę lub poprawię**

---

### Faza 2: Zbuduj Plan (15 min)

Dla każdej hipotezy utworzę plan zawierający:
- 📋 **Założenia** (co weryfikujemy)
- 🔧 **Kroki** (które warstwy / kolumny / łączenia)
- 📝 **SQL z komentarzami** (każdy query objaśniony)

Plany będą proste, o jeden SELECT na raz.

→ **Przejrzyj SQL — zaproponuj modyfikacje**

---

### Faza 3: Weryfikuj na Bazie (5-10 min per query)

- Wykonam query na RetailDW
- Pokażę wyniki z kontekstem
- Jeśli liczby się zgadzają → hipoteza potwierdzam
- Jeśli się nie zgadzają → formułujemy nową hipotezę

→ **Przejrzyj wyniki — czy pokrywają się z oczekiwaniami?**

---

### Faza 4: Podsumuj i Planuj Następne (5 min)

- 📝 Dokumentuję co znaleźliśmy
- 🎯 Wskazuję root cause
- 🔄 Proponuję następne kroki (jeśli potrzebne)
- 📌 Zapisuję wnioski dla zespołu

---

## Warstwa po Warstwie: Jak Czytać Wyniki

| Warstwa | Co zawiera | Klucz do problemów |
|---------|-----------|------------------|
| **src.SalesRaw** | Dane surowe z CSV (NVARCHAR) | Duplikaty, brakujące kolumny, źródło |
| **stg.Sales** | Dane po TRY_CAST i walidacji | NULL w kolumnach krytycznych |
| **dbo.FactSales** | Po lookup wymiarów (final) | Brutto = źródło, Netto = VAT konwersja |

**Netto = Brutto / 1.23** (zawsze)

---

## Szablon Planu Analizy

```
📌 PROBLEM
Metryka: __________ | Okres: __________ | Hipoteza: __________

✏️ PLAN
Kroki:
1. src.SalesRaw: Ile wierszy dla tego okresu? Ile plików?
2. stg.Sales: Wszystkie przeszły walidację (COUNT == COUNT)?
3. dbo.FactSales: Suma brutto == suma ze stg.Sales?
4. GROUP BY SourceFile / TransactionNo / DateKey dla anomalii

🔍 SQL
-- [SQL tutaj]

📊 WYNIKI
[Wyniki tutaj]

✅ WNIOSEK
Root cause: __________
Kolejne kroki: __________
```

---

## Szablony SQL — Co Kopiowaćć

Patrz plik [szablon-sql.md](./references/szablon-sql.md) — gotowe queriesy do:
- ✓ Porównania wierszy na każdej warstwie
- ✓ Znalezienia duplikatów po TransactionNo
- ✓ Śledzenia SourceFile
- ✓ Weryfikacji datowania
- ✓ Porównania sum brutto/netto

---

## Słownik: Struktury ETL

Szybka referentja dla warstwowych pól — patrz [slownik-etl-layers.md](./references/slownik-etl-layers.md)

---

## Przykład: Case Study 17 sierpnia 2026

### Problem
Sprzedaż netto sierpień: 2,666,549.81 PLN (hurtownia)  
vs. 2,608,664.46 PLN (dane użytkownika)  
**Różnica: 57,885.35 PLN (2.2%)**

### Plan
1. Rozbić sprzedaż dzień po dniu → znaleźć anomalny dzień
2. Dla anomalnego dnia sprawdzić pliki źródłowe (SourceFile)
3. Porównać wiersze na każdej warstwie
4. Znaleźć duplikaty

### Wyniki
- 17 sierpnia: 131,743.93 PLN (77% wyżej niż normalny poniedziałek)
- Źródło: 3 pliki
  - `POS_20260817.csv`: 223 wiersze, 71,199 PLN
  - `POS_20260817_RETRY.csv`: 223 wiersze, **71,199 PLN (DUPLIKAT!)**
  - `WEB_20260817.csv`: 70 wierszy, 19,647 PLN

### Root Cause
**POS_20260817_RETRY.csv to zduplikowana zawartość POS_20260817.csv**
- Nie usunął oryginalnego pliku
- Wszystkie 223 wiersze załadowane dwukrotnie
- Efekt: +57,894 PLN netto (71,199 / 1.23 = 57,894)
- 🎯 To dokładnie brakująca różnica!

### Wniosek
- ✅ ETL działa prawidłowo (nie deduplikuje, ale wszystko przechodzi)
- ❌ Proces wznowienia (RETRY) powinien czyszczać poprzednie załadowania
- 📌 Wymaganą korekta historycznych danych w src/stg/facts

---

## Następne Kroki Po Znalezieniu Root Cause

1. **Czy to błąd jednorazowy?**
   - Sprawdź czy inne dni mają RETRY pliki
   - Czy są duplikaty między dniami?

2. **Czy dane wymagają czyszczenia?**
   - Skalę problemu (ile dni, ile PLN)
   - Plan usunięcia duplikatów z src.SalesRaw

3. **Czy proces ETL wymaga poprawy?**
   - Deduplikacja przed załadowaniem?
   - Walidacja — czy RETRY zawsze ma dokładnie te same TxNo?

---

## Szybkie Linki

- 📖 [Procedura Interaktywna — Szczegóły](./references/procedura-interaktywna.md)
- 🔧 [Szablony SQL — Copy-Paste Ready](./references/szablon-sql.md)
- 📚 [Słownik Pól ETL](./references/slownik-etl-layers.md)
- 📋 [Plan Analizy — Szablon do Wypełnienia](./templates/plan-analizy.md)

---

## Wskazówki

💡 **Zawsze zaczynaj od najwyższego poziomu** (dzień/tydzień/kanał) zanim nurkujesz w wiersze.  
💡 **Wizualizuj liczby** — jeśli sum brutto na dwóch warstwach się nie zgadzają, to jest błąd.  
💡 **Nie zgaduj** — pytaj pytania i weryfikuj każdą hipotezę na bazie danych.  
💡 **Dokumentuj kroki** — może się przydać zespołowi lub audytorowi.
