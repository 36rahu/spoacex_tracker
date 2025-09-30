from collections import defaultdict
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from spacextracker.services.utils import to_datetime
from spacextracker.services.cache_service import redis_cache
from spacextracker.services.store_to_db import update_launches_in_db
from spacextracker.db import (
    launches_collection,
    rockets_collection,
    launchpads_collection,
    CACHE_TTL,
)
from spacextracker.logger import logger


@redis_cache(ttl=CACHE_TTL)
def get_launches(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    rocket_name: Optional[str] = None,
    success: Optional[bool] = None,
    launchpad: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch launches filtered by date, rocket, success, or launchpad.
    """
    try:
        # Only update DB if collection is empty
        if launches_collection.count_documents({}) == 0:
            update_launches_in_db()
        
        query: Dict[str, Any] = {}

        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = to_datetime(start_date)
            if end_date:
                query["date"]["$lte"] = to_datetime(end_date)

        if rocket_name:
            query["rocket.name"] = {"$regex": rocket_name, "$options": "i"}

        if success is not None:
            query["success"] = success

        if launchpad:
            query["launchpad.name"] = {"$regex": launchpad, "$options": "i"}

        launches: List[Dict[str, Any]] = list(
            launches_collection.find(query, {"_id": 0})
        )
        return launches

    except ValueError as e:
        logger.error(f"Invalid input in get_launches: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception:
        logger.exception("Unexpected error in get_launches")
        raise HTTPException(status_code=500, detail="Failed to fetch launches")


def get_launch_frequency() -> Dict[str, Dict[str, int]]:
    """
    Calculate monthly and yearly launch frequencies.
    """
    try:
        launches = list(launches_collection.find({}, {"_id": 0, "date": 1}))

        monthly_stats: Dict[str, int] = defaultdict(int)
        yearly_stats: Dict[int, int] = defaultdict(int)

        for launch in launches:
            launch_date = launch.get("date")
            if not launch_date:
                continue
            if isinstance(launch_date, str):
                launch_date = to_datetime(launch_date)

            year_month = launch_date.strftime("%Y-%m")
            year_only = launch_date.year

            monthly_stats[year_month] += 1
            yearly_stats[year_only] += 1

        return {
            "monthly_launch_frequency": dict(monthly_stats),
            "yearly_launch_frequency": dict(yearly_stats),
        }

    except ValueError as e:
        logger.error(f"Invalid date format in get_launch_frequency: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception:
        logger.exception("Unexpected error in get_launch_frequency")
        raise HTTPException(
            status_code=500, detail="Failed to calculate launch frequency"
        )


def get_rocket_success_rates() -> Dict[str, float]:
    """
    Fetch rocket success rates by rocket name.
    """
    try:
        rockets = list(
            rockets_collection.find({}, {"_id": 0, "name": 1, "success_rate_pct": 1})
        )
        return {
            rocket["name"]: rocket["success_rate_pct"]
            for rocket in rockets
            if rocket.get("success_rate_pct") is not None
        }
    except Exception:
        logger.exception("Unexpected error in get_rocket_success_rates")
        raise HTTPException(
            status_code=500, detail="Failed to fetch rocket success rates"
        )


def get_launchpad_totals() -> Dict[str, Dict[str, Any]]:
    """
    Fetch total launch attempts and successes per launch site.
    """
    try:
        launchpads = list(
            launchpads_collection.find(
                {},
                {
                    "_id": 0,
                    "name": 1,
                    "full_name": 1,
                    "launch_attempts": 1,
                    "launch_successes": 1,
                },
            )
        )

        return {
            lp["name"]: {
                "full_name": lp.get("full_name"),
                "launch_attempts": lp.get("launch_attempts", 0),
                "launch_successes": lp.get("launch_successes", 0),
            }
            for lp in launchpads
        }
    except Exception:
        logger.exception("Unexpected error in get_launchpad_totals")
        raise HTTPException(status_code=500, detail="Failed to fetch launchpad totals")


@redis_cache(ttl=CACHE_TTL)
def get_all_statistics() -> Dict[str, Any]:
    """
    Aggregate all launch statistics into one response.
    """
    try:
        return {
            "rocket_success_rates": get_rocket_success_rates(),
            "launchpad_totals": get_launchpad_totals(),
            "launch_frequency": get_launch_frequency(),
        }
    except Exception:
        logger.exception("Unexpected error in get_all_statistics")
        raise HTTPException(status_code=500, detail="Failed to aggregate statistics")
