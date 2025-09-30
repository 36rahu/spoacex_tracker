import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from requests.exceptions import HTTPError

from src.spacextracker.services import spacex_data


def test_get_json_from_api_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status.return_value = None

    with patch(
        "src.spacextracker.services.spacex_data.requests.get",
        return_value=mock_response,
    ) as mock_get:
        result = spacex_data.get_json_from_api("rockets")
        assert result == {"key": "value"}
        mock_get.assert_called_once_with(
            "https://api.spacexdata.com/v4/rockets", timeout=10
        )


def test_get_json_from_api_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")

    with patch(
        "src.spacextracker.services.spacex_data.requests.get",
        return_value=mock_response,
    ):
        with pytest.raises(HTTPError):
            spacex_data.get_json_from_api("rockets")


def test_get_rockets_from_api():
    rockets_mock = [
        {
            "id": "1",
            "name": "Falcon 9",
            "type": "rocket",
            "description": "desc",
            "active": True,
            "cost_per_launch": 50000000,
            "success_rate_pct": 98,
            "first_flight": "2010-06-04",
            "country": "USA",
            "company": "SpaceX",
            "wikipedia": "link",
        }
    ]

    with patch(
        "src.spacextracker.services.spacex_data.get_json_from_api",
        return_value=rockets_mock,
    ):
        result = spacex_data.get_rockets_from_api()
        assert len(result) == 1
        assert result[0]["name"] == "Falcon 9"


def test_get_launchpads_from_api():
    launchpads_mock = [
        {
            "id": "lp1",
            "name": "LC-39A",
            "full_name": "Kennedy Space Center LC-39A",
            "locality": "Florida",
            "region": "USA",
            "status": "active",
            "launch_attempts": 10,
            "launch_successes": 9,
            "details": "details",
            "images": {"large": ["img1"]},
            "rockets": ["r1"],
            "launches": ["l1"],
        }
    ]

    with patch(
        "src.spacextracker.services.spacex_data.get_json_from_api",
        return_value=launchpads_mock,
    ):
        result = spacex_data.get_launchpads_from_api()
        assert len(result) == 1
        assert result[0]["name"] == "LC-39A"
        assert result[0]["images"] == ["img1"]


def test_get_data_from_api():
    rockets_mock = [{"id": "r1", "name": "Falcon 9", "success_rate_pct": 98}]
    launchpads_mock = [
        {
            "id": "lp1",
            "name": "LC-39A",
            "full_name": "KSC LC-39A",
            "launch_attempts": 10,
            "launch_successes": 9,
        }
    ]
    launches_mock = [
        {
            "id": "l1",
            "name": "Test Launch",
            "success": True,
            "date_utc": "2025-09-30T12:00:00Z",
            "details": "details",
            "rocket": "r1",
            "launchpad": "lp1",
            "links": {
                "patch": {"small": "img"},
                "webcast": "webcast",
                "article": "article",
                "wikipedia": "wiki",
            },
        }
    ]

    with patch(
        "src.spacextracker.services.spacex_data.get_rockets_from_api",
        return_value=rockets_mock,
    ), patch(
        "src.spacextracker.services.spacex_data.get_launchpads_from_api",
        return_value=launchpads_mock,
    ), patch(
        "src.spacextracker.services.spacex_data.get_json_from_api",
        return_value=launches_mock,
    ):

        launches, rockets_data, launchpads_data = spacex_data.get_data_from_api()

        assert len(launches) == 1
        assert launches[0]["rocket"]["name"] == "Falcon 9"
        assert launches[0]["launchpad"]["name"] == "LC-39A"
        assert launches[0]["date"] == datetime(2025, 9, 30, 12, 0, tzinfo=timezone.utc)
        assert rockets_data == rockets_mock
        assert launchpads_data == launchpads_mock
