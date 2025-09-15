"""
CRUD operations for the Meal Planner application using SQLAlchemy.
"""

from typing import List, Optional, Dict, Union
from sqlalchemy.orm import joinedload
from .database import db
from .models.recipe import Recipe
from .models.ingredient import Ingredient
from .models.meal_plan import MealPlan
from .models.shopping_list import ShoppingList, ShoppingListItem

# --- Recipe CRUD Operations ---


def create_recipe(
    name: str,
    instructions: str,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
) -> Recipe:
    """Creates a new recipe and adds it to the database."""
    new_recipe = Recipe(
        name=name,
        instructions=instructions,
        description=description,
        source_url=source_url,
    )
    if ingredients_data:
        for ing_data in ingredients_data:
            new_ingredient = Ingredient(
                name=ing_data["name"],
                quantity=str(ing_data.get("quantity", "")),
                unit=ing_data.get("unit", ""),
            )
            new_recipe.ingredients.append(new_ingredient)
    db.session.add(new_recipe)
    db.session.commit()
    return new_recipe


def get_recipe(recipe_id: str) -> Optional[Recipe]:
    """Retrieves a single recipe by its ID, including its ingredients."""
    return (
        db.session.query(Recipe)
        .options(joinedload(Recipe.ingredients))
        .filter_by(id=recipe_id)
        .first()
    )


def list_recipes() -> List[Recipe]:
    """Returns a list of all recipes."""
    return db.session.query(Recipe).order_by(Recipe.name).all()


# pylint: disable=too-many-arguments, too-many-positional-arguments
def update_recipe(
    recipe_id: str,
    name: Optional[str] = None,
    instructions: Optional[str] = None,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
) -> Optional[Recipe]:
    """Updates an existing recipe."""
    recipe = get_recipe(recipe_id)
    if not recipe:
        return None

    if name is not None:
        recipe.name = name
    if instructions is not None:
        recipe.instructions = instructions
    if description is not None:
        recipe.description = description
    if source_url is not None:
        recipe.source_url = source_url

    if ingredients_data is not None:
        recipe.ingredients = []
        for ing_data in ingredients_data:
            new_ingredient = Ingredient(
                name=ing_data["name"],
                quantity=str(ing_data.get("quantity", "")),
                unit=ing_data.get("unit", ""),
            )
            recipe.ingredients.append(new_ingredient)

    db.session.commit()
    return recipe


def delete_recipe(recipe_id: str) -> bool:
    """Deletes a recipe by its ID."""
    recipe = get_recipe(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
        return True
    return False


def reset_database():
    """Drops all tables and recreates them. For testing purposes."""
    db.drop_all()
    db.create_all()
    db.session.commit()


def generate_shopping_list(
    meal_plan_id: str,
) -> Optional[List[Dict[str, Union[str, float]]]]:
    """Generates an aggregated shopping list for a given meal plan."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    aggregated_ingredients = {}
    for recipe in meal_plan.recipes:
        for ingredient in recipe.ingredients:
            key = (
                ingredient.name.lower(),
                ingredient.unit.lower() if ingredient.unit else "",
            )
            if key not in aggregated_ingredients:
                aggregated_ingredients[key] = {
                    "name": ingredient.name,
                    "quantity": 0.0,
                    "unit": ingredient.unit,
                    "non_numeric_quantities": [],
                }

            try:
                quantity_float = float(ingredient.quantity)
                aggregated_ingredients[key]["quantity"] += quantity_float
            except (ValueError, TypeError):
                aggregated_ingredients[key]["non_numeric_quantities"].append(
                    ingredient.quantity
                )

    shopping_list = []
    for item in aggregated_ingredients.values():
        quantity_str = str(item["quantity"] if item["quantity"] > 0 else "")
        if item["non_numeric_quantities"]:
            all_quantities = [quantity_str] + item["non_numeric_quantities"]
            quantity_str = ", ".join(filter(None, all_quantities))

        shopping_list.append(
            {"name": item["name"], "quantity": quantity_str, "unit": item["unit"]}
        )

    return shopping_list


# --- MealPlan CRUD Operations ---
def create_meal_plan(
    name: str, description: str = "", recipe_ids: Optional[List[str]] = None
) -> MealPlan:
    """Creates a new meal plan."""
    new_meal_plan = MealPlan(name=name, description=description)
    if recipe_ids:
        recipes = db.session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        new_meal_plan.recipes = recipes
    db.session.add(new_meal_plan)
    db.session.commit()
    return new_meal_plan


def get_meal_plan(meal_plan_id: str) -> Optional[MealPlan]:
    """Retrieves a meal plan by its ID."""
    return (
        db.session.query(MealPlan)
        .options(joinedload(MealPlan.recipes))
        .filter_by(id=meal_plan_id)
        .first()
    )


def list_meal_plans() -> List[MealPlan]:
    """Returns a list of all meal plans."""
    return db.session.query(MealPlan).order_by(MealPlan.name).all()


def create_shopping_list(meal_plan_id: str) -> Optional[ShoppingList]:
    """Generates and saves a new shopping list for a meal plan."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    generated_items = generate_shopping_list(meal_plan_id)

    new_shopping_list = ShoppingList(
        name=f"Shopping List for {meal_plan.name}", meal_plan_id=meal_plan_id
    )

    for item_data in generated_items:
        list_item = ShoppingListItem(
            name=item_data["name"],
            quantity=str(item_data.get("quantity", "")),
            unit=item_data.get("unit", ""),
        )
        new_shopping_list.items.append(list_item)

    db.session.add(new_shopping_list)
    db.session.commit()
    return new_shopping_list
