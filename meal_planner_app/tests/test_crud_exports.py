import meal_planner_app.crud as crud  # pylint: disable=consider-using-from-import

REQUIRED = [
    "get_dao",
    "create_recipe",
    "create_meal_plan",
    "generate_shopping_list",
    "create_master_ingredient",
    "DuplicateIngredientNameError",
]


def test_crud_reexports_public_names():
    for name in REQUIRED:
        assert hasattr(crud, name), name
