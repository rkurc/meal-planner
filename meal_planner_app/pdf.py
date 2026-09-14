"""
PDF generation for shopping lists.
"""

from importlib import resources
from pathlib import Path
from typing import Callable, List, Dict, Union, Optional
import os
import unicodedata
from fpdf import FPDF

from meal_planner_app.i18n.pdf_strings import pdf_chrome

_SYSTEM_DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_SYSTEM_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class FontUnavailableError(RuntimeError):
    """Raised when neither bundled nor system DejaVu TTF files are present."""


def pdf_text(text: Optional[str]) -> str:
    """NFC-normalize user text for PDF drawing. Never latin-1-strips."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", str(text))


def _bundled_font_path(filename: str) -> Optional[str]:
    try:
        candidate = resources.files("meal_planner_app") / "static" / "fonts" / filename
        if candidate.is_file():
            return str(candidate)
    except (FileNotFoundError, ModuleNotFoundError, AttributeError, TypeError):
        pass
    fallback = Path(__file__).resolve().parent / "static" / "fonts" / filename
    if fallback.is_file():
        return str(fallback)
    return None


def resolve_dejavu_fonts() -> tuple:
    """Return (regular, bold) TTF paths. Bundled first, then system; else raise."""
    regular = _bundled_font_path("DejaVuSans.ttf")
    bold = _bundled_font_path("DejaVuSans-Bold.ttf")
    if not (regular and os.path.isfile(regular)):
        if os.path.isfile(_SYSTEM_DEJAVU_REGULAR):
            regular = _SYSTEM_DEJAVU_REGULAR
        else:
            regular = None
    if not (bold and os.path.isfile(bold)):
        if os.path.isfile(_SYSTEM_DEJAVU_BOLD):
            bold = _SYSTEM_DEJAVU_BOLD
        else:
            bold = None
    if not regular or not bold:
        raise FontUnavailableError("DejaVu Sans TTF (regular + bold) not found")
    return regular, bold


def _register_dejavu(pdf: FPDF, regular: str, bold: str) -> str:
    pdf.add_font("DejaVu", "", regular)
    pdf.add_font("DejaVu", "B", bold)
    return "DejaVu"


def _format_quantity(quantity_val: Union[str, float, List[str], None]) -> str:
    """Format a quantity value (str, float, list, or None) into a display string."""
    if isinstance(quantity_val, list):
        return ", ".join(map(str, quantity_val))
    return str(quantity_val or "")


_COL_GUTTER_MM = 6.0
_NAME_FRAC = 0.52
_QTY_FRAC = 0.18
_UNIT_FRAC = 0.30


def _two_column_layout(pdf: FPDF, line_height: float) -> tuple:
    """Widths for one page-column (name|qty|unit) plus the right column's x origin."""
    mid = pdf.w / 2
    col_w = mid - pdf.l_margin - _COL_GUTTER_MM / 2
    right_x = mid + _COL_GUTTER_MM / 2
    return (
        col_w * _NAME_FRAC,
        col_w * _QTY_FRAC,
        col_w * _UNIT_FRAC,
        line_height,
        right_x,
    )


def _item_cell_triple(item: dict, pdf_text_fn: Callable, na_copy: str) -> tuple:
    """Return (name, quantity, unit) strings for one shopping-list item."""
    name = pdf_text_fn(item.get("name", na_copy))
    quantity_str = pdf_text_fn(_format_quantity(item.get("quantity", "")))
    unit = pdf_text_fn(item.get("unit", ""))
    return name, quantity_str, unit


def _write_pdf_table_row(
    pdf: FPDF,
    name: str,
    quantity_str: str,
    unit: str,
    layout: tuple,
) -> None:
    """Write one item's name|qty|unit cells without advancing to the next line."""
    col_width_name, col_width_quantity, col_width_unit, line_height = layout[:4]
    pdf.cell(col_width_name, line_height, name, border=1)
    pdf.cell(col_width_quantity, line_height, quantity_str, border=1)
    pdf.cell(col_width_unit, line_height, unit, border=1)


def _write_pdf_pair_row(
    pdf: FPDF,
    left: tuple,
    right: Optional[tuple],
    layout: tuple,
) -> None:
    """Write two side-by-side items (or a left item alone), then advance one line."""
    _write_pdf_table_row(pdf, *left, layout)
    if right is not None:
        pdf.set_x(layout[4])
        _write_pdf_table_row(pdf, *right, layout)
    pdf.ln(layout[3])


def _item_groups(
    data: Union[
        List[Dict[str, Union[str, float, List[str]]]],
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]],
    ],
) -> List[List[Dict[str, Union[str, float, List[str]]]]]:
    """Normalize grouped dict or flat list into non-empty location groups (order kept)."""
    if isinstance(data, dict):
        return [items for items in data.values() if items]
    return [data] if data else []


def _render_shopping_list_items(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    pdf: FPDF,
    data: Union[
        List[Dict[str, Union[str, float, List[str]]]],
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]],
    ],
    pdf_text_fn: Callable,
    layout: tuple,
    empty_copy: str,
    na_copy: str,
) -> None:
    """Render items two-up; location groups are separated by one empty line."""
    if not data:
        pdf.cell(0, 10, pdf_text_fn(empty_copy), 0, 1)
        return

    groups = _item_groups(data)
    for group_index, items in enumerate(groups):
        if group_index:
            pdf.ln(layout[3])
        for i in range(0, len(items), 2):
            left = _item_cell_triple(items[i], pdf_text_fn, na_copy)
            right = (
                _item_cell_triple(items[i + 1], pdf_text_fn, na_copy)
                if i + 1 < len(items)
                else None
            )
            _write_pdf_pair_row(pdf, left, right, layout)


def generate_shopping_list_pdf(
    meal_plan_name: str,
    shopping_list_data: Union[
        List[Dict[str, Union[str, float, List[str]]]],
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]],
    ],
    lang: str = "en",
) -> bytes:
    """
    Generates a PDF document for the given shopping list data.
    Supports flat list or grouped dict {location: [items...]}.
    Each item is still name|qty|unit; two items sit side by side (page split in half).
    Location groups are separated by one empty line (no location headers).
    Requires DejaVu TTF (bundled or system). Raises FontUnavailableError if missing.
    lang selects PDF chrome (en/pl); stored names are not translated.
    """
    chrome = pdf_chrome(lang)
    pdf = FPDF()
    pdf.add_page()
    regular, bold = resolve_dejavu_fonts()
    family = _register_dejavu(pdf, regular, bold)

    def _set_font(style: str, size: int):
        pdf.set_font(family, style, size)

    _set_font("B", 16)
    pdf.cell(0, 10, pdf_text(chrome["heading"]), 0, 1, "C")
    _set_font("", 12)
    pdf.cell(0, 8, pdf_text(meal_plan_name), 0, 1, "C")
    pdf.ln(8)

    header_layout = _two_column_layout(pdf, 10)
    item_layout = _two_column_layout(pdf, 8)
    header_cells = (
        pdf_text(chrome["col_ingredient"]),
        pdf_text(chrome["col_quantity"]),
        pdf_text(chrome["col_unit"]),
    )

    _set_font("B", 12)
    _write_pdf_pair_row(pdf, header_cells, header_cells, header_layout)

    _set_font("", 11)
    _render_shopping_list_items(
        pdf,
        shopping_list_data,
        pdf_text,
        item_layout,
        chrome["empty"],
        chrome["na"],
    )

    out = pdf.output()
    if isinstance(out, (bytearray, memoryview)):
        out = bytes(out)
    return out
