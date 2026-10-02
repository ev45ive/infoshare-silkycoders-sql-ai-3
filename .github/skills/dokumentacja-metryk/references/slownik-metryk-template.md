# Szablon struktury słownika metryk

Używaj tego układu, gdy tworzysz lub porządkujesz `docs/slownik-metryk.md`.

## Przykładowa struktura

```markdown
# Słownik metryk Nordvik

Krótki opis, kiedy i do czego używamy słownika.

## Sprzedaż

| Metryka | Definicja | Źródło | Link do opisu |
| --- | --- | --- | --- |
| **Sprzedaż netto** | Sprzedaż brutto bez VAT. | `FactSales.NetAmount` | [opis](metryki/sprzedaz-netto.md) |

## Rentowność

| Metryka | Definicja | Źródło | Link do opisu |
| --- | --- | --- | --- |
| **Marża brutto** | Sprzedaż netto minus koszt własny minus zwroty netto. | `FactSales`, `FactReturns` | [opis](metryki/marza-brutto.md) |

## Transakcje i koszyk

| Metryka | Definicja | Źródło | Link do opisu |
| --- | --- | --- | --- |
| **Liczba transakcji** | Liczba unikalnych paragonów. | `FactSales.TransactionNo` | [opis](metryki/liczba-transakcji.md) |
```

## Zasady

- Jedna metryka = jeden wiersz.
- Definicja ma być krótka i jednoznaczna.
- W kolumnie linku prowadź do osobnego pliku dokumentacji metryki.
- Jeśli metryka ma warianty, nazwij je w definicji albo w osobnej kolumnie.
