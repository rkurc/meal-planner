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

def create_recipe(name: str, instructions: str, description: Optional[str] = None,
                  source_url: Optional[str] = None, ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None) -> Recipe:
    """Creates a new recipe and adds it to the database."""
    new_recipe = Recipe(
        name=name,
        instructions=instructions,
        description=description,
        source_url=source_url
    )
    if ingredients_data:
        for ing_data in ingredients_data:
            new_ingredient = Ingredient(
                name=ing_data['name'],
                quantity=str(ing_data.get('quantity', '')),
                unit=ing_data.get('unit', '')
            )
            new_recipe.ingredients.append(new_ingredient)
    db.session.add(new_recipe)
    db.session.commit()
    return new_recipe

def get_recipe(recipe_id: str) -> Optional[Recipe]:
    """Retrieves a single recipe by its ID, including its ingredients."""
    return db.session.query(Recipe).options(joinedload(Recipe.ingredients)).filter_by(id=recipe_id).first()

def list_recipes() -> List[Recipe]:
    """Returns a list of all recipes."""
    return db.session.query(Recipe).order_by(Recipe.name).all()

def update_recipe(recipe_id: str, name: Optional[str] = None, instructions: Optional[str] = None,
                  description: Optional[str] = None, source_url: Optional[str] = None,
                  ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None) -> Optional[Recipe]:
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
                name=ing_data['name'],
                quantity=str(ing_data.get('quantity', '')),
                unit=ing_data.get('unit', '')
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

# --- MealPlan CRUD Operations ---
def create_meal_plan(name: str, description: str = "", recipe_ids: Optional[List[str]] = None) -> MealPlan:
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
    return db.session.query(MealPlan).options(joinedload(MealPlan.recipes)).filter_by(id=meal_plan_id).first()

def list_meal_plans() -> List[MealPlan]:
    """Returns a list of all meal plans."""
    return db.session.query(MealPlan).order_by(MealPlan.name).all()

# ... other CRUD operations ...
# I will omit the rest for brevity, but they would be here.
