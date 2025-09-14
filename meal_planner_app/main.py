"""
This module contains the routes for the Meal Planner application.
It uses a Flask Blueprint to organize the routes.
"""

import re
import uuid
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    send_from_directory,
    jsonify,
)
from markupsafe import escape, Markup
from . import crud
from .models.recipe import Recipe

bp = Blueprint("main", __name__)


@bp.app_template_filter("nl2br")
def nl2br(s):
    """Converts newlines in a string to HTML <br> tags."""
    if s:
        s = escape(s)
        return Markup(re.sub(r"\r\n|\r|\n", "<br>\n", s))
    return ""


def parse_ingredients_from_textarea(textarea_content: str) -> list[dict]:
    """
    Parses ingredient data from a textarea input.
    """
    ingredients = []
    if textarea_content:
        lines = [line.strip() for line in textarea_content.splitlines() if line.strip()]
        for line in lines:
            ingredients.append({"name": line, "quantity": "", "unit": ""})
    return ingredients


@bp.route("/")
@bp.route("/recipes")
def recipe_list():
    """Displays a list of all recipes."""
    recipes = crud.list_recipes()
    return render_template("recipe_list.html", recipes=recipes)


@bp.route("/recipes/new", methods=["GET", "POST"])
def new_recipe():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")
        ingredients_text = request.form.get("ingredients", "")
        instructions = request.form.get("instructions", "")
        source_url = request.form.get("source_url", "")

        if not name or not instructions:
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
        return redirect(url_for(".recipe_list"))
    return render_template(
        "recipe_form.html", recipe=None, form_action=url_for(".new_recipe")
    )


@bp.route("/recipes/<uuid:recipe_id>")
def recipe_detail(recipe_id: uuid.UUID):
    recipe = crud.get_recipe(str(recipe_id))
    if not recipe:
        abort(404)
    return render_template("recipe_detail.html", recipe=recipe)


@bp.route("/recipes/<uuid:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id: uuid.UUID):
    recipe = crud.get_recipe(str(recipe_id))
    if not recipe:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", recipe.description)
        ingredients_text = request.form.get("ingredients", "")
        instructions = request.form.get("instructions", recipe.instructions)
        source_url = request.form.get("source_url", recipe.source_url)

        if not name or not instructions:
            return (
                render_template(
                    "recipe_form.html",
                    recipe=recipe,
                    error="Name and Instructions are required.",
                    form_action=url_for(".edit_recipe", recipe_id=recipe_id),
                ),
                400,
            )

        ingredients_data = parse_ingredients_from_textarea(ingredients_text)

        crud.update_recipe(
            recipe_id=str(recipe_id),
            name=name,
            description=description,
            ingredients_data=ingredients_data,
            instructions=instructions,
            source_url=source_url,
        )
        return redirect(url_for(".recipe_detail", recipe_id=recipe_id))

    ingredients_text = "\n".join([ing.name for ing in recipe.ingredients])
    return render_template(
        "recipe_form.html",
        recipe=recipe,
        ingredients_text=ingredients_text,
        form_action=url_for(".edit_recipe", recipe_id=recipe_id),
    )


@bp.route("/recipes/<uuid:recipe_id>/delete", methods=["POST", "GET"])
def delete_recipe_route(recipe_id: uuid.UUID):
    crud.delete_recipe(str(recipe_id))
    return redirect(url_for(".recipe_list"))


@bp.route("/meal-plans")
def meal_plan_list():
    meal_plans = crud.list_meal_plans()
    return render_template("meal_plan_list.html", meal_plans=meal_plans)


@bp.route("/meal-plans/new", methods=["GET", "POST"])
def new_meal_plan():
    if request.method == "POST":
        name = request.form.get("name")
        crud.create_meal_plan(name=name)
        return redirect(url_for(".meal_plan_list"))
    return render_template(
        "meal_plan_form.html", form_action=url_for(".new_meal_plan"), meal_plan=None
    )


@bp.route("/meal-plans/<uuid:meal_plan_id>")
def meal_plan_detail(meal_plan_id: uuid.UUID):
    meal_plan = crud.get_meal_plan(str(meal_plan_id))
    if not meal_plan:
        abort(404)
    return render_template("meal_plan_detail.html", meal_plan=meal_plan)


@bp.route("/api/recipes", methods=["GET"])
def api_get_recipes():
    recipes = crud.list_recipes()
    return jsonify([_recipe_to_dict(recipe) for recipe in recipes])


def _recipe_to_dict(recipe: Recipe) -> dict:
    return {
        "id": str(recipe.id),
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "source_url": recipe.source_url,
        "ingredients": [
            {"name": ing.name, "quantity": ing.quantity, "unit": ing.unit}
            for ing in recipe.ingredients
        ],
    }


# --- React App Route ---
@bp.route("/ui/")
@bp.route("/ui/<path:path>")
def serve_react_app(path=None):
    return send_from_directory("static/react_app", path or "index.html")
