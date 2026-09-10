"""
Main Flask application file for the Meal Planner App.
Flask serves JSON API, PDF, and the React SPA at /ui/.
Integrates with CRUD operations and other services.
"""

import logging
import os
import re
import time
import uuid  # Required for recipe_id conversion

from urllib.parse import quote

from flask import (
    Flask,
    request,
    redirect,
    abort,
    Response,
    send_from_directory,
    jsonify,
)
from werkzeug.exceptions import HTTPException

from meal_planner_app import crud
from meal_planner_app.ingest.fetch import FetchError, fetch_page
from meal_planner_app.ingest.llm_client import LlmTimeoutError, LlmUnavailableError
from meal_planner_app.ingest.service import (
    ParseUnusableError,
    ParseValidationError,
    parse_recipe,
)
from meal_planner_app.seed_db import seed_database
from meal_planner_app.models.meal_plan import MealPlan, _normalize_recipe_entries
from meal_planner_app.models.recipe import Recipe
from meal_planner_app.pdf import FontUnavailableError, generate_shopping_list_pdf
from dataclasses import asdict
from meal_planner_app.models.shopping_list import ShoppingList

_LOG = logging.getLogger(__name__)


def handle_http_exception(exc):
    if request.path.startswith("/api/"):
        return jsonify({"error": exc.description or exc.name}), exc.code
    return exc


def remove_trailing_slash():
    """Normalize URLs: collapse multiple slashes and redirect trailing slash versions.
    e.g. /api/recipes/ -> /api/recipes

    We skip /ui paths so the React SPA and its client-side router aren't interfered with.
    """
    if request.path.startswith("/ui"):
        return None

    if request.path != "/":
        # Collapse //+ to single / and strip trailing /
        normalized = re.sub(r"/+", "/", request.path).rstrip("/")
        if not normalized:
            normalized = "/"
        if normalized != request.path:
            return redirect(normalized, code=308)

    return None


def root():
    return redirect("/ui/", code=302)


def _resolve_pdf_lang() -> str:
    """Whitelist lang query, else Accept-Language, else en."""
    raw = (request.args.get("lang") or "").strip().lower()
    if raw in ("en", "pl"):
        return raw
    return request.accept_languages.best_match(["en", "pl"]) or "en"


def _pdf_attachment_response(title: str, grouped_data: dict) -> Response:
    """Build and return a PDF download response for grouped shopping list data."""
    lang = _resolve_pdf_lang()
    try:
        pdf_bytes = generate_shopping_list_pdf(title, grouped_data, lang=lang)
    except FontUnavailableError:
        abort(500)
    # Ensure bytes for WSGI compatibility (gunicorn rejects bytearray/memoryview)
    if isinstance(pdf_bytes, (bytearray, memoryview)):
        pdf_bytes = bytes(pdf_bytes)
    response = Response(pdf_bytes, mimetype="application/pdf")
    ascii_name = "shopping_list.pdf"
    raw = f"shopping_list_{title}".replace("\r", "").replace("\n", "")
    star = quote(f"{raw}.pdf", safe="")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{star}"
    )
    return response


