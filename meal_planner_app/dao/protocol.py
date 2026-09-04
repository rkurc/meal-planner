"""Persistence protocols. SQL does not belong here."""

import uuid
from typing import List, Optional, Protocol

from meal_planner_app.models.ingredient import MasterIngredient
from meal_planner_app.models.meal_plan import MealPlan
from meal_planner_app.models.recipe import Recipe
from meal_planner_app.models.shopping_list import ShoppingList


class IngredientDao(Protocol):
    """Catalog ingredients (no quantity)."""

    def insert(self, ingredient: MasterIngredient) -> MasterIngredient: ...

    def find_by_id(self, ingredient_id: uuid.UUID) -> Optional[MasterIngredient]: ...

    def find_by_name(self, name: str) -> Optional[MasterIngredient]: ...

    def find_all(self) -> List[MasterIngredient]: ...

    def update(self, ingredient: MasterIngredient) -> Optional[MasterIngredient]: ...

    def delete(self, ingredient_id: uuid.UUID) -> bool: ...


class RecipeDao(Protocol):
    """Recipes. Line items must already have ingredient_id set."""

    def insert(self, recipe: Recipe) -> Recipe: ...

    def find_by_id(self, recipe_id: uuid.UUID) -> Optional[Recipe]: ...

    def find_all(self) -> List[Recipe]: ...

    def update(self, recipe: Recipe) -> Optional[Recipe]: ...

    def delete(self, recipe_id: uuid.UUID) -> bool: ...


class MealPlanDao(Protocol):
    """Meal plans with recipe ids and counts."""

    def insert(self, meal_plan: MealPlan) -> MealPlan: ...

    def find_by_id(self, meal_plan_id: uuid.UUID) -> Optional[MealPlan]: ...

    def find_all(self) -> List[MealPlan]: ...

    def update(self, meal_plan: MealPlan) -> Optional[MealPlan]: ...

    def delete(self, meal_plan_id: uuid.UUID) -> bool: ...


class ShoppingListDao(Protocol):
    """Persisted shopping lists (item snapshots)."""

    def insert(self, shopping_list: ShoppingList) -> ShoppingList: ...

    def find_by_id(self, shopping_list_id: uuid.UUID) -> Optional[ShoppingList]: ...

    def find_all(self) -> List[ShoppingList]: ...

    def update(self, shopping_list: ShoppingList) -> Optional[ShoppingList]: ...

    def delete(self, shopping_list_id: uuid.UUID) -> bool: ...


class MealPlannerDao(Protocol):
    """Root persistence port. Nested entity DAOs share one backend."""

    ingredients: IngredientDao
    recipes: RecipeDao
    meal_plans: MealPlanDao
    shopping_lists: ShoppingListDao

    def reset(self) -> None: ...

    def close(self) -> None: ...
