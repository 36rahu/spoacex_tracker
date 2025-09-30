import os
from typing import Any, Dict, List, Union
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, Response

from spacextracker.logger import logger
from spacextracker.models import LaunchQueryParams
from spacextracker.services.data_access import get_launches, get_all_statistics

app = FastAPI(title="SpaceX Tracker API")

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/launches")
def fetch_launches(
    params: LaunchQueryParams = Depends(),
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    logger.info(f"Fetching launches with params: {params}")
    try:
        launches = get_launches(**params.model_dump(exclude_none=True))
        logger.info(f"Fetched {len(launches)} launches successfully")
        return launches
    except HTTPException as e:
        logger.warning(f"HTTPException while fetching launches: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching launches: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/statistics")
def fetch_statistics() -> Dict[str, Any]:
    logger.info("Fetching launch statistics")
    try:
        stats = get_all_statistics()
        logger.info("Fetched statistics successfully")
        return stats
    except HTTPException as e:
        logger.warning(f"HTTPException while fetching statistics: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/launches/download")
def download_launches(params: LaunchQueryParams = Depends()) -> JSONResponse:
    logger.info(f"Downloading launches with params: {params}")
    try:
        launches = get_launches(**params.dict(exclude_none=True))
        logger.info(f"Downloaded {len(launches)} launches successfully")
        return JSONResponse(
            content=launches,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=launches.json"},
        )
    except Exception as e:
        logger.error(f"Error downloading launches: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics/download")
def download_statistics() -> JSONResponse:
    logger.info("Downloading launch statistics")
    try:
        stats = get_all_statistics()
        logger.info("Downloaded statistics successfully")
        return JSONResponse(
            content=stats,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=statistics.json"},
        )
    except Exception as e:
        logger.error(f"Error downloading statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ui", response_class=HTMLResponse)
def index(request: Request) -> Response:
    logger.info("Rendering UI page")
    return templates.TemplateResponse("index.html", {"request": request})
