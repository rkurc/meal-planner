"""PDF font resolution, NFC text, and FontUnavailableError (i18n PR-1)."""

import importlib.resources
import inspect
import os
import unicodedata
import unittest
from unittest.mock import patch

from fpdf import FPDF

from meal_planner_app import crud, pdf
from meal_planner_app.i18n.pdf_strings import pdf_chrome
from meal_planner_app.main import app


class TestPdfTextNfc(unittest.TestCase):
    """pdf_text emits NFC and never latin-1-strips."""

    def test_pdf_text_composes_combining_ogonek(self):
        decomposed = "e\u0328"
        result = pdf.pdf_text(decomposed)
        self.assertEqual(result, "ę")
        self.assertEqual(result, unicodedata.normalize("NFC", decomposed))

    def test_pdf_text_keeps_precomposed_polish(self):
        polish = "Żurek ąęćłńóśźż"
        self.assertEqual(pdf.pdf_text(polish), polish)

    def test_pdf_text_none_and_empty(self):
        self.assertEqual(pdf.pdf_text(None), "")
        self.assertEqual(pdf.pdf_text(""), "")

    def test_pdf_text_source_has_no_latin1_ignore(self):
        source = inspect.getsource(pdf.pdf_text)
        self.assertNotIn('errors="ignore"', source)
        self.assertNotIn("errors='ignore'", source)
        self.assertNotIn("NFKD", source)


class TestSanitizeRemoved(unittest.TestCase):
    def test_sanitize_for_pdf_deleted(self):
        self.assertFalse(hasattr(pdf, "sanitize_for_pdf"))


class TestBundledFonts(unittest.TestCase):
    def test_bundled_regular_ttf_via_importlib_resources(self):
        path = (
            importlib.resources.files("meal_planner_app")
            / "static"
            / "fonts"
            / "DejaVuSans.ttf"
        )
        self.assertTrue(path.is_file(), "bundled DejaVuSans.ttf missing")

    def test_bundled_bold_ttf_via_importlib_resources(self):
        path = (
            importlib.resources.files("meal_planner_app")
            / "static"
            / "fonts"
            / "DejaVuSans-Bold.ttf"
        )
        self.assertTrue(path.is_file(), "bundled DejaVuSans-Bold.ttf missing")

    def test_license_file_is_not_named_license(self):
        fonts = importlib.resources.files("meal_planner_app") / "static" / "fonts"
        self.assertTrue((fonts / "DejaVu.LICENSE").is_file())
        self.assertFalse((fonts / "LICENSE").is_file())


class TestResolveDejavuFonts(unittest.TestCase):
    def test_resolver_returns_bundled_pair_when_present(self):
        regular, bold = pdf.resolve_dejavu_fonts()
        self.assertTrue(os.path.isfile(regular))
        self.assertTrue(os.path.isfile(bold))
        self.assertTrue(regular.endswith("DejaVuSans.ttf"))
        self.assertTrue(bold.endswith("DejaVuSans-Bold.ttf"))
        bundled = str(
            importlib.resources.files("meal_planner_app") / "static" / "fonts"
        )
        self.assertTrue(
            regular.startswith(bundled) or "static/fonts" in regular.replace("\\", "/")
        )

    def test_resolver_raises_when_no_fonts(self):
        with patch.object(pdf, "_bundled_font_path", return_value=None), patch.object(
            pdf, "_SYSTEM_DEJAVU_REGULAR", "/no/such/DejaVuSans.ttf"
        ), patch.object(pdf, "_SYSTEM_DEJAVU_BOLD", "/no/such/DejaVuSans-Bold.ttf"):
            with self.assertRaises(pdf.FontUnavailableError):
                pdf.resolve_dejavu_fonts()


