import meal_planner_app.crud as crud  # pylint: disable=consider-using-from-import

def test_crud_reexports_public_names():
    assert crud.__all__
    for name in crud.__all__:
        assert hasattr(crud, name), name
