from typing import Dict
from .celery_app import celery, celery_logger
from .services.store_to_db import update_launches_in_db
from .logger import logger


@celery.task
def fetch_and_store_launches() -> Dict[str, int]:
    """
    Fetch latest launches from SpaceX API and store them in MongoDB.

    Returns:
        Dict[str, int]: Number of processed launches under the key 'processed'.
    """
    try:
        celery_logger.info("Celery task 'fetch_and_store_launches' started")
        count = update_launches_in_db()
        celery_logger.info(
            f"Celery task 'fetch_and_store_launches' completed successfully, processed {count} launches"
        )
        return {"processed": count}
    except Exception as e:
        celery_logger.error(
            f"Celery task 'fetch_and_store_launches' failed: {e}", exc_info=True
        )
        raise
