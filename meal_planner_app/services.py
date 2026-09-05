"""
Application services, such as PDF generation.
"""

from importlib import resources
from pathlib import Path
from typing import Callable, List, Dict, Union, Optional
import os
import unicodedata
from fpdf import FPDF


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


def _write_pdf_table_row(
    pdf: FPDF,
    name: str,
    quantity_str: str,
    unit: str,
    layout: tuple,
) -> None:
    """Write a single row in the shopping list PDF table (cols+height in layout tuple)."""
    col_width_name, col_width_quantity, col_width_unit, line_height = layout
    pdf.cell(col_width_name, line_height, name, border=1)
    pdf.cell(col_width_quantity, line_height, quantity_str, border=1)
    pdf.cell(col_width_unit, line_height, unit, border=1)
    pdf.ln(line_height)


def _render_shopping_list_items(
    pdf: FPDF,
    data: Union[
        List[Dict[str, Union[str, float, List[str]]]],
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]],
    ],
    pdf_text_fn: Callable,
    set_font: Callable,
    layout: tuple,
) -> None:
    """Render the body (empty msg, grouped headers+rows, or flat rows) of the PDF."""
    if not data:
        pdf.cell(0, 10, pdf_text_fn("This shopping list is empty."), 0, 1)
        return

    if isinstance(data, dict):
        for loc, items in data.items():
            if loc:
                set_font("B", 12)
                pdf.cell(0, 8, pdf_text_fn(f"--- {loc} ---"), 0, 1)
                set_font("", 11)
            for item in items:
                name = pdf_text_fn(item.get("name", "N/A"))
                quantity_str = pdf_text_fn(_format_quantity(item.get("quantity", "")))
                unit = pdf_text_fn(item.get("unit", ""))
                _write_pdf_table_row(pdf, name, quantity_str, unit, layout)
    else:
        for item in data:
            name = pdf_text_fn(item.get("name", "N/A"))
            quantity_str = pdf_text_fn(_format_quantity(item.get("quantity", "")))
            unit = pdf_text_fn(item.get("unit", ""))
            _write_pdf_table_row(pdf, name, quantity_str, unit, layout)


def generate_shopping_list_pdf(
    meal_plan_name: str,
    shopping_list_data: Union[
        List[Dict[str, Union[str, float, List[str]]]],
        Dict[str, List[Dict[str, Union[str, float, List[str]]]]],
    ],
) -> bytes:
    """
    Generates a PDF document for the given shopping list data.
    Supports flat list or grouped dict {location: [items...]} for grouping by lokalizacje.
    Requires DejaVu TTF (bundled or system). Raises FontUnavailableError if missing.
    """
    pdf = FPDF()
    pdf.add_page()
    regular, bold = resolve_dejavu_fonts()
    family = _register_dejavu(pdf, regular, bold)

    def _set_font(style: str, size: int):
        pdf.set_font(family, style, size)

    # KD-9: English chrome heading + stored name as subtitle (no "Shopping List for:").
    _set_font("B", 16)
    pdf.cell(0, 10, pdf_text("Shopping List"), 0, 1, "C")
    _set_font("", 12)
    pdf.cell(0, 8, pdf_text(meal_plan_name), 0, 1, "C")
    pdf.ln(8)

    _set_font("B", 12)
    pdf.cell(pdf.w * 0.5, 10, pdf_text("Ingredient"), border=1)
    pdf.cell(pdf.w * 0.25, 10, pdf_text("Quantity"), border=1)
    pdf.cell(pdf.w * 0.15, 10, pdf_text("Unit"), border=1)
    pdf.ln(10)

    _set_font("", 11)
    layout = (pdf.w * 0.5, pdf.w * 0.25, pdf.w * 0.15, 8)

    _render_shopping_list_items(
        pdf,
        shopping_list_data,
        pdf_text,
        _set_font,
        layout,
    )

    out = pdf.output()
    if isinstance(out, (bytearray, memoryview)):
        out = bytes(out)
    return out
