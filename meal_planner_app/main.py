"""
Main Flask application file for the Meal Planner App.
Handles web routes, request processing, and rendering HTML templates.
Integrates with CRUD operations and other services.
"""

import re
import uuid  # Required for recipe_id conversion

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    Response,
    send_from_directory,
    jsonify,
)
from markupsafe import escape, Markup

from meal_planner_app import crud
from meal_planner_app.models.meal_plan import MealPlan
from meal_planner_app.models.recipe import Recipe
from meal_planner_app.services import generate_shopping_list_pdf
from dataclasses import asdict
from meal_planner_app.models.shopping_list import ShoppingList

app = Flask(__name__)


@app.template_filter("nl2br")
def nl2br(s):
    """Converts newlines in a string to HTML <br> tags."""
    if s:
        s = escape(s)
        return Markup(re.sub(r"\r\n|\r|\n", "<br>\n", s))
    return ""


def parse_ingredients_from_textarea(textarea_content: str) -> list[dict]:
    """
    Parses ingredient data from a textarea input.
    Each line is expected to be an ingredient.
    For MVP, the whole line is treated as the ingredient's name,
    with quantity and unit set to empty strings.

    Args:
        textarea_content: The string content from the textarea.

    Returns:
        A list of dictionaries, where each dictionary represents an ingredient
        formatted for use with `crud.create_recipe` or `crud.update_recipe`.
        Example: [{'name': '1 cup sugar', 'quantity': '', 'unit': ''}]
    """
    ingredients = []
    if textarea_content:
        lines = [line.strip() for line in textarea_content.splitlines() if line.strip()]
        for line in lines:
            # For MVP: treat the whole line as the name, quantity and unit are empty/default
            ingredients.append({"name": line, "quantity": "", "unit": ""})
    return ingredients


@app.route("/")
@app.route("/recipes")
def recipe_list():
    """Displays a list of all recipes, with optional search and filtering."""
    search_query = request.args.get("search_query", "").strip()
    filter_ingredient = request.args.get("filter_ingredient", "").strip()

    if search_query or filter_ingredient:
        recipes = crud.search_recipes(
            query=search_query, filter_ingredient=filter_ingredient
        )
    else:
        recipes = crud.list_recipes()
    return render_template(
        "recipe_list.html",
        recipes=recipes,
        search_query=search_query,
        filter_ingredient=filter_ingredient,
    )


@app.route("/recipes/new", methods=["GET", "POST"])
def new_recipe():
    """Handles the creation of a new recipe via a web form."""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")
        ingredients_text = request.form.get("ingredients", "")
        instructions = request.form.get("instructions", "")
        source_url = request.form.get("source_url", "")

        if not name or not instructions:  # Basic validation
            # Consider flashing a message here
            return (
                render_template(
                    "recipe_form.html",
                    error="Name and Instructions are required.",
                    **request.form,
                ),
                400,
            )

        ingredients_data = parse_ingredients_from_textarea(ingredients_text)

        crud.create_recipe(
            name=name,
            description=description,
            ingredients_data=ingredients_data,
            instructions=instructions,
            source_url=source_url,
        )
        return redirect(url_for("recipe_list"))
    return render_template(
        "recipe_form.html", recipe=None, form_action=url_for("new_recipe")
    )


@app.route("/recipes/<uuid:recipe_id>")
def recipe_detail(recipe_id: uuid.UUID):
    """Displays the details of a single recipe."""
    recipe = crud.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    return render_template("recipe_detail.html", recipe=recipe)


