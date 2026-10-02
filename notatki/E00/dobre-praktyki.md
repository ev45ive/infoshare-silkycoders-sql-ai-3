# E00 — Dobre praktyki: od niejasnego polecenia do szkicu SQL

**Zakres:** praca w ASK bez plików, internetu, bazy i narzędzi. Rezultatem jest szkic zapytania, jawne założenia i lista spraw do wyjaśnienia przed użyciem SQL w raporcie.

## Jakich problemów i zadań analityka dotyczy ten moduł?

- Doprecyzowanie niejasnego zlecenia: „sprawdź sprzedaż”, „napisz złożone zapytanie”, „porównaj kanały”.
- Przygotowanie roboczego szkicu SQL do rozmowy z zespołem hurtowni.
- Zebranie pytań o źródła, strukturę danych i znaczenie miar, zanim powstanie raport.
- Wychwycenie tabel, kolumn i reguł, które AI dopowiedziało bez źródła.
- Uzyskanie odpowiedzi AI w formie, którą łatwo przejrzeć i skomentować.
- Wyjaśnienie firmowego skrótu lub pojęcia, które może mieć kilka znaczeń.
- Przekazanie zadania do nowej rozmowy z kompletnym kontekstem.

## Pojęcia AI — krótkie definicje

| Pojęcie | Definicja |
| --- | --- |
| Model językowy / LLM | Generowanie tekstu według wzorców |
| Prompt | Polecenie dla modelu |
| Rola w poleceniu | Perspektywa wykonywania zadania |
| Kontekst | Informacje dostępne przy odpowiedzi |
| Historia rozmowy | Wcześniejsze wiadomości i odpowiedzi |
| Sesja | Ciąg pracy w rozmowie |
| Token | Jednostka przetwarzanego tekstu |
| Okno kontekstu | Limit informacji na wejściu |
| Harness / otoczka | Organizacja kontekstu i narzędzi |
| Zero-shot | Polecenie bez przykładów |
| One-shot | Jeden przykład odpowiedzi |
| Few-shot | Kilka przykładów odpowiedzi |
| Agent | Model działający przez narzędzia |
| Samokontrola modelu | Przegląd własnej odpowiedzi |

## Metody, narzędzia i procedury do zastosowania

- **Czat ASK:** przygotowanie szkicu, pytań i planu sprawdzenia.
- **Stopniowe doprecyzowanie polecenia:** dodawanie celu, roli, domeny, reguł i formatu odpowiedzi.
- **Rejestr założeń:** tabela `co dodano | co model założył | co trzeba sprawdzić`.
- **Lista brakujących informacji:** pytania o silnik SQL, schemat, ziarno, definicję metryki i zakres analizy.
- **Kontrakt odpowiedzi:** stały układ `cel → założenia i braki → szkic SQL → sposób sprawdzenia`.
- **Przykład oczekiwanego układu:** pokazanie formy z wyraźnym oddzieleniem jej od faktów o bazie.
- **Przegląd założeń SQL przez AI:** zlecenie wskazania podstaw, domysłów i brakujących źródeł.
- **Przekazanie kontekstu:** zlecenie przygotowania pakietu z celem, ustaleniami, szkicem i otwartymi pytaniami.

## Trzy procedury — polecenia do przekazania AI

Każdy krok poniżej jest poleceniem do wysłania. W E00 wykonujemy je w ASK, więc przegląd dotyczy treści rozmowy, a sprawdzenia na bazie pozostają planem.

### 1. Przygotowanie szkicu SQL

1. „Chcę przygotować szkic SQL do [cel]. Zadaj mi do trzech pytań, które pomogą doprecyzować oczekiwany rezultat. Poczekaj na odpowiedzi.”

   - **Po co:** ogranicza ryzyko rozwiązania innego problemu niż ten, który mamy na myśli.

2. „Pracuj jako analityk hurtowni danych. Kontekst firmy i znane fakty: [opis]. Oddziel te informacje od założeń potrzebnych do przygotowania szkicu.”

   - **Po co:** nadaje kierunek odpowiedzi i pomaga oddzielić fakty od domysłów modelu.

3. „Wypisz brakujące informacje o silniku SQL, schemacie, ziarnie danych i definicji sprzedaży. Zamień je w pytania do zespołu DW; zaznacz, które blokują użycie zapytania w raporcie.”

   - **Po co:** daje konkretną listę ustaleń potrzebnych przed dalszą pracą.

4. „Przygotuj odpowiedź w układzie: cel, założenia i braki, szkic SQL z komentarzami, plan sprawdzenia. Nieznane tabele i kolumny oznacz jako umowne.”

   - **Po co:** ułatwia przegląd propozycji i ogranicza ryzyko uznania wymyślonych nazw za rzeczywisty schemat.

