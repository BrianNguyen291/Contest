#!/usr/bin/env python3
"""
Debug script to test search button detection and clicking
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_search_button():
    """Debug the search button detection and clicking"""
    print("🔍 Debugging Search Button Detection")
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
        
        # Take snapshot to see the page
        logger.info("📸 Taking page snapshot...")
        snapshot = scraper._call_mcp_tool('browser_snapshot')
        if snapshot:
            logger.info(f"✅ Got snapshot ({len(str(snapshot))} bytes)")
        
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
        
        # Fill "Depart" date" field
        logger.info("  Filling 'Depart' date field...")
        scraper._call_mcp_tool('browser_type', element='Depart date textbox', ref='e149', text='12/15/2025')
        time.sleep(1)
        
        # Now test the search button detection
        logger.info("🔍 Testing search button detection...")
        button_selector = scraper.find_search_button()
        if button_selector:
            logger.info(f"✅ Found search button: {button_selector}")
        else:
            logger.warning("❌ No search button found")
        
        # Try to click the search button using the found selector
        if button_selector:
            logger.info("🔍 Testing search button click...")
            js_code = f"""
            () => {{
                const button = document.querySelector('{button_selector}');
                if (button) {{
                    button.click();
                    return {{ success: true, selector: '{button_selector}', buttonText: button.value }};
                }}
                return {{ success: false, message: 'Button not found with selector' }};
            }}
            """
            
            result = scraper._call_mcp_tool('browser_evaluate', function=js_code)
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                logger.info(f"📋 Search button click result: {result_text}")
                if 'success": true' in result_text:
                    logger.info("✅ Search button clicked successfully")
                else:
                    logger.warning("❌ Search button click failed")
            else:
                logger.warning("❌ No result from search button click")
        
        # Wait a bit to see if navigation occurs
        logger.info("⏳ Waiting for navigation...")
        time.sleep(5)
        
        # Check current URL
        logger.info("🔍 Checking current URL...")
        url_check = scraper._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, title: document.title }; }")
        if url_check and 'content' in url_check and len(url_check['content']) > 0:
            url_data = url_check['content'][0]['text']
            logger.info(f"📄 Current page: {url_data}")
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
    finally:
        scraper.close()

if __name__ == "__main__":
    debug_search_button()
