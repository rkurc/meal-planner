"""English/Polish chrome strings for shopping-list PDFs (i18n PR-5)."""

PDF_STRINGS = {
    "en": {
        "heading": "Shopping List",
        "col_ingredient": "Ingredient",
        "col_quantity": "Quantity",
        "col_unit": "Unit",
        "empty": "This shopping list is empty.",
        "na": "N/A",
    },
    "pl": {
        "heading": "Lista zakupów",
        "col_ingredient": "Składnik",
        "col_quantity": "Ilość",
        "col_unit": "Jednostka",
        "empty": "Ta lista zakupów jest pusta.",
        "na": "b.d.",
    },
}


def pdf_chrome(lang: str) -> dict:
    """Return chrome dict for a whitelisted language (default English)."""
    key = (lang or "en").split("-")[0].lower()
    return PDF_STRINGS.get(key, PDF_STRINGS["en"])
