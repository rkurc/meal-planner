"""SQLite implementation of MealPlannerDao. Only module that imports sqlite3."""

import json
import os
import sqlite3
import uuid
from typing import Any, List, Optional, Union

from meal_planner_app.models.ingredient import Ingredient, MasterIngredient
from meal_planner_app.models.meal_plan import MealPlan
from meal_planner_app.models.recipe import Recipe
from meal_planner_app.models.shopping_list import ShoppingList, ShoppingListItem

_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    default_unit TEXT NOT NULL DEFAULT '',
    location TEXT,
    location_id TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);

CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL DEFAULT '',
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id TEXT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL,
    quantity TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS meal_plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS meal_plan_recipes (
    meal_plan_id TEXT NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
    recipe_id TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    count REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (meal_plan_id, recipe_id)
);

CREATE TABLE IF NOT EXISTS shopping_lists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    meal_plan_id TEXT REFERENCES meal_plans(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS shopping_list_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopping_list_id TEXT NOT NULL REFERENCES shopping_lists(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT '',
    purchased INTEGER NOT NULL DEFAULT 0,
    location TEXT,
    location_id TEXT
);
"""


def _qty_dump(value: Any) -> str:
    return json.dumps(value)


def _qty_load(raw: Optional[str]) -> Union[str, float, int, list]:
    if raw is None:
        return ""
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return raw


def _uuid_str(value: uuid.UUID) -> str:
    return str(value)


class _SqliteIngredientDao:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def insert(self, ingredient: MasterIngredient) -> MasterIngredient:
        self._conn.execute(
            """
            INSERT INTO ingredients (id, name, default_unit, location, location_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                _uuid_str(ingredient.ingredient_id),
                ingredient.name,
                ingredient.default_unit or "",
                ingredient.location,
                ingredient.location_id,
            ),
        )
        self._conn.commit()
        return ingredient

    def find_by_id(self, ingredient_id: uuid.UUID) -> Optional[MasterIngredient]:
        row = self._conn.execute(
            "SELECT * FROM ingredients WHERE id = ?",
            (_uuid_str(ingredient_id),),
        ).fetchone()
        return self._from_row(row) if row else None

    def find_by_name(self, name: str) -> Optional[MasterIngredient]:
        row = self._conn.execute(
            "SELECT * FROM ingredients WHERE name = ?",
            (name.strip(),),
        ).fetchone()
        return self._from_row(row) if row else None

    def find_all(self) -> List[MasterIngredient]:
        rows = self._conn.execute(
            "SELECT * FROM ingredients ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, ingredient: MasterIngredient) -> Optional[MasterIngredient]:
        cursor = self._conn.execute(
            """
            UPDATE ingredients
            SET name = ?, default_unit = ?, location = ?, location_id = ?
            WHERE id = ?
            """,
            (
                ingredient.name,
                ingredient.default_unit or "",
                ingredient.location,
                ingredient.location_id,
                _uuid_str(ingredient.ingredient_id),
            ),
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            return None
        return ingredient

    def delete(self, ingredient_id: uuid.UUID) -> bool:
        try:
            cursor = self._conn.execute(
                "DELETE FROM ingredients WHERE id = ?",
                (_uuid_str(ingredient_id),),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            return False
        return cursor.rowcount > 0

    @staticmethod
    def _from_row(row: sqlite3.Row) -> MasterIngredient:
        return MasterIngredient(
            name=row["name"],
            default_unit=row["default_unit"] or "",
            location=row["location"],
            location_id=row["location_id"],
            ingredient_id=uuid.UUID(row["id"]),
        )


class _SqliteRecipeDao:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def insert(self, recipe: Recipe) -> Recipe:
        self._insert_recipe_row(recipe)
        self._replace_lines(recipe)
        self._conn.commit()
        return recipe

    def find_by_id(self, recipe_id: uuid.UUID) -> Optional[Recipe]:
        row = self._conn.execute(
            "SELECT * FROM recipes WHERE id = ?",
            (_uuid_str(recipe_id),),
        ).fetchone()
        if not row:
            return None
        return self._recipe_from_row(row)

    def find_all(self) -> List[Recipe]:
        rows = self._conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
        return [self._recipe_from_row(row) for row in rows]

    def update(self, recipe: Recipe) -> Optional[Recipe]:
        cursor = self._conn.execute(
            """
            UPDATE recipes
            SET name = ?, description = ?, instructions = ?, source_url = ?
            WHERE id = ?
            """,
            (
                recipe.name,
                recipe.description,
                recipe.instructions,
                recipe.source_url,
                _uuid_str(recipe.recipe_id),
            ),
        )
        if cursor.rowcount == 0:
            self._conn.commit()
            return None
        self._conn.execute(
            "DELETE FROM recipe_ingredients WHERE recipe_id = ?",
            (_uuid_str(recipe.recipe_id),),
        )
        self._replace_lines(recipe)
        self._conn.commit()
        return recipe

    def delete(self, recipe_id: uuid.UUID) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM recipes WHERE id = ?",
            (_uuid_str(recipe_id),),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def _insert_recipe_row(self, recipe: Recipe) -> None:
        self._conn.execute(
            """
            INSERT INTO recipes (id, name, description, instructions, source_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                _uuid_str(recipe.recipe_id),
                recipe.name,
                recipe.description,
                recipe.instructions,
                recipe.source_url,
            ),
        )

    def _replace_lines(self, recipe: Recipe) -> None:
        for position, line in enumerate(recipe.ingredients or []):
            if line.ingredient_id is None:
                raise ValueError(
                    "Recipe ingredient is missing ingredient_id; "
                    "crud must get-or-create the master row first"
                )
            self._conn.execute(
                """
                INSERT INTO recipe_ingredients
                    (recipe_id, ingredient_id, position, quantity, unit)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    _uuid_str(recipe.recipe_id),
                    _uuid_str(line.ingredient_id),
                    position,
                    _qty_dump(line.quantity),
                    line.unit or "",
                ),
            )

    def _recipe_from_row(self, row: sqlite3.Row) -> Recipe:
        recipe_id = uuid.UUID(row["id"])
        line_rows = self._conn.execute(
            """
            SELECT ri.quantity, ri.unit, ri.ingredient_id,
                   i.name, i.default_unit, i.location, i.location_id
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = ?
            ORDER BY ri.position
            """,
            (_uuid_str(recipe_id),),
        ).fetchall()
        ingredients = []
        for line in line_rows:
            unit = line["unit"] or line["default_unit"] or ""
            ingredients.append(
                Ingredient(
                    name=line["name"],
                    quantity=_qty_load(line["quantity"]),
                    unit=unit,
                    location=line["location"],
                    location_id=line["location_id"],
                    ingredient_id=uuid.UUID(line["ingredient_id"]),
                )
            )
        return Recipe(
            name=row["name"],
            instructions=row["instructions"] or "",
            ingredients=ingredients,
            description=row["description"],
            source_url=row["source_url"],
            recipe_id=recipe_id,
        )


class _SqliteMealPlanDao:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def insert(self, meal_plan: MealPlan) -> MealPlan:
        self._insert_row(meal_plan)
        self._replace_recipes(meal_plan)
        self._conn.commit()
        return meal_plan

    def find_by_id(self, meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
        row = self._conn.execute(
            "SELECT * FROM meal_plans WHERE id = ?",
            (_uuid_str(meal_plan_id),),
        ).fetchone()
        if not row:
            return None
        return self._from_row(row)

    def find_all(self) -> List[MealPlan]:
        rows = self._conn.execute("SELECT * FROM meal_plans ORDER BY name").fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, meal_plan: MealPlan) -> Optional[MealPlan]:
        cursor = self._conn.execute(
            "UPDATE meal_plans SET name = ?, description = ? WHERE id = ?",
            (
                meal_plan.name,
                meal_plan.description or "",
                _uuid_str(meal_plan.meal_plan_id),
            ),
        )
        if cursor.rowcount == 0:
            self._conn.commit()
            return None
        self._conn.execute(
            "DELETE FROM meal_plan_recipes WHERE meal_plan_id = ?",
            (_uuid_str(meal_plan.meal_plan_id),),
        )
        self._replace_recipes(meal_plan)
        self._conn.commit()
        return meal_plan

    def delete(self, meal_plan_id: uuid.UUID) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM meal_plans WHERE id = ?",
            (_uuid_str(meal_plan_id),),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def _insert_row(self, meal_plan: MealPlan) -> None:
        self._conn.execute(
            "INSERT INTO meal_plans (id, name, description) VALUES (?, ?, ?)",
            (
                _uuid_str(meal_plan.meal_plan_id),
                meal_plan.name,
                meal_plan.description or "",
            ),
        )

    def _replace_recipes(self, meal_plan: MealPlan) -> None:
        for entry in meal_plan.recipes or []:
            rid = entry.get("recipe_id") or entry.get("id")
            if rid is None:
                continue
            self._conn.execute(
                """
                INSERT INTO meal_plan_recipes (meal_plan_id, recipe_id, count)
                VALUES (?, ?, ?)
                """,
                (
                    _uuid_str(meal_plan.meal_plan_id),
                    _uuid_str(
                        rid if isinstance(rid, uuid.UUID) else uuid.UUID(str(rid))
                    ),
                    float(entry.get("count", 1.0)),
                ),
            )

    def _from_row(self, row: sqlite3.Row) -> MealPlan:
        meal_plan_id = uuid.UUID(row["id"])
        link_rows = self._conn.execute(
            """
            SELECT recipe_id, count FROM meal_plan_recipes
            WHERE meal_plan_id = ?
            """,
            (_uuid_str(meal_plan_id),),
        ).fetchall()
        recipes = [
            {"recipe_id": uuid.UUID(link["recipe_id"]), "count": float(link["count"])}
            for link in link_rows
        ]
        return MealPlan(
            name=row["name"],
            description=row["description"] or "",
            recipes=recipes,
            meal_plan_id=meal_plan_id,
        )


class _SqliteShoppingListDao:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def insert(self, shopping_list: ShoppingList) -> ShoppingList:
        self._insert_row(shopping_list)
        self._replace_items(shopping_list)
        self._conn.commit()
        return shopping_list

    def find_by_id(self, shopping_list_id: uuid.UUID) -> Optional[ShoppingList]:
        row = self._conn.execute(
            "SELECT * FROM shopping_lists WHERE id = ?",
            (_uuid_str(shopping_list_id),),
        ).fetchone()
        if not row:
            return None
        return self._from_row(row)

    def find_all(self) -> List[ShoppingList]:
        rows = self._conn.execute(
            "SELECT * FROM shopping_lists ORDER BY name"
        ).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, shopping_list: ShoppingList) -> Optional[ShoppingList]:
        cursor = self._conn.execute(
            "UPDATE shopping_lists SET name = ?, meal_plan_id = ? WHERE id = ?",
            (
                shopping_list.name,
                (
                    _uuid_str(shopping_list.meal_plan_id)
                    if shopping_list.meal_plan_id
                    else None
                ),
                _uuid_str(shopping_list.id),
            ),
        )
        if cursor.rowcount == 0:
            self._conn.commit()
            return None
        self._conn.execute(
            "DELETE FROM shopping_list_items WHERE shopping_list_id = ?",
            (_uuid_str(shopping_list.id),),
        )
        self._replace_items(shopping_list)
        self._conn.commit()
        return shopping_list

    def delete(self, shopping_list_id: uuid.UUID) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM shopping_lists WHERE id = ?",
            (_uuid_str(shopping_list_id),),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def _insert_row(self, shopping_list: ShoppingList) -> None:
        meal_plan_id = (
            _uuid_str(shopping_list.meal_plan_id)
            if shopping_list.meal_plan_id
            else None
        )
        self._conn.execute(
            "INSERT INTO shopping_lists (id, name, meal_plan_id) VALUES (?, ?, ?)",
            (_uuid_str(shopping_list.id), shopping_list.name, meal_plan_id),
        )

    def _replace_items(self, shopping_list: ShoppingList) -> None:
        for position, item in enumerate(shopping_list.items or []):
            self._conn.execute(
                """
                INSERT INTO shopping_list_items (
                    shopping_list_id, position, name, quantity, unit,
                    purchased, location, location_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _uuid_str(shopping_list.id),
                    position,
                    item.name,
                    _qty_dump(item.quantity),
                    item.unit or "",
                    1 if item.purchased else 0,
                    item.location,
                    item.location_id,
                ),
            )

    def _from_row(self, row: sqlite3.Row) -> ShoppingList:
        list_id = uuid.UUID(row["id"])
        item_rows = self._conn.execute(
            """
            SELECT name, quantity, unit, purchased, location, location_id
            FROM shopping_list_items
            WHERE shopping_list_id = ?
            ORDER BY position
            """,
            (_uuid_str(list_id),),
        ).fetchall()
        items = [
            ShoppingListItem(
                name=item["name"],
                quantity=_qty_load(item["quantity"]),
                unit=item["unit"] or "",
                purchased=bool(item["purchased"]),
                location=item["location"],
                location_id=item["location_id"],
            )
            for item in item_rows
        ]
        meal_plan_id = uuid.UUID(row["meal_plan_id"]) if row["meal_plan_id"] else None
        return ShoppingList(
            name=row["name"],
            items=items,
            id=list_id,
            meal_plan_id=meal_plan_id,
        )


class SqliteDao:
    """MealPlannerDao backed by one sqlite3 connection."""

    def __init__(self, path: str):
        if path != ":memory:":
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._ensure_schema_version()
        self.ingredients = _SqliteIngredientDao(self._conn)
        self.recipes = _SqliteRecipeDao(self._conn)
        self.meal_plans = _SqliteMealPlanDao(self._conn)
        self.shopping_lists = _SqliteShoppingListDao(self._conn)

    def _ensure_schema_version(self) -> None:
        row = self._conn.execute("SELECT version FROM schema_version").fetchone()
        if row is None:
            self._conn.execute("INSERT INTO schema_version (version) VALUES (1)")
            self._conn.commit()

    def reset(self) -> None:
        """Truncate all application tables. Order respects foreign keys."""
        self._conn.executescript(
            """
            DELETE FROM shopping_list_items;
            DELETE FROM shopping_lists;
            DELETE FROM meal_plan_recipes;
            DELETE FROM meal_plans;
            DELETE FROM recipe_ingredients;
            DELETE FROM recipes;
            DELETE FROM ingredients;
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
