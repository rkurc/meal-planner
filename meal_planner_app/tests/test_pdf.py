"""PDF font resolution, NFC text, and FontUnavailableError (i18n PR-1)."""

import importlib.resources
import inspect
import os
import unicodedata
import unittest
from unittest.mock import patch

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
