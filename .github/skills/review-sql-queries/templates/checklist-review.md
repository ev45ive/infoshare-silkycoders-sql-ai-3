# Checklist: Przed Wysłaniem Raportu do Odbiorcy

> Użyj tego checklist'u w Kroku 5, jeśli raport idzie do zespołu biznesowego

## Logika SQL ✅

- [ ] Nie ma `COUNT(*)` na agregacji (zamiast `COUNT(DISTINCT ...)` lub `SUM(...)`)
- [ ] Nie ma `AVG(metryka_zagregowana)` (zamiast `SUM(licznik) / SUM(mianownik)`)
- [ ] JOINy mają `ON` klauzule (nie ma cartesian product)
- [ ] Tygodnie: `IsoYear` razem z `IsoWeek` (nie `Year` z `IsoWeek`)
- [ ] Brak NULLów w agregacji (jeśli oczekujesz pełnych danych) — `COALESCE` gdzieś trzeba?
- [ ] Metryki zgadzają się ze [slownik-metryk.md](../../../docs/slownik-metryk.md)

## Dane i Sensowność 📊

- [ ] **Liczby są rozsądne biznesowo?**
  - Średni koszyk w zakresie 50–300 PLN (dla odzieży)?
  - Liczba transakcji w cztery cyfry czy pięć?
  - Sztuki zgadzają się z przychódem?
  
- [ ] **Brak wyników dla kanału / okresu?**
  - Czy to oczekiwane (np. ONLINE nie sprzedawał)?
  - Czy to błąd danych?
  - Czy to błąd SQL (np. WHERE odfiltrował zbyt dużo)?

- [ ] **Anomalie są wyjaśnione?**
  - Jeśli sprzedaż spadła 50% WoW — czy to normalne?
  - Czy zawiera notatka dla odbiorcy ("Uwaga: brak danych w poniedziałek")?

## Raport Finalny 📄

- [ ] Jasne pytanie biznesowe na początek
- [ ] Okres wyraźnie nazwany (nie "ostatni miesiąc", ale "sierpień 2026")
- [ ] Założenia wymienione (co jest stałe, co zmiennie)
- [ ] Metryki ze źródłami (ile sztuk = kolumna X z tabeli Y)
- [ ] Definicje dla odbiorcy (co to "średni koszyk"?)
- [ ] Poprawne SQL **w załączeniu** (nie w tekście)

## Do Rozmowy z Biznesem 🗣️

Zanim wysłasz raport, potwierdzić:

- [ ] **Czy SQL powinno liczyć sprzedaż brutto czy netto po zwrotach?**
  - Brutto (przed zwrotami): SUM(FactSales.NetAmount)
  - Netto po zwrotach: SUM(FactSales.NetAmount) - COALESCE(SUM(FactReturns.ReturnAmount / 1.23), 0)

- [ ] **Czy chcecie per sklep czy per kanał razem?**
  - Per kanał razem: `GROUP BY Channel` ← prosta
  - Per sklep: dodać `st.StoreCode, st.StoreName` do SELECT i GROUP BY

- [ ] **Czy czasem pytanie powinno być bardziej szczegółowe?**
  - Po kategoriach (Topy, Spodnie, Buty)?
  - Po dniach (WoW trend)?
  - Po czynnościach (pracownicy, przesunięcia)?

## Sign-Off ✍️

Gdy wszystkie checkboxy są zaznaczone:

> ✅ **Raport gotowy do wysłania 2026-10-02 o HH:MM**
> 
> Review: [Twoje imię]  
> SQL Status: [Poprawny / Warunkowo / Wymaga dyskusji]  
> Otwarte pytania: [0 / 2 / itp.]

---

**Jeśli któreś pole nie może być zaznaczone, zaznacz kolumną powód i wróć do step'u review:**

| Pole | Dlaczego nie? | Akcja |
|------|---------------|-------|
| ? | ? | Wróć do Kroku [1/2/3/4] w SKILL.md |