def download_shopping_list_pdf(meal_plan_id: uuid.UUID):
    """Generates and serves a PDF of the shopping list for a meal plan."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)

    generated = crud.generate_shopping_list(meal_plan_id)
    if generated is None:
        abort(404)
    return _pdf_attachment_response(meal_plan.name, generated or {})


def download_persisted_shopping_list_pdf(shopping_list_id: uuid.UUID):
    """Generates and serves a PDF for a persisted (user-editable) shopping list.
    This is the modern path used by React for downloading the current/edited list.
    Purchased items are excluded from the PDF (to-buy list).
    """
    shopping_list = crud.get_shopping_list(shopping_list_id)
    if not shopping_list:
        abort(404)

    grouped = crud.shopping_list_to_pdf_data(shopping_list)  # pylint: disable=no-member
    return _pdf_attachment_response(shopping_list.name, grouped)


# --- API Routes ---


def _recipe_to_dict(recipe: Recipe) -> dict:
    """Serializes a Recipe object to a dictionary."""
    return {
        "id": str(recipe.recipe_id),
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "source_url": recipe.source_url,
        "ingredients": [
            {
                "name": ing.name,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "location_id": getattr(ing, "location_id", None),
                "location": getattr(ing, "location", None),
            }
            for ing in recipe.ingredients
        ],
    }


def _meal_plan_to_dict(meal_plan: MealPlan, recipes_by_id=None) -> dict:
    """Serialize a meal plan as JSON with recipes: [{id, name, count}].

    Does not emit legacy `recipe_ids`. Writers still accept that key (see
    api_create_meal_plan / api_update_meal_plan) so old clients do not wipe plans.
    """
    if recipes_by_id is None:
        recipes_by_id = {
            str(recipe.recipe_id): recipe for recipe in crud.list_recipes()
        }
    recipes_out = []
    for e in meal_plan.recipes or []:
        rid = e.get("recipe_id") or e.get("id")
        if rid:
            recipe = recipes_by_id.get(str(rid))
            recipes_out.append(
                {
                    "id": str(rid),
                    "name": (recipe.name if recipe else ""),
                    "count": float(e.get("count", 1.0)),
                }
            )
    return {
        "id": str(meal_plan.meal_plan_id),
        "name": meal_plan.name,
        "description": meal_plan.description,
        "recipes": recipes_out,
    }


def api_get_recipes():
    """List recipes, optionally filtered with q / ingredient query params."""
    query = (request.args.get("q") or "").strip()
    ingredient = (request.args.get("ingredient") or "").strip()
    if query or ingredient:
        recipes = crud.search_recipes(query=query, filter_ingredient=ingredient)
    else:
        recipes = crud.list_recipes()
    return jsonify([_recipe_to_dict(recipe) for recipe in recipes])


def _master_ingredient_to_dict(ingredient) -> dict:
    """Serialize a catalog ingredient plus usage/recipes for JSON responses."""
    recipes_using = crud.get_recipes_for_ingredient(ingredient.name)
    return {
        "id": str(ingredient.ingredient_id),
        "name": ingredient.name,
        "default_unit": ingredient.default_unit or "",
        "unit": ingredient.default_unit or "",
        "location": ingredient.location or ingredient.location_id or "",
        "location_id": ingredient.location_id,
        "usage_count": len(recipes_using),
        "recipes": [
            {
                "id": str(recipe.recipe_id),
                "name": recipe.name,
                "description": recipe.description,
            }
            for recipe in recipes_using
        ],
    }


def api_get_ingredients():
    """Return catalog summaries [{id, name, usage_count, unit, location}, ...].

    POST on this same path still creates a master ingredient (REST collision).
    """
    summaries = crud.list_ingredients_summary()  # pylint: disable=no-member
    return jsonify(summaries)


def api_create_ingredient():
    """Create a master ingredient. Name is required and must be unique after trim."""
    data = request.get_json()
    if not data or not str(data.get("name") or "").strip():
        abort(400, description="`name` is required.")
    try:
        created = crud.create_master_ingredient(
            name=data["name"],
            default_unit=data.get("default_unit") or "",
            location=data.get("location"),
            location_id=data.get("location_id"),
        )
    except crud.DuplicateIngredientNameError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify(_master_ingredient_to_dict(created)), 201


def api_get_locations():
    """API endpoint to get unique location names for suggestions (resolved where possible)."""
    locs = crud.list_unique_locations()  # pylint: disable=no-member
    return jsonify(locs)


def api_get_units():
    """API endpoint to get unique units for suggestions (collected from recipe ingredients)."""
    units = crud.list_unique_units()  # pylint: disable=no-member
    return jsonify(units)


def api_get_ingredient(ingredient_id: uuid.UUID):
    """Return a single catalog ingredient by id, including usage and recipes."""
    ingredient = crud.get_master_ingredient(ingredient_id)
    if not ingredient:
        abort(404)
    return jsonify(_master_ingredient_to_dict(ingredient))


def api_update_ingredient(ingredient_id: uuid.UUID):
    """Update a catalog ingredient by id. Unique name is still enforced."""
    data = request.get_json()
    if not data:
        abort(400)
    if "name" in data and not str(data.get("name") or "").strip():
        abort(400, description="`name` is required.")
    try:
        updated = crud.update_master_ingredient(
            ingredient_id,
            name=data.get("name"),
            default_unit=data.get("default_unit") if "default_unit" in data else None,
            location=data.get("location") if "location" in data else None,
            location_id=data.get("location_id") if "location_id" in data else None,
        )
    except crud.DuplicateIngredientNameError as exc:
        return jsonify({"error": str(exc)}), 409
    except ValueError:
        abort(400, description="`name` is required.")
    if not updated:
        abort(404)
    return jsonify(_master_ingredient_to_dict(updated))


def api_delete_ingredient(ingredient_id: uuid.UUID):
    """Delete a catalog ingredient. 409 if recipes still reference it."""
    try:
        deleted = crud.delete_master_ingredient(ingredient_id)
    except crud.IngredientInUseError as exc:
        return (
            jsonify({"error": str(exc), "usage_count": exc.usage_count}),
            409,
        )
    if not deleted:
        abort(404)
    return "", 204


def api_create_recipe():
    """API endpoint to create a new recipe."""
    data = request.get_json()
    if not data or not data.get("name") or not data.get("instructions"):
        abort(400, description="`name` and `instructions` are required.")

    # crud.create_recipe expects ingredients_data to be a list of dicts
    # The client should send ingredients in the correct format, e.g.,
    # [{"name": "Flour", "quantity": 2, "unit": "cups"}]
    ingredients_data = data.get("ingredients", [])

    created_recipe = crud.create_recipe(
        name=data["name"],
        instructions=data["instructions"],
        description=data.get("description"),
        source_url=data.get("source_url"),
        ingredients_data=ingredients_data,
    )

    return jsonify(_recipe_to_dict(created_recipe)), 201


def api_parse_recipe():
    """Parse pasted text/HTML into a recipe draft. Does not persist."""
    data = request.get_json(silent=True) or {}
    started = time.monotonic()
    try:
        draft = parse_recipe(
            data.get("text"),
            source_url=data.get("source_url") or "",
            catalog_names=crud.list_unique_ingredient_names(),
        )
    except ParseValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except FetchError as exc:
        status = getattr(exc, "status_code", 400)
        _LOG.warning("recipe parse fetch %s: %s", exc.__class__.__name__, status)
        return jsonify({"error": str(exc)}), status
    except ParseUnusableError as exc:
        return jsonify({"error": str(exc)}), 422
    except LlmTimeoutError as exc:
        _LOG.warning("recipe parse timeout: %s", exc.__class__.__name__)
        return jsonify({"error": str(exc)}), 504
    except LlmUnavailableError as exc:
        _LOG.warning("recipe parse llm unavailable: %s", exc.__class__.__name__)
        return jsonify({"error": str(exc)}), 503
    elapsed_ms = int((time.monotonic() - started) * 1000)
    _LOG.info(
        "recipe parse ok parser=%s model=%s elapsed_ms=%s",
        draft.parser,
        draft.model,
        elapsed_ms,
    )
    return jsonify(draft.to_dict()), 200


def api_fetch_recipe_page():
    """Download a public recipe page as text. Does not persist or call the LLM."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or data.get("source_url") or "").strip()
    try:
        result = fetch_page(url)
    except FetchError as exc:
        status = getattr(exc, "status_code", 400)
        _LOG.warning("recipe fetch %s: %s", exc.__class__.__name__, status)
        return jsonify({"error": str(exc)}), status
    return (
        jsonify(
            {
                "text": result.text,
                "source_url": result.source_url,
                "content_type": result.content_type,
            }
        ),
        200,
    )