class TestGenerateShoppingListPdf(unittest.TestCase):
    def test_generate_uses_dejavu_family(self):
        family = []
        real = pdf._register_dejavu  # pylint: disable=protected-access

        def capture(pdf_doc, regular, bold):
            result = real(pdf_doc, regular, bold)
            family.append(result)
            return result

        with patch.object(pdf, "_register_dejavu", side_effect=capture):
            data = pdf.generate_shopping_list_pdf(
                "Żurek",
                {"nabiał": [{"name": "Mąka", "quantity": "500", "unit": "ząbek"}]},
            )
        self.assertEqual(family, ["DejaVu"])
        self.assertTrue(data.startswith(b"%PDF"))

    def test_quantity_and_unit_go_through_pdf_text(self):
        seen = []
        real = pdf.pdf_text

        def spy(text):
            seen.append(text)
            return real(text)

        with patch.object(pdf, "pdf_text", side_effect=spy):
            pdf.generate_shopping_list_pdf(
                "Plan",
                {"": [{"name": "Czosnek", "quantity": "2", "unit": "ząbek"}]},
            )
        joined = " ".join(str(s) for s in seen)
        self.assertIn("Czosnek", joined)
        self.assertIn("2", joined)
        self.assertIn("ząbek", joined)

    def test_empty_list_still_uses_unicode_font(self):
        out = pdf.generate_shopping_list_pdf("Empty", {})
        self.assertTrue(out.startswith(b"%PDF"))


def _capture_pdf_cells(title, data, lang="en"):
    """Generate a PDF and return (page_width, cell records with x/y/text)."""
    records = []
    orig = FPDF.cell
    page_w = []

    def cell(self, *args, **kwargs):
        if not page_w:
            page_w.append(self.w)
        width = args[0] if args else kwargs.get("w")
        if len(args) >= 3:
            txt = args[2]
        else:
            txt = kwargs.get("txt", "")
        records.append(
            {
                "x": self.get_x(),
                "y": self.get_y(),
                "w": width,
                "txt": "" if txt is None else str(txt),
            }
        )
        return orig(self, *args, **kwargs)

    with patch.object(FPDF, "cell", cell):
        pdf.generate_shopping_list_pdf(title, data, lang=lang)
    return page_w[0], records


def _cell_named(records, name):
    return next(r for r in records if r["txt"] == name)


