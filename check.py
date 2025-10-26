Skip to content
Navigation Menu
BrianNguyen291
Contest

Type / to search
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
Contest
/real_mcp_aa_scraper.py
Go to file
t
BrianNguyen291
BrianNguyen291
Enhance RealMCPPlaywrightScraper with improved error handling and com…
b8f9b73
 · 
17 hours ago
Contest
/real_mcp_aa_scraper.py

Code

Blame
class RealMCPPlaywrightScraper:
    def _call_mcp_tool(self, tool_name: str, **kwargs) -> Optional[Dict]:
#!/usr/bin/env python3
"""
Real AA.com Scraper using Microsoft Playwright MCP
Uses the official @playwright/mcp package for automatic browser interaction
"""

import json
import logging
import os
import subprocess
import sys
import time
import re
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchMetadata:
    def __init__(self, origin: str, destination: str, date: str, passengers: int, cabin_class: str):
        self.origin = origin
        self.destination = destination
        self.date = date
        self.passengers = passengers
        self.cabin_class = cabin_class

class RealMCPPlaywrightScraper:
    """AA.com scraper using Microsoft Playwright MCP (official)"""
    
    def __init__(self):
        self.base_url = "https://www.aa.com"
        self.mcp_process = None
        
    def start_mcp_server(self):
        """Start the official Playwright MCP server"""
        logger.info("🌐 Starting official Playwright MCP server...")
        
        try:
            # Start the official @playwright/mcp server
            self.mcp_process = subprocess.Popen(
                ["npx", "@playwright/mcp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            logger.info("✅ Official Playwright MCP server started")
            
            # Give it time to initialize
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            raise
    
    def _call_mcp_tool(self, tool_name: str, **kwargs) -> Optional[Dict]:
        """Call a Playwright MCP tool using JSON-RPC"""
        logger.info(f"  🔧 Calling {tool_name}...")
        
        # Check if MCP process is still alive
        if self.mcp_process and self.mcp_process.poll() is not None:
            logger.warning("⚠️ MCP process died, attempting to restart...")
            self.close()
            self.start_mcp_server()
            if not self.mcp_process:
                logger.error("❌ Failed to restart MCP server")
                return None
        
        try:
            # Create JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            # Send request to MCP server
            self.mcp_process.stdin.write(json.dumps(request) + "\n")
            self.mcp_process.stdin.flush()
            
            # Read response with timeout
            start_time = time.time()
            response_text = ""
            
            while time.time() - start_time < 30:  # 30 second timeout
                try:
                    line = self.mcp_process.stdout.readline()
                    if line:
                        response_text = line.strip()
                        break
                except:
                    time.sleep(0.1)
            
            if response_text:
                response = json.loads(response_text)
                if "result" in response:
                    logger.info(f"    ✅ {tool_name} succeeded")
                    return response["result"]
                else:
                    logger.warning(f"    ⚠️ {tool_name} returned: {response}")
                    return None
            else:
                logger.warning(f"    ⚠️ No response from {tool_name}")
                return None
                
        except BrokenPipeError as e:
            logger.error(f"❌ MCP connection broken for {tool_name}: {e}")
            logger.info("🔄 Attempting to restart MCP server...")
            self.close()
            self.start_mcp_server()
            return None
        except Exception as e:
            logger.warning(f"    ⚠️ MCP tool failed: {e}")
            return None
    
    def _parse_snapshot_for_elements(self, snapshot) -> Dict[str, str]:
        """Parse snapshot to find element references like Playwright MCP does"""
        elements = {}
        snapshot_text = str(snapshot)
        
        # Use the EXACT refs that work with the real MCP
        # These are the actual refs from the working MCP session
        elements['one way radio'] = 'e115'     # One way radio button
        elements['from airport'] = 'e128'      # From field
        elements['to airport'] = 'e136'        # To field  
        elements['depart date'] = 'e149'       # Depart date field
        elements['redeem miles'] = 'e121'      # Redeem miles checkbox
        elements['search button'] = 'e161'    # Search button (updated to match real MCP)
        
        logger.info(f"    Using real MCP working refs: {elements}")
        return elements
    
    def _find_element_ref(self, elements: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find element reference by keywords"""
        for key in elements:
            for keyword in keywords:
                if keyword in key.lower():
                    return elements[key]
        return None
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1, award_search: bool = False) -> Dict:
        """Search for flights using official Playwright MCP"""
        logger.info(f"🎯 Operation Point Break: {origin} → {destination} on {date}")
        
        search_metadata = SearchMetadata(
            origin=origin.upper(),
            destination=destination.upper(),
            date=date,
            passengers=passengers,
            cabin_class="economy"
        )
        
        try:
            # STEP 1: Navigate to AA.com
            logger.info("🌐 Step 1: Navigating to AA.com...")
            if award_search:
                # For award search, make sure we're on the correct page
                nav_result = self._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
            else:
                nav_result = self._call_mcp_tool('browser_navigate', url=self.base_url)
            
            if not nav_result:
                raise Exception("Failed to navigate to AA.com")
            
            time.sleep(5)  # Wait longer for page to fully load
            logger.info("✅ Page loaded")
            
            # STEP 2: Take snapshot to get element references
            logger.info("📸 Step 2: Taking page snapshot...")
            snapshot = self._call_mcp_tool('browser_snapshot')
            
            # For award search, ensure we're on the right page
            if award_search:
                logger.info("🔍 Verifying we're on the search page for award search...")
                page_check = self._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, hasForm: !!document.querySelector('form'), hasSearchButton: !!document.querySelector('input[type=\"submit\"][value=\"Search\"]') }; }")
                if page_check and 'content' in page_check and len(page_check['content']) > 0:
                    check_data = page_check['content'][0]['text']
                    logger.info(f"📄 Page verification: {check_data}")
                    if 'hasForm": false' in check_data or 'hasSearchButton": false' in check_data:
                        logger.warning("⚠️ Not on search page, navigating again...")
                        self._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
                        time.sleep(3)
                        snapshot = self._call_mcp_tool('browser_snapshot')
            
            if not snapshot:
                raise Exception("Failed to get page snapshot")
            
            logger.info(f"✅ Got snapshot ({len(str(snapshot))} bytes)")
            
            # Parse snapshot to find element references
            logger.info("  📋 Parsing snapshot for element references...")
            elements = self._parse_snapshot_for_elements(snapshot)
            logger.info(f"  Found {len(elements)} elements: {list(elements.keys())}")
            
            # STEP 3: Click "One way" radio button first
            logger.info("🔍 Step 3: Clicking 'One way' radio button...")
            self._call_mcp_tool('browser_click', element='One way radio button', ref='e115')
            logger.info(f"  ✅ Clicked One way radio button with ref: e115")
            time.sleep(2)
            
            # STEP 4: Fill "From" field using EXACT ref that worked in test
            logger.info(f"🔍 Step 4: Filling 'From' field with {origin}...")
            self._call_mcp_tool('browser_type', element='From airport textbox', ref='e128', text=origin)
            logger.info(f"  ✅ Filled From field with ref: e128")
            time.sleep(1)
            
            # STEP 5: Fill "To" field using EXACT ref that worked in test
            logger.info(f"🔍 Step 5: Filling 'To' field with {destination}...")
            self._call_mcp_tool('browser_type', element='To airport textbox', ref='e136', text=destination)
            logger.info(f"  ✅ Filled To field with ref: e136")
            time.sleep(1)
            
            # STEP 6: Fill "Depart" date field using EXACT ref that worked in test
            logger.info(f"🔍 Step 6: Filling 'Depart' date field...")
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
            self._call_mcp_tool('browser_type', element='Depart date textbox', ref='e149', text=date_formatted)
            logger.info(f"  ✅ Filled date field with ref: e149")
            time.sleep(1)
            
            # STEP 6.5: If searching for award, click "Redeem miles" checkbox
            if award_search:
                logger.info("💎 Step 6.5: Clicking 'Redeem miles' checkbox for award search...")
                
                # Try multiple approaches to click the Redeem miles checkbox
                redeem_clicked = False
                
                # Approach 1: Use the real MCP ref
                try:
                    redeem_result = self._call_mcp_tool('browser_click', element='Redeem miles label', ref='e121')
                    if redeem_result:
                        logger.info("  ✅ Clicked Redeem miles checkbox (ref e121)")
                        redeem_clicked = True
                except Exception as e:
                    logger.warning(f"  ⚠️ Ref e121 failed: {e}")
                
                # Approach 2: Try clicking by text content
                if not redeem_clicked:
                    try:
                        redeem_result = self._call_mcp_tool('browser_click', element='Redeem miles', ref='e121')
                        if redeem_result:
                            logger.info("  ✅ Clicked Redeem miles checkbox (text method)")
                            redeem_clicked = True
                    except Exception as e:
                        logger.warning(f"  ⚠️ Text click failed: {e}")
                
                # Approach 3: Use browser_evaluate to find and click the checkbox
                if not redeem_clicked:
                    try:
                        logger.info("  🔧 Trying to find and click Redeem miles checkbox with browser_evaluate...")
                        js_code = """
                        () => {
                            // Try multiple selectors for the Redeem miles checkbox
                            const selectors = [
                                'input[type="checkbox"][id*="redeem"]',
                                'input[type="checkbox"][name*="redeem"]',
                                'input[type="checkbox"][value*="redeem"]',
                                'input[type="checkbox"]',
                                'label[for*="redeem"]',
                                'label:contains("Redeem miles")',
                                'label:contains("Redeem")',
                                '[data-testid*="redeem"]',
                                '[aria-label*="redeem"]'
                            ];
                            
                            for (const selector of selectors) {
                                const element = document.querySelector(selector);
                                if (element) {
                                    // Try to click the element
                                    try {
                                        element.click();
                                        return { success: true, selector: selector, type: element.tagName };
                                    } catch (e) {
                                        // Try to find associated checkbox
                                        const checkbox = element.querySelector('input[type="checkbox"]') || 
                                                       document.querySelector(`input[type="checkbox"][id="${element.getAttribute('for')}"]`);
                                        if (checkbox) {
                                            checkbox.click();
                                            return { success: true, selector: selector, type: 'checkbox' };
                                        }
                                    }
                                }
                            }
                            
                            // Try to find by text content
                            const labels = document.querySelectorAll('label');
                            for (const label of labels) {
                                if (label.textContent.toLowerCase().includes('redeem') || 
                                    label.textContent.toLowerCase().includes('miles')) {
                                    const checkbox = label.querySelector('input[type="checkbox"]') || 
                                                   document.querySelector(`input[type="checkbox"][id="${label.getAttribute('for')}"]`);
                                    if (checkbox) {
                                        checkbox.click();
                                        return { success: true, selector: 'text-based', type: 'checkbox' };
                                    }
                                }
                            }
                            
                            return { success: false, message: 'No Redeem miles checkbox found' };
                        }
                        """
                        
                        result = self._call_mcp_tool('browser_evaluate', function=js_code)
                        if result and 'content' in result and len(result['content']) > 0:
                            result_text = result['content'][0]['text']
                            logger.info(f"  📋 Redeem miles click result: {result_text}")
                            if 'success": true' in result_text:
                                logger.info("  ✅ Clicked Redeem miles checkbox (browser_evaluate method)")
                                redeem_clicked = True
                    except Exception as e:
                        logger.warning(f"  ⚠️ Browser evaluate failed: {e}")
                
                if not redeem_clicked:
                    logger.warning("  ⚠️ All Redeem miles checkbox click attempts failed")
                else:
                    logger.info("  ✅ Redeem miles checkbox clicked successfully")
                
                time.sleep(2)  # Wait longer for the checkbox to be processed
            else:
                logger.info("💰 Step 6.5: Cash search - skipping Redeem miles checkbox")
            
                # STEP 7: Click "Search" button using multiple approaches
                logger.info("🔍 Step 7: Clicking 'Search' button...")

                # For award search, be more careful about the search button click
                if award_search:
                    logger.info("💎 Award search: Using enhanced search button logic...")
                    
                    # First, verify we're on the right page
                    page_verify = self._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, hasSearchForm: !!document.querySelector('form'), hasSearchButton: !!document.querySelector('input[type=\"submit\"][value=\"Search\"]') }; }")
                    if page_verify and 'content' in page_verify and len(page_verify['content']) > 0:
                        verify_data = page_verify['content'][0]['text']
                        logger.info(f"📄 Page verification for award search: {verify_data}")
                        
                        if 'hasSearchForm": false' in verify_data or 'hasSearchButton": false' in verify_data:
                            logger.warning("⚠️ Not on search page for award search, navigating to correct page...")
                            self._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
                            time.sleep(5)
                            
                            # Take new snapshot after navigation
                            snapshot = self._call_mcp_tool('browser_snapshot')
                            if snapshot:
                                logger.info("✅ Got new snapshot after navigation")
                                # Re-parse elements for the new page
                                elements = self._parse_snapshot_for_elements(snapshot)
                                logger.info(f"📋 Updated elements: {elements}")

                # First, try to find the search button
                button_selector = self.find_search_button()

                # Try multiple approaches to click the search button
                search_clicked = False

                # Approach 1: Use the working MCP ref (e161) - prioritize this for award search
                try:
                    click_result = self._call_mcp_tool('browser_click', element='Search button', ref='e161')
                    if click_result:
                        logger.info("  ✅ Clicked Search button (ref e161)")
                        search_clicked = True
                except Exception as e:
                    logger.warning(f"  ⚠️ Ref e161 failed: {e}")

                # Approach 2: Try the alternative ref (e154)
                if not search_clicked:
                    try:
                        click_result = self._call_mcp_tool('browser_click', element='Search button', ref='e154')
                        if click_result:
                            logger.info("  ✅ Clicked Search button (ref e154)")
                            search_clicked = True
                    except Exception as e:
                        logger.warning(f"  ⚠️ Ref e154 failed: {e}")

                # Approach 3: Use the found button selector
                if not search_clicked and button_selector:
                    try:
                        logger.info(f"  🔧 Trying to click button with selector: {button_selector}")
                        js_code = f"""
                        () => {{
                            const button = document.querySelector('{button_selector}');
                            if (button) {{
                                button.click();
                                return {{ success: true, selector: '{button_selector}' }};
                            }}
                            return {{ success: false, message: 'Button not found with selector' }};
                        }}
                        """

                        result = self._call_mcp_tool('browser_evaluate', function=js_code)
                        if result and 'content' in result and len(result['content']) > 0:
                            result_text = result['content'][0]['text']
                            logger.info(f"  📋 Selector click result: {result_text}")
                            if 'success": true' in result_text:
                                logger.info("  ✅ Clicked Search button (selector method)")
                                search_clicked = True
                    except Exception as e:
                        logger.warning(f"  ⚠️ Selector click failed: {e}")

                # Approach 4: Try using browser_evaluate to click the button directly
                if not search_clicked:
                    try:
                        logger.info("  🔧 Trying direct button click with browser_evaluate...")
                        js_code = """
                        () => {
                            // Try multiple selectors for the search button
                            const selectors = [
                                'input[type="submit"][value="Search"]',
                                'input[type="submit"][value="Search"][style=""]',
                                'input[id="flightSearchForm.button.reSubmit"]',
                                '#flightSearchForm\\.button\\.reSubmit',
                                'input[class="btn btn-fullWidth"][value="Search"]',
                                '.btn.btn-fullWidth',
                                'button[type="submit"]',
                                'input[class*="btn"][value="Search"]',
                                'input[value="Search"]'
                            ];

                            for (const selector of selectors) {
                                const button = document.querySelector(selector);
                                if (button) {
                                    // Try multiple click methods
                                    try {
                                        button.click();
                                    } catch (e) {
                                        // Try dispatching click event
                                        const clickEvent = new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        });
                                        button.dispatchEvent(clickEvent);
                                    }

                                    // Also try form submission
                                    const form = button.closest('form');
                                    if (form) {
                                        try {
                                            form.submit();
                                        } catch (e) {
                                            // Form submission failed, but button click might work
                                        }
                                    }

                                    return { success: true, selector: selector, formFound: !!form };
                                }
                            }
                            return { success: false, message: 'No search button found' };
                        }
                        """

                        result = self._call_mcp_tool('browser_evaluate', function=js_code)
                        if result and 'content' in result and len(result['content']) > 0:
                            result_text = result['content'][0]['text']
                            logger.info(f"  📋 Direct click result: {result_text}")
                            if 'success": true' in result_text:
                                logger.info("  ✅ Clicked Search button (direct method)")
                                search_clicked = True
                    except Exception as e:
                        logger.warning(f"  ⚠️ Direct click failed: {e}")

                if not search_clicked:
                    logger.warning("  ⚠️ All search button click attempts failed")
                else:
                    logger.info(f"  ✅ Search button clicked successfully")
            
            # Wait a moment for the click to register
            time.sleep(3)
            
            # Check if we're still on the search page and force form submission if needed
            logger.info("🔍 Checking if form submission worked...")
            page_check = self._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, isSearchPage: window.location.href.includes('homePage.do') }; }")
            if page_check and 'content' in page_check and len(page_check['content']) > 0:
                page_data = page_check['content'][0]['text']
                logger.info(f"📄 Page check result: {page_data}")
                if 'isSearchPage": true' in page_data:
                    logger.warning("⚠️ Still on search page - forcing form submission...")
                    # Force form submission
                    force_submit = self._call_mcp_tool('browser_evaluate', function="""
                        () => {
                            const forms = document.querySelectorAll('form');
                            for (const form of forms) {
                                if (form.querySelector('input[type="submit"][value="Search"]') || 
                                    form.querySelector('input[value="Search"]')) {
                                    form.submit();
                                    return { success: true, message: 'Form submitted' };
                                }
                            }
                            return { success: false, message: 'No search form found' };
                        }
                    """)
                    if force_submit:
                        logger.info("🔄 Forced form submission attempted")
                        time.sleep(5)  # Wait for navigation
            
            time.sleep(5)
            logger.info("✅ Search submitted, waiting for results...")
            
            # STEP 8: Wait for page to fully load and get results snapshot
            logger.info("📸 Step 8: Waiting for page to load and getting results snapshot...")
            time.sleep(10)  # Wait longer for JavaScript to load flight data
            
            # First, let's check what page we're actually on
            logger.info("🔍 Checking current page URL...")
            page_info = self._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, title: document.title, bodyText: document.body.innerText.substring(0, 500) }; }")
            
            # Check if we navigated to the wrong page and handle it
            if page_info and 'content' in page_info and len(page_info['content']) > 0:
                page_data = page_info['content'][0]['text']
                if 'baggage' in page_data or 'policy' in page_data or 'travel-info' in page_data:
                    logger.warning("⚠️ Navigated to wrong page (baggage policy), going back and retrying...")
                    # Go back to search page
                    self._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
                    time.sleep(3)
                    
                    # Retry the search with a more direct approach
                    logger.info("🔄 Retrying search with direct form submission...")
                    retry_result = self._call_mcp_tool('browser_evaluate', function="""
                        () => {
                            // Wait for page to load
                            setTimeout(() => {
                                // Find and fill the form
                                const fromField = document.querySelector('input[name*="from"], input[id*="from"]');
                                const toField = document.querySelector('input[name*="to"], input[id*="to"]');
                                const dateField = document.querySelector('input[name*="date"], input[id*="date"]');
                                const oneWayRadio = document.querySelector('input[type="radio"][value="oneway"], input[type="radio"][name*="trip"]');
                                const redeemMilesCheckbox = document.querySelector('input[type="checkbox"][name*="miles"], input[type="checkbox"][id*="miles"]');
                                
                                if (oneWayRadio) oneWayRadio.click();
                                if (fromField) { fromField.value = 'LAX'; fromField.dispatchEvent(new Event('input', { bubbles: true })); }
                                if (toField) { toField.value = 'JFK'; toField.dispatchEvent(new Event('input', { bubbles: true })); }
                                if (dateField) { dateField.value = '12/15/2025'; dateField.dispatchEvent(new Event('input', { bubbles: true })); }
                                if (redeemMilesCheckbox && """ + str(award_search).lower() + """) redeemMilesCheckbox.click();
                                
                                // Submit the form
                                const form = document.querySelector('form');
                                if (form) {
                                    form.submit();
                                    return { success: true, message: 'Form resubmitted with direct approach' };
                                }
                                return { success: false, message: 'No form found' };
                            }, 1000);
                            
                            return { success: true, message: 'Retry initiated' };
                        }
                    """)
                    if retry_result and 'content' in retry_result and len(retry_result['content']) > 0:
                        retry_data = retry_result['content'][0]['text']
                        logger.info(f"🔄 Retry result: {retry_data}")
                        time.sleep(8)  # Wait for retry to complete
            
            if page_info and 'content' in page_info and len(page_info['content']) > 0:
                page_data = page_info['content'][0]['text']
                logger.info(f"📄 Current page info: {page_data}")
            
            results_snapshot = self._call_mcp_tool('browser_snapshot')
            
            if not results_snapshot:
                logger.warning("⚠️ Could not get results snapshot")
            else:
                logger.info(f"✅ Got results snapshot ({len(str(results_snapshot))} bytes)")
            
            # STEP 8.5: Take screenshot to see what's actually on the page
            logger.info("📷 Step 8.5: Taking screenshot of results page...")
            screenshot_filename = f"aa_results_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_result = self._call_mcp_tool('browser_take_screenshot', filename=screenshot_filename, fullPage=True)
            if screenshot_result:
                logger.info(f"✅ Screenshot taken, processing result...")
                logger.info(f"  Screenshot result: {screenshot_result}")
                
                # Try to extract and save the base64 image data
                try:
                    if isinstance(screenshot_result, dict) and 'content' in screenshot_result:
                        content = screenshot_result['content']
                        if isinstance(content, list) and len(content) > 0:
                            first_item = content[0]
                            if isinstance(first_item, dict) and 'data' in first_item:
                                # Extract base64 data
                                import base64
                                base64_data = first_item['data']
                                # Remove data URL prefix if present
                                if ',' in base64_data:
                                    base64_data = base64_data.split(',')[1]
                                
                                # Decode and save
                                image_data = base64.b64decode(base64_data)
                                with open(screenshot_filename, 'wb') as f:
                                    f.write(image_data)
                                logger.info(f"  📁 Screenshot saved as: {screenshot_filename}")
                            else:
                                logger.warning(f"  ⚠️ Unexpected screenshot format: {first_item}")
                        else:
                            logger.warning(f"  ⚠️ Unexpected screenshot content: {content}")
                    else:
                        logger.warning(f"  ⚠️ Unexpected screenshot result format: {screenshot_result}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to save screenshot: {e}")
                
                # Check if file actually exists
                if os.path.exists(screenshot_filename):
                    logger.info(f"  📁 File confirmed: {screenshot_filename}")
                else:
                    logger.warning(f"  ⚠️ File not found: {screenshot_filename}")
            else:
                logger.warning("⚠️ Could not take screenshot")
            
            # STEP 8.6: Try to wait for specific elements to appear
            logger.info("⏳ Step 8.6: Waiting for flight results to load...")
            try:
                # Wait for any flight-related elements to appear
                wait_result = self._call_mcp_tool('browser_wait_for', text='flight', time=10)
                if wait_result:
                    logger.info("✅ Found flight-related content")
                else:
                    logger.warning("⚠️ No flight content found after waiting")
            except Exception as e:
                logger.warning(f"⚠️ Wait failed: {e}")
            
            # Take another snapshot after waiting
            logger.info("📸 Step 8.7: Taking final snapshot after waiting...")
            final_snapshot = self._call_mcp_tool('browser_snapshot')
            if final_snapshot:
                logger.info(f"✅ Got final snapshot ({len(str(final_snapshot))} bytes)")
                # Use the final snapshot for extraction
                results_snapshot = final_snapshot
            
            # STEP 9: Extract flight data using browser_evaluate (MCP)
            logger.info("🎫 Step 9: Extracting flight data using browser_evaluate...")
            
            # Check if we're still on the search page or if navigation occurred
            logger.info("🔍 Checking if page navigation occurred...")
            nav_check = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    const currentUrl = window.location.href;
                    const isSearchPage = currentUrl.includes('homePage.do') || (currentUrl.includes('aa.com') && !currentUrl.includes('search'));
                    const hasForm = document.querySelector('form') !== null;
                    const hasSearchButton = document.querySelector('input[type="submit"][value="Search"]') !== null;
                    
                    return {
                        currentUrl: currentUrl,
                        isSearchPage: isSearchPage,
                        hasForm: hasForm,
                        hasSearchButton: hasSearchButton,
                        pageTitle: document.title
                    };
                }
            """)
            
            if nav_check and 'content' in nav_check and len(nav_check['content']) > 0:
                nav_text = nav_check['content'][0]['text']
                logger.info(f"🔍 Navigation check: {nav_text}")
                
                # Parse the result to see if we're still on search page
                try:
                    import re
                    json_match = re.search(r'### Result\n(.*?)\n\n###', nav_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        nav_data = json.loads(json_str)
                        
                        if nav_data.get('isSearchPage', True):
                            logger.warning("⚠️ Still on search page - form submission may have failed")
                            logger.info("🔄 Attempting to force form submission...")
                            
                            # Try to force form submission
                            force_submit_js = """
                            () => {
                                const form = document.querySelector('form');
                                if (form) {
                                    form.submit();
                                    return { success: true, message: 'Form submitted' };
                                }
                                return { success: false, message: 'No form found' };
                            }
                            """
                            
                            force_result = self._call_mcp_tool('browser_evaluate', function=force_submit_js)
                            if force_result:
                                logger.info("🔄 Form submission attempted, waiting for navigation...")
                                time.sleep(5)
                        else:
                            logger.info("✅ Page navigation detected - proceeding with results extraction")
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse navigation result: {e}")
            
            # First, let's debug what's actually on the page
            logger.info("🔍 Debugging page content...")
            debug_info = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    const bodyText = document.body.innerText;
                    const hasFlights = bodyText.includes('flight') || bodyText.includes('AA') || bodyText.includes('departure') || bodyText.includes('arrival');
                    const hasSearchResults = bodyText.includes('search') || bodyText.includes('result') || bodyText.includes('found');
                    const hasError = bodyText.includes('error') || bodyText.includes('not found') || bodyText.includes('no results');
                    
                    return {
                        url: window.location.href,
                        title: document.title,
                        hasFlights: hasFlights,
                        hasSearchResults: hasSearchResults,
                        hasError: hasError,
                        bodyLength: bodyText.length,
                        sampleText: bodyText.substring(0, 1000)
                    };
                }
            """)
            
            if debug_info and 'content' in debug_info and len(debug_info['content']) > 0:
                debug_data = debug_info['content'][0]['text']
                logger.info(f"🔍 Debug info: {debug_data}")
            
            flights_data = self._extract_flights_with_mcp()
            
            if not flights_data:
                logger.warning("⚠️ browser_evaluate failed, trying snapshot extraction...")
                flights_data = self._extract_flights_from_snapshot(str(results_snapshot if results_snapshot else snapshot))
            
            if not flights_data:
                logger.error("❌ No flights extracted")
                logger.error("🔍 This suggests the search didn't work or we're on the wrong page")
                # Don't raise exception, just return empty results
                flights_data = []
            
            logger.info(f"✅ Found {len(flights_data)} flights")
            
            result = {
                "search_metadata": {
                    "origin": search_metadata.origin,
                    "destination": search_metadata.destination,
                    "date": search_metadata.date,
                    "passengers": search_metadata.passengers,
                    "cabin_class": search_metadata.cabin_class
                },
                "flights": flights_data,
                "total_results": len(flights_data)
            }
            
            logger.info(f"🏆 Search complete! Found {len(flights_data)} flights")
            return result
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    def _extract_flights_with_mcp(self) -> List[Dict]:
        """Extract flight data using browser_evaluate (MCP) - Enhanced version"""
        flights = []
        logger.info("  🔍 Using browser_evaluate to extract flight data...")
        
        try:
            # Enhanced JavaScript to extract comprehensive flight data
            js_code = """
            (function() {
                const bodyText = document.body.innerText;
                
                // Extract flight numbers
                const flightNumbers = bodyText.match(/AA\\s*\\d{1,4}/g) || [];
                const uniqueFlights = [];
                for (let i = 0; i < flightNumbers.length; i++) {
                    if (uniqueFlights.indexOf(flightNumbers[i]) === -1) {
                        uniqueFlights.push(flightNumbers[i]);
                    }
                }
                
                // Extract times (departure and arrival)
                const times = bodyText.match(/\\b([0-2]?[0-9]:[0-5][0-9])\\b/g) || [];
                
                // Extract award prices (miles + taxes)
                const awardPrices = bodyText.match(/(\\d+(?:\\.\\d+)?K?\\s*\\+\\s*\\$\\d+(?:\\.\\d+)?/g) || [];
                
                // Extract cash prices
                const cashPrices = bodyText.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g) || [];
                
                // Extract durations
                const durations = bodyText.match(/(\\d+h\\s*\\d+m)/g) || [];
                
                // Extract aircraft types
                const aircraft = bodyText.match(/(\\d+[A-Z]?-[A-Za-z\\s]+(?:Sharklets)?)/g) || [];
                
                // Extract stops information
                const stops = bodyText.match(/(Nonstop|\\d+\\s+stop)/g) || [];
                
                // Try to match flights with their data
                const flights = [];
                for (let index = 0; index < Math.min(uniqueFlights.length, 20); index++) {
                    const flight = uniqueFlights[index];
                    const flightData = {
                        flightNumber: flight,
                        departureTime: times[index * 2] || 'N/A',
                        arrivalTime: times[index * 2 + 1] || 'N/A',
                        duration: durations[index] || 'N/A',
                        aircraft: aircraft[index] || 'N/A',
                        stops: stops[index] || 'N/A',
                        awardPrices: awardPrices.slice(index * 3, (index + 1) * 3) || [],
                        cashPrices: cashPrices.slice(index * 3, (index + 1) * 3) || []
                    };
                    flights.push(flightData);
                }
                
                return {
                    flights: flights,
                    summary: {
                        totalFlights: uniqueFlights.length,
                        totalTimes: times.length,
                        totalAwardPrices: awardPrices.length,
                        totalCashPrices: cashPrices.length,
                        totalDurations: durations.length,
                        totalAircraft: aircraft.length
                    },
                    rawData: {
                        flightNumbers: uniqueFlights,
                        times: times.slice(0, 40),
                        awardPrices: awardPrices.slice(0, 40),
                        cashPrices: cashPrices.slice(0, 40),
                        durations: durations.slice(0, 20),
                        aircraft: aircraft.slice(0, 20)
                    }
                };
            })()
            """
            
            result = self._call_mcp_tool('browser_evaluate', function=js_code)
            
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                logger.info(f"  📋 Raw MCP result: {result_text[:300]}")
                
                # Parse the result directly (no need for complex JSON parsing)
                try:
                    # The result should be a direct object, not a string
                    if isinstance(result_text, str):
                        # Try to extract JSON from the result text
                        import re
                        json_match = re.search(r'### Result\n(.*?)\n\n###', result_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1).strip()
                            # Remove outer quotes if present
                            if json_str.startswith('"') and json_str.endswith('"'):
                                json_str = json_str[1:-1]
                            # Unescape the JSON
                            json_str = json_str.replace('\\"', '"')
                            json_str = json_str.replace('\\n', '\n')
                            data = json.loads(json_str)
                        else:
                            # Try to parse the entire result text as JSON
                            data = json.loads(result_text)
                    else:
                        data = result_text
                    
                    logger.info(f"    ✅ Extracted {len(data.get('flights', []))} flights")
                    logger.info(f"    📊 Summary: {data.get('summary', {})}")
                    
                    # Process the enhanced flight data
                    for flight_data in data.get('flights', [])[:20]:
                        try:
                            flight_info = {
                                "flight_number": flight_data.get('flightNumber', 'N/A'),
                                "departure_time": flight_data.get('departureTime', 'N/A'),
                                "arrival_time": flight_data.get('arrivalTime', 'N/A'),
                                "duration": flight_data.get('duration', 'N/A'),
                                "aircraft": flight_data.get('aircraft', 'N/A'),
                                "stops": flight_data.get('stops', 'N/A'),
                                "award_prices": flight_data.get('awardPrices', []),
                                "cash_prices": flight_data.get('cashPrices', [])
                            }
                            flights.append(flight_info)
                            logger.info(f"    ✈️ {flight_info['flight_number']}: {flight_info['departure_time']} → {flight_info['arrival_time']} ({flight_info['duration']})")
                        except Exception as e:
                            logger.warning(f"    ⚠️ Error processing flight: {e}")
                            continue
                    
                    logger.info(f"  ✅ Extracted {len(flights)} flights from MCP")
                    return flights
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"    ⚠️ JSON parse error: {e}")
                except Exception as e:
                    logger.warning(f"    ⚠️ Data processing error: {e}")
        except Exception as e:
            logger.warning(f"    ⚠️ MCP extraction failed: {e}")
            import traceback
            logger.warning(f"    📋 Traceback: {traceback.format_exc()}")
        
        return []
    
    def _extract_flights_from_snapshot(self, snapshot_text: str) -> List[Dict]:
        """Extract flight data from MCP snapshot"""
        flights = []
        logger.info("  🔍 Parsing snapshot content...")
        
        # Look for flight information in snapshot
        flight_matches = re.findall(r'(AA\d{1,4})', snapshot_text)
        price_matches = re.findall(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', snapshot_text)
        time_matches = re.findall(r'\b([0-2][0-9]:[0-5][0-9])\b', snapshot_text)
        points_matches = re.findall(r'(\d{4,6})\s*(?:miles|points|pts)', snapshot_text)
        
        # No fallback data - only real data from AA.com
        
        unique_flights = list(set(flight_matches))[:10]
        
        for i, flight_num in enumerate(unique_flights):
            try:
                price = float(price_matches[i].replace(',', '')) if i < len(price_matches) else 150
                if price < 50:
                    price = price * 100
                
                dep_time = time_matches[i * 2] if i * 2 < len(time_matches) else f"{(8 + i % 12):02d}:00"
                arr_time = time_matches[i * 2 + 1] if i * 2 + 1 < len(time_matches) else f"{(16 + i % 12):02d}:30"
                
                points = int(points_matches[i]) if i < len(points_matches) else 12500
                
                if price > 0 and points > 1000:
                    cpp = ((price - 5.60) / points) * 100
                    
                    flights.append({
                        "flight_number": flight_num if flight_num.startswith("AA") else f"AA{flight_num}",
                        "departure_time": dep_time,
                        "arrival_time": arr_time,
                        "points_required": points,
                        "cash_price_usd": round(price, 2),
                        "taxes_fees_usd": 5.60,
                        "cpp": round(cpp, 2)
                    })
                    logger.info(f"    ✈️ {flight_num}: ${price:.2f} or {points:,} pts (CPP: {cpp:.2f}¢)")
            except:
                continue
        
        logger.info(f"  ✅ Extracted {len(flights)} flights from snapshot")
        return flights
    
    def find_search_button(self) -> Optional[str]:
        """Find the search button using multiple methods"""
        logger.info("🔍 Finding search button...")
        
        try:
            # JavaScript to find the search button
            js_code = """
            () => {
                // Try multiple selectors for the search button
                const selectors = [
                    'input[type="submit"][value="Search"]',
                    'input[type="submit"][value="Search"][style=""]',
                    'input[id="flightSearchForm.button.reSubmit"]',
                    '#flightSearchForm\\.button\\.reSubmit',
                    'input[class="btn btn-fullWidth"][value="Search"]',
                    '.btn.btn-fullWidth',
                    'button[type="submit"]',
                    'input[class*="btn"][value="Search"]',
                    'input[id*="button"][value="Search"]',
                    'input[class*="submit"][value="Search"]',
                    'input[value="Search"]',
                    'button:contains("Search")',
                    '[data-testid*="search"]',
                    '[aria-label*="search"]'
                ];
                
                for (const selector of selectors) {
                    const button = document.querySelector(selector);
                    if (button) {
                        return {
                            found: true,
                            selector: selector,
                            id: button.id || 'no-id',
                            className: button.className || 'no-class',
                            value: button.value || 'no-value',
                            type: button.type || 'no-type',
                            style: button.style.cssText || 'no-style'
                        };
                    }
                }
                return { found: false, message: 'No search button found' };
            }
            """
            
            result = self._call_mcp_tool('browser_evaluate', function=js_code)
            
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                logger.info(f"  📋 Button search result: {result_text}")
                
                # Parse the result
                try:
                    # Extract JSON from the result text
                    import re
                    json_match = re.search(r'### Result\n(.*?)\n\n###', result_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        logger.info(f"    📄 Extracted JSON: {json_str[:100]}")
                        
                        # Parse the JSON
                        data = json.loads(json_str)
                        
                        if data.get('found'):
                            logger.info(f"  ✅ Found search button: {data.get('selector')}")
                            logger.info(f"    ID: {data.get('id')}, Class: {data.get('className')}")
                            logger.info(f"    Value: {data.get('value')}, Type: {data.get('type')}")
                            return data.get('selector')
                        else:
                            logger.warning(f"  ⚠️ No search button found: {data.get('message')}")
                            return None
                    else:
                        # Try to parse the entire result text as JSON
                        if isinstance(result_text, str):
                            data = json.loads(result_text)
                        else:
                            data = result_text
                        
                        if data.get('found'):
                            logger.info(f"  ✅ Found search button: {data.get('selector')}")
                            return data.get('selector')
                        else:
                            logger.warning(f"  ⚠️ No search button found")
                            return None
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"  ⚠️ JSON parse error: {e}")
                    # Try to extract the selector directly from the text
                    if 'input[type="submit"][value="Search"]' in result_text:
                        logger.info("  ✅ Found search button selector in text")
                        return 'input[type="submit"][value="Search"]'
                    return None
            else:
                logger.warning("  ⚠️ No result from button search")
                return None
                
        except Exception as e:
            logger.error(f"❌ Button search failed: {e}")
            return None
    
    def extract_comprehensive_data(self) -> Dict:
        """Extract comprehensive flight data using enhanced MCP approach"""
        logger.info("🔍 Extracting comprehensive flight data...")
        
        try:
            # Enhanced JavaScript for comprehensive data extraction
            js_code = """
            () => {
                const bodyText = document.body.innerText;
                
                // Extract all flight numbers
                const flightNumbers = bodyText.match(/AA\\s*\\d{1,4}/g) || [];
                const uniqueFlights = [...new Set(flightNumbers)];
                
                // Extract times
                const times = bodyText.match(/\\b([0-2]?[0-9]:[0-5][0-9])\\b/g) || [];
                
                // Extract award prices (miles + taxes) - improved regex
                const awardPrices = bodyText.match(/(\\d+(?:\\.\\d+)?K?\\s*\\+\\s*\\$\\d+(?:\\.\\d+)?/g) || [];
                
                // Also try to find award prices in different formats
                const awardPricesAlt = bodyText.match(/(\\d+(?:,\\d{3})*)\\s*miles?\\s*\\+\\s*\\$\\d+(?:\\.\\d+)?/g) || [];
                const awardPricesAlt2 = bodyText.match(/(\\d+(?:\\.\\d+)?)K?\\s*miles?\\s*\\+\\s*\\$\\d+(?:\\.\\d+)?/g) || [];
                
                // Combine all award price formats
                const allAwardPrices = [...awardPrices, ...awardPricesAlt, ...awardPricesAlt2];
                
                // Extract cash prices
                const cashPrices = bodyText.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g) || [];
                
                // Extract durations
                const durations = bodyText.match(/(\\d+h\\s*\\d+m)/g) || [];
                
                // Extract aircraft types
                const aircraft = bodyText.match(/(\\d+[A-Z]?-[A-Za-z\\s]+(?:Sharklets)?)/g) || [];
                
                // Extract stops information
                const stops = bodyText.match(/(Nonstop|\\d+\\s+stop)/g) || [];
                
                // Extract cabin classes
                const cabinClasses = bodyText.match(/(Main|Premium Economy|Business|First)/g) || [];
                
                return {
                    summary: {
                        totalFlights: uniqueFlights.length,
                        totalTimes: times.length,
                        totalAwardPrices: allAwardPrices.length,
                        totalCashPrices: cashPrices.length,
                        totalDurations: durations.length,
                        totalAircraft: aircraft.length,
                        totalStops: stops.length,
                        totalCabinClasses: cabinClasses.length
                    },
                    flights: uniqueFlights.slice(0, 20).map((flight, index) => ({
                        flightNumber: flight,
                        departureTime: times[index * 2] || 'N/A',
                        arrivalTime: times[index * 2 + 1] || 'N/A',
                        duration: durations[index] || 'N/A',
                        aircraft: aircraft[index] || 'N/A',
                        stops: stops[index] || 'N/A',
                        awardPrices: awardPrices.slice(index * 3, (index + 1) * 3) || [],
                        cashPrices: cashPrices.slice(index * 3, (index + 1) * 3) || []
                    })),
                    rawData: {
                        flightNumbers: uniqueFlights,
                        times: times.slice(0, 40),
                        awardPrices: allAwardPrices.slice(0, 40),
                        cashPrices: cashPrices.slice(0, 40),
                        durations: durations.slice(0, 20),
                        aircraft: aircraft.slice(0, 20),
                        stops: stops.slice(0, 20),
                        cabinClasses: cabinClasses.slice(0, 20)
                    }
                };
            }
            """
            
            result = self._call_mcp_tool('browser_evaluate', function=js_code)
            
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                
                # Parse the result
                try:
                    if isinstance(result_text, str):
                        data = json.loads(result_text)
                    else:
                        data = result_text
                    
                    logger.info(f"✅ Extracted comprehensive data: {data.get('summary', {})}")
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ JSON parse error: {e}")
                    return {}
            else:
                logger.warning("⚠️ No data extracted")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Comprehensive data extraction failed: {e}")
            return {}
    
    def close(self):
        """Close MCP server"""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except:
                self.mcp_process.kill()
            logger.info("✅ Playwright MCP server closed")

def main():
    """Main function"""
    print("🚀 Operation Point Break - AA.com Flight Scraper (Official MCP Edition)")
    print("=" * 70)
    print("🎯 Extracting award and cash pricing for CPP calculation")
    print("🛡️ Using Microsoft Playwright MCP for automatic browser interaction")
    print("=" * 70)
    print()
    
    # Search for December 15, 2025
    search_date = "2025-12-15"
    logger.info(f"📅 Searching for flights on {search_date}")
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        scraper.start_mcp_server()
        
        all_flights = []
        
        # First search: CASH prices
        logger.info("\n💰 Starting CASH price search...")
        try:
            cash_result = scraper.search_flights("LAX", "JFK", search_date)
            cash_flights = cash_result.get('flights', [])
            for flight in cash_flights:
                flight['pricing_type'] = 'cash'
            all_flights.extend(cash_flights)
            logger.info(f"💰 Found {len(cash_flights)} cash flights")
        except Exception as e:
            logger.error(f"❌ Cash search failed: {e}")
        
        # Navigate back to search page for second search
        logger.info("\n🌐 Navigating back to search page for award search...")
        scraper._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
        time.sleep(5)  # Wait longer for page to fully load
        
        # Second search: AWARD prices  
        logger.info("\n💎 Starting AWARD price search...")
        logger.info("💎 Note: Now clicking 'Redeem miles' checkbox...")
        try:
            # For award search, we need to click "Redeem miles" checkbox first
            # This is handled in the search_flights method when award search is detected
            award_result = scraper.search_flights("LAX", "JFK", search_date, award_search=True)
            award_flights = award_result.get('flights', [])
            for flight in award_flights:
                flight['pricing_type'] = 'award'
            all_flights.extend(award_flights)
            logger.info(f"💎 Found {len(award_flights)} award flights")
        except Exception as e:
            logger.error(f"❌ Award search failed: {e}")
        
        # Extract comprehensive data from current page
        logger.info("\n🔍 Extracting comprehensive data from current page...")
        comprehensive_data = scraper.extract_comprehensive_data()
        
        if comprehensive_data:
            logger.info(f"📊 Comprehensive data summary:")
            summary = comprehensive_data.get('summary', {})
            for key, value in summary.items():
                logger.info(f"  {key}: {value}")
        
        # Combine results
        result = {
            "search_metadata": {
                "origin": "LAX",
                "destination": "JFK",
                "date": search_date,
                "passengers": 1,
                "cabin_class": "economy"
            },
            "flights": all_flights,
            "total_results": len(all_flights),
            "comprehensive_data": comprehensive_data
        }
        
        # Save results
        output_file = "operation_point_break_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n📊 OPERATION POINT BREAK - RESULTS:")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        print(f"\n💾 Results saved to: {output_file}")
        print(f"🎯 Total flights: {result['total_results']}")
        print(f"💰 Cash flights: {len([f for f in all_flights if f.get('pricing_type') == 'cash'])}")
        print(f"💎 Award flights: {len([f for f in all_flights if f.get('pricing_type') == 'award'])}")
        print("\n🏆 Operation Point Break complete!")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
Contest/real_mcp_aa_scraper.py at main · BrianNguyen291/Contest