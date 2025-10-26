#!/usr/bin/env python3
"""
Test script for the improved AA scraper
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_improved_scraper():
    """Test the improved scraper"""
    print("🧪 Testing Improved AA Scraper")
    print("=" * 50)
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        print("🌐 Starting MCP server...")
        scraper.start_mcp_server()
        
        # Test search
        print("🔍 Testing flight search...")
        result = scraper.search_flights("LAX", "JFK", "2025-12-15")
        
        # Validate results
        print("\n📊 VALIDATION RESULTS:")
        print("=" * 50)
        
        flights = result.get('flights', [])
        total_results = result.get('total_results', 0)
        
        print(f"Total flights found: {total_results}")
        
        if flights:
            print("\n✈️ Flight Details:")
            null_count = 0
            total_fields = 0
            
            for i, flight in enumerate(flights):
                print(f"\nFlight {i+1}:")
                print(f"  Number: {flight.get('flight_number', 'NULL')}")
                print(f"  Departure: {flight.get('departure_time', 'NULL')}")
                print(f"  Arrival: {flight.get('arrival_time', 'NULL')}")
                print(f"  Cash Price: ${flight.get('cash_price_usd', 'NULL')}")
                print(f"  Points: {flight.get('points_required', 'NULL')}")
                print(f"  CPP: {flight.get('cpp', 'NULL')}¢")
                
                # Count null values
                for key, value in flight.items():
                    total_fields += 1
                    if value is None:
                        null_count += 1
                        print(f"    ⚠️ {key} is NULL")
            
            print(f"\n📈 Summary:")
            print(f"  Total flights: {len(flights)}")
            print(f"  Null values: {null_count}")
            print(f"  Total fields: {total_fields}")
            if total_fields > 0:
                completeness = ((total_fields - null_count) / total_fields) * 100
                print(f"  Data completeness: {completeness:.1f}%")
            
            # Save test results
            with open('test_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Test results saved to: test_results.json")
            
            # Show improvement metrics
            print(f"\n🎯 Improvement Metrics:")
            if completeness >= 80:
                print(f"  ✅ Excellent data completeness ({completeness:.1f}%)")
            elif completeness >= 60:
                print(f"  ⚠️ Good data completeness ({completeness:.1f}%)")
            else:
                print(f"  ❌ Poor data completeness ({completeness:.1f}%)")
            
        else:
            print("❌ No flights found!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
    finally:
        scraper.close()
        print("\n✅ Test complete!")

if __name__ == "__main__":
    test_improved_scraper()
