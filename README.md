# SpaceX Tracker

**SpaceX Tracker** is a FastAPI-based application that allows you to track SpaceX launches and statistics. It provides a REST API for fetching launch data, downloading JSON reports, and a simple web UI for visualization. Celery is used for background tasks such as fetching and storing SpaceX launch data in the database.

---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Commands](#docker-commands)
- [API Endpoints](#api-endpoints)
- [Celery Tasks](#celery-tasks)
- [Testing](#testing)
- [Development Tools](#development-tools)
- [License](#license)

---

## Features
- Fetch SpaceX launches with filters (date, rocket, launchpad, success)
- Fetch launch statistics
- Download launches and statistics as JSON files
- Simple web UI
- Background tasks for syncing SpaceX data using Celery
- Logging for API and Celery tasks

---

## Project Structure

```
.
├── makefile
├── poetry.lock
├── pyproject.toml
├── README.md
├── src
│   └── spacextracker
│       ├── __init__.py
│       ├── app.py                  # FastAPI application and endpoints
│       ├── celery_app.py           # Celery configuration
│       ├── db.py                   # Database connection
│       ├── logger.py               # Logger configuration
│       ├── logs                    # Celery log files
│       ├── models.py               # Pydantic models
│       ├── services                # Business logic and utilities
│       │   ├── cache_service.py    # Cache services
│       │   ├── data_access.py      # Data fetch DB
│       │   ├── spacex_data.py      # Fetch from spacex APIs
│       │   ├── store_to_db.py      # Store to DB
│       │   └── utils.py            # Utils services
│       ├── tasks.py                # Celery tasks
│       └── templates
│           └── index.html          # Web UI template
└── tests                           # Unit tests
```

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/36rahu/spoacex_tracker.git
cd spacextracker
```

2. Install dependencies with Poetry:
```bash
make install
```

3. Create `.env` file from the sample
```bash
make setup-env
```
---

## Usage

### Run the FastAPI App
```bash
make run
```
The app will be available at `http://localhost:8000`.

Note:
##### Please ensure that MongoDB and Redis are installed and running.

### Access Web UI
Open `http://localhost:8000/ui` in your browser.

### Start Celery Worker
```bash
make start-celery
```
This will run the Celery worker with the beat scheduler.

---
## Docker Commands
You can use the following Makefile commands to manage the Docker setup:

### Build and start all containers
Builds the images and starts all services (FastAPI, Celery, MongoDB, Redis).
```bash
make docker-up
```
### Stop and remove all containers
Stops all containers and removes them.
```bash
make docker-down
```

---
## API Endpoints

| Method | Endpoint                 | Description                           |
|--------|--------------------------|---------------------------------------|
| GET    | `/launches`              | Fetch filtered SpaceX launches        |
| GET    | `/statistics`            | Fetch launch statistics               |
| GET    | `/launches/download`     | Download filtered launches as JSON    |
| GET    | `/statistics/download`   | Download launch statistics as JSON    |
| GET    | `/ui`                    | Render web UI page                    |

**Query Parameters for `/launches`:**
- `start_date` – Filter launches from this date
- `end_date` – Filter launches up to this date
- `rocket_name` – Filter by rocket name
- `launchpad` – Filter by launchpad
- `success` – Filter by launch success (True/False)

---

## Celery Tasks

- `fetch_and_store_launches`: Fetches latest SpaceX launches from the API and stores them in the database.
- Run Celery worker with beat scheduler:
```bash
make start-celery
```

---

## Testing

Run tests using Pytest:
```bash
make test
```

---

## Development Tools

- **Linting:**  
```bash
make lint        # Check code style
make lint-fix    # Auto-fix lint issues
```

- **Formatting:**  
```bash
make format      # Apply black formatting
```

- **Clean Project:**  
```bash
make clean       # Remove __pycache__ and .pyc files
```

- **Clear Redis Cache (use with caution!):**  
```bash
make clear-cache
```

---

## Notes
- Logging is implemented in `logger.py` and used throughout the project for both API and Celery tasks.
- All services and utilities are modularized under `services/` for maintainability.
- The project uses Poetry for dependency management.

