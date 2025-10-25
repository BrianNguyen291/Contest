#!/usr/bin/env python3
"""
Test script to verify the MCP scraper works with the backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_mcp_aa_scraper import MCPPlaywrightScraper
import json
from datetime import datetime

def test_scraper():
    """Test the MCP scraper directly"""
    print("🧪 Testing MCP Scraper...")
    
    try:
        scraper = MCPPlaywrightScraper()
        
        # Test with a simple search
        print("🔍 Testing flight search...")
        flights = scraper.search_flights(
            origin="LAX",
            destination="JFK", 
            date="2025-12-15",
            adults=1
        )
        
        print(f"✅ Found {len(flights)} flights")
        
        # Save results
        result = {
            "search_metadata": {
                "origin": "LAX",
                "destination": "JFK",
                "date": "2025-12-15",
                "passengers": 1,
                "search_timestamp": datetime.now().isoformat()
            },
            "flights": flights,
            "total_results": len(flights),
            "flights_with_cpp": len([f for f in flights if f.get('cpp') is not None])
        }
        
        with open("test_results.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print("✅ Test completed successfully!")
        print(f"📊 Results saved to test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)
