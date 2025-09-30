import pytest
from unittest.mock import patch
from datetime import datetime
from fastapi import HTTPException

from src.spacextracker.services import data_access


def test_get_launches_success_no_cache():
    mock_data = [{"rocket": {"name": "Falcon 9"}, "success": True}]

    # Patch redis_client used inside the decorator
    with patch(
        "src.spacextracker.services.data_access.launches_collection"
    ) as mock_col:
        mock_col.find.return_value = mock_data
        result = data_access.get_launches.__wrapped__()
        assert result == mock_data
        mock_col.find.assert_called_once()


def test_get_launches_db_exception():
    with patch(
        "src.spacextracker.services.data_access.launches_collection"
    ) as mock_col:
        mock_col.find.side_effect = Exception("MongoDB down")
        with pytest.raises(HTTPException) as exc:
            data_access.get_launches.__wrapped__()
        assert exc.value.status_code == 500
        assert "Failed to fetch launches" in exc.value.detail


def test_get_launch_frequency_success():
    mock_launches = [
        {"date": datetime(2025, 1, 1)},
        {"date": datetime(2025, 1, 2)},
        {"date": datetime(2025, 2, 1)},
    ]
    with patch(
        "src.spacextracker.services.data_access.launches_collection"
    ) as mock_col, patch(
        "src.spacextracker.services.data_access.to_datetime", side_effect=lambda x: x
    ):
        mock_col.find.return_value = mock_launches
        result = data_access.get_launch_frequency()
        assert "monthly_launch_frequency" in result
        assert "yearly_launch_frequency" in result
        assert result["monthly_launch_frequency"]["2025-01"] == 2
        assert result["monthly_launch_frequency"]["2025-02"] == 1


def test_get_launch_frequency_exception():
    with patch(
        "src.spacextracker.services.data_access.launches_collection"
    ) as mock_col:
        mock_col.find.side_effect = Exception("MongoDB down")
        with pytest.raises(HTTPException) as exc:
            data_access.get_launch_frequency()
        assert exc.value.status_code == 500


def test_get_rocket_success_rates_success():
    mock_rockets = [
        {"name": "Falcon 9", "success_rate_pct": 98},
        {"name": "Falcon Heavy", "success_rate_pct": 100},
    ]
    with patch("src.spacextracker.services.data_access.rockets_collection") as mock_col:
        mock_col.find.return_value = mock_rockets
        result = data_access.get_rocket_success_rates()
        assert result == {"Falcon 9": 98, "Falcon Heavy": 100}


def test_get_rocket_success_rates_exception():
    with patch("src.spacextracker.services.data_access.rockets_collection") as mock_col:
        mock_col.find.side_effect = Exception("MongoDB down")
        with pytest.raises(HTTPException):
            data_access.get_rocket_success_rates()


def test_get_launchpad_totals_success():
    mock_launchpads = [
        {
            "name": "LC-39A",
            "full_name": "Kennedy Space Center LC-39A",
            "launch_attempts": 10,
            "launch_successes": 9,
        }
    ]
    with patch(
        "src.spacextracker.services.data_access.launchpads_collection"
    ) as mock_col:
        mock_col.find.return_value = mock_launchpads
        result = data_access.get_launchpad_totals()
        assert result["LC-39A"]["launch_attempts"] == 10
        assert result["LC-39A"]["launch_successes"] == 9


def test_get_launchpad_totals_exception():
    with patch(
        "src.spacextracker.services.data_access.launchpads_collection"
    ) as mock_col:
        mock_col.find.side_effect = Exception("MongoDB down")
        with pytest.raises(HTTPException):
            data_access.get_launchpad_totals()


def test_get_all_statistics_success():
    with patch(
        "src.spacextracker.services.data_access.get_rocket_success_rates"
    ) as mock_rockets, patch(
        "src.spacextracker.services.data_access.get_launchpad_totals"
    ) as mock_launchpads, patch(
        "src.spacextracker.services.data_access.get_launch_frequency"
    ) as mock_frequency:
        mock_rockets.return_value = {"Falcon 9": 98}
        mock_launchpads.return_value = {
            "LC-39A": {"launch_attempts": 10, "launch_successes": 9}
        }
        mock_frequency.return_value = {
            "monthly_launch_frequency": {"2025-01": 2},
            "yearly_launch_frequency": {2025: 2},
        }

        result = data_access.get_all_statistics.__wrapped__()
        assert "rocket_success_rates" in result
        assert "launchpad_totals" in result
        assert "launch_frequency" in result


def test_get_all_statistics_exception():
    with patch(
        "src.spacextracker.services.data_access.get_rocket_success_rates"
    ) as mock_rockets:
        mock_rockets.side_effect = Exception("Unexpected error")
        with pytest.raises(HTTPException):
            data_access.get_all_statistics.__wrapped__()
