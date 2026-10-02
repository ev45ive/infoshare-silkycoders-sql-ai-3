# E02 — Dobre praktyki: wyjaśnienie rozbieżności w raporcie

**Zakres:** agent korzysta z MSSQL, schematu XML, słownika metryk i opisu źródeł. Odtwarza pochodzenie kwoty, sprawdza przyczynę rozbieżności i oblicza wariant skorygowany. Pracuje odczytowo; nie uruchamia ETL ani nie zmienia danych.

## Jakich problemów i zadań analityka dotyczy ten moduł?

- Wyjaśnienie różnicy między raportem hurtowni a podsumowaniem controllingu.
- Ustalenie, czy obie liczby dotyczą tej samej miary, okresu i zakresu danych.
- Prześledzenie kwoty od pliku źródłowego do raportu.
- Uzgodnienie liczności i wartości na kolejnych warstwach przetwarzania.
- Wykrycie powtórzonego wsadu mimo poprawnego zakończenia ładowania.
- Udowodnienie, że podejrzane zapisy są kopiami tych samych pozycji sprzedaży.
- Obliczenie wpływu powtórki i wskazanie kwoty do raportowania bez zmiany bazy.
- Przygotowanie opisu problemu dla właściciela danych i utrwalenie sposobu diagnozy.

## Pojęcia AI — krótkie definicje

| Pojęcie | Definicja |
| --- | --- |
| Plan diagnostyczny | Kolejność sprawdzeń dla hipotez |
| Hipoteza | Wyjaśnienie wymagające sprawdzenia |
| Ślad dowodów | Powiązanie wniosków z kontrolami |
| Kontrtest | Próba podważenia wyjaśnienia |
| Granica autonomii | Zakres samodzielnego działania agenta |
| Instrukcja wielokrotnego użytku | Zapis powtarzalnego sposobu pracy |
| Test transferu | Próba na innym zadaniu |

## Pojęcia analityczne występujące w E02

| Pojęcie | Definicja |
| --- | --- |
| Lineage / pochodzenie danych | Pochodzenie i przekształcenia danych |
| Reconciliation / uzgodnienie warstw | Porównanie liczności i wartości |
| Retry wsadu | Ponowne dostarczenie wsadu |
| Klucz biznesowy pozycji | Identyfikator pozycji zdarzenia biznesowego |
| Deduplikacja | Wyłączenie nadmiarowych kopii |

## Metody, narzędzia i procedury do zastosowania

- **Odtworzenie liczby raportu:** wykonanie SQL na wspólnej metryce i okresie.
- **Odczyt XML i definicji przez MSSQL:** ustalenie obiektów, transformacji i miejsc zachowania pochodzenia.
- **Diagram lineage:** pokazanie ścieżki danych oraz zmiany ziarna między obiektami.
- **Uzgodnienie warstw:** porównanie wierszy i kwot z uwzględnieniem transformacji oraz zaokrągleń.
- **Odczyt `LoadLog`:** ustalenie przebiegu ładowania i zakresu informacji potwierdzanych przez log.
- **Zawężanie rozbieżności:** zejście od miesiąca do dnia, kanału, sklepu i pliku.
- **Porównanie zawartości plików:** sprawdzenie pól biznesowych i liczności ich kombinacji.
- **Odczytowe wyłączenie kopii:** obliczenie wariantu wyniku bez potwierdzonej powtórki.
- **Kontrtest:** sprawdzenie, czy przyjęty klucz nie wyklucza legalnych pozycji.
- **Instrukcja i prompt lineage:** zapis metody i próba na drugim okresie.

## Trzy procedury — polecenia dla agenta

Każdy krok jest poleceniem do wysłania. Wykonane kontrole mają wracać z SQL i wynikiem; przy brakującym źródle agent ma nazwać brak zamiast zgadywać przyczynę.

### 1. Odtworzenie raportu i prześledzenie warstw

1. „Przeczytaj zgłoszenie, słownik metryk i opis źródeł. Ustal wspólną definicję sprzedaży netto, okres i zakres porównania. Wypisz brakujące ustalenia.”

   - **Po co:** chroni przed diagnozowaniem rozbieżności wynikającej z porównania różnych miar lub okresów.

2. „Odtwórz kwotę raportu za sierpień 2026 z `FactSales` i `reporting.vw_SalesDaily`. Pokaż wykonany SQL, filtry i różnicę względem liczby z maila.”

   - **Po co:** ustala punkt wyjścia i wielkość rozbieżności przed szukaniem przyczyny.

3. „Na podstawie XML, opisu źródeł i dostępnych definicji narysuj ścieżkę `src.SalesRaw → stg.Sales → dbo.FactSales → reporting.vw_SalesDaily`. Wskaż rolę `etl.LoadSales`, ziarno obiektów i miejsce utraty `SourceFile`. Odczytaj definicję ETL; nie uruchamiaj procedury.”

   - **Po co:** wskazuje miejsca dalszych kontroli i chroni przed przypadkowym przebudowaniem danych podczas diagnozy.

4. „Dla tego samego miesiąca uzgodnij liczność i kwotę netto w `src`, `stg` i fakcie oraz kwotę w widoku. W warstwach wejściowych zastosuj przeliczenia i zaokrąglenia na poziomie pozycji zgodne z ETL. Pokaż nieudane konwersje.”

   - **Po co:** ujawnia, gdzie zmieniły się dane; przy innym ziarnie widoku porównuje wartości zamiast liczby wierszy.

5. „Odczytaj `dbo.LoadLog` dla ładowania sprzedaży. Pokaż status i liczniki, oddzielając zakres całego ładowania od sierpniowych filtrów. Podsumuj, co potwierdzają log i zgodność warstw, a jakie kontrole źródła są nadal potrzebne.”

   - **Po co:** odróżnia poprawne wykonanie procesu od jakości danych, które proces przyjął.