def api_get_recipe(recipe_id: uuid.UUID):
    """API endpoint to get a single recipe by its ID."""
    recipe = crud.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    return jsonify(_recipe_to_dict(recipe))


def api_update_recipe(recipe_id: uuid.UUID):
    """API endpoint to update an existing recipe."""
    data = request.get_json()
    if not data:
        abort(400)

    # Extract ingredients data if provided
    ingredients_data = data.get("ingredients")

    updated_recipe = crud.update_recipe(
        recipe_id=recipe_id,
        name=data.get("name"),
        description=data.get("description"),
        instructions=data.get("instructions"),
        source_url=data.get("source_url"),
        ingredients_data=ingredients_data,
    )

    if not updated_recipe:
        abort(404)
    return jsonify(_recipe_to_dict(updated_recipe))


def api_delete_recipe(recipe_id: uuid.UUID):
    """API endpoint to delete a recipe."""
    if not crud.delete_recipe(recipe_id):
        abort(404)
    return "", 204


def api_get_meal_plans():
    """API endpoint to get a list of all meal plans."""
    meal_plans = crud.list_meal_plans()
    recipes_by_id = {str(recipe.recipe_id): recipe for recipe in crud.list_recipes()}
    return jsonify([_meal_plan_to_dict(mp, recipes_by_id) for mp in meal_plans])


