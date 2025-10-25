"""
FastAPI Backend for AA Flight Scraper
Provides REST API endpoints for the web frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import sys
import os
import json
import subprocess
import tempfile
from datetime import datetime

# Add the parent directory to the path so we can import the scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our working MCP scraper
from real_mcp_aa_scraper import MCPPlaywrightScraper

app = FastAPI(
    title="AA Flight Scraper API",
    description="REST API for American Airlines flight scraping with CPP calculation",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    date: str
    passengers: int = 1
    proxy: Optional[str] = None

class FlightSearchResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AA Flight Scraper API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "AA Flight Scraper API",
        "endpoints": {
            "search": "/api/search",
            "health": "/health"
        }
    }

@app.post("/api/search", response_model=FlightSearchResponse)
async def search_flights(request: FlightSearchRequest):
    """
    Search for flights and return pricing data with CPP calculation
    """
    import time
    start_time = time.time()
    
    try:
        # Validate inputs
        if not request.origin or not request.destination:
            raise HTTPException(status_code=400, detail="Origin and destination are required")
        
        if len(request.origin) != 3 or len(request.destination) != 3:
            raise HTTPException(status_code=400, detail="Airport codes must be 3 characters")
        
        # Initialize our working MCP scraper
        scraper = MCPPlaywrightScraper()
        
        # Perform the search with our MCP scraper
        flights = scraper.search_flights(
            origin=request.origin.upper(),
            destination=request.destination.upper(),
            date=request.date,
            adults=request.passengers
        )
        
        # Format the response to match frontend expectations
        result = {
            "search_metadata": {
                "origin": request.origin.upper(),
                "destination": request.destination.upper(),
                "date": request.date,
                "passengers": request.passengers,
                "search_timestamp": datetime.now().isoformat()
            },
            "flights": flights,
            "total_results": len(flights),
            "flights_with_cpp": len([f for f in flights if f.get('cpp') is not None])
        }
        
        execution_time = time.time() - start_time
        
        return FlightSearchResponse(
            success=True,
            data=result,
            execution_time=execution_time
        )
            
    except Exception as e:
        execution_time = time.time() - start_time
        return FlightSearchResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )

@app.get("/api/airports")
async def get_airports():
    """Get list of common airport codes"""
    return {
        "airports": [
            {"code": "LAX", "name": "Los Angeles International", "city": "Los Angeles"},
            {"code": "JFK", "name": "John F. Kennedy International", "city": "New York"},
            {"code": "SFO", "name": "San Francisco International", "city": "San Francisco"},
            {"code": "MIA", "name": "Miami International", "city": "Miami"},
            {"code": "BOS", "name": "Logan International", "city": "Boston"},
            {"code": "ORD", "name": "O'Hare International", "city": "Chicago"},
            {"code": "DFW", "name": "Dallas/Fort Worth International", "city": "Dallas"},
            {"code": "ATL", "name": "Hartsfield-Jackson Atlanta International", "city": "Atlanta"},
            {"code": "DEN", "name": "Denver International", "city": "Denver"},
            {"code": "SEA", "name": "Seattle-Tacoma International", "city": "Seattle"},
            {"code": "LAS", "name": "McCarran International", "city": "Las Vegas"},
            {"code": "PHX", "name": "Phoenix Sky Harbor International", "city": "Phoenix"},
            {"code": "IAH", "name": "George Bush Intercontinental", "city": "Houston"},
            {"code": "MCO", "name": "Orlando International", "city": "Orlando"},
            {"code": "CLT", "name": "Charlotte Douglas International", "city": "Charlotte"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
