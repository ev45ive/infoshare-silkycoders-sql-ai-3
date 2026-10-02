---
name: dokumentacja-metryk
description: "Create, update, or review metric documentation for RetailDW. Use when: verifying metric definitions, checking grain and examples, comparing docs with reporting views, proposing documentation changes, or listing unresolved questions before a doc update."
argument-hint: "opisz metrykę, dokument do sprawdzenia, zakres zmian albo wklej fragment dokumentacji do przeglądu"
user-invocable: true
disable-model-invocation: false
---

# Dokumentacja Metryk — RetailDW

## Cel

Utrzymać spójną, biznesową dokumentację metryk w RetailDW tak, aby każda definicja była:
- zgodna ze słownikiem metryk,
- zgodna z ziarniem danych i raportowaniem,
- zweryfikowana na przykładach,
- opisana razem z ograniczeniami i otwartymi kwestiami.

---

## Kiedy stosować

Użyj tego skilla, gdy użytkownik chce:
- utworzyć nowy opis metryki,
- zaktualizować istniejącą definicję,
- porównać dokumentację z implementacją w widoku raportowym,
- przeglądnąć przykład obliczenia i wyłapać rozjazdy,
- przygotować listę nierozstrzygniętych kwestii przed publikacją zmian.

---

## Zasady

- Oparcie zawsze na źródłach: `docs/slownik-metryk.md`, definicje tabel, widoki raportowe i wynik SQL.
- Nie zgaduj definicji, jeśli są dwuznaczne. Zamiast tego wypisz warianty i oznacz brak rozstrzygnięcia.
- Jeśli metryka ma więcej niż jedno sensowne ziarno, opisz oba i nazwij ich zastosowania.
- Jeśli dokumentacja i implementacja różnią się, pokaż różnicę wprost i wskaż, który wariant jest źródłem prawdy dla raportu.
- Nie przenoś wniosków z pamięci ani z wcześniejszych sesji bez aktualnego potwierdzenia w plikach lub SQL.

---

## Szablony i zasoby

Korzystaj z osobnych plików referencyjnych zamiast duplikować wzorce w tym pliku:

- [Szablon struktury słownika metryk](references/slownik-metryk-template.md)
- [Szablon wpisu metryki w słowniku](references/wpis-metryki-template.md)
- [Szablon pliku z dokumentacją metryki](references/dokumentacja-metryki-template.md)

Używaj ich jako materiału startowego przy tworzeniu lub aktualizacji dokumentacji, a w głównym skilu zostawiaj tylko decyzje, kroki i kryteria jakości.

---

## Procedura

### 1. Ustal zakres

Najpierw ustal:
- jaka metryka jest opisywana,
- czy chodzi o tworzenie, aktualizację czy przegląd,
- jaki obszar obejmuje zmiana: definicja, ziarno, przykład, ostrzeżenia, nazewnictwo, źródło danych.

Jeśli zakres jest niejasny, dopytaj użytkownika zanim zaczniesz pisać.

### 2. Zbierz źródła

Zbierz tylko potrzebne źródła do tej metryki:
- definicję z `docs/slownik-metryk.md`,
- definicję tabel i kolumn z `RetailDW/Tables`,
- implementację z `RetailDW/Views`, jeśli istnieje,
- wynik SQL dla jednego reprezentatywnego okna, jeśli potrzebny jest przykład.

Jeśli metryka nie występuje w słowniku, zatrzymaj się i poproś użytkownika o decyzję, czy dodajemy nową definicję, czy mapujemy ją do istniejącej.

### 3. Sprawdź definicję

Porównaj dokumentację z implementacją i potwierdź:
- czy wzór liczenia jest taki sam,
- czy w mianowniku i liczniku są te same elementy,
- czy uwzględniane są zwroty, rabaty, koszt, VAT lub inne korekty,
- czy granica okresu jest jasna,
- czy definicja dotyczy sprzedaży, marży, zapasu, zwrotów albo koszyka.

Jeśli widzisz konflikt, opisz go jako osobny punkt, nie scalaj go w jedną interpretację.

### 4. Sprawdź ziarno

Ustal, na jakim poziomie metryka jest poprawna:
- dzień, tydzień, miesiąc,
- kanał, sklep, region,
- kategoria, department, styl, SKU,
- pojedynczy dokument, linia transakcji albo migawka.

Jeśli widok lub słownik używa innego ziarna niż użytkownik oczekuje, powiedz to wprost i zaproponuj sposób bezpiecznego użycia.

### 5. Zweryfikuj na przykładzie

Jeśli to ma sens dla metryki:
- policz prosty przykład na krótkim oknie,
- pokaż wzór z podstawionymi liczbami,
- porównaj wynik z widokiem raportowym,
- zaznacz ewentualne różnice i ich przyczynę.

Przykład ma potwierdzać definicję, a nie zastępować pełną analizę.

### 6. Przygotuj zmianę dokumentacji

Gdy trzeba zaktualizować dokumentację, przygotuj:
- krótki opis zmiany,
- starą definicję i nową definicję,
- wpływ na raporty lub przykłady,
- listę otwartych pytań,
- rekomendację, czy zmiana może wejść od razu, czy wymaga potwierdzenia.

Jeśli są dwie poprawne interpretacje, dokumentuj obie i wskaż preferowaną.

---

## Decyzje i gałęzie

### Jeśli definicja jest jasna i zgodna

- Potwierdź zgodność.
- Wypisz źródła.
- Podaj krótki przykład.
- Zakończ listą kontrolną.

### Jeśli definicja i widok się różnią

- Pokaż różnicę wprost.
- Nazwij element różniący się: ziarno, zwroty, VAT, rabat, filtr, agregacja.
- Nie poprawiaj dokumentacji bez wskazania, który wariant jest używany w raporcie.
- Zostaw otwarte pytanie o docelową definicję biznesową.

### Jeśli definicja jest niepełna

- Wypisz, czego brakuje.
- Zapytaj użytkownika o brakujący element.
- Zatrzymaj się przed zapisaniem sprzecznej definicji.

### Jeśli przykład nie zgadza się z definicją

- Sprawdź najpierw ziarno i filtr okresu.
- Potem sprawdź zwroty i korekty.
- Dopiero na końcu sprawdź różnicę w implementacji.

---

## Format wyniku

Zwracaj odpowiedź w tej kolejności:
1. Co sprawdzono.
2. Co jest zgodne.
3. Co się różni.
4. Jakie źródła wykorzystano.
5. Jakie są otwarte kwestie.
6. Propozycja zmiany dokumentacji albo następnego pytania do użytkownika.

---

## Checklist jakości

- [ ] Metryka ma jednoznaczną nazwę.
- [ ] Źródło definicji jest wskazane.
- [ ] Ziarno jest opisane.
- [ ] Wzór jest zgodny z implementacją albo różnica jest nazwana.
- [ ] Przykład liczbowy jest policzony lub świadomie pominięty.
- [ ] Otwarte kwestie są wypisane jasno.
- [ ] Użytkownik wie, co można zmienić od razu, a co wymaga decyzji.

---

## Szablon notatki

```text
Metryka: ...
Cel: tworzenie / aktualizacja / przegląd
Źródła: ...
Definicja: ...
Ziarno: ...
Przykład: ...
Różnice względem widoku: ...
Otwarte kwestie: ...
Rekomendacja: ...
```
