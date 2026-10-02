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

3. **Sformułuj wstępne hipotezy** (min. 2-3, wybierz z listy lub dodaj własne)

   **Hipotezy techniczne (dane sie duplikują/tracą):**
   - Zduplikowana sprzedaż w pliku (RETRY, ponowne załadowanie)
   - Brakujące zapisy (wiersze nigdy nie przeszły przez ETL)
   - Wiersze załadowane dwukrotnie (do różnych tabel/baz)
   - Wiersze załadowane do złego miesiąca (datowanie)

   **Hipotezy biznesowe (źródło danych):**
   - Błąd w konwersji VAT / walut (złą formułę w ETL)
   - Transakcje z promocji / zwrotów (nieuwzględniane w liczbie)
   - Rezim skarbowy (czy wszystkie kanały raportują w tym samym dniu?)
   - Zmiany cen / rabatów (liczymy na dzień, ale ceny zmieniane intra-dzień)

   **Hipotezy procesowe (ludzie):**
   - Błąd w raporcie użytkownika (źle sformatowana liczba)
   - Różne okresy rozliczeniowe (my: data transakcji, user: data płatności)
   - Różne zakresy: my raportujemy GDA+WAW+ONL, user ma tylko GDA
   - Ręczna korekta w czaku (system koryguje duplikaty ręcznie)

→ **Zaproponuj min. 2 hipotezy, które chcesz testować først — ustalimy kolejność**

---

### Faza 2: Zbuduj Plan (15 min) — Wybór Metody

Dla każdej hipotezy oferuję **co najmniej 3 podejścia** — do wyboru:

#### 🎯 Metoda A: Top-Down (od okresu do szczegółów)
- Szukamy anomalii na poziomie **dzień/tydzień**
- Potem: które kanały? Które pliki?
- Potem: który TransactionNo?
- **Gdy**: szybka orientacja, wiadomo że problem jest lokalizowany
- **SQL**: agregacje, SUM/COUNT po DateKey → SourceFile → TransactionNo

#### 🔍 Metoda B: Bottom-Up (od linii do całości)
- Zaczynamy od duplikatów w **TransactionNo / LineNumber**
- Budujemy rolę do góry: ile wierszy ma każdy plik?
- Potem: które dni są dotknięte?
- **Gdy**: podejrzewamy dokładnie zduplikowane linie, chcemy znaleźć wzór
- **SQL**: PARTITION BY, ROW_NUMBER(), GROUP BY SourceFile

#### 📊 Metoda C: Comparative (porównanie warstwowe)
- Najpierw: COUNT i SUM na każdej warstwie (src → stg → dbo)
- Czy liczby się zgadzają między warstwami?
- Jeśli nie: którą warstwę Problem na której warstwie?
- **Gdy**: chcemy wiedzieć czy ETL działa, czy problem to z danymi źródłowymi
- **SQL**: UNION ALL z trzema SELECT (src/stg/dbo), porównanie sum

#### 🎲 Metoda D: By Channel/Source (rozdzielenie kanałów)
- Rozdzielamy **STORE vs ONLINE** lub **CSV vs inny kanał**
- Każdy kanał osobny query
- Szukamy anomalii tylko w jednym kanale
- **Gdy**: podejrzewamy że problem dotyka tylko część sprzedaży
- **SQL**: WHERE Channel = 'STORE' lub WHERE SourceFile LIKE 'POS%'

→ **Wybiórz metodę A/B/C/D — opiszę SQL krok po kroku, lub połącz 2-3 podejścia naraz**

---

### Faza 3: Weryfikuj na Bazie (5-10 min per query) — Warianty Działania

Po każdym query oferuję **opcje działania** zależnie od wyników:

#### 📌 Scenariusz A: Liczby Się Zgadzają ✅
- Hipoteza **potwierdzona** → wpisujemy jako root cause
- **Opcje dalsze:**
  1. Sprawdzić czy problem dotyczy tylko tego okresu (query czasowo-zakresy)
  2. Oszacować skalę (ile dni / transakcji / PLN w historii)
  3. Przejść do planu czyszczenia (jeśli wymagane)

#### 📌 Scenariusz B: Liczby Się Nie Zgadzają ❌
- Hipoteza **odrzucona** → formułujemy nową
- **Opcje dalsze:**
  1. **Pivot:** przełączyć na inną hipotezę z listy (A→B, B→C itd)
  2. **Drill down:** nurkować w szczegóły tej warstwy (które TransactionNo?)
  3. **Widen:** wziąć szerszy zakres (nie 1 dzień, ale cały tydzień)
  4. **Cross-check:** przeskoczyć warstwę (zamiast stg → src, sprawdzić dbo)

