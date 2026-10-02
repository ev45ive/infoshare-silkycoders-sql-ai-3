"""
Konfiguracja skilla raport-sprzedazy-poniedzialkowy.
Hardcoded ustawienia serwera, bazy, ścieżek.
"""

import os
from pathlib import Path

# === MSSQL Connection ===
MSSQL_SERVER = "127.0.0.1,14331"
MSSQL_DATABASE = "RetailDW_WorkshopNext"
MSSQL_DRIVER = "{ODBC Driver 17 for SQL Server}"
MSSQL_UID = "sa"
MSSQL_PWD = "Wk_Aa1!1AA15EE5C3429BC6100E6F04E53190FB35C7F4517649DDD7"

# === Ścieżki ===
SKILL_DIR = Path(__file__).parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
TEMPLATES_DIR = SKILL_DIR / "templates"
REPO_ROOT = SKILL_DIR.parent.parent.parent  # .github/skills/... -> root

# Output dla raportów
REPORTS_OUTPUT_DIR = REPO_ROOT / "raporty"
REPORTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === Słownik metryk ===
METRICS_DOC = REPO_ROOT / "docs" / "slownik-metryk.md"

# === Format nazw plików ===
REPORT_FILENAME_TEMPLATE = "raport-sprzedazy-{week}.{ext}"  # week = 2026-W38

# === Formaty danych ===
DATE_FORMAT = "%Y-%m-%d"
WEEK_FORMAT = "%Y-W%W"  # ISO format: 2026-W38 (note: %W is 0-based, manual handling needed)

# === Próg istotności ===
CHANGE_THRESHOLD = 15.0  # % — zmiana > tego wynagradzuje uwagę w raporcie

# === Logowanie ===
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
VERBOSE = False

# === Szablony ===
MARKDOWN_TEMPLATE = TEMPLATES_DIR / "report.md.jinja2"
HTML_TEMPLATE = TEMPLATES_DIR / "report.html.jinja2"
EXCEL_CONFIG = TEMPLATES_DIR / "excel_structure.json"

# === Dependencje Python ===
REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "jinja2": "jinja2",
    "openpyxl": "openpyxl",
    "pyodbc": "pyodbc",
}

VENV_DIR = SKILL_DIR / "venv"  # Wirtualne środowisko (jeśli potrzebne)
