# Skill: raport-sprzedazy-poniedzialkowy

Automatyczne generowanie cotygodniowych raportów sprzedaży Nordvik w trzech formatach (Markdown, HTML, Excel).

## Struktura katalogów

```
raport-sprzedazy-poniedzialkowy/
├── SKILL.md                        # Instrukcja dla skilla (główny dokument)
├── config.py                       # Hardcoded: serwer, baza, ścieżki
├── scripts/
│   ├── generate_report.py          # Entry point: orchestracja, CLI
│   ├── dependencies.py             # Check & install Python packages
│   ├── validators.py               # Walidacja okresu, danych
│   ├── sql_builder.py              # Budowanie SQL dynamicznie
│   └── formatters.py               # Rendery: MD, HTML, Excel
├── templates/
│   ├── report.md.jinja2            # Szablon Markdown
│   ├── report.html.jinja2          # Szablon HTML (Tailwind CDN, print-friendly)
│   └── excel_structure.json        # Config Excel (arkusze, formatowanie)
└── README.md                       # Ten plik
```

## Szybki start

### Zainstaluj dependencje (jeśli nie ma automatycznie)

```bash
pip install pandas jinja2 openpyxl pyodbc
```

### Uruchom raport z CLI

```bash
python scripts/generate_report.py --week 2026-W38 --format all
```

### Uruchom z Pythona

```python
from scripts.generate_report import generate_report

result = generate_report(
    iso_year=2026,
    iso_week=38,
    formats=['md', 'html', 'xlsx'],
    output_dir=Path('raporty')
)

print(f"Sukces: {result['success']}")
print(f"Pliki: {result['files']}")
```

## Konfiguracja

Wszystkie ustawienia są w `config.py`:

```python
MSSQL_SERVER = "127.0.0.1,14331"
MSSQL_DATABASE = "RetailDW_WorkshopNext"
REPORTS_OUTPUT_DIR = REPO_ROOT / "raporty"
```

Zmień wartości jeśli inny serwer/baza.

## Flow

1. **Wejście** → `--week 2026-W38` (lub pytanie interaktywne)
2. **Walidacja** → czy okres istnieje w DimDate? Czy dane kompletne?
3. **SQL** → `sql_builder.py` tworzy SELECT dla W38, W37, YoY
4. **Egzekucja** → pyodbc na RetailDW
5. **Transformacja** → `formatters.py` wylicza zmiany, przygotowuje context
6. **Rendering** → jinja2 dla MD/HTML, openpyxl dla Excel
7. **Zapis** → `raporty/raport-sprzedazy-2026-W38.{md,html,xlsx}`

## Troubleshooting

### ModuleNotFoundError: No module named 'pyodbc'

Uruchom skrypt z dependencjami:

```bash
python scripts/dependencies.py
```

### RAPORT NIEGOTOWY

Brakuje danych za ostatni dzień. Czekaj na ETL lub wybierz inny tydzień.

### Liczby nie zgadzają się z vw_SalesWeekly

Normalnie — inne poziomy agregacji. Jeśli różnica < 1%, OK.

### HTML nie ma CSS

Tailwind CDN wymaga dostępu do internetu. W systemie offline: edytuj `report.html.jinja2` i dodaj `<style>` zamiast `<script src=...>`.

## Testy

### Test sql_builder

```bash
python scripts/sql_builder.py
```

### Test formatters

```bash
python scripts/formatters.py
```

### Test pełny (end-to-end)

```bash
python scripts/generate_report.py --week 2026-W38 --format md --output /tmp/
```

Sprawdź `/tmp/raport-sprzedazy-2026-W38.md`.

## Dalsze ulepszenia

- [ ] Drill-down: kliknąć kanał → szczegóły po kategoriach
- [ ] MoM trend (porównanie wielomiesięczne)
- [ ] Powiadomienie e-mail
- [ ] Slack integration
- [ ] Scheduled task (co poniedziałek)
- [ ] Cache wyników SQL (jeśli ten sam tydzień pytany wielokrotnie)
- [ ] Error recovery (retry SQL na timeout)

## Kontakt

Pytania o skill: patrz `SKILL.md`.
