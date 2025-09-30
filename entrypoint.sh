#!/bin/bash
set -e

if [ "$RUN_TYPE" = "celery" ]; then
    echo "Starting Celery worker..."
    celery -A spacextracker.celery_app.celery worker -B --loglevel=info
else
    echo "Starting FastAPI server..."
    uvicorn spacextracker.app:app --host 0.0.0.0 --port 8000
fi
