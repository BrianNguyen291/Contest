#!/usr/bin/env python3
"""
Simple test to verify search button functionality
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_simple_search():
    """Test just the search button click"""
    print("🔍 Testing Simple Search Button Click")
    print("=" * 50)
    
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
        
        # Fill in the search form
        logger.info("🔍 Filling search form...")
        
        # Click "One way" radio button
        logger.info("  Clicking 'One way' radio button...")
        scraper._call_mcp_tool('browser_click', element='One way radio button', ref='e115')
        time.sleep(1)
        
        # Fill "From" field
        logger.info("  Filling 'From' field with LAX...")
        scraper._call_mcp_tool('browser_type', element='From airport textbox', ref='e128', text='LAX')
        time.sleep(1)
        
        # Fill "To" field
        logger.info("  Filling 'To' field with JFK...")
        scraper._call_mcp_tool('browser_type', element='To airport textbox', ref='e136', text='JFK')
        time.sleep(1)
        
        # Fill "Depart" date field
        logger.info("  Filling 'Depart' date field...")
        scraper._call_mcp_tool('browser_type', element='Depart date textbox', ref='e149', text='12/15/2025')
        time.sleep(1)
        
        # Click search button
        logger.info("🔍 Clicking search button...")
        result = scraper._call_mcp_tool('browser_click', element='Search button', ref='e161')
        
        if result:
            logger.info("✅ Search button clicked successfully!")
            logger.info(f"📋 Result: {result}")
        else:
            logger.warning("❌ Search button click failed")
        
        # Wait a bit to see if navigation occurs
        logger.info("⏳ Waiting for navigation...")
        time.sleep(5)
        
        # Check current URL
        logger.info("🔍 Checking current URL...")
        url_check = scraper._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, title: document.title }; }")
        if url_check:
            logger.info(f"📄 Current page: {url_check}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_simple_search()
