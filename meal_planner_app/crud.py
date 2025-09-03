"""
CRUD (Create, Read, Update, Delete) operations for managing recipes and meal plans
using in-memory data structures. Also includes shopping list generation and recipe search.
"""
import uuid
from typing import List, Dict, Optional, Union
from .models.recipe import Recipe
from .models.ingredient import Ingredient
from .models.meal_plan import MealPlan

recipes_db: List[Recipe] = []

def create_recipe(name: str,
                  instructions: str,
                  ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
                  description: Optional[str] = None,
                  source_url: Optional[str] = None) -> Recipe:
    """
    Creates a new recipe and stores it in the in-memory database.
    ingredients_data should be a list of dicts like:
    [{'name': 'sugar', 'quantity': 1, 'unit': 'cup'}]
    """
    parsed_ingredients = []
    if ingredients_data:
        for ing_data in ingredients_data:
            parsed_ingredients.append(Ingredient(name=ing_data['name'],
                                                 quantity=ing_data['quantity'],
                                                 unit=ing_data['unit']))

    recipe = Recipe(name=name,
                    description=description,
                    ingredients=parsed_ingredients,
                    instructions=instructions,
                    source_url=source_url)
    recipes_db.append(recipe)
    return recipe

def get_recipe(recipe_id: uuid.UUID) -> Optional[Recipe]:
    """Retrieves a recipe by its ID."""
    for recipe in recipes_db:
        if recipe.id == recipe_id:
            return recipe
    return None

def update_recipe(recipe_id: uuid.UUID,
                  name: Optional[str] = None,
                  description: Optional[str] = None,
                  ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
                  instructions: Optional[str] = None,
                  source_url: Optional[str] = None) -> Optional[Recipe]:
    """Updates an existing recipe."""
    recipe = get_recipe(recipe_id)
    if not recipe:
        return None

    if name is not None:
        recipe.name = name
    if description is not None:
        recipe.description = description
    if instructions is not None:
        recipe.instructions = instructions
    if source_url is not None:
        recipe.source_url = source_url

    if ingredients_data is not None:
        parsed_ingredients = []
        for ing_data in ingredients_data:
            parsed_ingredients.append(Ingredient(name=ing_data['name'],
                                                 quantity=ing_data['quantity'],
                                                 unit=ing_data['unit']))
        recipe.ingredients = parsed_ingredients

    return recipe

def delete_recipe(recipe_id: uuid.UUID) -> bool:
    """Deletes a recipe by its ID."""
    recipe = get_recipe(recipe_id)
    if recipe:
        recipes_db.remove(recipe)
        return True
    return False

def list_recipes() -> List[Recipe]:
    """Returns all recipes."""
    return recipes_db

def reset_recipes_db():
    """Helper function to reset the database, primarily for testing."""
    global recipes_db
    recipes_db = []

# --- MealPlan CRUD Operations ---

meal_plans_db: List[MealPlan] = []

def reset_meal_plans_db():
    """Helper function to reset the meal plans database, primarily for testing."""
    global meal_plans_db
    meal_plans_db = []

def create_meal_plan(name: str, recipe_ids: Optional[List[uuid.UUID]] = None) -> MealPlan:
    """Creates a new meal plan."""
    if recipe_ids is None:
        recipe_ids = []
    meal_plan = MealPlan(name=name, recipe_ids=recipe_ids)
    meal_plans_db.append(meal_plan)
    return meal_plan

