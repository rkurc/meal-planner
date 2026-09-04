"""Tests for compatible-unit conversion used when consolidating shopping lists.

Rules (must stay in sync with meal_planner_app.units and shopping-list tests):
- Mass family: g/gram/grams and kg/kilogram/kilograms (case-insensitive, trimmed).
- Volume family: ml/millilitre/milliliter(s) and l/litre/liter(s).
- Never convert across families (g ↛ ml) or to count units (apples ↛ grams).
- After summing in base units (g or ml):
  - same scale → keep that scale (canonical short form g/kg/ml/l)
  - mixed scales → kg/l when total >= 1000 base units, else g/ml
"""

import unittest

from meal_planner_app.units import (
    add_to_aggregate,
    aggregation_key,
    consolidate_numeric,
    finalize_aggregated,
    normalize_unit,
    unit_family,
)


class TestNormalizeAndFamily(unittest.TestCase):
    def test_normalize_trims_and_lowercases(self):
        self.assertEqual(normalize_unit(" Kg "), "kg")
        self.assertEqual(normalize_unit(None), "")
        self.assertEqual(normalize_unit("  "), "")

    def test_mass_and_volume_families(self):
        self.assertEqual(unit_family("G"), "mass")
        self.assertEqual(unit_family("kilograms"), "mass")
        self.assertEqual(unit_family("millilitre"), "volume")
        self.assertEqual(unit_family("Liters"), "volume")
        self.assertIsNone(unit_family("pc"))
        self.assertIsNone(unit_family("cup"))


class TestConsolidateNumeric(unittest.TestCase):
    def test_500g_plus_half_kg_is_one_kg(self):
        qty, unit = consolidate_numeric([(500, "g"), (0.5, "kg")])
        self.assertEqual(unit, "kg")
        self.assertEqual(qty, 1)

    def test_mixed_mass_below_threshold_stays_grams(self):
        qty, unit = consolidate_numeric([(100, "g"), (0.2, "kg")])
        self.assertEqual(unit, "g")
        self.assertEqual(qty, 300)

    def test_ml_plus_l_at_threshold(self):
        qty, unit = consolidate_numeric([(500, "ml"), (0.5, "l")])
        self.assertEqual(unit, "l")
        self.assertEqual(qty, 1)

    def test_spellings_and_whitespace(self):
        qty, unit = consolidate_numeric(
            [(200, " millilitre "), (0.3, "Liter"), (100, "ML")]
        )
        self.assertEqual(unit, "ml")
        self.assertEqual(qty, 600)

    def test_incompatible_g_and_ml_returns_none(self):
        self.assertIsNone(consolidate_numeric([(100, "g"), (100, "ml")]))

    def test_incompatible_count_and_mass_returns_none(self):
        self.assertIsNone(consolidate_numeric([(2, "pc"), (100, "g")]))

    def test_single_kg_is_not_rewritten_to_grams(self):
        qty, unit = consolidate_numeric([(0.5, "kg")])
        self.assertEqual(unit, "kg")
        self.assertEqual(qty, 0.5)

    def test_same_scale_grams_are_not_promoted(self):
        qty, unit = consolidate_numeric([(1500, "g"), (500, "grams")])
        self.assertEqual(unit, "g")
        self.assertEqual(qty, 2000)


class TestAggregationIdentity(unittest.TestCase):
    def test_g_and_kg_share_key_for_same_name_and_location(self):
        self.assertEqual(
            aggregation_key("Mąka", "g", "pieczywo"),
            aggregation_key("Mąka", "kg", "pieczywo"),
        )

    def test_same_name_different_location_has_distinct_keys(self):
        """mąka / pieczywo vs nabiał stay separate even with compatible units."""
        self.assertNotEqual(
            aggregation_key("Mąka", "g", "pieczywo"),
            aggregation_key("Mąka", "kg", "nabiał"),
        )

    def test_add_to_aggregate_does_not_merge_across_aisles(self):
        aggregated = {}
        add_to_aggregate(
            aggregated,
            {
                "name": "Mąka",
                "quantity": 500,
                "unit": "g",
                "location": "pieczywo",
                "location_id": None,
            },
        )
        add_to_aggregate(
            aggregated,
            {
                "name": "Mąka",
                "quantity": 0.5,
                "unit": "kg",
                "location": "nabiał",
                "location_id": None,
            },
        )
        items = finalize_aggregated(aggregated)
        self.assertEqual(len(items), 2)
        by_loc = {item["location"]: item for item in items}
        self.assertEqual(by_loc["pieczywo"]["unit"], "g")
        self.assertEqual(by_loc["pieczywo"]["quantity"], 500)
        self.assertEqual(by_loc["nabiał"]["unit"], "kg")
        self.assertEqual(by_loc["nabiał"]["quantity"], 0.5)

    def test_add_to_aggregate_merges_g_and_kg_same_aisle(self):
        aggregated = {}
        add_to_aggregate(
            aggregated,
            {"name": "Flour", "quantity": 500, "unit": "g", "location": None},
        )
        add_to_aggregate(
            aggregated,
            {"name": "Flour", "quantity": 0.5, "unit": "kg", "location": None},
        )
        items = finalize_aggregated(aggregated)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["unit"], "kg")
        self.assertEqual(items[0]["quantity"], 1)


if __name__ == "__main__":
    unittest.main()
