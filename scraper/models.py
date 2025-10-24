from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class SearchMetadata(BaseModel):
    """Metadata about the search parameters"""
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    date: str = Field(..., description="Flight date in YYYY-MM-DD format")
    passengers: int = Field(..., ge=1, le=9, description="Number of passengers")
    cabin_class: str = Field(default="economy", description="Cabin class")


class Flight(BaseModel):
    """Individual flight data with pricing information"""
    flight_number: str = Field(..., description="Flight number (e.g., AA123)")
    departure_time: str = Field(..., description="Departure time in HH:MM format")
    arrival_time: str = Field(..., description="Arrival time in HH:MM format")
    points_required: Optional[int] = Field(None, description="Points required for award booking")
    cash_price_usd: Optional[float] = Field(None, description="Cash price in USD")
    taxes_fees_usd: Optional[float] = Field(None, description="Taxes and fees in USD")
    cpp: Optional[float] = Field(None, description="Cents per point value")


class ScraperResult(BaseModel):
    """Complete scraper result with metadata and flights"""
    search_metadata: SearchMetadata
    flights: List[Flight] = Field(default_factory=list)
    total_results: int = Field(default=0, description="Total number of flights found")
