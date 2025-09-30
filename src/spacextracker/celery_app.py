import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Dict
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import timedelta

load_dotenv()

log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = RotatingFileHandler(
    "logs/celery.log", maxBytes=5*1024*1024, backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Get Celery logger
celery_logger = logging.getLogger("celery")
celery_logger.setLevel(logging.INFO)
celery_logger.addHandler(file_handler)


REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_FETCH_MINUTES: int = int(os.getenv("CELERY_FETCH_MINUTES", 5))


celery: Celery = Celery(
    "spacextracker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

import spacextracker.tasks  # noqa: F401 # Ensure tasks are registered

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-launches-every-5-minutes": {
            "task": "spacextracker.tasks.fetch_and_store_launches",
            "schedule": timedelta(minutes=CELERY_FETCH_MINUTES),
        }
    },
)
