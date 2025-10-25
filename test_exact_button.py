#!/usr/bin/env python3
"""
Test script to test the exact search button with style="" attribute
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_exact_button():
    """Test the exact search button with style="" attribute"""
    print("🔍 Testing Exact Search Button with style=\"\" attribute")
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
        
        # Test the exact button selector
        logger.info("🔍 Testing exact button selector...")
        js_code = """
        () => {
            // Test the exact button with all attributes
            const exactButton = document.querySelector('input[type="submit"][value="Search"][id="flightSearchForm.button.reSubmit"][class="btn btn-fullWidth"][style=""]');
            
            if (exactButton) {
                return {
                    found: true,
                    selector: 'input[type="submit"][value="Search"][id="flightSearchForm.button.reSubmit"][class="btn btn-fullWidth"][style=""]',
                    id: exactButton.id,
                    className: exactButton.className,
                    value: exactButton.value,
                    type: exactButton.type,
                    style: exactButton.style.cssText,
                    visible: exactButton.offsetParent !== null,
                    enabled: !exactButton.disabled
                };
            }
            
            // Try other variations
            const variations = [
                'input[type="submit"][value="Search"]',
                'input[id="flightSearchForm.button.reSubmit"]',
                '#flightSearchForm\\.button\\.reSubmit',
                'input[class="btn btn-fullWidth"][value="Search"]'
            ];
            
            for (const selector of variations) {
                const button = document.querySelector(selector);
                if (button) {
                    return {
                        found: true,
                        selector: selector,
                        id: button.id,
                        className: button.className,
                        value: button.value,
                        type: button.type,
                        style: button.style.cssText,
                        visible: button.offsetParent !== null,
                        enabled: !button.disabled
                    };
                }
            }
            
            return { found: false, message: 'No search button found' };
        }
        """
        
        result = scraper._call_mcp_tool('browser_evaluate', function=js_code)
        
        if result and 'content' in result and len(result['content']) > 0:
            result_text = result['content'][0]['text']
            print(f"📋 Button test result: {result_text}")
            
            # Parse the result
            try:
                import re
                json_match = re.search(r'### Result\n(.*?)\n\n###', result_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    data = json.loads(json_str)
                    
                    if data.get('found'):
                        print(f"✅ Found search button: {data.get('selector')}")
                        print(f"    ID: {data.get('id')}")
                        print(f"    Class: {data.get('className')}")
                        print(f"    Value: {data.get('value')}")
                        print(f"    Type: {data.get('type')}")
                        print(f"    Style: {data.get('style')}")
                        print(f"    Visible: {data.get('visible')}")
                        print(f"    Enabled: {data.get('enabled')}")
                        
                        # Try to click the button
                        if data.get('enabled') and data.get('visible'):
                            logger.info("🖱️ Testing button click...")
                            click_js = f"""
                            () => {{
                                const button = document.querySelector('{data.get('selector')}');
                                if (button) {{
                                    button.click();
                                    return {{ success: true, selector: '{data.get('selector')}' }};
                                }}
                                return {{ success: false, message: 'Button not found for click' }};
                            }}
                            """
                            
                            click_result = scraper._call_mcp_tool('browser_evaluate', function=click_js)
                            if click_result and 'content' in click_result and len(click_result['content']) > 0:
                                click_data = click_result['content'][0]['text']
                                print(f"📋 Click result: {click_data}")
                                
                                if 'success": true' in click_data:
                                    print("✅ Button click successful!")
                                else:
                                    print("❌ Button click failed")
                            else:
                                print("❌ No result from button click")
                        else:
                            print("⚠️ Button is not visible or enabled")
                    else:
                        print(f"❌ No search button found: {data.get('message')}")
                else:
                    print("❌ Could not parse button test result")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
        else:
            print("❌ No result from button test")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_exact_button()