### 2. Dowód powtórki i obliczenie jej wpływu

1. „Zawęź rozbieżność przez porównanie dni, kanałów i sklepów. Zestaw kwoty, liczbę pozycji i liczbę paragonów. Wskaż fragment danych do sprawdzenia w źródle.”

   - **Po co:** ogranicza obszar poszukiwań i pomaga zauważyć powtórzone pozycje bez proporcjonalnego wzrostu liczby paragonów.

2. „Dla wskazanego fragmentu porównaj pliki w `src.SalesRaw`: pola biznesowe, liczność każdej kombinacji pól i kwoty. Pomiń techniczne identyfikatory przy porównaniu treści. Nie uznawaj nazwy pliku ani równej sumy za dowód kopii.”

   - **Po co:** potwierdza powtórkę zawartości i wykrywa różnice, które same sumy mogłyby ukryć.

3. „Sprawdź klucz pozycji: data, sklep, numer paragonu i numer pozycji. Dla powtórek porównaj też SKU, ilość, cenę i rabat. Powiąż je z faktami przez zgodność klucza i wartości; wskaż przypadki niejednoznaczne.”

   - **Po co:** odróżnia kopie od legalnych zdarzeń i odtwarza pochodzenie mimo braku `SourceFile` w fakcie.

4. „Dla potwierdzonych kopii wykonaj odczytowe obliczenie zachowujące jedną kopię pozycji. Pokaż kwotę przed wyłączeniem, po wyłączeniu oraz wpływ powtórki. Nie usuwaj wierszy i nie zmieniaj ETL.”

   - **Po co:** mierzy wpływ błędu na raport bez ingerowania w dane źródłowe.

5. „Uruchom kontrtest: sprawdź, że wyłączone pozycje odpowiadają udowodnionej kopii, różnica kwot równa się jej wartości, a legalne pozycje z innych dni i sklepów pozostają. Przy konflikcie wróć do klucza i porównania treści.”

   - **Po co:** chroni przed skorygowaniem raportu przez zbyt szerokie wyłączenie danych.

6. „Przygotuj odpowiedź dla Tomasza: przyczyna, kwota do raportowania, skala różnicy, wykonane kontrole i pozostałe ograniczenia. Dołącz opis problemu dla właściciela danych oraz potrzebnego działania naprawczego.”

   - **Po co:** łączy wniosek biznesowy z dowodem i przekazuje naprawę procesu właściwemu zespołowi.

### 3. Zapis metody lineage i próba na innym okresie

Kroki 1–2 dotyczą bieżącej rozmowy. Krok 3 wyślij w nowej sesji z dostępem do zapisanych plików, bazy i dokumentacji. Krok 4 służy ocenie wyniku tej próby.

1. „Zapisz instrukcję diagnozy: wspólna miara i okres, odtworzenie raportu, diagram lineage, uzgodnienie warstw, zawężenie, dowód źródłowy, kontrtest i odpowiedź. Uwzględnij pracę odczytową oraz reakcję na brak źródeł.”

   - **Po co:** utrwala kolejność dochodzenia i granice działania agenta.

2. „Zapisz prompt do tej instrukcji z parametrami okresu, miary i pytania. Wskaż potrzebne źródła oraz wymagany format dowodów. Nie wpisuj na stałe sierpniowej przyczyny ani nazw podejrzanych plików.”

   - **Po co:** pozwala zastosować metodę do nowego przypadku bez narzucania starej odpowiedzi.

3. „Użyj zapisanej instrukcji i promptu, aby prześledzić sprzedaż netto za `2026-W38`. Pokaż ścieżkę danych, wykonane kontrole, wykryte różnice i granice wniosku. Jeśli nie znajdziesz powtórki, podaj zakres sprawdzenia.”

   - **Po co:** sprawdza działanie procedury na innym okresie bez założenia, że musi wystąpić ten sam błąd.

4. „Przejrzyj wynik próby i ślad wykonania: [wynik i SQL]. Wskaż pominięte etapy oraz wnioski bez dowodu. Popraw instrukcję lub prompt tam, gdzie próba wykazała brak, i przygotuj ponowną próbę.”

   - **Po co:** poprawia procedurę na podstawie jej użycia, zamiast uznawać sam zapis za działający artefakt.

## Przykładowy prompt do ponownego użycia

```text
Wyjaśnij rozbieżność: [pytanie i porównywane kwoty].
Okres: [zakres]. Miara: [definicja lub źródło definicji].
Pracuj odczytowo; nie uruchamiaj ETL i nie zmieniaj danych.

Odtwórz raport i prześledź jego pochodzenie od źródła.
Uzgodnij liczności i wartości z uwzględnieniem ziarna oraz przeliczeń.
Oddziel powodzenie ładowania od oceny jakości wsadu.

Zawęź rozbieżność i sprawdź hipotezę na danych źródłowych.
Jeśli potwierdzisz kopie, zweryfikuj klucz i zgodność wartości,
policz ich wpływ odczytowo oraz wykonaj kontrtest zakresu wyłączenia.

Zwróć diagram, wykonany SQL, wyniki kontroli, wniosek biznesowy,
ograniczenia i proponowane działanie dla właściciela danych.
Nie przedstawiaj planowanych kontroli jako wykonanych.
```

Podstawa: [zgłoszenie E02](../../materialy-uczestnika/E02/zgloszenie.md), [opis źródeł](../../materialy-uczestnika/docs/zrodla-danych.md), [słownik metryk](../../materialy-uczestnika/docs/slownik-metryk.md) i [notatka prowadzącego](notatka-prowadzacego.md).
