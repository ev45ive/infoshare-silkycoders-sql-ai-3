# E01 — Dobre praktyki: sprawdzona odpowiedź o sprzedaży

**Zakres:** agent korzysta z MSSQL i pełnego schematu XML. W pierwszej próbie nie ma słownika metryk; po jego otrzymaniu ponawia obliczenie i kontrole. Na końcu zapisuje prompt i reguły pracy w `AGENTS.md`.

## Jakich problemów i zadań analityka dotyczy ten moduł?

- Odpowiedź na nieprecyzyjne pytanie: „ile sprzedaliśmy w zeszłym tygodniu?”.
- Ustalenie, czy pytanie dotyczy kwoty, sztuk, sprzedaży brutto, netto czy sprzedaży po zwrotach.
- Obliczenie sprzedaży według kanału i porównanie dwóch pełnych tygodni.
- Rozstrzygnięcie, czy „online rośnie” oznacza wzrost kwoty, dynamikę czy wzrost udziału.
- Porównanie pierwszego obliczenia z wynikiem opartym na firmowej definicji.
- Przygotowanie krótkiej odpowiedzi zarządczej z okresem, jednostką, źródłem i wykonanymi kontrolami.
- Utrwalenie sposobu pracy, żeby agent reagował właściwie na brak dokumentacji w kolejnych zadaniach.

## Pojęcia AI — krótkie definicje

| Pojęcie | Definicja |
| --- | --- |
| Narzędzie MSSQL | Dostęp do wykonania SQL |
| Trwały kontekst | Informacje dostępne między sesjami |
| Ugruntowanie odpowiedzi | Oparcie odpowiedzi na źródłach |
| Dowód wykonania | Wynik rzeczywiście uruchomionej operacji |
| Kontrakt odpowiedzi | Uzgodniony zakres i format |
| Prompt wielokrotnego użytku | Polecenie z parametrami zadania |
| `AGENTS.md` | Reguły pracy agenta |
| Test w nowej sesji | Próba bez poprzedniej historii |

## Pojęcia analityczne występujące w E01

| Pojęcie | Definicja |
| --- | --- |
| Liczba kandydacka | Wynik przy niepotwierdzonej definicji |
| Sprzedaż zarządcza | Netto przed odjęciem zwrotów |
| Tydzień ISO | Poniedziałek–niedziela według ISO |
| Rok ISO | Rok numeracji tygodni |
| WoW | Zmiana tydzień do tygodnia |
| Punkt procentowy | Różnica wartości procentowych |

## Metody, narzędzia i procedury do zastosowania

- **Doprecyzowanie zakresu:** zlecenie agentowi ustalenia okresu, miary i znaczenia pytania o online.
- **Odczyt schematu XML i MSSQL:** znalezienie rzeczywistych obiektów i wykonanie zapytań.
- **Obliczenie z jawnym założeniem:** oddzielenie wyniku liczbowego od niepotwierdzonej definicji biznesowej.
- **Odczyt słownika metryk:** powiązanie użytej miary i okresu z konkretną definicją.
- **Porównanie prób:** zachowanie pierwszego SQL, wyniku i założeń przed ponownym obliczeniem.
- **Kontrole wyniku:** zlecenie sprawdzenia dat, kanałów, zgodności sum i drugiej ścieżki agregacji.
- **Rozdzielenie wzrostu i udziału:** osobne obliczenie zmiany kwoty, dynamiki WoW i udziału kanału.
- **Prompt i `AGENTS.md`:** zapis procedury oraz sprawdzenie jej działania w nowej sesji.

## Trzy procedury — polecenia dla agenta

Każdy krok jest poleceniem do wysłania. Procedurę 1 stosuj przy E01-A, procedurę 2 po otrzymaniu E01-B i słownika, a procedurę 3 po uzyskaniu sprawdzonej odpowiedzi.

### 1. Pierwsze obliczenie z jawnymi założeniami

1. „Przeczytaj zgłoszenie Marty. Wypisz niejasności dotyczące okresu, znaczenia sprzedaży i wzrostu online. Okres wyznacz względem daty wiadomości, nie dzisiejszej daty.”

   - **Po co:** zapobiega odpowiedzi dla niewłaściwego tygodnia lub na inne pytanie niż zgłoszone.

2. „Odczytaj udostępniony schemat XML i sprawdź przez MSSQL obiekty potrzebne do obliczenia. Wskaż miary, daty, kanały oraz ziarno użytych tabel.”

   - **Po co:** opiera SQL na rzeczywistej strukturze i pomaga uniknąć zwielokrotnienia sprzedaży przez złączenia.

3. „Wskaż, którą miarę możesz teraz policzyć. Jeśli nie masz firmowej definicji sprzedaży, nazwij jej wybór założeniem i wypisz brakujące źródło.”

   - **Po co:** oddziela dostępność kolumny od potwierdzenia jej znaczenia biznesowego.

4. „Wykonaj SQL dla dwóch przyjętych pełnych tygodni: według kanału i dla całej sieci. Pokaż daty, przyjętą miarę, wynik oraz faktycznie wykonane zapytanie.”

   - **Po co:** daje liczbę kandydacką z możliwym do odtworzenia sposobem obliczenia.

5. „Zapisz pierwszą próbę: SQL, wynik, okres, przyjętą definicję i braki. Przygotuj pytania do Marty potrzebne do obrony tej liczby.”

   - **Po co:** zachowuje podstawę porównania po otrzymaniu dokumentacji.

### 2. Obliczenie według słownika i odpowiedź dla Marty