def api_create_meal_plan():
    """Create a meal plan.

    Preferred body: ``recipes`` as ``[{id, count}, ...]``.
    Still accepts legacy ``recipe_ids`` (list of uuid strings) when ``recipes``
    is absent so old clients do not persist empty plans.
    """
    data = request.get_json()
    if not data or not data.get("name"):
        abort(400, description="Name is required.")

    name = data["name"]
    description = data.get("description", "")

    recipes_input = data.get("recipes") or data.get("recipe_ids")
    recipes_arg = _normalize_recipe_entries(recipes_input)

    created_meal_plan = crud.create_meal_plan(  # pylint: disable=unexpected-keyword-arg
        name, description=description, recipes=recipes_arg
    )
    return jsonify(_meal_plan_to_dict(created_meal_plan)), 201


def api_get_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to get a single meal plan by its ID."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)
    return jsonify(_meal_plan_to_dict(meal_plan))


def api_update_meal_plan(meal_plan_id: uuid.UUID):
    """Update a meal plan.

    Preferred body: ``recipes`` as ``[{id, count}, ...]``.
    Still accepts legacy ``recipe_ids`` when ``recipes`` is absent so old
    clients do not wipe the plan's recipes. Omitting both leaves recipes unchanged.
    """
    data = request.get_json()
    if not data:
        abort(400)

    name = data.get("name")
    description = data.get("description")

    update_kwargs = {
        "name": name,
        "description": description,
    }
    if "recipes" in data or "recipe_ids" in data:
        recipes_input = data.get("recipes") or data.get("recipe_ids")
        update_kwargs["recipes"] = _normalize_recipe_entries(recipes_input)

    updated_meal_plan = crud.update_meal_plan(  # pylint: disable=unexpected-keyword-arg
        meal_plan_id,
        **update_kwargs,
    )
    if not updated_meal_plan:
        abort(404)
    return jsonify(_meal_plan_to_dict(updated_meal_plan))


def api_delete_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to delete a meal plan."""
    if not crud.delete_meal_plan(meal_plan_id):
        abort(404)
    return "", 204


def api_add_recipe_to_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to add a recipe to a meal plan."""
    data = request.get_json()
    if not data or not data.get("recipe_id"):
        abort(400, description="recipe_id is required.")

    recipe_id = uuid.UUID(data["recipe_id"])
    try:
        count = float(data.get("count", 1.0))
    except (TypeError, ValueError):
        abort(400, description="count must be a number.")
    meal_plan = crud.add_recipe_to_meal_plan(meal_plan_id, recipe_id, count=count)
    if not meal_plan:
        abort(404, description="Meal plan or recipe not found.")
    return jsonify(_meal_plan_to_dict(meal_plan))


def api_remove_recipe_from_meal_plan(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID):
    """API endpoint to remove a recipe from a meal plan."""
    meal_plan = crud.remove_recipe_from_meal_plan(meal_plan_id, recipe_id)
    if not meal_plan:
        abort(404, description="Meal plan not found.")
    return jsonify(_meal_plan_to_dict(meal_plan))


def api_get_shopping_list(meal_plan_id: uuid.UUID):
    """API endpoint to generate a shopping list for a meal plan."""
    shopping_list = crud.generate_shopping_list(meal_plan_id)
    if shopping_list is None:
        abort(404, description="Meal plan not found.")
    # Returns grouped dict {location_name: [items...]} for easy grouping by lokalizacje
    return jsonify(shopping_list)


