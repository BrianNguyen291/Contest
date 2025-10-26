#!/usr/bin/env python3
"""
Quick test to validate the improved AA scraper
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_test():
    """Quick test of the improved scraper"""
    print("🧪 Quick Test - Improved AA Scraper")
    print("=" * 50)
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        print("🌐 Starting MCP server...")
        scraper.start_mcp_server()
        
        # Test search
        print("🔍 Testing flight search...")
        result = scraper.search_flights("LAX", "JFK", "2025-12-15")
        
        # Quick analysis
        flights = result.get('flights', [])
        print(f"\n📊 Quick Results:")
        print(f"  Total flights: {len(flights)}")
        
        if flights:
            # Count non-null values
            cash_prices = sum(1 for f in flights if f.get('cash_price_usd') is not None)
            points_data = sum(1 for f in flights if f.get('points_required') is not None)
            cpp_data = sum(1 for f in flights if f.get('cpp') is not None)
            
            print(f"  Flights with cash prices: {cash_prices}")
            print(f"  Flights with points: {points_data}")
            print(f"  Flights with CPP: {cpp_data}")
            
            # Show first few flights with data
            print(f"\n✈️ Sample flights with data:")
            count = 0
            for flight in flights:
                if flight.get('cash_price_usd') or flight.get('points_required'):
                    print(f"  {flight['flight_number']}: ${flight.get('cash_price_usd', 'N/A')} or {flight.get('points_required', 'N/A')} pts")
                    count += 1
                    if count >= 5:  # Show first 5
                        break
            
            # Save results
            with open('quick_test_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: quick_test_results.json")
            
        else:
            print("❌ No flights found!")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        
    finally:
        scraper.close()
        print("\n✅ Quick test complete!")

if __name__ == "__main__":
    quick_test()