1. „Przeczytaj słownik metryk. Wskaż definicję sprzedaży zarządczej, tygodnia handlowego i zmiany WoW. Podaj źródło każdej definicji oraz daty obu tygodni względem maila Marty.”

   - **Po co:** ustala wspólną podstawę obliczenia i interpretacji odpowiedzi.

2. „Porównaj definicje ze słownika z założeniami pierwszej próby. Wypisz potrzebne zmiany w SQL i uzasadnieniu; zachowaj wcześniejszy wynik do porównania.”

   - **Po co:** pokazuje, czy zmienia się liczba, jej uzasadnienie, czy oba elementy.

3. „Wykonaj obliczenie zgodnie ze słownikiem dla obu tygodni i kanałów. Sumuj `FactSales.NetAmount` przed zwrotami; nie przeliczaj ponownie tej kwoty przez VAT. Pokaż wykonany SQL i wynik.”

   - **Po co:** stosuje firmową miarę i zachowuje kwoty netto wyliczone dla poszczególnych pozycji.

4. „Uruchom kontrole: zakres dat, dni kalendarza i dni ze sprzedażą według kanału, sumę kanałów wobec całości oraz porównanie z `reporting.vw_SalesDaily`. Pokaż wynik każdej kontroli i jej ograniczenia.”

   - **Po co:** wykrywa różnice filtrów i agregacji; zgodność widoku z faktem nie potwierdza jakości wspólnego wsadu.

5. „Oblicz dla online zmianę kwoty, dynamikę WoW i udział w sprzedaży sieci w obu tygodniach. Zmianę udziału podaj w punktach procentowych. Przy zerowym mianowniku pozostaw wskaźnik pusty.”

   - **Po co:** rozdziela różne znaczenia wzrostu i chroni przed mylącym porównaniem procentów.

6. „Przygotuj krótką odpowiedź dla Marty: okres, sprzedaż sieci i kanałów, porównanie tygodni, znaczenie wzrostu online, źródło definicji i wykonane kontrole. Dodaj pozostałe ograniczenia.”

   - **Po co:** przekłada obliczenie na odpowiedź, której zakres można jasno przedstawić na spotkaniu.

### 3. Zapis procedury i próba w nowych sesjach

Kroki 1–3 wykonaj w bieżącej rozmowie. Polecenie z kroku 4 wyślij w dwóch nowych sesjach, każdej z odpowiednim pakietem. Krok 5 służy porównaniu odpowiedzi z tych prób.

1. „Zapisz prompt »sprawdź sprzedaż« z parametrami: data odniesienia, okres, przekroje i pytanie biznesowe. Uwzględnij odczyt definicji, wykonanie SQL, kontrole i format odpowiedzi.”

   - **Po co:** pozwala powtarzać sposób pracy dla innych zgłoszeń bez kopiowania liczb z tego przypadku.

2. „Uzupełnij moje `AGENTS.md`: szukaj definicji w dostępnych źródłach, pytaj o brakujące, nie wymyślaj firmowych metryk, wymieniaj użyte definicje i nierozstrzygnięte braki. Zachowaj istniejące reguły.”

   - **Po co:** utrwala sposób reagowania na brak dokumentacji także poza bieżącą rozmową.

3. „Przygotuj dwa odizolowane środowiska próby z tymi samymi regułami, bazą i schematem. W pierwszym słownik ma być faktycznie poza dostępem agenta; w drugim dostępny. Nie kopiuj historii ani odpowiedzi z tej rozmowy. Zachowaj materiały bieżącego ćwiczenia.”

   - **Po co:** pozwala sprawdzić zachowanie przy brakującym i dostępnym źródle bez podpowiedzi z historii.

4. „Sprawdź sprzedaż z zeszłego tygodnia względem 22 września 2026. Podaj wynik według kanału, porównanie z poprzednim tygodniem i odpowiedź, czy online rośnie.”

   - **Po co:** to samo zgłoszenie w obu sesjach pozwala ocenić działanie zapisanych reguł bez przypominania ich w poleceniu.

5. „Porównaj odpowiedzi z obu prób: [odpowiedzi i ślad wykonania]. Czy bez słownika nazwano brak lub założenie, a ze słownikiem wskazano definicję, wykonany SQL i kontrole? Jeśli próba nie spełnia warunków, popraw reguły i pakiety do ponownej próby z kroku 4.”

   - **Po co:** ocenia faktyczne zachowanie agenta i daje podstawę do poprawienia procedury oraz powtórzenia próby.

## Przykładowy prompt do ponownego użycia

```text
Sprawdź sprzedaż dla zgłoszenia: [treść pytania].
Data odniesienia: [data wiadomości]. Przekroje: [np. kanały].

Odczytaj dostępny schemat i definicje biznesowe.
Jeśli brakuje definicji, poproś o źródło. Ewentualne obliczenie
kandydackie przedstaw z jawnym założeniem.

Wykonaj SQL dla ustalonego okresu i porównania. Pokaż zapytanie i wynik.
Uruchom kontrole okresu, podziału na kanały i zgodności sum.
Oddziel zmianę wartości od zmiany udziału.

Odpowiedz krótko: liczby, okres, jednostka, użyte definicje,
źródła, wykonane kontrole i pozostałe braki.
```

Podstawa: [E01-A](../../materialy-uczestnika/E01/zgloszenie-a.md), [E01-B](../../materialy-uczestnika/E01/zgloszenie-b.md), [słownik metryk](../../materialy-uczestnika/docs/slownik-metryk.md) i [notatka prowadzącego](notatka-prowadzacego.md).