# --- Shopping List API Routes ---


def _shopping_list_to_dict(shopping_list: ShoppingList) -> dict:
    """Serializes a ShoppingList object to a dictionary."""
    sl_dict = asdict(shopping_list)
    sl_dict["id"] = str(sl_dict["id"])
    mp_id = sl_dict.get("meal_plan_id")
    sl_dict["meal_plan_id"] = str(mp_id) if mp_id else None
    return sl_dict


def api_create_shopping_list():
    """API endpoint to create a new shopping list.
    Supports:
    - { "meal_plan_id": "..." }  (optionally with "name")
    - { "name": "My List" } for a new standalone empty shopping list.
    """
    data = request.get_json() or {}
    meal_plan_id_str = data.get("meal_plan_id")
    name = data.get("name")

    if meal_plan_id_str:
        try:
            meal_plan_id = uuid.UUID(meal_plan_id_str)
        except ValueError:
            abort(400, description="Invalid meal_plan_id format.")

        shopping_list = crud.create_shopping_list(meal_plan_id=meal_plan_id, name=name)
        if not shopping_list:
            abort(404, description="Meal plan not found.")
    else:
        # Standalone "new list" - name optional, defaults in crud
        shopping_list = crud.create_shopping_list(name=name)

    return jsonify(_shopping_list_to_dict(shopping_list)), 201


def api_list_shopping_lists():
    """API endpoint to get all saved shopping lists."""
    shopping_lists = crud.list_shopping_lists()
    return jsonify([_shopping_list_to_dict(sl) for sl in shopping_lists])


def api_get_single_shopping_list(shopping_list_id: uuid.UUID):
    """API endpoint to get a single shopping list by its ID."""
    shopping_list = crud.get_shopping_list(shopping_list_id)
    if not shopping_list:
        abort(404)
    return jsonify(_shopping_list_to_dict(shopping_list))


def api_update_shopping_list(shopping_list_id: uuid.UUID):
    """API endpoint to update an existing shopping list."""
    data = request.get_json()
    if not data:
        abort(400)

    # The crud function expects 'name' and 'items' as optional kwargs
    updated_list = crud.update_shopping_list(
        shopping_list_id, name=data.get("name"), items=data.get("items")
    )

    if not updated_list:
        abort(404)
    return jsonify(_shopping_list_to_dict(updated_list))


def api_delete_shopping_list(shopping_list_id: uuid.UUID):
    """API endpoint to delete a shopping list."""
    if not crud.delete_shopping_list(shopping_list_id):
        abort(404)
    return "", 204


# --- Test-only seed view. Registered by create_app when testing is on.
# Enabled via testing=True or TESTING=true env (gunicorn E2E). See seed_db.py:RECIPES_TO_SEED.
def api_seed_database():
    """Seeds the database. For testing/E2E purposes only."""
    seed_database()
    return jsonify({"message": "Database seeded successfully"}), 200


# --- React App Route ---
def serve_react_app(path=""):
    """Serves the React frontend application."""
    if not path or "." not in path:
        return send_from_directory("static/react_app", "index.html")
    return send_from_directory("static/react_app", path)


