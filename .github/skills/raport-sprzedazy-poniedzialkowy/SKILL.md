---
name: raport-sprzedazy-poniedzialkowy
description: "Poniedziałkowy raport sprzedaży tygodniowej dla Nordvik (RetailDW): automatyczne podsumowanie sprzedaży, porównanie WoW/YoY, integracja z SQL, export do MD/HTML/Excel. Use when: potrzebny raport tygodniowy za ostatni/wskazany tydzień ISO; generowanie w formatach MD (do e-maila), HTML (print-friendly, PDF), Excel (do analizy biznesowej)."
argument-hint: "Numer tygodnia (np. 2026-W38) — skill pyta interaktywnie jeśli puste. Opcjonalnie: --format md|html|xlsx|all"
user-invocable: true
disable-model-invocation: false
---

# Raport sprzedaży — Poniedziałkowy (automatyzacja)

## Cel

Generować cotygodniowy raport sprzedaży Nordvik w trzech formatach (Markdown, HTML, Excel) na podstawie danych z `RetailDW`. Raport zawiera:
- Podsumowanie sprzedaży netto, sztuk, liczby transakcji po kanałach (ONLINE / STORE / RAZEM)
- Porównania: tydzień do tygodnia (WoW) i rok do roku (YoY)
- Wstępna interpretacja (zmiany > 15%, anomalie)
- Walidacja kompletności danych (brak := baner "RAPORT NIEGOTOWY")

---

## Użycie

### Z Copilot Chat

```
#skill raport-sprzedazy-poniedzialkowy

Wygeneruj raport za ostatni pełny tydzień ISO. Format: Markdown + HTML.
```

Skill pyta interaktywnie:
- Który tydzień? (numer ISO, data, ostatnie 7 dni)
- Format? (MD, HTML, Excel, kombinacja)
- Zapisać do pliku? (tak/lokalizacja)

### Parametry (wewnętrzne, CLI)

```bash
python scripts/generate_report.py \
  --week 2026-W38 \
  --format all \
  --output raporty/
```

Parametry:
- `--week YYYY-Www` lub `--week YYYY-MM-DD` lub `--week 7days` — okres raportu
- `--format md|html|xlsx|all` — format(y) wyjściowe (domyślnie: `all`)
- `--output PATH` — katalog docelowy (domyślnie: `raporty/`)
- `--verbose` — debug logging

---

## Architektura

### Pliki skilla

```
raport-sprzedazy-poniedzialkowy/
├── SKILL.md                     # ta instrukcja
├── config.py                    # hardcoded: serwer, baza, ścieżki
├── scripts/
│   ├── generate_report.py       # entry point: CLI + orchestration
│   ├── sql_builder.py           # buduje SQL queries dynamicznie
│   ├── formatters.py            # rendery MD, HTML, Excel
│   ├── dependencies.py          # check & install libs
│   └── validators.py            # walidacja danych, okresu
├── templates/
│   ├── report.md.jinja2         # szablon Markdown
│   ├── report.html.jinja2       # szablon HTML (Tailwind CDN, print-friendly)
│   └── excel_structure.json     # config: arkusze, formatowanie
└── README.md                    # quick-start dla developera
```

### Flow

1. **Wejście** → CLI (`--week`, `--format`) lub pytania interaktywne
2. **Walidacja** → okres istnieje w `DimDate`? Dane sięgają końca okresu?
3. **SQL Builder** → buduje zapytania SELECT dynamicznie (WoW, YoY)
4. **Egzekucja** → uruchamia na `RetailDW` (pyodbc)
5. **Transformacja** → przygotowuje słownik danych dla szablonów
6. **Rendering** → Markdown (jinja2), HTML (jinja2 + Tailwind), Excel (openpyxl)
7. **Zapis** → do `raporty/raport-sprzedazy-YYYY-Www.{md,html,xlsx}`
8. **Output** → podsumowanie ścieżek i status

---

## Kroki dla skilla

### Krok 1: Interaktywne pytania

Jeśli użytkownik nie podał `--week`, zapytaj `#tool:vscode_askQuestions`:

```
- Który tydzień? (ISO, data, 7 dni temu)
- Format? (Markdown / HTML / Excel / wszystkie)
- Zapisać do pliku? (tak/lokalizacja)
```

### Krok 2: Walidacja

- Czy okres istnieje w `DimDate`?
- Czy okres ma 7 dni?
- Czy dane w `FactSales` sięgają końca analizowanego okresu?
- **Jeśli nie** → ostrzeżenie "RAPORT NIEGOTOWY" i przerwa.

### Krok 3: Budowanie SQL

`sql_builder.py` tworzy trzy zapytania:
1. Aktualna sprzedaż po kanałach (SELECT ... GROUP BY Channel)
2. Poprzedni tydzień (WoW)
3. Rok temu (YoY, same daty kalendarzowe — patrz uwaga poniżej)

### Krok 4: Egzekucja SQL

Uruchamia zapytania na RetailDW (hardcoded serwer, baza). Zbiera wyniki.

### Krok 5: Transformacja

