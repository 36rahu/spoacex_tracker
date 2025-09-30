from fastapi.testclient import TestClient
from unittest.mock import patch

from src.spacextracker.app import app

client = TestClient(app)


# launches API test cases
# ------------------------
def test_get_launches_success():
    with patch("src.spacextracker.app.get_launches") as mock_get:
        mock_get.return_value = [{"id": "1", "name": "Falcon 1"}]
        response = client.get("/launches")
        assert response.status_code == 200
        assert response.json() == [{"id": "1", "name": "Falcon 1"}]


def test_get_launches_db_error():
    with patch("src.spacextracker.app.get_launches") as mock_get:
        mock_get.side_effect = Exception("DB connection failed")
        response = client.get("/launches")
        assert response.status_code == 500
        assert "DB connection failed" in response.text


def test_get_launches_invalid_params():
    response = client.get("/launches?start_date=invalid-date")
    assert response.status_code == 422  # FastAPI validation error


def test_launches_valid_params_success():
    with patch("src.spacextracker.app.get_launches") as mock_get:
        mock_get.return_value = [{"id": "2"}]
        response = client.get(
            "/launches?start_date=2025-01-01&end_date=2025-01-31&rocket_name=Falcon"
        )
        assert response.status_code == 200
        assert response.json() == [{"id": "2"}]


def test_launches_start_date_only():
    response = client.get("/launches?start_date=2025-01-01")
    assert response.status_code == 422
    assert (
        "Both start_date and end_date must be provided together"
        in response.json()["detail"]
    )


def test_launches_end_date_only():
    response = client.get("/launches?end_date=2025-01-31")
    assert response.status_code == 422
    assert (
        "Both start_date and end_date must be provided together"
        in response.json()["detail"]
    )


def test_launches_start_after_end():
    response = client.get("/launches?start_date=2025-02-01&end_date=2025-01-31")
    assert response.status_code == 422
    assert "start_date must be before or equal to end_date" in response.json()["detail"]


def test_launches_rocket_name_too_short():
    response = client.get("/launches?rocket_name=A")
    assert response.status_code == 422


def test_launches_rocket_name_too_long():
    response = client.get("/launches?rocket_name=" + "A" * 51)
    assert response.status_code == 422


def test_launches_launchpad_too_short():
    response = client.get("/launches?launchpad=A")
    assert response.status_code == 422


# statistics API test cases
# ------------------------
def test_fetch_statistics_success():
    mock_stats = {
        "rocket_success_rates": {"Falcon 9": 98},
        "launchpad_totals": {"LC-39A": {"attempts": 10, "successes": 9}},
        "launch_frequency": {"monthly": [1, 2, 3], "yearly": [5, 10, 15]},
    }
    with patch("src.spacextracker.app.get_all_statistics") as mock_get:
        mock_get.return_value = mock_stats
        response = client.get("/statistics")
        assert response.status_code == 200
        assert response.json() == mock_stats


def test_fetch_statistics_generic_exception():
    with patch("src.spacextracker.app.get_all_statistics") as mock_get:
        mock_get.side_effect = Exception("Database error")
        response = client.get("/statistics")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
        assert "Database error" in response.json()["detail"]


# Export APIs test cases
# ------------------------
def test_download_launches_success():
    mock_launches = [{"id": "1", "name": "Falcon 9"}]

    with patch("src.spacextracker.app.get_launches", return_value=mock_launches):
        response = client.get("/launches/download")

        assert response.status_code == 200
        assert response.json() == mock_launches
        assert (
            response.headers["content-disposition"]
            == "attachment; filename=launches.json"
        )


def test_download_launches_exception():
    with patch("src.spacextracker.app.get_launches", side_effect=Exception("DB error")):
        response = client.get("/launches/download")
        assert response.status_code == 500
        assert "DB error" in response.json()["detail"]


def test_download_statistics_success():
    mock_stats = {
        "rocket_success_rates": {"Falcon 9": 98},
        "launchpad_totals": {"LC-39A": {"launch_attempts": 10, "launch_successes": 9}},
        "launch_frequency": {
            "monthly_launch_frequency": {},
            "yearly_launch_frequency": {},
        },
    }

    with patch("src.spacextracker.app.get_all_statistics", return_value=mock_stats):
        response = client.get("/statistics/download")
        assert response.status_code == 200
        assert response.json() == mock_stats
        assert (
            response.headers["content-disposition"]
            == "attachment; filename=statistics.json"
        )


def test_download_statistics_exception():
    with patch(
        "src.spacextracker.app.get_all_statistics", side_effect=Exception("API error")
    ):
        response = client.get("/statistics/download")
        assert response.status_code == 500
        assert "API error" in response.json()["detail"]
