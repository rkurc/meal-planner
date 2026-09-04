# Persistent SQLite storage (DAO)

**Date:** 2026-09-04  
**Status:** Approved for implementation  
**Branch:** `feat/persistent-sqlite-dao`

## Goal

Survive process restart with a single SQLite file. Persistence sits behind a DAO so Flask, domain models, and SQL never mix. A later Postgres adapter can implement the same protocols.

## Non-goals

- Auth, OpenAPI, recipe discovery, calendar, g↔kg conversion
- SQLAlchemy / ORM
- Master-ingredient **UI** CRUD (list can read the table; no new forms)
- Multiple gunicorn workers
- Alembic

## Layers

```
Flask (main.py)          HTTP / JSON / PDF
        ↓
crud.py                  domain objects, get-or-create ingredient,
                         search, shopping aggregation
        ↓
MealPlannerDao           nested entity DAOs (no SQL)
        ↓
SqliteDao                sqlite3 + schema (the only replaceable adapter)
```

- `models/` stay plain Python. They do not import `sqlite3`.
- Flask does not import `meal_planner_app.dao.sqlite`.
- The SQLite adapter does not import Flask or PDF code.
- `crud.py` does **not** re-declare `insert` / `find_by_id` / `find_all`. Those verbs live on the entity DAOs.

## DAO interface

Entity protocols use classic DAO names. They cannot be flattened onto one class (`insert` would collide), so `MealPlannerDao` **nests** them:

```python
class IngredientDao(Protocol):
    def insert(self, ingredient: MasterIngredient) -> MasterIngredient: ...
    def find_by_id(self, ingredient_id: uuid.UUID) -> Optional[MasterIngredient]: ...
    def find_by_name(self, name: str) -> Optional[MasterIngredient]: ...
    def find_all(self) -> List[MasterIngredient]: ...
    def update(self, ingredient: MasterIngredient) -> Optional[MasterIngredient]: ...
    def delete(self, ingredient_id: uuid.UUID) -> bool: ...

class RecipeDao(Protocol):
    def insert(self, recipe: Recipe) -> Recipe: ...
    def find_by_id(self, recipe_id: uuid.UUID) -> Optional[Recipe]: ...
    def find_all(self) -> List[Recipe]: ...
    def update(self, recipe: Recipe) -> Optional[Recipe]: ...
    def delete(self, recipe_id: uuid.UUID) -> bool: ...

class MealPlanDao(Protocol):
    def insert(self, meal_plan: MealPlan) -> MealPlan: ...
    def find_by_id(self, meal_plan_id: uuid.UUID) -> Optional[MealPlan]: ...
    def find_all(self) -> List[MealPlan]: ...
    def update(self, meal_plan: MealPlan) -> Optional[MealPlan]: ...
    def delete(self, meal_plan_id: uuid.UUID) -> bool: ...

class ShoppingListDao(Protocol):
    def insert(self, shopping_list: ShoppingList) -> ShoppingList: ...
    def find_by_id(self, shopping_list_id: uuid.UUID) -> Optional[ShoppingList]: ...
    def find_all(self) -> List[ShoppingList]: ...
    def update(self, shopping_list: ShoppingList) -> Optional[ShoppingList]: ...
    def delete(self, shopping_list_id: uuid.UUID) -> bool: ...

class MealPlannerDao(Protocol):
    ingredients: IngredientDao
    recipes: RecipeDao
    meal_plans: MealPlanDao
    shopping_lists: ShoppingListDao
    def reset(self) -> None: ...
    def close(self) -> None: ...
```

`insert` receives an already-built domain object (UUID already assigned). The DAO does not parse request JSON.

`Recipe.ingredients` line items must have `ingredient_id` set before `recipes.insert`. Resolving name → master row is **crud** (`get-or-create` by stripped name).

`delete` on an ingredient returns `False` if any recipe still uses it (`ON DELETE RESTRICT`).

