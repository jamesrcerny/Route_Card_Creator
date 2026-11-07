"""Builds a printable Excel sheet of route cards (one per team member) using openpyxl.

Each card pairs a Primary Route table with an Alternate Route table, built from
kml_actions.build_route(). Card height adapts to however many checkpoints the
route has. Cards are tiled across the sheet, print area is set to landscape and
scaled to fit the page width, so the sheet can be printed straight from Excel.
"""
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

import kml_actions

DARK_GREEN = "1F5C1F"
HEADER_FONT = Font(color="FFFFFF", bold=True, size=9)
DATA_FONT = Font(size=9)
NAME_FONT = Font(size=9, italic=True)
THIN = Side(style="thin", color="000000")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center")

# (row dict key, column header, column width)
COLUMNS = [
    ("checkpoint", "Check points", 12),
    ("grid", "Grid", 16),
    ("flow", "Flow", 8),
    ("distance", "Distance (m)", 12),
    ("direction", "Direction (Mag)", 13),
]

CARDS_PER_ROW = 3
CARD_COL_GAP = 1
CARD_ROW_GAP = 1


def _style_cell(ws, row, col, value, fill=None, font=DATA_FONT, alignment=CENTER):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = font
    cell.alignment = alignment
    cell.border = BORDER
    if fill:
        cell.fill = PatternFill("solid", fgColor=fill)
    return cell


def _write_section(ws, row, col, title, rows, row_count):
    n_cols = len(COLUMNS)

    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + n_cols - 1)
    _style_cell(ws, row, col, title, fill=DARK_GREEN, font=HEADER_FONT)
    for c in range(col + 1, col + n_cols):
        _style_cell(ws, row, c, None, fill=DARK_GREEN, font=HEADER_FONT)

    header_row = row + 1
    for i, (_, label, width) in enumerate(COLUMNS):
        c = col + i
        _style_cell(ws, header_row, c, label, fill=DARK_GREEN, font=HEADER_FONT)
        ws.column_dimensions[get_column_letter(c)].width = width

    for r in range(row_count):
        data_row = header_row + 1 + r
        record = rows[r] if r < len(rows) else None
        for i, (key, _, _width) in enumerate(COLUMNS):
            c = col + i
            _style_cell(ws, data_row, c, record[key] if record else None)


def _write_card(ws, row, col, member_label, primary_rows, alt_rows, row_count):
    section_cols = len(COLUMNS)
    card_cols = section_cols * 2

    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + card_cols - 1)
    _style_cell(ws, row, col, f"{member_label}   Name: ___________________",
                font=NAME_FONT, alignment=LEFT)

    table_row = row + 1
    _write_section(ws, table_row, col, "PRIMARY ROUTE", primary_rows, row_count)
    _write_section(ws, table_row, col + section_cols, "ALTERNATE ROUTE", alt_rows, row_count)


def generate_route_cards_xlsx(primary_kml_path, alternate_kml_path, team_size, output_dir=None):
    """Builds RouteCards.xlsx with one card per team member. Returns the output path."""
    if team_size < 1:
        raise ValueError("Team size must be at least 1.")

    primary_rows = kml_actions.build_route(primary_kml_path)
    alt_rows = kml_actions.build_route(alternate_kml_path)
    row_count = max(len(primary_rows), len(alt_rows))

    section_cols = len(COLUMNS)
    card_cols = section_cols * 2
    card_rows = 1 + 2 + row_count  # name line + title row + header row + data rows

    wb = Workbook()
    ws = wb.active
    ws.title = "Route Cards"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.3, right=0.3, top=0.3, bottom=0.3)

    last_row = 0
    last_col = 0
    for i in range(team_size):
        card_row_idx, card_col_idx = divmod(i, CARDS_PER_ROW)
        row = 1 + card_row_idx * (card_rows + CARD_ROW_GAP)
        col = 1 + card_col_idx * (card_cols + CARD_COL_GAP)
        _write_card(ws, row, col, f"#{i + 1}", primary_rows, alt_rows, row_count)
        last_row = max(last_row, row + card_rows - 1)
        last_col = max(last_col, col + card_cols - 1)

    ws.print_area = f"A1:{get_column_letter(last_col)}{last_row}"

    out_dir = output_dir or os.path.dirname(primary_kml_path)
    output_path = os.path.join(out_dir, "RouteCards.xlsx")
    wb.save(output_path)
    return output_path
