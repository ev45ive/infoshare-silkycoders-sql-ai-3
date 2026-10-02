"""
Formatery dla wyjścia: Markdown, HTML, Excel.
Przygotowują context i renderują szablony.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from decimal import Decimal

try:
    from jinja2 import Environment, FileSystemLoader
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    pass  # Zależy zainstalują dependencies.py

logger = logging.getLogger(__name__)


def prepare_context(
    current_data: List[Dict],
    prev_week_data: List[Dict],
    yoy_data: List[Dict],
    iso_year: int,
    iso_week: int,
    is_complete: bool,
    detail_data: List[Dict] = None
) -> Dict[str, Any]:
    """
    Przygotowuje słownik context dla szablonów jinja2.
    Wylicza zmiany WoW/YoY, przygotowuje interpretację.
    """
    
    # Konwersja do słowników po kanałach
    current_by_channel = {row['Channel']: row for row in current_data}
    prev_by_channel = {row['Channel']: row for row in prev_week_data}
    yoy_by_channel = {row['Channel']: row for row in yoy_data}
    
    # Przygotowanie metryka po kanałach
    channels = ['ONLINE', 'STORE', 'RAZEM']
    metrics = {}
    changes = {}
    
    # RAZEM — obliczamy ręcznie
    for channel in ['ONLINE', 'STORE']:
        if channel not in current_by_channel:
            current_by_channel[channel] = {'Channel': channel, 'NetAmount': 0, 'Quantity': 0, 'Transactions': 0}
        if channel not in prev_by_channel:
            prev_by_channel[channel] = {'Channel': channel, 'NetAmount': 0, 'Quantity': 0, 'Transactions': 0}
        if channel not in yoy_by_channel:
            yoy_by_channel[channel] = {'Channel': channel, 'NetAmount': 0, 'Quantity': 0, 'Transactions': 0}
    
    current_by_channel['RAZEM'] = {
        'Channel': 'RAZEM',
        'NetAmount': sum(current_by_channel[c].get('NetAmount', 0) for c in ['ONLINE', 'STORE']),
        'Quantity': sum(current_by_channel[c].get('Quantity', 0) for c in ['ONLINE', 'STORE']),
        'Transactions': sum(current_by_channel[c].get('Transactions', 0) for c in ['ONLINE', 'STORE']),
    }
    prev_by_channel['RAZEM'] = {
        'Channel': 'RAZEM',
        'NetAmount': sum(prev_by_channel[c].get('NetAmount', 0) for c in ['ONLINE', 'STORE']),
        'Quantity': sum(prev_by_channel[c].get('Quantity', 0) for c in ['ONLINE', 'STORE']),
        'Transactions': sum(prev_by_channel[c].get('Transactions', 0) for c in ['ONLINE', 'STORE']),
    }
    yoy_by_channel['RAZEM'] = {
        'Channel': 'RAZEM',
        'NetAmount': sum(yoy_by_channel[c].get('NetAmount', 0) for c in ['ONLINE', 'STORE']),
        'Quantity': sum(yoy_by_channel[c].get('Quantity', 0) for c in ['ONLINE', 'STORE']),
        'Transactions': sum(yoy_by_channel[c].get('Transactions', 0) for c in ['ONLINE', 'STORE']),
    }
    
    # Wyliczanie zmian
    for channel in channels:
        curr = current_by_channel.get(channel, {})
        prev = prev_by_channel.get(channel, {})
        yoy = yoy_by_channel.get(channel, {})
        
        curr_net = float(curr.get('NetAmount', 0) or 0)
        prev_net = float(prev.get('NetAmount', 0) or 0)
        yoy_net = float(yoy.get('NetAmount', 0) or 0)
        
        wow_pct = ((curr_net - prev_net) / prev_net * 100) if prev_net > 0 else 0
        yoy_pct = ((curr_net - yoy_net) / yoy_net * 100) if yoy_net > 0 else 0
        
        metrics[channel] = {
            'NetAmount': round(curr_net, 2),
            'Quantity': int(curr.get('Quantity', 0) or 0),
            'Transactions': int(curr.get('Transactions', 0) or 0),
            'PrevWeekNet': round(prev_net, 2),
            'YoYNet': round(yoy_net, 2),
        }
        
        changes[channel] = {
            'WoW_pct': round(wow_pct, 2),
            'WoW_pln': round(curr_net - prev_net, 2),
            'YoY_pct': round(yoy_pct, 2),
            'YoY_pln': round(curr_net - yoy_net, 2),
            'IsSignificant': abs(yoy_pct) > 15,  # próg 15%
        }
    
    # Wstępna interpretacja
    interpretation = []
    if changes['RAZEM']['YoY_pct'] > 15:
        interpretation.append(f"📈 Wzrost YoY +{changes['RAZEM']['YoY_pct']:.1f}% — wzrost w kanale ONLINE")
    elif changes['RAZEM']['YoY_pct'] < -15:
        interpretation.append(f"📉 Spadek YoY {changes['RAZEM']['YoY_pct']:.1f}%")
    
    if changes['RAZEM']['WoW_pct'] < -10:
        interpretation.append(f"⚠️  Spadek WoW {changes['RAZEM']['WoW_pct']:.1f}% — sprawdzić STORE")
    
    if changes['ONLINE']['YoY_pct'] > 20:
        interpretation.append(f"🔥 ONLINE rosnę szybciej (+{changes['ONLINE']['YoY_pct']:.1f}% YoY) — monitorować trend")
    
    if not is_complete:
        interpretation.insert(0, "⚠️  RAPORT NIEKOMPLETNY — brakuje danych")
    
    # Źródło danych
    data_source = [
        f"Tabela: FactSales, DimDate, DimStore, DimProduct",
        f"Tydzień: 2026-W38 (14–20.09.2026)",
        f"Porównanie WoW: W38 vs W37",
        f"Porównanie YoY: daty 14–20.09 w obu latach",
        f"Metryki: Sprzedaż netto, sztuki, transakcje",
    ]
    
    context = {
        'period': f"2026-W{iso_week} (2026)",
        'iso_year': iso_year,
        'iso_week': iso_week,
        'status': 'ready' if is_complete else 'incomplete',
        'metrics': metrics,
        'changes': changes,
        'interpretation': interpretation,
        'data_source': data_source,
        'generated_at': datetime.now().isoformat(),
    }
    
    return context


def render_markdown(context: Dict[str, Any], template_path: Path) -> str:
    """Renderuje raport w Markdown."""
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    return template.render(context)


def render_html(context: Dict[str, Any], template_path: Path) -> str:
    """Renderuje raport w HTML (print-friendly, Tailwind CDN)."""
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    return template.render(context)


def render_excel(
    context: Dict[str, Any],
    config_path: Path,
    output_path: Path
) -> None:
    """Renderuje raport w Excel (3 arkusze: Podsumowanie, Szczegóły, Trends)."""
    
    with open(config_path) as f:
        excel_config = json.load(f)
    
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Usuń domyślny arkusz
    
    # === Arkusz 1: Podsumowanie ===
    ws = wb.create_sheet("Podsumowanie", 0)
    
    ws['A1'] = f"Raport sprzedaży — {context['period']}"
    ws['A1'].font = Font(size=14, bold=True)
    
    row = 3
    ws[f'A{row}'] = 'Kanał'
    ws[f'B{row}'] = 'Sprzedaż netto (PLN)'
    ws[f'C{row}'] = 'Sztuki'
    ws[f'D{row}'] = 'Transakcje'
    ws[f'E{row}'] = 'WoW %'
    ws[f'F{row}'] = 'YoY %'
    
    # Formatowanie nagłówka
    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
        cell = ws[f'{col}{row}']
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    row = 4
    for channel in ['ONLINE', 'STORE', 'RAZEM']:
        metrics = context['metrics'].get(channel, {})
        changes = context['changes'].get(channel, {})
        
        ws[f'A{row}'] = channel
        ws[f'B{row}'] = metrics.get('NetAmount', 0)
        ws[f'C{row}'] = metrics.get('Quantity', 0)
        ws[f'D{row}'] = metrics.get('Transactions', 0)
        ws[f'E{row}'] = changes.get('WoW_pct', 0)
        ws[f'F{row}'] = changes.get('YoY_pct', 0)
        
        # Formatowanie liczb
        ws[f'B{row}'].number_format = '#,##0.00'
        ws[f'E{row}'].number_format = '0.00"%"'
        ws[f'F{row}'].number_format = '0.00"%"'
        
        if channel == 'RAZEM':
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                ws[f'{col}{row}'].font = Font(bold=True)
        
        row += 1
    
    # Auto-width
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 12
    
    # === Arkusz 2: Szczegóły ===
    ws = wb.create_sheet("Szczegóły", 1)
    ws['A1'] = "Szczegóły (zarezerwowano na future drill-down)"
    ws['A1'].font = Font(italic=True)
    
    # === Arkusz 3: Trends ===
    ws = wb.create_sheet("Trends", 2)
    ws['A1'] = "Trendy (zarezerwowano)"
    ws['A1'].font = Font(italic=True)
    
    wb.save(output_path)
    logger.info(f"✅ Excel zapisany: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Test
    test_context = prepare_context(
        current_data=[
            {'Channel': 'ONLINE', 'NetAmount': 148893.07, 'Quantity': 1012, 'Transactions': 239},
            {'Channel': 'STORE', 'NetAmount': 515858.96, 'Quantity': 3575, 'Transactions': 843},
        ],
        prev_week_data=[
            {'Channel': 'ONLINE', 'NetAmount': 138798.79, 'Quantity': 958, 'Transactions': 230},
            {'Channel': 'STORE', 'NetAmount': 552916.42, 'Quantity': 3704, 'Transactions': 872},
        ],
        yoy_data=[
            {'Channel': 'ONLINE', 'NetAmount': 122039.27, 'Quantity': 872, 'Transactions': 206},
            {'Channel': 'STORE', 'NetAmount': 503141.20, 'Quantity': 3327, 'Transactions': 781},
        ],
        iso_year=2026,
        iso_week=38,
        is_complete=True,
    )
    
    print(json.dumps(test_context, indent=2, default=str))
