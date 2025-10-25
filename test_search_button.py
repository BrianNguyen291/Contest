#!/usr/bin/env python3
"""
Test script to specifically test search button detection
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_search_button_detection():
    """Test the search button detection capabilities"""
    print("🔍 Testing Search Button Detection")
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
        
        # Test search button detection
        logger.info("🔍 Testing search button detection...")
        button_selector = scraper.find_search_button()
        
        if button_selector:
            print(f"✅ Found search button with selector: {button_selector}")
            
            # Try to click the button
            logger.info("🖱️ Testing button click...")
            try:
                js_code = f"""
                () => {{
                    const button = document.querySelector('{button_selector}');
                    if (button) {{
                        button.click();
                        return {{ success: true, selector: '{button_selector}' }};
                    }}
                    return {{ success: false, message: 'Button not found' }};
                }}
                """
                
                result = scraper._call_mcp_tool('browser_evaluate', function=js_code)
                if result and 'content' in result and len(result['content']) > 0:
                    result_text = result['content'][0]['text']
                    print(f"📋 Click result: {result_text}")
                    
                    if 'success": true' in result_text:
                        print("✅ Button click successful!")
                    else:
                        print("❌ Button click failed")
                else:
                    print("❌ No result from button click")
                    
            except Exception as e:
                print(f"❌ Button click test failed: {e}")
        else:
            print("❌ No search button found")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_search_button_detection()
