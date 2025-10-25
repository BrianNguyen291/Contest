#!/usr/bin/env python3
"""
Test script to demonstrate enhanced data extraction capabilities
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_extraction():
    """Test the enhanced data extraction capabilities"""
    print("🧪 Testing Enhanced Data Extraction Capabilities")
    print("=" * 60)
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        scraper.start_mcp_server()
        
        # Navigate to AA.com
        logger.info("🌐 Navigating to AA.com...")
        scraper._call_mcp_tool('browser_navigate', url="https://www.aa.com")
        
        # Wait for page to load
        import time
        time.sleep(3)
        
        # Extract comprehensive data
        logger.info("🔍 Extracting comprehensive data...")
        data = scraper.extract_comprehensive_data()
        
        if data:
            print("\n📊 COMPREHENSIVE DATA EXTRACTION RESULTS:")
            print("=" * 60)
            
            # Display summary
            summary = data.get('summary', {})
            print(f"📈 Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            # Display flights
            flights = data.get('flights', [])
            print(f"\n✈️ Flights ({len(flights)}):")
            for i, flight in enumerate(flights[:5]):  # Show first 5
                print(f"  {i+1}. {flight.get('flightNumber', 'N/A')}: {flight.get('departureTime', 'N/A')} → {flight.get('arrivalTime', 'N/A')}")
                print(f"     Duration: {flight.get('duration', 'N/A')}, Aircraft: {flight.get('aircraft', 'N/A')}")
                print(f"     Stops: {flight.get('stops', 'N/A')}")
                print(f"     Award Prices: {flight.get('awardPrices', [])}")
                print(f"     Cash Prices: {flight.get('cashPrices', [])}")
                print()
            
            # Display raw data
            raw_data = data.get('rawData', {})
            print(f"📋 Raw Data:")
            for key, value in raw_data.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items - {value[:3]}...")
                else:
                    print(f"  {key}: {value}")
            
            # Save results
            output_file = "enhanced_extraction_test.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
            
        else:
            print("❌ No data extracted")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_enhanced_extraction()
