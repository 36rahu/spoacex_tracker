from datetime import datetime
from typing import Any, Dict, List, Tuple
import requests
from spacextracker.logger import logger

API_BASE_URL = "https://api.spacexdata.com/v4/"


def get_json_from_api(endpoint: str) -> Any:
    """
    Fetch JSON data from a SpaceX API endpoint.
    """
    API_URL = f"{API_BASE_URL}{endpoint}"
    try:
        logger.info(f"Requesting SpaceX API: {API_URL}")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(
            f"Received {len(data) if isinstance(data, list) else '1'} records from {endpoint}"
        )
        return data
    except requests.RequestException as e:
        logger.error(f"Request error while fetching {endpoint}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching {endpoint}: {e}", exc_info=True)
        raise


def get_data_from_api() -> (
    Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]
):
    """
    Fetch launches with full rocket and launchpad info.
    """
    logger.info("Fetching rockets data")
    rockets_data = get_rockets_from_api()
    rockets: Dict[str, Dict[str, Any]] = {
        rocket["id"]: {
            "id": rocket["id"],
            "name": rocket["name"],
            "success_rate_pct": rocket.get("success_rate_pct"),
        }
        for rocket in rockets_data
    }

    logger.info("Fetching launchpads data")
    launchpads_data = get_launchpads_from_api()
    launchpads: Dict[str, Dict[str, Any]] = {
        lp["id"]: {
            "id": lp["id"],
            "name": lp["name"],
            "full_name": lp.get("full_name"),
            "launch_attempts": lp.get("launch_attempts"),
            "launch_successes": lp.get("launch_successes"),
        }
        for lp in launchpads_data
    }

    logger.info("Fetching launches data")
    launches_data = get_json_from_api("launches")
    launches: List[Dict[str, Any]] = []

    for launch in launches_data:
        launch_data: Dict[str, Any] = {
            "id": launch.get("id"),
            "name": launch.get("name", "Unknown"),
            "success": launch.get("success"),
            "date": datetime.fromisoformat(
                launch.get("date_utc").replace("Z", "+00:00")
            ),
            "details": launch.get("details"),
            "links": {
                "img": launch.get("links", {}).get("patch", {}).get("small"),
                "webcast": launch.get("links", {}).get("webcast"),
                "article": launch.get("links", {}).get("article"),
                "wikipedia": launch.get("links", {}).get("wikipedia"),
            },
            "rocket": rockets.get(launch.get("rocket"), {}),
            "launchpad": launchpads.get(launch.get("launchpad"), {}),
        }
        launches.append(launch_data)

    logger.info(f"Processed {len(launches)} launches")
    return launches, rockets_data, launchpads_data


def get_rockets_from_api() -> List[Dict[str, Any]]:
    """
    Fetch all rockets with key features.
    """
    data = get_json_from_api("rockets")
    rockets = [
        {
            "id": rocket.get("id"),
            "name": rocket.get("name"),
            "type": rocket.get("type"),
            "description": rocket.get("description"),
            "active": rocket.get("active"),
            "cost_per_launch": rocket.get("cost_per_launch"),
            "success_rate_pct": rocket.get("success_rate_pct"),
            "first_flight": rocket.get("first_flight"),
            "country": rocket.get("country"),
            "company": rocket.get("company"),
            "wikipedia": rocket.get("wikipedia"),
        }
        for rocket in data
    ]
    logger.info(f"Retrieved {len(rockets)} rockets from API")
    return rockets


def get_launchpads_from_api() -> List[Dict[str, Any]]:
    """
    Fetch all launchpads with key features.
    """
    data = get_json_from_api("launchpads")
    launchpads = [
        {
            "id": launchpad.get("id"),
            "name": launchpad.get("name"),
            "full_name": launchpad.get("full_name"),
            "locality": launchpad.get("locality"),
            "region": launchpad.get("region"),
            "status": launchpad.get("status"),
            "launch_attempts": launchpad.get("launch_attempts"),
            "launch_successes": launchpad.get("launch_successes"),
            "details": launchpad.get("details"),
            "images": launchpad.get("images", {}).get("large", []),
            "rockets": launchpad.get("rockets", []),
            "launches": launchpad.get("launches", []),
        }
        for launchpad in data
    ]
    logger.info(f"Retrieved {len(launchpads)} launchpads from API")
    return launchpads
