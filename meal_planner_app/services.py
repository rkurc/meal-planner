"""
Application services, such as PDF generation.
"""

from typing import List, Dict, Union
import unicodedata
from fpdf import FPDF


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

    # Use a Unicode font (DejaVu) so that Polish characters (ę, ą, ś, ć, ż, ź, ł, ó, etc.)
    # from legacy location/ingredient data are supported. Core fonts (Arial/Helvetica)
    # are limited to Latin-1.
    PDF_FONT_FAMILY = "DejaVu"
    using_unicode_font = True
    try:
        pdf.add_font(PDF_FONT_FAMILY, "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        pdf.add_font(PDF_FONT_FAMILY, "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    except Exception:
        # Fallback if the font package is not installed (e.g. local run without rebuild)
        PDF_FONT_FAMILY = "Helvetica"
        using_unicode_font = False

    def _set_font(style: str, size: int):
        pdf.set_font(PDF_FONT_FAMILY, style, size)

    def _cell_text(text: str) -> str:
        if using_unicode_font:
            return text
        # Fallback: strip diacritics / non-Latin1 chars
        normalized = unicodedata.normalize("NFKD", text)
        return normalized.encode("latin-1", "ignore").decode("latin-1")

    # Title
    _set_font("B", 16)
    pdf.cell(0, 10, _cell_text(f"Shopping List for: {meal_plan_name}"), 0, 1, "C")
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
                    pdf.cell(0, 8, _cell_text(f"--- {loc} ---"), 0, 1)
                    _set_font("", 11)
                for item in items:
                    name = _cell_text(item.get("name", "N/A"))
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
                name = _cell_text(item.get("name", "N/A"))
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
    return pdf.output()
