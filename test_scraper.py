#!/usr/bin/env python3
"""Test script for AA Flight Scraper"""

import asyncio
import json
from scraper.models import SearchMetadata, Flight, ScraperResult
from scraper.utils import calculate_cpp, parse_price, parse_time, parse_flight_number, match_flights

def test_utility_functions():
    """Test utility functions"""
    print("Testing utility functions...")
    
    # Test CPP calculation
    cpp = calculate_cpp(289.0, 5.60, 12500)
    print(f"CPP calculation: {cpp}")
    assert cpp == 2.27, f"Expected 2.27, got {cpp}"
    
    # Test price parsing
    price = parse_price("$289.00")
    print(f"Price parsing: {price}")
    assert price == 289.0, f"Expected 289.0, got {price}"
    
    # Test time parsing
    time_str = parse_time("8:00 AM")
    print(f"Time parsing: {time_str}")
    assert time_str == "08:00", f"Expected 08:00, got {time_str}"
    
    # Test flight number parsing
    flight_num = parse_flight_number("AA123")
    print(f"Flight number parsing: {flight_num}")
    assert flight_num == "AA123", f"Expected AA123, got {flight_num}"
    
    print("✅ All utility functions working correctly!")

def test_models():
    """Test Pydantic models"""
    print("\nTesting Pydantic models...")
    
    # Test SearchMetadata
    search_meta = SearchMetadata(
        origin="LAX",
        destination="JFK",
        date="2025-12-15",
        passengers=1
    )
    print(f"SearchMetadata: {search_meta.model_dump()}")
    
    # Test Flight
    flight = Flight(
        flight_number="AA123",
        departure_time="08:00",
        arrival_time="16:30",
        points_required=12500,
        cash_price_usd=289.00,
        taxes_fees_usd=5.60,
        cpp=2.27
    )
    print(f"Flight: {flight.model_dump()}")
    
    # Test ScraperResult
    result = ScraperResult(
        search_metadata=search_meta,
        flights=[flight],
        total_results=1
    )
    
    # Test JSON serialization
    json_output = result.model_dump_json(indent=2)
    print(f"JSON output:\n{json_output}")
    
    # Verify JSON structure
    parsed = json.loads(json_output)
    assert "search_metadata" in parsed
    assert "flights" in parsed
    assert "total_results" in parsed
    assert len(parsed["flights"]) == 1
    assert parsed["flights"][0]["flight_number"] == "AA123"
    assert parsed["flights"][0]["cpp"] == 2.27
    
    print("✅ All models working correctly!")

def test_flight_matching():
    """Test flight matching logic"""
    print("\nTesting flight matching...")
    
    award_flights = [
        {
            "flight_number": "AA123",
            "departure_time": "08:00",
            "arrival_time": "16:30",
            "points_required": 12500,
            "taxes_fees_usd": 5.60
        },
        {
            "flight_number": "AA456",
            "departure_time": "14:15",
            "arrival_time": "22:45",
            "points_required": 10000,
            "taxes_fees_usd": 5.60
        }
    ]
    
    cash_flights = [
        {
            "flight_number": "AA123",
            "departure_time": "08:00",
            "cash_price_usd": 289.00
        },
        {
            "flight_number": "AA456",
            "departure_time": "14:15",
            "cash_price_usd": 189.00
        }
    ]
    
    matched = match_flights(award_flights, cash_flights)
    print(f"Matched flights: {len(matched)}")
    
    assert len(matched) == 2, f"Expected 2 matched flights, got {len(matched)}"
    
    # Check first flight
    flight1 = matched[0]
    assert flight1["flight_number"] == "AA123"
    assert flight1["points_required"] == 12500
    assert flight1["cash_price_usd"] == 289.00
    assert flight1["cpp"] == 2.27
    
    # Check second flight
    flight2 = matched[1]
    assert flight2["flight_number"] == "AA456"
    assert flight2["points_required"] == 10000
    assert flight2["cash_price_usd"] == 189.00
    assert flight2["cpp"] == 1.83
    
    print("✅ Flight matching working correctly!")

async def test_scraper_initialization():
    """Test scraper initialization without actual scraping"""
    print("\nTesting scraper initialization...")
    
    try:
        from scraper.aa_scraper import AAScraper
        
        # Test scraper creation
        scraper = AAScraper(headless=True)
        print("✅ AAScraper created successfully")
        
        # Test search metadata creation
        search_meta = SearchMetadata(
            origin="LAX",
            destination="JFK",
            date="2025-12-15",
            passengers=1
        )
        print("✅ SearchMetadata created successfully")
        
        print("✅ Scraper initialization working correctly!")
        
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        raise

def main():
    """Run all tests"""
    print("🧪 Testing AA Flight Scraper Components")
    print("=" * 50)
    
    try:
        test_utility_functions()
        test_models()
        test_flight_matching()
        
        # Test async components
        asyncio.run(test_scraper_initialization())
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\nTo run the scraper:")
        print("python main.py --origin LAX --destination JFK --date 2025-12-15")
        print("\nTo build Docker image:")
        print("docker build -t aa-flight-scraper .")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())