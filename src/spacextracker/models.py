from datetime import datetime, date
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any
from fastapi import HTTPException


class LaunchModel(BaseModel):
    """
    Model representing a SpaceX launch.
    """

    id: str
    name: str
    success: Optional[bool]
    date: datetime
    launchpad: str
    details: Optional[str]
    links: Dict[str, Any]


class LaunchQueryParams(BaseModel):
    """
    Query parameters for filtering launches.
    """

    start_date: Optional[date] = Field(
        None, description="Start of date range (YYYY-MM-DD)"
    )
    end_date: Optional[date] = Field(None, description="End of date range (YYYY-MM-DD)")
    rocket_name: Optional[str] = Field(None, min_length=2, max_length=50)
    success: Optional[bool] = Field(None, description="Launch success (true/false)")
    launchpad: Optional[str] = Field(None, min_length=2)

    @model_validator(mode="after")
    def validate_dates(self) -> "LaunchQueryParams":
        """
        Ensure both start_date and end_date are provided together and in correct order.
        """
        if (self.start_date and not self.end_date) or (
            self.end_date and not self.start_date
        ):
            raise HTTPException(
                status_code=422,
                detail="Both start_date and end_date must be provided together",
            )
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise HTTPException(
                status_code=422, detail="start_date must be before or equal to end_date"
            )
        return self
