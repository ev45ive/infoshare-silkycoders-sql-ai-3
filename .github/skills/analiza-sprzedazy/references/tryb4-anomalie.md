# Tryb 4 — Analiza anomalii: brak towaru vs brak popytu vs błąd danych

## Kiedy stosować

- Użytkownik pyta wprost "dlaczego sprzedaż spadła/wzrosła".
- Tryb 1/2/3 wykrył zmianę > 15% i użytkownik potwierdził (`#tool:vscode_askQuestions`), że chce drążyć.

## Zasada: nie zgaduj, testuj hipotezy liczbami

Nie formułuj wniosku ("to brak towaru") na podstawie samej korelacji dwóch spadających liczb (sprzedaż ↓ i zapas ↓). Spadek zapasu i spadek sprzedaży mogą współwystępować zarówno przy niedoborze towaru, jak i przy spadku popytu — rozróżnia je **tempo konsumpcji zapasu**, nie sam kierunek zmiany.

## Hipotezy do rozróżnienia

1. **Brak towaru (stockout):** popyt jest, ale towaru brakuje — klienci kupiliby więcej, gdyby było dostępne.
2. **Brak popytu:** towar jest dostępny, ale klienci go nie chcą — sezon się skończył, zmiana trendu, konkurencja.
3. **Błąd danych / ETL:** liczby się nie zgadzają między warstwami, podejrzane duplikaty lub braki — **to NIE jest problem biznesowy, przejdź do skilla `analiza-pochodzenia-danych`** zamiast kontynuować tutaj.

## Test rozstrzygający: tempo konsumpcji zapasu

$$\text{Tempo konsumpcji} = \frac{\text{Sztuki sprzedane w okresie}}{\text{Stan zapasu na koniec okresu}} \times 100\%$$

- **Tempo rośnie między okresami** → zapas kurczy się szybciej niż wcześniej względem tego, co zostało → **sygnał braku towaru** (sprzedajemy proporcjonalnie więcej z malejącej puli, popyt "goni" malejący zapas).
- **Tempo stabilne lub maleje**, a sprzedaż i zapas spadają razem w podobnym tempie → **sygnał braku popytu** (zapas się kurczy bo go nie uzupełniamy/sprzedajemy mniej, ale nie dlatego że go brakuje).

Uzupełniające sygnały:
- **Zwroty rosną** (szt. i wartość) → niedopasowanie produktu do oczekiwań klienta → wspiera hipotezę braku popytu / problemu z produktem.
- **Zwroty maleją** → klienci zadowoleni, kupują co jest, konkurują o malejący zapas → wspiera hipotezę braku towaru.
- **Liczba aktywnych SKU ze sprzedażą spada** (np. 20 → 19) → model/wariant wypadł z oferty lub wyprzedał się całkowicie.
- **Dostępność SKU w magazynie (udział SKU ze stanem > 0)** — jeśli spada drastycznie, to silny sygnał stockout; jeśli stabilna mimo spadku sprzedaży, wspiera brak popytu.

## Procedura

### Krok 1: Policz tempo konsumpcji dla obu okresów porównania

```sql
WITH sprzedaze_tygodnie AS (
    SELECT
        dp.Department, -- lub inny wymiar/grupa do porównania
        dd.IsoWeek,
        CAST(SUM(fs.Quantity) AS INT) AS Sprzedane_szt
    FROM dbo.FactSales fs
    INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
    INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
      AND dp.Category = @Category
    GROUP BY dp.Department, dd.IsoWeek
),
stany_koniec_tygodnia AS (
    SELECT
        dp.Department,
        dd.IsoWeek,
        CAST(SUM(fid.StockQuantity) AS INT) AS Stan_Koniec_szt
    FROM dbo.FactInventoryDaily fid
    INNER JOIN dbo.DimDate dd ON fid.DateKey = dd.DateKey
    INNER JOIN dbo.DimProduct dp ON fid.ProductKey = dp.ProductKey
    WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
      AND dp.Category = @Category
      AND dd.DayOfWeek = 7  -- niedziela = koniec tygodnia handlowego
    GROUP BY dp.Department, dd.IsoWeek
)
SELECT
    COALESCE(st.Department, sp.Department) AS Department,
    COALESCE(st.IsoWeek, sp.IsoWeek) AS Tydzien,
    sp.Sprzedane_szt,
    st.Stan_Koniec_szt,
    CAST(sp.Sprzedane_szt * 100.0 / NULLIF(st.Stan_Koniec_szt, 0) AS DECIMAL(6, 2)) AS Tempo_Konsumpcji_Proc
FROM sprzedaze_tygodnie sp
FULL OUTER JOIN stany_koniec_tygodnia st
    ON sp.Department = st.Department AND sp.IsoWeek = st.IsoWeek
ORDER BY Department, Tydzien;
```

