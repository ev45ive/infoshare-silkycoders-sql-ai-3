---
description: "Zapisuje podsumowanie bieżącej rozmowy (kontekst, źródła, decyzje, kroki, błędy do uniknięcia, dalsze kroki) do pliku w docs/ai-sessions/, aby przekazać kontekst do nowego czatu lub agenta. Use when: handoff, przekaż rozmowę, zapisz kontekst sesji, kontynuuj w nowym chacie."
argument-hint: "(opcjonalnie) temat/slug do nazwy pliku"
agent: "agent"
---
Przeanalizuj całą dotychczasową rozmowę w tej sesji i zapisz jej podsumowanie
do nowego pliku w `docs/ai-sessions/`, tak aby ktoś (lub Ty w nowym czacie)
mógł kontynuować pracę bez utraty kontekstu.

## Parametry
- Temat z wywołania: `${input:temat:krótki temat/slug}`. Jeśli nie podano,
  wywnioskuj krótki slug (2-4 słowa, kebab-case) z głównego wątku rozmowy.
- Nazwa pliku: `docs/ai-sessions/handoff-<slug>-<RRRR-MM-DD>.md` (data dzisiejsza).
  Jeśli plik o takiej nazwie już istnieje, dopisz `-2`, `-3` itd.

## Zasady
- Opieraj się wyłącznie na treści bieżącej rozmowy (pytania użytkownika,
  Twoje odpowiedzi, wyniki narzędzi/zapytań SQL, odwiedzone pliki). Nie
  wymyślaj faktów, których nie było w rozmowie.
- Pisz po polsku, zwięźle, punktowo. Rozróżniaj fakty zweryfikowane (np. wynik
  zapytania SQL) od założeń/niepewności.
- Jeśli w rozmowie padły liczby/wyniki z bazy danych, zapisz je dosłownie wraz
  z zapytaniem SQL, które je wygenerowało (żeby można było zweryfikować).

## Struktura pliku
```markdown
# Handoff: <temat>

## Kontekst
- Workspace, data, język, kto pyta, jaki był cel rozmowy.

## Co ustalono / zweryfikowano
- Fakty, wyniki zapytań SQL (z treścią zapytania), odpowiedzi użytkownika na
  pytania doprecyzowujące.

## Źródła
- Konkretne pliki/widoki/tabele/dokumenty, z których korzystano (ścieżki
  względne), oraz ewentualne strony www (fetch_webpage).

## Decyzje i założenia
- Co przyjęto i dlaczego; co zostało potwierdzone przez użytkownika, a co
  jest założeniem niepotwierdzonym.

## Błędy / ślepe uliczki do uniknięcia
- Nieudane podejścia, błędne pierwsze odpowiedzi, poprawki.

## Stan na teraz
- Co jest zrobione, co w trakcie, co jeszcze nie zaczęte.

## Następne kroki
- Konkretne, kolejne działania do wykonania w nowej sesji.

## Otwarte pytania
- Kwestie nierozstrzygnięte, które nowy agent/analityk powinien dopytać
  użytkownika, zanim ruszy dalej.
```

## Kroki
1. Zbierz z historii rozmowy: pytania, odpowiedzi, zapytania SQL i ich wyniki,
   odwiedzone pliki/dokumenty, podjęte decyzje, napotkane błędy.
2. Wypełnij strukturę powyżej — pomiń sekcje, dla których naprawdę nie ma
   treści, zamiast wypełniać je na siłę.
3. Zapisz plik pod wyliczoną ścieżką (patrz Parametry).
4. Potwierdź użytkownikowi ścieżkę zapisanego pliku i krótko (1-3 zdania)
   podsumuj, co się w nim znalazło.
