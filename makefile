.PHONY: install run dev lint format test clean

PACKAGE := spacextracker

install:
	poetry install

setup-env:
	cp env_example .env

run:
	poetry run uvicorn spacextracker.app:app --reload --host 0.0.0.0 --port 8000

lint:
	poetry run ruff check src tests
	poetry run black --check src tests

lint-fix:
	poetry run ruff check src tests --fix

format:
	poetry run black src tests

test:
	PYTHONPATH=src poetry run pytest tests/ --disable-warnings -v

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

start-celery:
	cd src/spacextracker && \
	poetry run celery -A celery_app.celery worker -B --loglevel=info >> logs/celery.log 2>&1

clear-cache:
	# Flush all keys in Redis (dangerous in prod!)
	redis-cli FLUSHALL

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down