class TestPdfTwoColumnLayout(unittest.TestCase):
    """Each item is still name|qty|unit; items sit two-up, groups split by a blank line."""

    def test_location_is_not_drawn_as_a_header(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {
                "nabiał": [{"name": "Mleko", "quantity": "1", "unit": "l"}],
                "pieczywo": [{"name": "Chleb", "quantity": "1", "unit": "szt"}],
            },
        )
        texts = [r["txt"] for r in records]
        self.assertTrue(any("Mleko" in t for t in texts))
        self.assertTrue(any("Chleb" in t for t in texts))
        self.assertFalse(any("---" in t for t in texts))
        self.assertFalse(any("nabiał" in t for t in texts))
        self.assertFalse(any("pieczywo" in t for t in texts))

    def test_two_items_in_same_group_are_side_by_side(self):
        page_w, records = _capture_pdf_cells(
            "Plan",
            {
                "aisle": [
                    {"name": "Alpha", "quantity": "1", "unit": "g"},
                    {"name": "Beta", "quantity": "2", "unit": "g"},
                ]
            },
        )
        alpha = _cell_named(records, "Alpha")
        beta = _cell_named(records, "Beta")
        mid = page_w / 2
        self.assertAlmostEqual(alpha["y"], beta["y"], delta=0.5)
        self.assertLess(alpha["x"], mid)
        self.assertGreaterEqual(beta["x"], mid - 0.5)

    def test_third_item_wraps_to_next_row_left_column(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {
                "aisle": [
                    {"name": "Alpha", "quantity": "1", "unit": "g"},
                    {"name": "Beta", "quantity": "2", "unit": "g"},
                    {"name": "Gamma", "quantity": "3", "unit": "g"},
                ]
            },
        )
        alpha = _cell_named(records, "Alpha")
        beta = _cell_named(records, "Beta")
        gamma = _cell_named(records, "Gamma")
        self.assertAlmostEqual(alpha["y"], beta["y"], delta=0.5)
        self.assertGreater(gamma["y"], alpha["y"])
        self.assertAlmostEqual(gamma["x"], alpha["x"], delta=0.5)

    def test_location_groups_separated_by_one_empty_line(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {
                "a": [
                    {"name": "Alpha", "quantity": "1", "unit": "g"},
                    {"name": "Beta", "quantity": "2", "unit": "g"},
                ],
                "b": [
                    {"name": "Gamma", "quantity": "3", "unit": "g"},
                    {"name": "Delta", "quantity": "4", "unit": "g"},
                ],
            },
        )
        alpha = _cell_named(records, "Alpha")
        gamma = _cell_named(records, "Gamma")
        item_h = 8
        # one item row plus one blank line between groups
        self.assertAlmostEqual(gamma["y"] - alpha["y"], item_h * 2, delta=0.5)

    def test_headers_appear_in_both_columns(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {"aisle": [{"name": "Alpha", "quantity": "1", "unit": "g"}]},
        )
        ingredients = [r for r in records if r["txt"] == "Ingredient"]
        self.assertEqual(len(ingredients), 2)
        self.assertAlmostEqual(ingredients[0]["y"], ingredients[1]["y"], delta=0.5)
        self.assertLess(ingredients[0]["x"], ingredients[1]["x"])

    def test_left_and_right_cells_do_not_overlap(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {
                "aisle": [
                    {"name": "Alpha", "quantity": "1", "unit": "g"},
                    {"name": "Beta", "quantity": "2", "unit": "g"},
                ]
            },
        )
        idx = next(i for i, rec in enumerate(records) if rec["txt"] == "Alpha")
        left_unit = records[idx + 2]
        beta = _cell_named(records, "Beta")
        self.assertLessEqual(left_unit["x"] + left_unit["w"], beta["x"])

    def test_unit_header_cell_fits_jednostka(self):
        _, records = _capture_pdf_cells(
            "Plan",
            {"aisle": [{"name": "Alpha", "quantity": "1", "unit": "g"}]},
            lang="pl",
        )
        unit_headers = [r for r in records if r["txt"] == "Jednostka"]
        self.assertEqual(len(unit_headers), 2)
        for rec in unit_headers:
            self.assertGreaterEqual(rec["w"], 24)


class TestPdfHttpFontMiss(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        crud.reset_shopping_lists_db()

    def test_pdf_route_returns_500_when_font_missing(self):
        recipe = crud.create_recipe(
            name="R",
            instructions="i",
            ingredients_data=[{"name": "X", "quantity": 1, "unit": "g"}],
        )
        plan = crud.create_meal_plan(
            name="P", description="", recipe_ids=[recipe.recipe_id]
        )
        sl = crud.create_shopping_list(meal_plan_id=plan.meal_plan_id)
        with patch.object(
            pdf,
            "resolve_dejavu_fonts",
            side_effect=pdf.FontUnavailableError("missing"),
        ):
            resp = self.client.get(f"/shopping-lists/{sl.id}/pdf")
        self.assertEqual(resp.status_code, 500)

    def test_pdf_lang_pl_still_returns_pdf(self):
        recipe = crud.create_recipe(
            name="R",
            instructions="i",
            ingredients_data=[{"name": "X", "quantity": 1, "unit": "g"}],
        )
        plan = crud.create_meal_plan(
            name="P", description="", recipe_ids=[recipe.recipe_id]
        )
        sl = crud.create_shopping_list(meal_plan_id=plan.meal_plan_id)
        resp = self.client.get(f"/shopping-lists/{sl.id}/pdf?lang=pl")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.startswith(b"%PDF"))
        self.assertIn("filename*=UTF-8''", resp.headers["Content-Disposition"])


class TestPdfChrome(unittest.TestCase):
    def test_pl_heading(self):
        self.assertEqual(pdf_chrome("pl")["heading"], "Lista zakupów")
        self.assertEqual(pdf_chrome("fr")["heading"], "Shopping List")
        self.assertEqual(pdf_chrome("PL")["heading"], "Lista zakupów")
