#!/usr/bin/env python3
"""
Główny script do generowania raportów sprzedaży.
Entry point dla skilla.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Dodaj parent dir do path (aby mogły importować z config, itp)
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

# Importy z skilla
from config import MSSQL_SERVER, MSSQL_DATABASE, MSSQL_DRIVER, REPORTS_OUTPUT_DIR, MARKDOWN_TEMPLATE, HTML_TEMPLATE, EXCEL_CONFIG
from scripts.dependencies import check_and_install_dependencies
from scripts.validators import parse_week_input, validate_period_in_dimdate, validate_data_coverage
from scripts.sql_builder import build_all_queries, execute_queries
from scripts.formatters import prepare_context, render_markdown, render_html, render_excel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def build_connection_string() -> str:
    """Buduje connection string do MSSQL."""
    from config import MSSQL_UID, MSSQL_PWD
    return f"Driver={MSSQL_DRIVER};Server={MSSQL_SERVER};Database={MSSQL_DATABASE};UID={MSSQL_UID};PWD={MSSQL_PWD};"


def generate_report(
    iso_year: int,
    iso_week: int,
    formats: list = None,
    output_dir: Optional[Path] = None
) -> dict:
    """
    Główna funkcja generowania raportu.
    
    Args:
        iso_year: Rok ISO (np. 2026)
        iso_week: Numer tygodnia ISO (np. 38)
        formats: Lista formatów ['md', 'html', 'xlsx'] (domyślnie wszystkie)
        output_dir: Katalog wyjściowy (domyślnie raporty/)
    
    Returns:
        Dict z ścieżkami i statusem wygenerowanych plików
    """
    
    if formats is None:
        formats = ['md', 'html', 'xlsx']
    
    if output_dir is None:
        output_dir = REPORTS_OUTPUT_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result = {
        'success': False,
        'period': f'{iso_year}-W{iso_week}',
        'files': {},
        'errors': [],
    }
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Generowanie raportu: {iso_year}-W{iso_week}")
        logger.info(f"Formaty: {', '.join(formats)}")
        logger.info(f"{'='*60}\n")
        
        # === Krok 1: Check dependencies ===
        logger.info("🔧 Sprawdzanie dependencji...")
        if not check_and_install_dependencies():
            result['errors'].append("Nie udało się zainstalować wymagane biblioteki")
            return result
        
        # === Krok 2: Walidacja okresu ===
        logger.info(f"📅 Walidacja okresu {iso_year}-W{iso_week}...")
        conn_str = build_connection_string()
        
        is_valid, msg = validate_period_in_dimdate(conn_str, iso_year, iso_week)
        logger.info(msg)
        if not is_valid:
            result['errors'].append(msg)
            return result
        
        # === Krok 3: Sprawdzenie pokrycia danych ===
        logger.info("📊 Sprawdzenie pokrycia danych...")
        is_complete, msg = validate_data_coverage(conn_str, iso_year, iso_week)
        logger.info(msg)
        # is_complete może być False, ale raportem robimy z adnotacją
        
        # === Krok 4: Budowanie i egzekucja SQL ===
        logger.info("🔨 Budowanie zapytań SQL...")
        queries = build_all_queries(iso_year, iso_week)
        
        logger.info("⚙️  Egzekucja zapytań...")
        sql_results = execute_queries(conn_str, queries)
        
        # === Krok 5: Przygotowanie context ===
        logger.info("📋 Przygotowanie danych dla szablonów...")
        context = prepare_context(
            current_data=sql_results.get('current', []),
            prev_week_data=sql_results.get('prev_week', []),
            yoy_data=sql_results.get('yoy', []),
            iso_year=iso_year,
            iso_week=iso_week,
            is_complete=is_complete,
            detail_data=sql_results.get('current_detail', []),
        )
        
        # === Krok 6: Rendering ===
        
        # Markdown
        if 'md' in formats:
            logger.info("📄 Rendering Markdown...")
            try:
                md_content = render_markdown(context, MARKDOWN_TEMPLATE)
                md_path = output_dir / f"raport-sprzedazy-{iso_year}-W{iso_week:02d}.md"
                md_path.write_text(md_content, encoding='utf-8')
                result['files']['md'] = str(md_path)
                logger.info(f"✅ Markdown: {md_path}")
            except Exception as e:
                logger.error(f"❌ Błąd Markdown: {e}")
                result['errors'].append(f"Markdown: {e}")
        
        # HTML
        if 'html' in formats:
            logger.info("🌐 Rendering HTML...")
            try:
                html_content = render_html(context, HTML_TEMPLATE)
                html_path = output_dir / f"raport-sprzedazy-{iso_year}-W{iso_week:02d}.html"
                html_path.write_text(html_content, encoding='utf-8')
                result['files']['html'] = str(html_path)
                logger.info(f"✅ HTML: {html_path}")
            except Exception as e:
                logger.error(f"❌ Błąd HTML: {e}")
                result['errors'].append(f"HTML: {e}")
        
        # Excel
        if 'xlsx' in formats:
            logger.info("📊 Rendering Excel...")
            try:
                xlsx_path = output_dir / f"raport-sprzedazy-{iso_year}-W{iso_week:02d}.xlsx"
                render_excel(context, EXCEL_CONFIG, xlsx_path)
                result['files']['xlsx'] = str(xlsx_path)
                logger.info(f"✅ Excel: {xlsx_path}")
            except Exception as e:
                logger.error(f"❌ Błąd Excel: {e}")
                result['errors'].append(f"Excel: {e}")
        
        # === Podsumowanie ===
        result['success'] = len(result['files']) > 0
        
        logger.info(f"\n{'='*60}")
        if result['success']:
            logger.info("✅ RAPORT GOTOWY")
            logger.info(f"📁 Zapisano {len(result['files'])} pliku(ów) do {output_dir}")
            for fmt, path in result['files'].items():
                logger.info(f"   - {fmt.upper()}: {path}")
        else:
            logger.error("❌ Brak wygenerowanych plików")
        logger.info(f"{'='*60}\n")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Krytyczny błąd: {e}", exc_info=True)
        result['errors'].append(str(e))
        return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generuj raport sprzedaży")
    parser.add_argument('--week', required=True, help='Tydzień ISO (np. 2026-W38)')
    parser.add_argument('--format', choices=['md', 'html', 'xlsx', 'all'], default='all',
                        help='Format wyjścia')
    parser.add_argument('--output', type=Path, default=None,
                        help='Katalog wyjściowy')
    
    args = parser.parse_args()
    
    # Parsuj week
    from scripts.validators import parse_week_input
    iso_year, iso_week = parse_week_input(args.week)
    if not iso_year:
        logger.error(f"Błędny format tygodnia: {args.week}")
        sys.exit(1)
    
    # Konwertuj format
    formats = ['md', 'html', 'xlsx'] if args.format == 'all' else [args.format]
    
    result = generate_report(
        iso_year=iso_year,
        iso_week=iso_week,
        formats=formats,
        output_dir=args.output,
    )
    
    sys.exit(0 if result['success'] else 1)
