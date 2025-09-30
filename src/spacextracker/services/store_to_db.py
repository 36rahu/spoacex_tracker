from spacextracker.services.spacex_data import get_data_from_api
from spacextracker.db import (
    launches_collection,
    rockets_collection,
    launchpads_collection,
)
from spacextracker.logger import logger


def update_launches_in_db() -> int:
    """
    Fetch the latest SpaceX launches, rockets, and launchpads data from the API
    and update the corresponding MongoDB collections. Uses upsert to insert or update.

    Returns:
        int: Number of launches updated/inserted.
    """
    try:
        logger.info("Starting update of SpaceX data in MongoDB")
        launches, rockets, launchpads = get_data_from_api()
        logger.info(
            f"Fetched {len(launches)} launches, {len(rockets)} rockets, {len(launchpads)} launchpads from API"
        )

        for launch in launches:
            launches_collection.update_one(
                {"_id": launch["id"]}, {"$set": launch}, upsert=True
            )

        for rocket in rockets:
            rockets_collection.update_one(
                {"_id": rocket["id"]}, {"$set": rocket}, upsert=True
            )

        for lp in launchpads:
            launchpads_collection.update_one(
                {"_id": lp["id"]}, {"$set": lp}, upsert=True
            )

        logger.info("SpaceX data update completed successfully")
        return len(launches)

    except Exception as e:
        logger.error(f"Error updating SpaceX data in MongoDB: {e}", exc_info=True)
        raise
