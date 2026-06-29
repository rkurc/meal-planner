"""
Application services, such as PDF generation.
"""

from typing import List, Dict, Union, Optional
import os
import unicodedata
from fpdf import FPDF


def sanitize_for_pdf(text: Optional[str]) -> str:
    """Data-side sanitization for text used in PDF output.

    This is the preferred defensive layer when we cannot (or should not)
    assume a full Unicode font is available in the environment.

    - Always performs NFKD normalization.
    - Strips characters that cannot be represented in latin-1 (the fallback
      for core fonts like Helvetica).

    For full i18n support (future goal), the meal-planner environment
    (Docker image or local dev setup) is expected to provide appropriate
    Unicode-capable fonts (e.g. via fonts-dejavu-core or equivalent) and
    font discovery so that sanitization can be reduced to a no-op for most
    European scripts.

    We deliberately do *not* bundle fonts. Font availability is an
    environment concern.
    """
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", str(text))
    # Defensive strip for latin-1 / core font compatibility
    return normalized.encode("latin-1", errors="ignore").decode("latin-1")


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
    pdf_text: callable,
    set_font: callable,
    layout: tuple,
) -> None:
    """Render the body (empty msg, grouped headers+rows, or flat rows) of the PDF."""
    if not data:
        pdf.cell(0, 10, "This shopping list is empty.", 0, 1)
        return

    if isinstance(data, dict):
        for loc, items in data.items():
            if loc:
                set_font("B", 12)
                pdf.cell(0, 8, pdf_text(f"--- {loc} ---"), 0, 1)
                set_font("", 11)
            for item in items:
                name = pdf_text(item.get("name", "N/A"))
                quantity_str = _format_quantity(item.get("quantity", ""))
                unit = item.get("unit", "")
                _write_pdf_table_row(pdf, name, quantity_str, unit, layout)
    else:
        for item in data:
            name = pdf_text(item.get("name", "N/A"))
            quantity_str = _format_quantity(item.get("quantity", ""))
            unit = item.get("unit", "")
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
    """
    pdf = FPDF()
    pdf.add_page()

    # Rely on environment (Docker or local dev setup) to provide Unicode fonts
    # (e.g. fonts-dejavu-core or equivalent system font with proper discovery).
    # We do *not* bundle fonts.
    # Use existence check (no try/except) to avoid broad-exception and reduce branches.
    pdf_font_family = "DejaVu"
    dejavu = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    dejavu_b = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if os.path.isfile(dejavu) and os.path.isfile(dejavu_b):
        pdf.add_font(pdf_font_family, "", dejavu)
        pdf.add_font(pdf_font_family, "B", dejavu_b)
        has_unicode_font = True
    else:
        pdf_font_family = "Helvetica"
        has_unicode_font = False

    def _set_font(style: str, size: int):
        pdf.set_font(pdf_font_family, style, size)

    # _pdf_text applies sanitization ONLY for core-font fallback (when no unicode font).
    # When DejaVu etc present, pass (normalized) full text so diacritics like 'ę' render.
    def _pdf_text(text: Optional[str]) -> str:
        if not text:
            return ""
        if has_unicode_font:
            return unicodedata.normalize("NFKD", str(text))
        return sanitize_for_pdf(text)

    # Title
    _set_font("B", 16)
    pdf.cell(0, 10, _pdf_text(f"Shopping List for: {meal_plan_name}"), 0, 1, "C")
    pdf.ln(10)

    # Table Header (inline sizes to minimize local var count for pylint)
    _set_font("B", 12)
    pdf.cell(pdf.w * 0.5, 10, "Ingredient", border=1)
    pdf.cell(pdf.w * 0.25, 10, "Quantity", border=1)
    pdf.cell(pdf.w * 0.15, 10, "Unit", border=1)
    pdf.ln(10)

    # Table Body
    _set_font("", 11)
    layout = (pdf.w * 0.5, pdf.w * 0.25, pdf.w * 0.15, 8)

    _render_shopping_list_items(
        pdf,
        shopping_list_data,
        _pdf_text,
        _set_font,
        layout,
    )

    # FPDF.output returns bytes by default since v2.7.7 for 'S' and 'F'
    # Explicitly ensure bytes (not bytearray) for WSGI/Flask/gunicorn compatibility.
    out = pdf.output()
    if isinstance(out, (bytearray, memoryview)):
        out = bytes(out)
    return out