@app.route("/recipes/<uuid:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id: uuid.UUID):
    """Handles the editing of an existing recipe via a web form."""
    recipe = crud.get_recipe(recipe_id)
    if not recipe:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", recipe.description)
        ingredients_text = request.form.get("ingredients", "")
        instructions = request.form.get("instructions", recipe.instructions)
        source_url = request.form.get("source_url", recipe.source_url)

        if not name or not instructions:  # Basic validation
            # Consider flashing a message here
            return (
                render_template(
                    "recipe_form.html",
                    recipe=recipe,
                    error="Name and Instructions are required.",
                    form_action=url_for("edit_recipe", recipe_id=recipe_id),
                ),
                400,
            )

        ingredients_data = parse_ingredients_from_textarea(ingredients_text)

        crud.update_recipe(
            recipe_id=recipe_id,
            name=name,
            description=description,
            ingredients_data=ingredients_data,
            instructions=instructions,
            source_url=source_url,
        )
        return redirect(url_for("recipe_detail", recipe_id=recipe_id))

    # Pre-fill ingredients textarea for GET request
    ingredients_text = "\n".join([ing.name for ing in recipe.ingredients])
    return render_template(
        "recipe_form.html",
        recipe=recipe,
        ingredients_text=ingredients_text,
        form_action=url_for("edit_recipe", recipe_id=recipe_id),
    )


@app.route(
    "/recipes/<uuid:recipe_id>/delete", methods=["POST", "GET"]
)  # GET for simplicity now
def delete_recipe_route(recipe_id: uuid.UUID):
    """Handles the deletion of a recipe."""
    success = crud.delete_recipe(recipe_id)
    if not success:
        abort(404)  # Or flash a message
    return redirect(url_for("recipe_list"))


# --- Meal Plan Routes ---


@app.route("/meal-plans")
def meal_plan_list():
    """Displays a list of all meal plans."""
    meal_plans = crud.list_meal_plans()
    return render_template("meal_plan_list.html", meal_plans=meal_plans)


@app.route("/meal-plans/new", methods=["GET", "POST"])
def new_meal_plan():
    """Handles the creation of a new meal plan via a web form."""
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return (
                render_template(
                    "meal_plan_form.html",
                    error="Name is required.",
                    form_action=url_for("new_meal_plan"),
                ),
                400,
            )
        crud.create_meal_plan(name=name)
        return redirect(url_for("meal_plan_list"))
    return render_template(
        "meal_plan_form.html", form_action=url_for("new_meal_plan"), meal_plan=None
    )


@app.route("/meal-plans/<uuid:meal_plan_id>")
def meal_plan_detail(meal_plan_id: uuid.UUID):
    """Displays the details of a single meal plan, including its recipes."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)

    recipes_in_plan = [
        crud.get_recipe(recipe_id)
        for recipe_id in meal_plan.recipe_ids
        if crud.get_recipe(recipe_id)
    ]

    all_recipes = crud.list_recipes()
    available_recipes = [
        recipe for recipe in all_recipes if recipe.recipe_id not in meal_plan.recipe_ids
    ]

    return render_template(
        "meal_plan_detail.html",
        meal_plan=meal_plan,
        recipes_in_plan=recipes_in_plan,
        available_recipes=available_recipes,
    )


@app.route("/meal-plans/<uuid:meal_plan_id>/edit", methods=["GET", "POST"])
def edit_meal_plan_name(meal_plan_id: uuid.UUID):
    """Handles editing the name of a meal plan."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return (
                render_template(
                    "meal_plan_form.html",
                    meal_plan=meal_plan,
                    error="Name is required.",
                    form_action=url_for(
                        "edit_meal_plan_name", meal_plan_id=meal_plan_id
                    ),
                ),
                400,
            )
        crud.update_meal_plan(meal_plan_id, name=name)
        return redirect(url_for("meal_plan_detail", meal_plan_id=meal_plan_id))

    return render_template(
        "meal_plan_form.html",
        meal_plan=meal_plan,
        form_action=url_for("edit_meal_plan_name", meal_plan_id=meal_plan_id),
    )


@app.route(
    "/meal-plans/<uuid:meal_plan_id>/add-recipe/<uuid:recipe_id>",
    methods=["POST", "GET"],
)
def add_recipe_to_meal_plan_route(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID):
    """Route to add a recipe to a meal plan."""
    # Ensure recipe exists before trying to add
    recipe = crud.get_recipe(recipe_id)
    if not recipe:
        abort(404)  # Or flash a message "Recipe not found"

    updated_meal_plan = crud.add_recipe_to_meal_plan(meal_plan_id, recipe_id)
    if not updated_meal_plan:
        abort(404)  # Or flash a message "Meal plan not found"
    return redirect(url_for("meal_plan_detail", meal_plan_id=meal_plan_id))


@app.route(
    "/meal-plans/<uuid:meal_plan_id>/remove-recipe/<uuid:recipe_id>",
    methods=["POST", "GET"],
)
def remove_recipe_from_meal_plan_route(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID):
    """Route to remove a recipe from a meal plan."""
    updated_meal_plan = crud.remove_recipe_from_meal_plan(meal_plan_id, recipe_id)
    if not updated_meal_plan:
        abort(404)  # Or flash a message "Meal plan not found"
    return redirect(url_for("meal_plan_detail", meal_plan_id=meal_plan_id))