def get_meal_plan(meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
    """Retrieves a meal plan by its ID."""
    for mp in meal_plans_db:
        if mp.id == meal_plan_id:
            return mp
    return None

def list_meal_plans() -> List[MealPlan]:
    """Returns all meal plans."""
    return meal_plans_db

def add_recipe_to_meal_plan(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID) -> Optional[MealPlan]:
    """Adds a recipe ID to a meal plan's recipe_ids list."""
    meal_plan = get_meal_plan(meal_plan_id)
    recipe = get_recipe(recipe_id) # Check if recipe exists

    if not meal_plan:
        return None # Meal plan not found
    if not recipe:
        # Depending on desired behavior, could raise error or just not add
        return meal_plan # Or None, if we want to signify failure due to non-existent recipe

    if recipe_id not in meal_plan.recipe_ids:
        meal_plan.recipe_ids.append(recipe_id)
    return meal_plan

def remove_recipe_from_meal_plan(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID) -> Optional[MealPlan]:
    """Removes a recipe ID from a meal plan's recipe_ids list."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    if recipe_id in meal_plan.recipe_ids:
        meal_plan.recipe_ids.remove(recipe_id)
    return meal_plan

def delete_meal_plan(meal_plan_id: uuid.UUID) -> bool:
    """Deletes a meal plan by its ID."""
    meal_plan = get_meal_plan(meal_plan_id)
    if meal_plan:
        meal_plans_db.remove(meal_plan)
        return True
    return False

def update_meal_plan(meal_plan_id: uuid.UUID, name: Optional[str] = None, recipe_ids: Optional[List[uuid.UUID]] = None) -> Optional[MealPlan]:
    """Updates an existing meal plan's name and/or recipe list."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    if name is not None:
        meal_plan.name = name

    if recipe_ids is not None:
        # Here we replace the entire list of recipe_ids
        meal_plan.recipe_ids = recipe_ids

    return meal_plan

# --- Shopping List Generation ---

def generate_shopping_list(meal_plan_id: uuid.UUID) -> Optional[List[Dict[str, Union[str, float, List[str]]]]]:
    """
    Generates an aggregated shopping list for a given meal plan.
    Returns a list of ingredient dictionaries, or None if the meal plan is not found.
    """
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    aggregated_ingredients: Dict[str, Dict[str, Union[str, float, List[str]]]] = {}

    for recipe_id in meal_plan.recipe_ids:
        recipe = get_recipe(recipe_id)
        if not recipe:
            continue # Skip if a recipe ID in the plan doesn't exist

        for ingredient in recipe.ingredients:
            ingredient_key = f"{ingredient.name}_{ingredient.unit}"
            current_quantity_str = str(ingredient.quantity) # Ensure it's a string for consistency first
            current_quantity_numeric: Optional[float] = None

            try:
                current_quantity_numeric = float(current_quantity_str)
            except (ValueError, TypeError):
                # Quantity is not a simple float (e.g., "to taste", "1-2", or empty)
                pass

            if ingredient_key in aggregated_ingredients:
                existing_entry = aggregated_ingredients[ingredient_key]
                existing_quantity = existing_entry['quantity']

                if current_quantity_numeric is not None and isinstance(existing_quantity, (int, float)):
                    # Both are numeric, sum them
                    existing_entry['quantity'] = existing_quantity + current_quantity_numeric
                elif isinstance(existing_quantity, list):
                    # Existing is already a list, append new quantity string
                    existing_quantity.append(current_quantity_str)
                else:
                    # Existing was a single value (numeric or string), convert to list and add both
                    existing_entry['quantity'] = [str(existing_quantity), current_quantity_str]
            else:
                # New ingredient for the shopping list
                aggregated_ingredients[ingredient_key] = {
                    'name': ingredient.name,
                    'quantity': current_quantity_numeric if current_quantity_numeric is not None else current_quantity_str,
                    'unit': ingredient.unit
                }
                # If quantity was empty string and we tried to make it float, it would be None.
                # Ensure it's stored as original string if not numeric.
                if current_quantity_numeric is None and aggregated_ingredients[ingredient_key]['quantity'] is None:
                     aggregated_ingredients[ingredient_key]['quantity'] = current_quantity_str


    return list(aggregated_ingredients.values())

# --- Recipe Search ---

def search_recipes(query: str, filter_ingredient: Optional[str] = None) -> List[Recipe]:
    """
    Searches for recipes based on a query string and optionally filters by an ingredient.
    The query is matched against recipe name, description, and ingredient names.
    If filter_ingredient is provided, results are further filtered to include only
    recipes containing that ingredient.
    Returns a list of unique matching Recipe objects.
    """
    base_recipes = []
    if query and query.strip() != "":
        normalized_query = query.lower().strip()
        matching_recipes_ids = set()

        for recipe in recipes_db:
            # Check name
            if normalized_query in recipe.name.lower():
                matching_recipes_ids.add(recipe.id)
                continue

            # Check description
            if recipe.description and normalized_query in recipe.description.lower():
                matching_recipes_ids.add(recipe.id)
                continue

            # Check ingredients for the main query
            for ingredient in recipe.ingredients:
                if normalized_query in ingredient.name.lower():
                    matching_recipes_ids.add(recipe.id)
                    break

        for recipe_id in matching_recipes_ids:
            recipe = get_recipe(recipe_id)
            if recipe:
                base_recipes.append(recipe)
    elif not filter_ingredient or filter_ingredient.strip() == "":
        # If no query and no filter_ingredient, return empty or all based on desired behavior.
        # Current: return empty if both are effectively empty.
        # If query is empty but filter_ingredient is present, we'll use all recipes as base.
        return []
    else: # No query, but there IS a filter_ingredient
        base_recipes = list_recipes()


    if not filter_ingredient or filter_ingredient.strip() == "":
        return base_recipes # No ingredient filter to apply

    normalized_filter_ingredient = filter_ingredient.lower().strip()
    filtered_results = []

    for recipe in base_recipes:
        for ingredient_obj in recipe.ingredients:
            if normalized_filter_ingredient in ingredient_obj.name.lower():
                filtered_results.append(recipe)
                break # Found matching ingredient in this recipe, move to next recipe

    return filtered_results