5. „Zastosuj ten wzór układu: [przykład]. Przejmij wyłącznie formę. Wypisz, co zmieniłeś względem poprzedniej odpowiedzi i jakie braki pozostały.”

   - **Po co:** pozwala ujednolicić odpowiedź bez przenoszenia niepotwierdzonych szczegółów z przykładu.

**W E00:** kolejne próby korzystają ze wspólnej historii. Porównanie odpowiedzi opisuje obserwowaną zmianę, ale nie dowodzi wpływu samej ostatniej linijki.

### 2. Ujawnienie założeń i braków w szkicu

1. „Przejrzyj poniższy szkic SQL: [SQL]. Wypisz założenia dotyczące tabel, połączeń, miar, okresu i zwrotów.”

   - **Po co:** wydobywa decyzje ukryte w zapytaniu, które mogą zmienić znaczenie wyniku.

2. „Przy każdym założeniu wskaż podstawę w przekazanych informacjach albo oznacz »brak źródła«. Nie dopisuj źródeł, których nie otrzymałeś.”

   - **Po co:** pomaga odróżnić uzasadnione wybory od domysłów wymagających potwierdzenia.

3. „Porównaj szkic z przykładem użytym w rozmowie. Wskaż nazwy i reguły przejęte z przykładu, których nie potwierdzają podane fakty.”

   - **Po co:** ogranicza ryzyko potraktowania wzoru odpowiedzi jako dokumentacji bazy.

4. „Dla niepotwierdzonych założeń zaproponuj źródło lub test oraz opisz, co ma on rozstrzygnąć. Oznacz wszystkie niewykonane kontrole jako planowane.”

   - **Po co:** tworzy plan dalszej weryfikacji; sam przegląd wykonany przez model nie jest niezależnym testem.

5. „Przygotuj krótką notatkę dla zespołu DW: co proponujemy, co zakładamy i o co pytamy. Oznacz SQL jako niezweryfikowany szkic.”

   - **Po co:** pozwala przekazać propozycję do uzgodnienia wraz z jej ograniczeniami.

### 3. Przygotowanie kontekstu do nowej rozmowy

Kroki 1–3 dotyczą bieżącej rozmowy. Krok 4 wyślij w nowej rozmowie razem z przygotowanym pakietem.

1. „Przygotuj samodzielny pakiet do kontynuacji pracy: cel, znane fakty, ograniczenia, aktualny szkic SQL i otwarte pytania.”

   - **Po co:** zbiera informacje potrzebne do kontynuacji bez dostępu do dotychczasowej historii.

2. „Podziel ustalenia na fakty podane w rozmowie, przyjęte założenia i niewiadome. Zachowaj informację, że SQL nie został wykonany.”

   - **Po co:** chroni przed zamianą domysłów i planowanych testów w pozornie potwierdzone ustalenia.

3. „Zwróć kompletny pakiet w jednym bloku do skopiowania. Umieść pełny SQL; usuń odwołania typu »jak wcześniej« i »ostatnie zapytanie«.”

   - **Po co:** zapewnia jednoznaczny przedmiot pracy w nowej sesji.

4. „Oto pakiet kontekstu: [pakiet]. Na jego podstawie wypisz brakujące ustalenia potrzebne do uzgodnienia szkicu z zespołem DW. Nie zakładaj dostępu do poprzedniej rozmowy.”

   - **Po co:** daje nowej rozmowie konkretne zadanie i jawną podstawę odpowiedzi.

**W E00:** tę procedurę zastosuj po porównaniu rozmów z kroku 6 karty uczestnika, które najpierw odbywa się bez przenoszenia SQL.

## Przykładowy prompt do ponownego użycia

```text
Pomóż mi przygotować roboczy szkic SQL do uzgodnienia z zespołem hurtowni.
Cel: [pytanie biznesowe i oczekiwany rezultat].
Domena i znane fakty: [informacje, które rzeczywiście posiadam].
Brakujące informacje: [np. silnik SQL, schemat, ziarno, definicja metryki].

Odpowiedz w układzie:
1. Cel zapytania.
2. Założenia, braki i pytania do właściciela danych.
3. Szkic SQL z komentarzami; nieznane obiekty oznacz jako umowne.
4. Źródła i kontrole potrzebne przed użyciem zapytania w raporcie.

Nie przedstawiaj domysłów ani szczegółów z przykładu jako faktów o bazie.
Nie przedstawiaj proponowanych testów jako wykonanych.
```

Podstawa: [karta E00](../../materialy-uczestnika/E00/eksperymenty-ask.md) i [notatka prowadzącego](notatka-prowadzacego.md).