#### 📌 Scenariusz C: Wynik Niespodziewany/Dziwny ⚠️
- Liczby istnieją ale nie wyjaśniają anomalii całkowicie
- **Opcje dalsze:**
  1. **Refinement:** zawęzić okres / kanał / pole (czym dokładnie się różnią?)
  2. **Segmentation:** rozbić wynik po wymiarze (dzień→godzina, store→produkt)
  3. **Recount:** powtórzyć query z innymi kolumnami/Join'ami
  4. **Manual check:** wziąć kilka transakcji i sprawdzić ręcznie (po czym się replikują?)

#### 🎯 Po Każdym Query

Pytam: 
- **Czy wynik odpowiada oczekiwaniom?** (TAK / NIE / CZĘŚCIOWO)
- **Co robić dalej?** (potwierdź hipotezę / spróbuj innego podejścia / nurkuj głębiej)
- **Czy chcesz zmienić zakres?** (inny dzień / inny kanał / inna metoda)

→ **Nie zmuszam cię do jednej ścieżki — adaptujemy plan na bieżąco**

---

### Faza 4: Podsumuj i Planuj Następne (5 min) — Opcje Działania

Po znalezieniu root cause oferuję **kilka ścieżek dalszych:**

#### ✅ Jeśli root cause to **dane źródłowe** (duplikaty, błędy w CSV)

**Opcja 1: Użytkownik ma rację — raportuj jego liczbę**
- Liczba do raportu: ta co zaraportował (bez błędu ETL)
- Status: hurtownia zawiera błąd, ale użytkownik ma prawidłową
- Akcja: zadokumentuj dla audytu, poinformuj zespół ETL

**Opcja 2: Wyczyść historię w hurtowni** (wymaga uprawnień)
- Usuń duplikaty z src/stg/dbo
- Raport zostanie automatycznie poprawiony
- Ryzyko: jeśli się pomylimy, cofamy dane

**Opcja 3: Zatrzymaj bieżące załadowania**
- Blokuj wznowienia (RETRY) do czasu naprawy procesu
- Czyszczenie = opcja na później (po stabilizacji)
- Ryzyko: mogą zgubić prawidłowe dane, jeśli rzeczywiście był błąd

#### ⚠️ Jeśli root cause to **problem w ETL logice** (VAT, wymiary, daty)

**Opcja A: Szybka naprawa (zmiana procedury)**
- Wydaj patch do ETL na produkcji
- Historyczne dane NIE konwertuj (trudne, ryzykowne)
- Status: od teraz będzie dobrze, przeszłość trzeba zgłosić osobno

**Opcja B: Historyczne czyszczenie** (długo)
- Napisz skrypt do usunięcia / przeliczenia danych wstecz
- Przetestuj na dev
- Wdrożyć na produkcji (poza szczytem)

**Opcja C: Uzgodnij nową definicję metryki**
- Może błąd się počwał już dawno? (seria dni, nie jeden)
- Uzgodnienie z biznesem: co raportujemy (ETL czy systemy źródłowe)?
- Status: jasna reguła na przyszłość

#### 📊 Jeśli problem **wciąż niejasny** (liczby się nie zgadzają ale nie znamy powodu)

**Opcja I: Poszerzenie zakresu analizy**
- Zamiast jednego miesiąca: weź 3 ostatnie miesiące
- Czy anomalia ma wzór? (każdy 17-ty dzień? każdy poniedziałek?)
- Czy to problem systematyczny czy jednorazowy?

**Opcja II: Pivot na inne hipotezy**
- Być może to nie duplikat, ale:
  - Brakujące zapisy z innego kanału?
  - Zwroty nie odliczone prawidłowo?
  - Różne VAT dla różnych produktów?
- Zaproponuj kolejne 2-3 hipotezy do testowania

**Opcja III: Ręczna weryfikacja** (dla pewności)
- Weź kilka TransactionNo z dni anomalnych
- Porównaj ręcznie: czy w systemach źródłowych faktycznie taka kwota?
- Jeśli tak → problem napewno w ETL
- Jeśli nie → problem w raportowaniu użytkownika

→ **Którą ścieżkę wybrać? Zależy od:**
- Czy się zdecydowaliśmy na root cause?
- Ile czasu / ryzyka możemy sobie pozwolić?
- Czy problem dotyczy przeszłości czy przyszłości?

---

## 🎛️ Jak Pracuje Skill — Elastyczne Gałęziowanie

**Skill oferuje kilka metod na każdym kroku — nie zmusza cię do jednej ścieżki.**

- **Faza 1**: Sformulujesz min. 2-3 hipotezy → wybiórz które testować
- **Faza 2**: Oferuję 4 podejścia (Top-Down / Bottom-Up / Comparative / By Channel) → wybiórz jedno lub połącz
- **Faza 3**: Po każdym query pokazuję opcje działania zależnie od wyniku (TAK/NIE/CZĘŚCIOWO) → adaptujemy na bieżąco
- **Faza 4**: Zależy od root cause → oferuję kilka scenariuszy działania

**Brak gotowego planu** — procedura się zmienia na podstawie wyników. Pytam pytania i daję opcje, nie narzucam ścieżki.

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