Unknown id: `find_by_id` / `update` return `None`; `delete` returns `False`. SQLite operational errors propagate.

## Domain

- `MasterIngredient` — catalog row: `ingredient_id`, `name`, `default_unit`, `location`, `location_id`. No quantity.
- Existing `Ingredient` — recipe line: `name`, `quantity`, `unit`, `location`, `location_id`, plus optional `ingredient_id`.
- `Recipe`, `MealPlan`, `ShoppingList` unchanged aside from recipe lines carrying `ingredient_id`.

JSON API stays `{name, quantity, unit, location, location_id}` on recipe ingredients. No required frontend change.

## Schema (ingredients first)

File: `data/meal_planner.db` (gitignored). Override: `MEAL_PLANNER_DB`. Tests: `:memory:` (one connection on the DAO). `PRAGMA foreign_keys = ON`. `CREATE TABLE IF NOT EXISTS` on init. `schema_version = 1`.

- `ingredients` — id TEXT PK, name TEXT NOT NULL UNIQUE, default_unit TEXT, location, location_id
- `recipes` — id, name, description, instructions, source_url
- `recipe_ingredients` — recipe_id **ON DELETE CASCADE**, ingredient_id **ON DELETE RESTRICT**, position, quantity TEXT (JSON), unit TEXT (empty → use default_unit on read)
- `meal_plans` — id, name, description
- `meal_plan_recipes` — (meal_plan_id, recipe_id) PK, count REAL; both FKs **ON DELETE CASCADE**
- `shopping_lists` — id, name, meal_plan_id **ON DELETE SET NULL**
- `shopping_list_items` — shopping_list_id **ON DELETE CASCADE**, position, name, quantity JSON, unit, purchased, location, location_id (snapshot; not an FK to ingredients)

Quantity JSON preserves `1`, `"to taste"`, and `["1", "2"]`. Invalid JSON on read → treat as the raw string.

## crud.py

Public functions stay (`create_recipe`, `get_recipe`, `list_recipes`, `search_recipes`, `generate_shopping_list`, …). Internals:

- `get_dao()` / `set_dao()` — process-wide DAO. Default path from `MEAL_PLANNER_DB` or `data/meal_planner.db`.
- `create_recipe`: build `Recipe`; for each line get-or-create `MasterIngredient` by name (fill empty default_unit / location from the line, do not overwrite non-empty defaults); `dao.recipes.insert`.
- `search_recipes` / shopping generation: still Python over `list_recipes()` / `get_recipe()`.
- `list_unique_ingredient_names` / locations: from `dao.ingredients.find_all()`.
- `list_unique_units`: union of recipe-line units and master `default_unit`.
- `list_ingredients_summary`: master rows + usage_count from recipe links.
- `reset_recipes_db`: delete recipes (cascades links) then ingredients. Other resets delete their tables only. Prefer `dao.reset()` when tests want a full wipe.

## Seed / migrate

- `seed_database()` still resets then inserts (E2E `/api/test/seed-db`).
- New `seed_if_empty()`: no-op when `list_recipes()` is non-empty. Used by `start_and_seed.sh`.
- `migrate_legacy.seed_from_legacy` already skips when recipes exist.

## Docker / ops

- `ENV MEAL_PLANNER_DB=/app/data/meal_planner.db`
- Create `/app/data` owned by `appuser`
- gunicorn stays `-w 1`
- `.gitignore` / `.dockerignore`: `*.db`, `data/*.db`
- Extract: `sqlite3 data/meal_planner.db .dump`

## Tests

- pytest autouse fixture: `create_dao(":memory:")` + `crud.set_dao`
- Existing CRUD/API tests keep calling `crud.*`
- New `test_dao.py`: ingredient/recipe round-trip; ingredient delete restricted; tempfile reopen still has rows
- Docker: `pytest`, `black --check`, `pylint` 10.00
