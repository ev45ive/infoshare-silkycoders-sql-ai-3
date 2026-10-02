# Szablon pliku z dokumentacją metryki

Używaj tego układu dla plików, do których linkuje słownik.

## Struktura

```markdown
# [Nazwa metryki] — RetailDW

## Cel

Krótko: po co istnieje ta metryka i kiedy jej używamy.

## Definicja

Jednoznaczny opis biznesowy z wzorem liczenia.

## Ziarno

Na jakim poziomie metryka jest liczona poprawnie.

## Źródło danych

- tabela lub widok,
- kolumny użyte w obliczeniu,
- ewentualne filtry.

## Przykład

Krótki przykład liczbowy z podstawionymi wartościami.

## Porównanie z widokiem

- zgodność z `reporting.*`,
- różnice względem implementacji,
- uwagi o zwrotach, rabatach, VAT lub innych korektach.

## Otwarte kwestie

- co wymaga decyzji biznesowej,
- co trzeba doprecyzować przed publikacją.

## Linki

- [Słownik metryk](../slownik-metryk.md)
- [Powiązany widok](../../RetailDW/Views/reporting.vw_NazwaWidoku.sql)
```

## Zasady

- Nazwa pliku powinna odpowiadać metryce.
- Opis ma rozwijać wpis ze słownika, a nie go powielać.
- Jeśli metryka ma warianty, pokaż oba i zaznacz preferowany.
- Na końcu zostaw listę nierozstrzygniętych kwestii.