Porównaj `Tempo_Konsumpcji_Proc` między okresami per grupa — wzrost sugeruje stockout, stabilność/spadek sugeruje brak popytu.

### Krok 2: Sprawdź zwroty jako sygnał potwierdzający

```sql
SELECT
    dp.Department,
    dd.IsoWeek,
    CAST(SUM(fr.Quantity) AS INT) AS Sztuki_Zwrotow,
    CAST(SUM(fr.ReturnAmount) / 1.23 AS DECIMAL(12, 2)) AS Wartosc_Zwrotow_Netto_PLN
FROM dbo.FactReturns fr
INNER JOIN dbo.DimDate dd ON fr.DateKey = dd.DateKey
INNER JOIN dbo.DimProduct dp ON fr.ProductKey = dp.ProductKey
WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
  AND dp.Category = @Category
GROUP BY dp.Department, dd.IsoWeek
ORDER BY dp.Department, dd.IsoWeek;
```

### Krok 3: Sprawdź liczbę aktywnych SKU ze sprzedażą i dostępność

```sql
-- Aktywne SKU ze sprzedażą (czy któryś model/wariant wypadł)
SELECT dd.IsoWeek, COUNT(DISTINCT fs.ProductKey) AS AktywneSkuZeSprzedaza
FROM dbo.FactSales fs
INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
  AND dp.Department = @Department AND dp.Category = @Category
GROUP BY dd.IsoWeek;

-- Dostępność SKU w magazynie per sklep (koniec tygodnia)
SELECT
    dd.IsoWeek, ds.Channel, ds.StoreName,
    COUNT(DISTINCT fid.ProductKey) AS SKU_Aktywnych,
    COUNT(DISTINCT CASE WHEN fid.StockQuantity > 0 THEN fid.ProductKey END) AS SKU_Dostepne,
    CAST(COUNT(DISTINCT CASE WHEN fid.StockQuantity > 0 THEN fid.ProductKey END) * 100.0
         / NULLIF(COUNT(DISTINCT fid.ProductKey), 0) AS DECIMAL(5, 2)) AS Dostepnosc_Proc
FROM dbo.FactInventoryDaily fid
INNER JOIN dbo.DimDate dd ON fid.DateKey = dd.DateKey
INNER JOIN dbo.DimStore ds ON fid.StoreKey = ds.StoreKey
INNER JOIN dbo.DimProduct dp ON fid.ProductKey = dp.ProductKey
WHERE dd.IsoYear = @Rok AND dd.IsoWeek IN (@TydzienPoprzedni, @TydzienBiezacy)
  AND dp.Department = @Department AND dp.Category = @Category
  AND dd.DayOfWeek = 7
GROUP BY dd.IsoWeek, ds.Channel, ds.StoreName
ORDER BY dd.IsoWeek, ds.Channel, ds.StoreName;
```

### Krok 4: Zbuduj werdykt — tabela dowodów

Zestaw wszystkie sygnały w jednej tabeli (grupa × tempo konsumpcji, kierunek zmiany, zwroty, SKU aktywne) i dopiero na tej podstawie sformułuj wniosek. Jeśli sygnały są sprzeczne (np. tempo rośnie, ale zwroty też rosną), zgłoś to jako niejednoznaczne i zaproponuj dalsze drążenie zamiast wymuszać jednoznaczny werdykt.

### Krok 5: Gdy coś nie gra — podejrzenie problemu technicznego

Jeśli podczas tej analizy liczby się nie zgadzają (np. suma zapasu ujemna, SKU bez odpowiednika w `DimProduct`, drastyczne niezgodności między warstwami) — **zatrzymaj analizę biznesową** i zaproponuj użytkownikowi przejście do skilla `analiza-pochodzenia-danych`, który ma dedykowaną procedurę śledzenia `src → stg → dbo`.

## Format odpowiedzi

1. **Hipotezy testowane:** brak towaru / brak popytu (+ ew. błąd danych).
2. **SQL** dla każdego testu, z komentarzami.
3. **Tabela dowodów:** grupa × tempo konsumpcji (oba okresy + zmiana p.p.) × zwroty × SKU aktywne.
4. **Werdykt per grupa**, z uzasadnieniem opartym na tabeli dowodów — nie na samej korelacji kierunków.
5. **Rekomendacja:** konkretna akcja (uzupełnić zapas / zbadać popyt / przenieść budżet) lub, jeśli dane są niespójne, link do `analiza-pochodzenia-danych`.
6. **Otwarte pytania:** co jeszcze warto sprawdzić (sezonowość, konkurencja, marża przy przesunięciu asortymentu).