@app.route("/meal-plans/<uuid:meal_plan_id>/delete", methods=["POST", "GET"])
def delete_meal_plan_route(meal_plan_id: uuid.UUID):
    """Route to delete a meal plan."""
    success = crud.delete_meal_plan(meal_plan_id)
    if not success:
        abort(404)  # Or flash a message
    return redirect(url_for("meal_plan_list"))


@app.route("/meal-plans/<uuid:meal_plan_id>/shopping-list")
def shopping_list_detail_route(meal_plan_id: uuid.UUID):
    """Displays the aggregated shopping list for a meal plan."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)

    shopping_list_items = crud.generate_shopping_list(meal_plan_id)
    # generate_shopping_list itself returns None if plan not found, but we check above.
    # It will return [] if plan exists but has no ingredients.

    return render_template(
        "shopping_list_detail.html",
        meal_plan_name=meal_plan.name,
        shopping_list=shopping_list_items,
        meal_plan_id=meal_plan_id,
    )


@app.route("/meal-plans/<uuid:meal_plan_id>/shopping-list/pdf")
def download_shopping_list_pdf(meal_plan_id: uuid.UUID):
    """Generates and serves a PDF of the shopping list for a meal plan."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)

    shopping_list_items = crud.generate_shopping_list(meal_plan_id)
    if (
        shopping_list_items is None
    ):  # Should not happen if meal_plan exists, but good practice
        # This case implies meal_plan was found, but generate_shopping_list failed
        # internally (e.g. if it could return None for other reasons)
        # However, our current generate_shopping_list returns [] for an existing
        # plan with no items.
        return redirect(
            url_for("shopping_list_detail_route", meal_plan_id=meal_plan_id)
        )

    pdf_bytes = generate_shopping_list_pdf(meal_plan.name, shopping_list_items)

    response = Response(pdf_bytes, mimetype="application/pdf")
    filename = f"shopping_list_{meal_plan.name.replace(' ', '_').lower()}.pdf"
    disposition = f'attachment; filename="{filename}"'
    response.headers["Content-Disposition"] = disposition

    return response


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
            {"name": ing.name, "quantity": ing.quantity, "unit": ing.unit}
            for ing in recipe.ingredients
        ],
    }


def _meal_plan_to_dict(meal_plan: MealPlan) -> dict:
    """Serializes a MealPlan object to a dictionary."""
    return {
        "id": str(meal_plan.meal_plan_id),
        "name": meal_plan.name,
        "description": meal_plan.description,
        "recipe_ids": [str(rid) for rid in meal_plan.recipe_ids],
    }


@app.route("/api/recipes", methods=["GET"])
def api_get_recipes():
    """API endpoint to get a list of all recipes."""
    recipes = crud.list_recipes()
    return jsonify([_recipe_to_dict(recipe) for recipe in recipes])


@app.route("/api/recipes", methods=["POST"])
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


@app.route("/api/meal-plans", methods=["GET"])
def api_get_meal_plans():
    """API endpoint to get a list of all meal plans."""
    meal_plans = crud.list_meal_plans()
    return jsonify([_meal_plan_to_dict(mp) for mp in meal_plans])


@app.route("/api/meal-plans", methods=["POST"])
def api_create_meal_plan():
    """API endpoint to create a new meal plan."""
    data = request.get_json()
    if not data or not data.get("name"):
        abort(400, description="Name is required.")

    name = data["name"]
    description = data.get("description", "")
    recipe_ids_str = data.get("recipe_ids", [])
    recipe_ids = [uuid.UUID(rid) for rid in recipe_ids_str]

    created_meal_plan = crud.create_meal_plan(
        name, description=description, recipe_ids=recipe_ids
    )
    return jsonify(_meal_plan_to_dict(created_meal_plan)), 201


@app.route("/api/meal-plans/<uuid:meal_plan_id>", methods=["GET"])
def api_get_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to get a single meal plan by its ID."""
    meal_plan = crud.get_meal_plan(meal_plan_id)
    if not meal_plan:
        abort(404)
    return jsonify(_meal_plan_to_dict(meal_plan))


@app.route("/api/meal-plans/<uuid:meal_plan_id>", methods=["PUT"])
def api_update_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to update an existing meal plan."""
    data = request.get_json()
    if not data:
        abort(400)

    name = data.get("name")
    description = data.get("description")
    recipe_ids_str = data.get("recipe_ids")
    recipe_ids = (
        [uuid.UUID(rid) for rid in recipe_ids_str]
        if recipe_ids_str is not None
        else None
    )

    updated_meal_plan = crud.update_meal_plan(
        meal_plan_id, name=name, description=description, recipe_ids=recipe_ids
    )
    if not updated_meal_plan:
        abort(404)
    return jsonify(_meal_plan_to_dict(updated_meal_plan))