Przelicza zmiany (%, PLN), przygotowuje słownik dla szablonów jinja2:

```python
context = {
    'period': '2026-W38 (14–20.09.2026)',
    'status': 'ready',  # lub 'incomplete'
    'metrics': {
        'ONLINE': {'net': 148893.07, 'qty': 1012, 'trans': 239},
        'STORE': {'net': 515858.96, 'qty': 3575, 'trans': 843},
        'RAZEM': {'net': 664752.03, 'qty': 4587, 'trans': 1082}
    },
    'prev_week': {...},
    'yoy': {...},
    'changes': {
        'wow_net_pct': -4.0,
        'yoy_net_pct': 6.3,
        ...
    },
    'interpretation': [...],  # lista wniosków
    'data_source': [...]       # lista założeń
}
```

### Krok 6: Rendering

- **Markdown**: jinja2 + `report.md.jinja2` → `raport-sprzedazy-YYYY-Www.md`
- **HTML**: jinja2 + `report.html.jinja2` (Tailwind CDN) → `raport-sprzedazy-YYYY-Www.html`
- **Excel**: `openpyxl` + `excel_structure.json` → `raport-sprzedazy-YYYY-Www.xlsx` (3 arkusze: Podsumowanie, Szczegóły, Trends)

### Krok 7: Zapis i output

Zapisuje do `raporty/`, wypisuje podsumowanie w czacie:
```
✅ Raport gotowy za 2026-W38 (14–20.09.2026)
📄 Markdown: raporty/raport-sprzedazy-2026-W38.md
🌐 HTML: raporty/raport-sprzedazy-2026-W38.html
📊 Excel: raporty/raport-sprzedazy-2026-W38.xlsx
```

---

## Notatki

### YoY: Same daty, nie numery tygodnia ISO

Rok do roku liczony jest **po datach kalendarzowych** (14–20.09 w obu latach), a nie po numerach tygodni ISO. Powód: tygodnie ISO mogą się nie pokrywać (W37 2025 kontra W38 2026). Skill automatycznie:
1. Wyciąga daty z analizowanego tygodnia ISO
2. Znajduje ten sam zakres dat rok wcześniej
3. Oblicza YoY

### Brak danych = RAPORT NIEGOTOWY

Jeśli którykolwiek dzień analizowanego tygodnia ma 0 transakcji w `FactSales`, raport dostaje baner:
```
⚠️ RAPORT NIEGOTOWY — brakuje danych za [daty]. Sprawdź ETL.
```

Raport i tak się generuje, ale z adnotacją.

### Weryfikacja vs vw_SalesWeekly

Po egzekucji SQL, skill porównuje `NetAmount` i `Units` ze zwykłym `SELECT` z `vw_SalesWeekly` (jeśli agregacja na kanały pokrywa się). Jeśli różnica > 1%, loguje warning.

### Dependencje

Skill sprawdza i instaluje (w katalogu `.github/skills/raport-sprzedazy-poniedzialkowy/venv` lub globalnie):
- `pandas` — transformacja danych
- `jinja2` — szablony
- `openpyxl` — Excel
- `pyodbc` — połączenie MSSQL
- `click` — CLI (opcjonalnie)

---

## Checklist — czy raport jest gotowy?

- [ ] Period został potwierdzony (lub interaktywnie wybrano)
- [ ] Okres istnieje w `DimDate` (7 dni, aktualna data)
- [ ] `FactSales` sięga ostatniego dnia okresu
- [ ] SQL znalazł dane (nie NULL, nie 0)
- [ ] Zmiany WoW/YoY wyliczone bez dzielenia przez 0
- [ ] Porównanie ze `vw_SalesWeekly` — spójne
- [ ] Szablony są uzupełnione (context pełny)
- [ ] Pliki zapisane do `raporty/`
- [ ] Output podsumowanie wypisane w czacie

---

## Troubleshooting

| Problem | Powód | Rozwiązanie |
|---------|-------|------------|
| `ModuleNotFoundError: No module named 'pyodbc'` | Brakuje biblioteki | Skill uruchamia `dependencies.py` — zainstaluje |
| `RAPORT NIEGOTOWY` | Brak danych za ostatni dzień W | Czekać na ETL, lub wybrać inny tydzień |
| Liczby nie zgadzają się z vw_SalesWeekly | Różna agregacja (kanał vs kanał+region) | Normalne, jeśli różnica < 1% |
| Plik HTML się nie otwiera | CSS z CDN niedostępny | Sprawdzić sieć, albo użyć offline CSS |
| Excel formułami z błędami | Dane zawierają NULL | Skill je obsługuje (0 domyślnie) |

---

## Dalsze kroki

- [ ] Wdrożyć jako scheduled task (co poniedziałek)
- [ ] Dodać powiadomienie e-mail z linkiem do raportu
- [ ] Integracja z Slack (post o nowym raporcie)
- [ ] Drill-down: kliknąć w kanał → szczegóły po kategoriach/sklepach
- [ ] Porównanie wielomiesięczne (MoM trend)
- [ ] Wykrywanie anomalii: alert jeśli zmiana > 20%

