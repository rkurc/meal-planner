"""
Application services, such as PDF generation.
"""
from fpdf import FPDF
from typing import List, Dict, Union

def generate_shopping_list_pdf(meal_plan_name: str, shopping_list_data: List[Dict[str, Union[str, float, List[str]]]]) -> bytes:
    """
    Generates a PDF document for the given shopping list data.
    """
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Shopping List for: {meal_plan_name}", 0, 1, "C")
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", 12)
    header_height = 10
    col_width_name = pdf.w * 0.5  # 50% of page width
    col_width_quantity = pdf.w * 0.25 # 25%
    col_width_unit = pdf.w * 0.15 # 15% (remaining, approx)

    pdf.cell(col_width_name, header_height, "Ingredient", border=1)
    pdf.cell(col_width_quantity, header_height, "Quantity", border=1)
    pdf.cell(col_width_unit, header_height, "Unit", border=1)
    pdf.ln(header_height)

    # Table Body
    pdf.set_font("Arial", "", 11)
    line_height = 8

    if not shopping_list_data:
        pdf.cell(0, 10, "This shopping list is empty.", 0, 1)
    else:
        for item in shopping_list_data:
            name = item.get('name', 'N/A')
            quantity_val = item.get('quantity', '')
            unit = item.get('unit', '')

            if isinstance(quantity_val, list):
                quantity_str = ", ".join(map(str, quantity_val))
            else:
                quantity_str = str(quantity_val)

            # Handle multi-line for long ingredient names or quantities if necessary
            # For simplicity, we'll use fixed height cells for now.
            # If text is too long, it will overflow. A more robust solution would calculate text width and adjust cell height or font.

            pdf.cell(col_width_name, line_height, name, border=1)
            pdf.cell(col_width_quantity, line_height, quantity_str, border=1)
            pdf.cell(col_width_unit, line_height, unit, border=1)
            pdf.ln(line_height)

    # FPDF.output returns bytes by default since v2.7.7 for 'S' and 'F'
    # For older versions, .encode('latin-1') might be needed if it returns string for 'S'
    return pdf.output()