@app.route("/api/meal-plans/<uuid:meal_plan_id>", methods=["DELETE"])
def api_delete_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to delete a meal plan."""
    if not crud.delete_meal_plan(meal_plan_id):
        abort(404)
    return "", 204


@app.route("/api/meal-plans/<uuid:meal_plan_id>/recipes", methods=["POST"])
def api_add_recipe_to_meal_plan(meal_plan_id: uuid.UUID):
    """API endpoint to add a recipe to a meal plan."""
    data = request.get_json()
    if not data or not data.get("recipe_id"):
        abort(400, description="recipe_id is required.")

    recipe_id = uuid.UUID(data["recipe_id"])
    meal_plan = crud.add_recipe_to_meal_plan(meal_plan_id, recipe_id)
    if not meal_plan:
        abort(404, description="Meal plan or recipe not found.")
    return jsonify(_meal_plan_to_dict(meal_plan))


@app.route(
    "/api/meal-plans/<uuid:meal_plan_id>/recipes/<uuid:recipe_id>", methods=["DELETE"]
)
def api_remove_recipe_from_meal_plan(meal_plan_id: uuid.UUID, recipe_id: uuid.UUID):
    """API endpoint to remove a recipe from a meal plan."""
    meal_plan = crud.remove_recipe_from_meal_plan(meal_plan_id, recipe_id)
    if not meal_plan:
        abort(404, description="Meal plan not found.")
    return jsonify(_meal_plan_to_dict(meal_plan))


@app.route("/api/meal-plans/<uuid:meal_plan_id>/shopping-list", methods=["GET"])
def api_get_shopping_list(meal_plan_id: uuid.UUID):
    """API endpoint to generate a shopping list for a meal plan."""
    shopping_list = crud.generate_shopping_list(meal_plan_id)
    if shopping_list is None:
        abort(404, description="Meal plan not found.")
    return jsonify(shopping_list)


# --- Shopping List API Routes ---


def _shopping_list_to_dict(shopping_list: ShoppingList) -> dict:
    """Serializes a ShoppingList object to a dictionary."""
    sl_dict = asdict(shopping_list)
    sl_dict["id"] = str(sl_dict["id"])
    sl_dict["meal_plan_id"] = str(sl_dict["meal_plan_id"])
    return sl_dict


@app.route("/api/shopping-lists", methods=["POST"])
def api_create_shopping_list():
    """API endpoint to create a new shopping list from a meal plan."""
    data = request.get_json()
    if not data or not data.get("meal_plan_id"):
        abort(400, description="meal_plan_id is required.")

    try:
        meal_plan_id = uuid.UUID(data["meal_plan_id"])
    except ValueError:
        abort(400, description="Invalid meal_plan_id format.")

    shopping_list = crud.create_shopping_list(meal_plan_id)
    if not shopping_list:
        abort(404, description="Meal plan not found.")

    return jsonify(_shopping_list_to_dict(shopping_list)), 201


@app.route("/api/shopping-lists", methods=["GET"])
def api_list_shopping_lists():
    """API endpoint to get all saved shopping lists."""
    shopping_lists = crud.list_shopping_lists()
    return jsonify([_shopping_list_to_dict(sl) for sl in shopping_lists])


@app.route("/api/shopping-lists/<uuid:shopping_list_id>", methods=["GET"])
def api_get_single_shopping_list(shopping_list_id: uuid.UUID):
    """API endpoint to get a single shopping list by its ID."""
    shopping_list = crud.get_shopping_list(shopping_list_id)
    if not shopping_list:
        abort(404)
    return jsonify(_shopping_list_to_dict(shopping_list))


@app.route("/api/shopping-lists/<uuid:shopping_list_id>", methods=["PUT"])
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


@app.route("/api/shopping-lists/<uuid:shopping_list_id>", methods=["DELETE"])
def api_delete_shopping_list(shopping_list_id: uuid.UUID):
    """API endpoint to delete a shopping list."""
    if not crud.delete_shopping_list(shopping_list_id):
        abort(404)
    return "", 204


# --- React App Route ---
@app.route("/ui/")
@app.route("/ui/<path:path>")  # Catch-all for client-side routing
def serve_react_app(path=None):
    """Serves the React frontend application."""
    if path is None or "." not in path:
        return send_from_directory("static/react_app", "index.html")
    return send_from_directory("static/react_app", path)


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
    app.run(debug=True)
