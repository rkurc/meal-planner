"""
Application services, such as PDF generation.
"""

from typing import List, Dict, Union, Optional
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


def generate_shopping_list_pdf(  # pylint: disable=too-many-locals,too-many-statements
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
    pdf_font_family = "DejaVu"
    try:
        pdf.add_font(
            pdf_font_family, "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        pdf.add_font(
            pdf_font_family, "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        )
        has_unicode_font = True
    except Exception:  # pylint: disable=broad-exception-caught
        # Environment does not have the expected Unicode font.
        # Fall back to core font + data-side sanitization.
        pdf_font_family = "Helvetica"
        has_unicode_font = False

    def _set_font(style: str, size: int):
        pdf.set_font(pdf_font_family, style, size)

    # Apply data-side sanitization for PDF safety.
    # This is defensive for the case where the env does not provide a
    # suitable Unicode font. Sanitization is applied to all text that will
    # be rendered in the PDF (locations and ingredient names).
    def _pdf_text(text: Optional[str]) -> str:
        safe = sanitize_for_pdf(text)
        if has_unicode_font:
            return safe  # keep as much as possible
        return safe  # already sanitized for core font

    # Title
    _set_font("B", 16)
    pdf.cell(0, 10, _pdf_text(f"Shopping List for: {meal_plan_name}"), 0, 1, "C")
    pdf.ln(10)

    # Table Header
    _set_font("B", 12)
    header_height = 10
    col_width_name = pdf.w * 0.5  # 50% of page width
    col_width_quantity = pdf.w * 0.25  # 25%
    col_width_unit = pdf.w * 0.15  # 15% (remaining, approx)

    pdf.cell(col_width_name, header_height, "Ingredient", border=1)
    pdf.cell(col_width_quantity, header_height, "Quantity", border=1)
    pdf.cell(col_width_unit, header_height, "Unit", border=1)
    pdf.ln(header_height)

    # Table Body
    _set_font("", 11)
    line_height = 8

    if not shopping_list_data:
        pdf.cell(0, 10, "This shopping list is empty.", 0, 1)
    else:
        # Support grouped by location
        if isinstance(shopping_list_data, dict):
            for loc, items in shopping_list_data.items():
                if loc:
                    _set_font("B", 12)
                    pdf.cell(0, 8, _pdf_text(f"--- {loc} ---"), 0, 1)
                    _set_font("", 11)
                for item in items:
                    name = _pdf_text(item.get("name", "N/A"))
                    quantity_val = item.get("quantity", "")
                    unit = item.get("unit", "")
                    if isinstance(quantity_val, list):
                        quantity_str = ", ".join(map(str, quantity_val))
                    else:
                        quantity_str = str(quantity_val)
                    pdf.cell(col_width_name, line_height, name, border=1)
                    pdf.cell(col_width_quantity, line_height, quantity_str, border=1)
                    pdf.cell(col_width_unit, line_height, unit, border=1)
                    pdf.ln(line_height)
        else:
            for item in shopping_list_data:
                name = _pdf_text(item.get("name", "N/A"))
                quantity_val = item.get("quantity", "")
                unit = item.get("unit", "")

                if isinstance(quantity_val, list):
                    quantity_str = ", ".join(map(str, quantity_val))
                else:
                    quantity_str = str(quantity_val)

                # Handle multi-line for long ingredient names or quantities if necessary
                # For simplicity, we'll use fixed height cells for now.
                # If text is too long, it will overflow. A more robust solution would
                # calculate text width and adjust cell height or font.

                pdf.cell(col_width_name, line_height, name, border=1)
                pdf.cell(col_width_quantity, line_height, quantity_str, border=1)
                pdf.cell(col_width_unit, line_height, unit, border=1)
                pdf.ln(line_height)

    # FPDF.output returns bytes by default since v2.7.7 for 'S' and 'F'
    # For older versions, .encode('latin-1') might be needed if it returns string for 'S'
    # Explicitly ensure bytes (not bytearray) for WSGI/Flask/gunicorn compatibility.
    # Some fpdf2 builds (especially with embedded Unicode fonts like DejaVu + ToUnicode)
    # can return bytearray depending on internal buffer.
    out = pdf.output()
    if isinstance(out, (bytearray, memoryview)):
        out = bytes(out)
    return out
