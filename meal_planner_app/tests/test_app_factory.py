from pathlib import Path

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


def test_dev_start_script_enables_seed_route():
    """Local E2E against start_and_seed.sh needs TESTING so seed-db is registered."""
    script = Path(__file__).resolve().parents[2] / "start_and_seed.sh"
    text = script.read_text(encoding="utf-8")
    assert "TESTING=true" in text
