from meal_planner_app.main import create_app


def test_seed_route_absent_without_testing():
    app = create_app(testing=False)
    client = app.test_client()
    response = client.post("/api/test/seed-db")
    assert response.status_code == 404


def test_seed_route_present_when_testing():
    app = create_app(testing=True)
    client = app.test_client()
    response = client.post("/api/test/seed-db")
    assert response.status_code == 200
