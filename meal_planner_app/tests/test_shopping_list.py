"""
Tests for the shopping list generation functionality in crud.py.
"""

import unittest
import uuid

from meal_planner_app import crud


class TestShoppingList(
    unittest.TestCase
):  # pylint: disable=too-many-instance-attributes
    """Tests for the generate_shopping_list function."""

    def setUp(self):
        """Set up a variety of recipes and meal plans for testing."""
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

        # Recipe 1: Basic ingredients
        self.recipe1 = crud.create_recipe(
            name="Pancakes",
            instructions="Mix and cook.",
            ingredients_data=[
                {"name": "Flour", "quantity": 2, "unit": "cup"},
                {"name": "Sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "Egg", "quantity": 1, "unit": "pc"},
            ],
        )

        # Recipe 2: More ingredients, some overlapping with Recipe 1, some non-numeric
        self.recipe2 = crud.create_recipe(
            name="Deluxe Omelette",
            instructions="Whisk eggs, add fillings, cook.",
            ingredients_data=[
                {"name": "Egg", "quantity": 3, "unit": "pc"},
                {"name": "Cheese", "quantity": 50, "unit": "g"},
                {"name": "Salt", "quantity": "to taste", "unit": ""},
                {"name": "Pepper", "quantity": "a pinch", "unit": "sprinkle"},
            ],
        )

        # Recipe 3: Different units for same ingredient name, another non-numeric
        self.recipe3 = crud.create_recipe(
            name="Milkshake",
            instructions="Blend.",
            ingredients_data=[
                {"name": "Milk", "quantity": 200, "unit": "ml"},
                {"name": "Sugar", "quantity": 2, "unit": "tbsp"},
                {"name": "Ice Cream", "quantity": "2 scoops", "unit": ""},
            ],
        )

        # Recipe 4: No ingredients
        self.recipe4_no_ing = crud.create_recipe(
            name="Water", instructions="Pour water."
        )

        self.meal_plan1 = crud.create_meal_plan(name="Breakfast Week")
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, self.recipe1.recipe_id
        )
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, self.recipe2.recipe_id
        )

        self.meal_plan2_complex = crud.create_meal_plan(name="Full Menu")
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe1.recipe_id
        )  # Pancakes
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe2.recipe_id
        )  # Omelette
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe3.recipe_id
        )  # Milkshake

        self.meal_plan_empty_recipes = crud.create_meal_plan(name="Empty Recipes Plan")
        crud.add_recipe_to_meal_plan(
            self.meal_plan_empty_recipes.meal_plan_id, self.recipe4_no_ing.recipe_id
        )

        self.meal_plan_no_recipes = crud.create_meal_plan(name="No Recipes Plan")

    def find_ingredient(self, shopping_list, name, unit):
        """Helper function to find an ingredient in a (now grouped) shopping list."""
        if isinstance(shopping_list, dict):
            for loc_items in shopping_list.values():
                for item in loc_items:
                    if item["name"] == name and item["unit"] == unit:
                        return item
        else:
            for item in shopping_list or []:
                if item["name"] == name and item["unit"] == unit:
                    return item
        return None

    def get_total_items(self, shopping_list):
        """Return total number of items across groups (or list)."""
        if isinstance(shopping_list, dict):
            return sum(len(v) for v in shopping_list.values())
        return len(shopping_list or [])

    def test_generate_shopping_list_basic_aggregation(self):
        """Test basic aggregation of numeric quantities for the same ingredient."""
        shopping_list = crud.generate_shopping_list(self.meal_plan1.meal_plan_id)
        self.assertIsNotNone(shopping_list)

        # Flour: 2 cup (from R1)
        flour = self.find_ingredient(shopping_list, "Flour", "cup")
        self.assertIsNotNone(flour)
        self.assertEqual(flour["quantity"], 2)

        # Sugar: 0.5 cup (from R1)
        sugar = self.find_ingredient(shopping_list, "Sugar", "cup")
        self.assertIsNotNone(sugar)
        self.assertEqual(sugar["quantity"], 0.5)

        # Egg: 1 pc (R1) + 3 pc (R2) = 4 pc
        egg = self.find_ingredient(shopping_list, "Egg", "pc")
        self.assertIsNotNone(egg)
        self.assertEqual(egg["quantity"], 4)

        # Cheese: 50 g (from R2)
        cheese = self.find_ingredient(shopping_list, "Cheese", "g")
        self.assertIsNotNone(cheese)
        self.assertEqual(cheese["quantity"], 50)

        # Salt: 'to taste' (from R2)
        salt = self.find_ingredient(shopping_list, "Salt", "")
        self.assertIsNotNone(salt)
        self.assertEqual(salt["quantity"], "to taste")

        # Pepper: 'a pinch' (from R2)
        pepper = self.find_ingredient(shopping_list, "Pepper", "sprinkle")
        self.assertIsNotNone(pepper)
        self.assertEqual(pepper["quantity"], "a pinch")

        self.assertEqual(
            self.get_total_items(shopping_list), 6
        )  # Flour, Sugar (cup), Egg, Cheese, Salt, Pepper

    def test_generate_shopping_list_complex_aggregation(self):
        """Test aggregation with different units and non-numeric quantities."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan2_complex.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)

        # Check some key aggregations
        # Egg: 1 pc (R1) + 3 pc (R2) = 4 pc
        egg = self.find_ingredient(shopping_list, "Egg", "pc")
        self.assertIsNotNone(egg)
        self.assertEqual(egg["quantity"], 4)

        # Sugar (cup): 0.5 cup (R1)
        sugar_cup = self.find_ingredient(shopping_list, "Sugar", "cup")
        self.assertIsNotNone(sugar_cup)
        self.assertEqual(sugar_cup["quantity"], 0.5)

        # Sugar (tbsp): 2 tbsp (R3)
        sugar_tbsp = self.find_ingredient(shopping_list, "Sugar", "tbsp")
        self.assertIsNotNone(sugar_tbsp)
        self.assertEqual(sugar_tbsp["quantity"], 2)

        # Milk (ml): 200 ml (R3)
        milk = self.find_ingredient(shopping_list, "Milk", "ml")
        self.assertIsNotNone(milk)
        self.assertEqual(milk["quantity"], 200)

        # Ice Cream: '2 scoops' (R3)
        ice_cream = self.find_ingredient(shopping_list, "Ice Cream", "")
        self.assertIsNotNone(ice_cream)
        self.assertEqual(ice_cream["quantity"], "2 scoops")

        # Expected number of unique ingredient_key items
        # R1: Flour_cup, Sugar_cup, Egg_pc (3)
        # R2: Egg_pc (exists), Cheese_g, Salt_, Pepper_sprinkle (3 new)
        # R3: Milk_ml, Sugar_tbsp, Ice Cream_ (3 new)
        # Total = 3 + 3 + 3 = 9
        self.assertEqual(self.get_total_items(shopping_list), 9)

    def test_shopping_list_with_mixed_numeric_non_numeric(self):
        """Test aggregation when an ingredient has both numeric and non-numeric quantities."""
        # Create a recipe that will cause mixed types for 'Flour_cup'
        recipe_extra = crud.create_recipe(
            name="Extra Flour",
            instructions="Add more flour.",
            ingredients_data=[
                {"name": "Flour", "quantity": "a bit more", "unit": "cup"}
            ],
        )
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, recipe_extra.recipe_id
        )
        # Now meal_plan1 has:
        # R1: Flour, 2 cup
        # R2: (no flour)
        # Extra: Flour, 'a bit more' cup

        shopping_list = crud.generate_shopping_list(self.meal_plan1.meal_plan_id)
        flour_cup = self.find_ingredient(shopping_list, "Flour", "cup")
        self.assertIsNotNone(flour_cup)
        self.assertIsInstance(flour_cup["quantity"], list)
        self.assertIn(
            "2.0", flour_cup["quantity"]
        )  # Original numeric becomes string in list
        self.assertIn("a bit more", flour_cup["quantity"])

    def test_shopping_list_empty_meal_plan(self):
        """Test generating a shopping list for a meal plan with no recipes."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan_no_recipes.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)
        self.assertEqual(self.get_total_items(shopping_list), 0)

    def test_shopping_list_meal_plan_with_empty_recipes(self):
        """Test generating a shopping list for a meal plan with recipes that have no ingredients."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan_empty_recipes.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)
        self.assertEqual(self.get_total_items(shopping_list), 0)

    def test_shopping_list_non_existent_meal_plan(self):
        """Test generating a shopping list for a non-existent meal plan ID."""
        non_existent_id = uuid.uuid4()
        shopping_list = crud.generate_shopping_list(non_existent_id)
        self.assertIsNone(shopping_list)


class TestShoppingListCompatibleUnits(unittest.TestCase):
    """FR-1.5.2: consolidate compatible units (g↔kg, ml↔l) at generation time.

    Display rule after summing in base units (g or ml):
    - If every contributing unit is the same scale (all grams, or all kg),
      keep that scale (canonical short form: g/kg/ml/l).
    - If scales are mixed (g+kg or ml+l), prefer the larger unit when the
      total is >= 1000 base units (1000g → kg, 1000ml → l); otherwise keep
      the smaller unit.
    - Do not convert across dimensions (g↛ml) or to count units.
    - Name + location remain part of identity.
    """

    def setUp(self):
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        if hasattr(crud, "reset_shopping_lists_db"):
            crud.reset_shopping_lists_db()

    def _plan_from_ingredient_lists(self, *ingredient_lists):
        recipe_ids = []
        for i, ings in enumerate(ingredient_lists):
            recipe = crud.create_recipe(
                name=f"Recipe {i}",
                instructions="Mix.",
                ingredients_data=ings,
            )
            recipe_ids.append(recipe.recipe_id)
        return crud.create_meal_plan(name="Unit plan", recipe_ids=recipe_ids)

    def _flatten(self, shopping_list):
        if isinstance(shopping_list, dict):
            items = []
            for loc_items in shopping_list.values():
                items.extend(loc_items)
            return items
        return list(shopping_list or [])

    def _by_name(self, shopping_list, name, location=None):
        matches = []
        for item in self._flatten(shopping_list):
            if item["name"] != name:
                continue
            if location is not None and (item.get("location") or "") != location:
                continue
            matches.append(item)
        return matches

    def test_500g_plus_half_kg_merges_to_one_kilogram(self):
        """Regression: 500g + 0.5kg of the same name/location → one line, 1 kg."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Flour", "quantity": 500, "unit": "g"}],
            [{"name": "Flour", "quantity": 0.5, "unit": "kg"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        flour = self._by_name(shopping_list, "Flour")
        self.assertEqual(len(flour), 1)
        self.assertEqual(flour[0]["unit"], "kg")
        self.assertEqual(flour[0]["quantity"], 1)

    def test_100g_plus_0_2kg_stays_in_grams(self):
        """Mixed g+kg totaling 300g (< 1000g) displays as grams."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Sugar", "quantity": 100, "unit": "g"}],
            [{"name": "Sugar", "quantity": 0.2, "unit": "kg"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        sugar = self._by_name(shopping_list, "Sugar")
        self.assertEqual(len(sugar), 1)
        self.assertEqual(sugar[0]["unit"], "g")
        self.assertEqual(sugar[0]["quantity"], 300)

    def test_ml_plus_l_merges_and_prefers_litre_at_threshold(self):
        """500ml + 0.5l → 1 l (same threshold rule as mass)."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Milk", "quantity": 500, "unit": "ml"}],
            [{"name": "Milk", "quantity": 0.5, "unit": "l"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        milk = self._by_name(shopping_list, "Milk")
        self.assertEqual(len(milk), 1)
        self.assertEqual(milk[0]["unit"], "l")
        self.assertEqual(milk[0]["quantity"], 1)

    def test_millilitre_liter_spellings_and_case_are_compatible(self):
        """millilitre/liter (and whitespace/case) consolidate with ml/l."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Stock", "quantity": 200, "unit": " millilitre "}],
            [{"name": "Stock", "quantity": 0.3, "unit": "Liter"}],
            [{"name": "Stock", "quantity": 100, "unit": "ML"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        stock = self._by_name(shopping_list, "Stock")
        self.assertEqual(len(stock), 1)
        # 200ml + 300ml + 100ml = 600ml < 1000 → ml
        self.assertEqual(stock[0]["unit"], "ml")
        self.assertEqual(stock[0]["quantity"], 600)

    def test_does_not_convert_grams_to_millilitres(self):
        mp = self._plan_from_ingredient_lists(
            [{"name": "Oil", "quantity": 100, "unit": "g"}],
            [{"name": "Oil", "quantity": 100, "unit": "ml"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        oil = self._by_name(shopping_list, "Oil")
        self.assertEqual(len(oil), 2)
        units = sorted(item["unit"] for item in oil)
        self.assertEqual(units, ["g", "ml"])

    def test_does_not_convert_count_units_to_mass(self):
        mp = self._plan_from_ingredient_lists(
            [{"name": "Apple", "quantity": 2, "unit": "pc"}],
            [{"name": "Apple", "quantity": 100, "unit": "g"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        apples = self._by_name(shopping_list, "Apple")
        self.assertEqual(len(apples), 2)

    def test_same_name_same_location_merges_across_units(self):
        mp = self._plan_from_ingredient_lists(
            [{"name": "Mąka", "quantity": 500, "unit": "g", "location": "pieczywo"}],
            [{"name": "Mąka", "quantity": 0.5, "unit": "kg", "location": "pieczywo"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        flour = self._by_name(shopping_list, "Mąka", location="pieczywo")
        self.assertEqual(len(flour), 1)
        self.assertEqual(flour[0]["unit"], "kg")
        self.assertEqual(flour[0]["quantity"], 1)

    def test_single_scale_is_not_rewritten(self):
        """A lone 0.5 kg line stays kg (conversion is for consolidating mixed scales)."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Rice", "quantity": 0.5, "unit": "kg"}],
        )
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        rice = self._by_name(shopping_list, "Rice")
        self.assertEqual(len(rice), 1)
        self.assertEqual(rice[0]["unit"], "kg")
        self.assertEqual(rice[0]["quantity"], 0.5)

    def test_persisted_list_stores_converted_units_at_generation(self):
        """Conversion applies when creating a list from a meal plan, not later."""
        mp = self._plan_from_ingredient_lists(
            [{"name": "Flour", "quantity": 500, "unit": "g"}],
            [{"name": "Flour", "quantity": 0.5, "unit": "kg"}],
        )
        saved = crud.create_shopping_list(meal_plan_id=mp.meal_plan_id)
        self.assertIsNotNone(saved)
        self.assertEqual(len(saved.items), 1)
        self.assertEqual(saved.items[0].unit, "kg")
        self.assertEqual(saved.items[0].quantity, 1)


