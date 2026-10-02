# Źródła danych Nordvik

Systemy źródłowe przekazują pliki do strefy `src`. W tej strefie wiersze są zapisane w postaci otrzymanej z systemu; konwersja i walidacja następują podczas ładowania.

| System | Dane | Wzór nazwy pliku | Tabela wejściowa |
| --- | --- | --- | --- |
| Kasy sklepowe (POS) | Pozycje paragonów | `POS_yyyymmdd.csv` | `src.SalesRaw` |
| Sklep internetowy | Pozycje zamówień | `WEB_yyyymmdd.csv` | `src.SalesRaw` |
| Magazyn (WMS) | Stany na koniec dnia | `WMS_yyyymmdd.csv` | `src.InventoryRaw` |
| Portal zwrotów | Przyjęte zwroty | `RET_yyyymm.csv` | `src.ReturnsRaw` |

W tabelach `src.*` kolumna `SourceFile` wskazuje plik, z którego pochodzi wiersz, a `ExtractedAt` — czas jego przyjęcia.

## Ładowanie sprzedaży

`etl.LoadSales` wykonuje konwersję typów, łączy sprzedaż z wymiarami i wylicza miary. Sprawdź w schemacie XML, przez które obiekty przechodzą wiersze i jakie ziarno mają użyte w raporcie tabele oraz widoki.

Kolumna `SourceFile` w strefie wejściowej wskazuje pochodzenie wiersza. Sprawdź, na których dalszych warstwach ta informacja pozostaje dostępna. Przebieg ładowania, w tym status oraz liczbę wierszy odczytanych, załadowanych i odrzuconych, zapisuje `dbo.LoadLog`.

Pełny model kolumn i powiązań sprawdź w udostępnionym schemacie XML. Bieżące definicje metryk są w [słowniku metryk](slownik-metryk.md).