_URL_RULES = (
    ("/", root, None),
    (
        "/meal-plans/<uuid:meal_plan_id>/shopping-list/pdf",
        download_shopping_list_pdf,
        None,
    ),
    (
        "/shopping-lists/<uuid:shopping_list_id>/pdf",
        download_persisted_shopping_list_pdf,
        None,
    ),
    ("/api/recipes", api_get_recipes, ["GET"]),
    ("/api/ingredients", api_get_ingredients, ["GET"]),
    ("/api/ingredients", api_create_ingredient, ["POST"]),
    ("/api/locations", api_get_locations, ["GET"]),
    ("/api/units", api_get_units, ["GET"]),
    ("/api/ingredients/<uuid:ingredient_id>", api_get_ingredient, ["GET"]),
    ("/api/ingredients/<uuid:ingredient_id>", api_update_ingredient, ["PUT"]),
    ("/api/ingredients/<uuid:ingredient_id>", api_delete_ingredient, ["DELETE"]),
    ("/api/recipes", api_create_recipe, ["POST"]),
    ("/api/recipes/parse", api_parse_recipe, ["POST"]),
    ("/api/recipes/fetch", api_fetch_recipe_page, ["POST"]),
    ("/api/recipes/<uuid:recipe_id>", api_get_recipe, ["GET"]),
    ("/api/recipes/<uuid:recipe_id>", api_update_recipe, ["PUT"]),
    ("/api/recipes/<uuid:recipe_id>", api_delete_recipe, ["DELETE"]),
    ("/api/meal-plans", api_get_meal_plans, ["GET"]),
    ("/api/meal-plans", api_create_meal_plan, ["POST"]),
    ("/api/meal-plans/<uuid:meal_plan_id>", api_get_meal_plan, ["GET"]),
    ("/api/meal-plans/<uuid:meal_plan_id>", api_update_meal_plan, ["PUT"]),
    ("/api/meal-plans/<uuid:meal_plan_id>", api_delete_meal_plan, ["DELETE"]),
    (
        "/api/meal-plans/<uuid:meal_plan_id>/recipes",
        api_add_recipe_to_meal_plan,
        ["POST"],
    ),
    (
        "/api/meal-plans/<uuid:meal_plan_id>/recipes/<uuid:recipe_id>",
        api_remove_recipe_from_meal_plan,
        ["DELETE"],
    ),
    (
        "/api/meal-plans/<uuid:meal_plan_id>/shopping-list",
        api_get_shopping_list,
        ["GET"],
    ),
    ("/api/shopping-lists", api_create_shopping_list, ["POST"]),
    ("/api/shopping-lists", api_list_shopping_lists, ["GET"]),
    (
        "/api/shopping-lists/<uuid:shopping_list_id>",
        api_get_single_shopping_list,
        ["GET"],
    ),
    ("/api/shopping-lists/<uuid:shopping_list_id>", api_update_shopping_list, ["PUT"]),
    (
        "/api/shopping-lists/<uuid:shopping_list_id>",
        api_delete_shopping_list,
        ["DELETE"],
    ),
)


def _register_routes(flask_app):
    """Attach production view functions to *flask_app*."""
    for rule, view_func, methods in _URL_RULES:
        if methods is None:
            flask_app.add_url_rule(rule, view_func=view_func)
        else:
            flask_app.add_url_rule(rule, view_func=view_func, methods=methods)
    flask_app.add_url_rule(
        "/ui",
        defaults={"path": ""},
        view_func=serve_react_app,
        strict_slashes=False,
    )
    flask_app.add_url_rule(
        "/ui/",
        defaults={"path": ""},
        view_func=serve_react_app,
        strict_slashes=False,
    )
    flask_app.add_url_rule("/ui/<path:path>", view_func=serve_react_app)


def create_app(*, testing=False):
    """Build the Flask app. Seed route is registered only when testing."""
    flask_app = Flask(__name__)
    if testing or os.environ.get("TESTING", "").lower() in ("1", "true", "yes"):
        flask_app.config["TESTING"] = True

    flask_app.register_error_handler(HTTPException, handle_http_exception)
    flask_app.before_request(remove_trailing_slash)
    _register_routes(flask_app)

    if flask_app.config.get("TESTING"):
        flask_app.add_url_rule(
            "/api/test/seed-db",
            view_func=api_seed_database,
            methods=["POST"],
        )
    return flask_app


app = create_app()


if __name__ == "__main__":
    # Reset DB for fresh start during development, if desired
    # crud.reset_recipes_db()
    # Example:
    # crud.create_recipe("Spaghetti Bolognese", "Cook spaghetti. Make sauce.",
    # ingredients_data=[{'name': 'Spaghetti', 'quantity': '200', 'unit': 'g'},
    # {'name': 'Minced Beef', 'quantity': '500', 'unit': 'g'}])
    # crud.create_recipe("Simple Salad", "Mix greens and dressing.",
    # ingredients_data=[{'name': 'Lettuce', 'quantity': '1', 'unit': 'head'}])

    # crud.reset_meal_plans_db() # Optional: clear meal plans on start
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