class TestShoppingListLocationGrouping(unittest.TestCase):
    """Generated list JSON is grouped by location for the UI / PDF."""

    def setUp(self):
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

    def test_generate_shopping_list_groups_by_location_empty_last(self):
        recipe = crud.create_recipe(
            name="Grouped",
            instructions="Cook.",
            ingredients_data=[
                {"name": "Mąka", "quantity": 500, "unit": "g", "location": "pieczywo"},
                {"name": "Mleko", "quantity": 1, "unit": "l", "location": "nabiał"},
                {"name": "Sól", "quantity": 1, "unit": "pinch"},
            ],
        )
        mp = crud.create_meal_plan(name="Loc plan", recipe_ids=[recipe.recipe_id])
        shopping_list = crud.generate_shopping_list(mp.meal_plan_id)
        self.assertIsInstance(shopping_list, dict)
        self.assertIn("pieczywo", shopping_list)
        self.assertIn("nabiał", shopping_list)
        self.assertIn("", shopping_list)
        self.assertEqual([item["name"] for item in shopping_list["pieczywo"]], ["Mąka"])
        self.assertEqual([item["name"] for item in shopping_list["nabiał"]], ["Mleko"])
        self.assertEqual([item["name"] for item in shopping_list[""]], ["Sól"])
        # Named locations alphabetical; empty/missing last (same as PDF)
        self.assertEqual(list(shopping_list.keys())[-1], "")
        named = [k for k in shopping_list if k]
        self.assertEqual(named, sorted(named))

    def test_persisted_items_keep_location_for_html_grouping(self):
        """Flat persisted items still carry location so the HTML UI can group."""
        recipe = crud.create_recipe(
            name="Grouped persist",
            instructions="Cook.",
            ingredients_data=[
                {"name": "Mąka", "quantity": 500, "unit": "g", "location": "pieczywo"},
                {"name": "Sól", "quantity": 1, "unit": "pinch"},
            ],
        )
        mp = crud.create_meal_plan(name="Loc persist", recipe_ids=[recipe.recipe_id])
        saved = crud.create_shopping_list(meal_plan_id=mp.meal_plan_id)
        locations = {item.location or "" for item in saved.items}
        self.assertEqual(locations, {"pieczywo", ""})
        names_by_loc = {(item.location or ""): item.name for item in saved.items}
        self.assertEqual(names_by_loc["pieczywo"], "Mąka")
        self.assertEqual(names_by_loc[""], "Sól")


if __name__ == "__main__":
    unittest.main()
