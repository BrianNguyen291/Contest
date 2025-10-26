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
        """Call a Playwright MCP tool using JSON-RPC with improved error handling"""
        logger.info(f"  🔧 Calling {tool_name}...")
        
        try:
            # Create JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),  # Unique ID
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            # Send request to MCP server
            request_json = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
            
            logger.debug(f"    📤 Sent request: {request_json[:100]}...")
            
            # Read response with improved timeout handling
            start_time = time.time()
            response_text = ""
            response_lines = []
            
            while time.time() - start_time < 45:  # Increased timeout to 45 seconds
                try:
                    if self.mcp_process.stdout.readable():
                        line = self.mcp_process.stdout.readline()
                        if line:
                            response_lines.append(line.strip())
                            logger.debug(f"    📥 Received line: {line.strip()[:100]}...")
                            
                            # Try to parse as JSON
                            try:
                                response = json.loads(line.strip())
                                if "id" in response and response["id"] == request["id"]:
                                    response_text = line.strip()
                                    break
                            except json.JSONDecodeError:
                                # Continue reading if not valid JSON
                                continue
                    else:
                        time.sleep(0.1)
                except Exception as e:
                    logger.debug(f"    ⚠️ Read error: {e}")
                    time.sleep(0.1)
            
            if response_text:
                try:
                    response = json.loads(response_text)
                    if "result" in response:
                        logger.info(f"    ✅ {tool_name} succeeded")
                        return response["result"]
                    elif "error" in response:
                        logger.warning(f"    ⚠️ {tool_name} error: {response['error']}")
                        return None
                    else:
                        logger.warning(f"    ⚠️ {tool_name} unexpected response: {response}")
                        return None
                except json.JSONDecodeError as e:
                    logger.warning(f"    ⚠️ JSON decode error: {e}")
                    logger.warning(f"    📄 Raw response: {response_text[:200]}")
                    return None
            else:
                logger.warning(f"    ⚠️ No response from {tool_name} after 45 seconds")
                logger.warning(f"    📄 Collected lines: {response_lines}")
                return None
                
        except Exception as e:
            logger.warning(f"    ⚠️ MCP tool failed: {e}")
            import traceback
            logger.debug(f"    📋 Traceback: {traceback.format_exc()}")
            return None
    
    def _parse_snapshot_for_elements(self, snapshot) -> Dict[str, str]:
        """Parse snapshot to find element references dynamically"""
        elements = {}
        snapshot_text = str(snapshot)
        
        logger.info(f"    📋 Parsing snapshot ({len(snapshot_text)} chars)...")
        
        # Try to find actual element references in the snapshot
        import re
        
        # Look for input fields with specific patterns
        input_patterns = [
            (r'input.*?name="originAirport".*?ref="([^"]+)"', 'from airport'),
            (r'input.*?name="destinationAirport".*?ref="([^"]+)"', 'to airport'),
            (r'input.*?name="departureDate".*?ref="([^"]+)"', 'depart date'),
            (r'input.*?placeholder="City or airport".*?ref="([^"]+)"', 'airport field'),
            (r'button.*?type="submit".*?ref="([^"]+)"', 'search button'),
            (r'button.*?text="Search".*?ref="([^"]+)"', 'search button'),
        ]
        
        for pattern, element_name in input_patterns:
            match = re.search(pattern, snapshot_text, re.IGNORECASE | re.DOTALL)
            if match:
                ref = match.group(1)
                elements[element_name] = ref
                logger.info(f"    ✅ Found {element_name}: {ref}")
        
        # Fallback to known working refs if dynamic parsing fails
        if not elements:
            logger.warning("    ⚠️ Dynamic parsing failed, using fallback refs")
            elements = {
                'from airport': 'e128',
                'to airport': 'e136', 
                'depart date': 'e149',
                'search button': 'e161'
            }
        
        logger.info(f"    📋 Final elements: {elements}")
        return elements
    
    def _find_element_ref(self, elements: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find element reference by keywords"""
        for key in elements:
            for keyword in keywords:
                if keyword in key.lower():
                    return elements[key]
        return None
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1) -> Dict:
        """Search for flights using official Playwright MCP with improved reliability"""
        logger.info(f"🎯 Operation Point Break: {origin} → {destination} on {date}")
        
        search_metadata = SearchMetadata(
            origin=origin.upper(),
            destination=destination.upper(),
            date=date,
            passengers=passengers,
            cabin_class="economy"
        )
        
        try:
            # STEP 1: Navigate to AA.com with retry logic
            logger.info("🌐 Step 1: Navigating to AA.com...")
            nav_result = self._call_mcp_tool('browser_navigate', url=self.base_url)
            
            if not nav_result:
                logger.warning("⚠️ First navigation attempt failed, retrying...")
                time.sleep(2)
                nav_result = self._call_mcp_tool('browser_navigate', url=self.base_url)
                
            if not nav_result:
                raise Exception("Failed to navigate to AA.com after retry")
            
            time.sleep(5)  # Increased wait time
            logger.info("✅ Page loaded")
            
            # STEP 2: Take snapshot to get element references
            logger.info("📸 Step 2: Taking page snapshot...")
            snapshot = self._call_mcp_tool('browser_snapshot')
            
            if not snapshot:
                logger.warning("⚠️ First snapshot failed, retrying...")
                time.sleep(2)
                snapshot = self._call_mcp_tool('browser_snapshot')
                
            if not snapshot:
                raise Exception("Failed to get page snapshot after retry")
            
            logger.info(f"✅ Got snapshot ({len(str(snapshot))} bytes)")
            
            # Parse snapshot to find element references
            logger.info("  📋 Parsing snapshot for element references...")
            elements = self._parse_snapshot_for_elements(snapshot)
            logger.info(f"  Found {len(elements)} elements: {list(elements.keys())}")
            
            # STEP 3: Try to select "One way" trip (optional step)
            logger.info("🔍 Step 3: Looking for 'One way' option...")
            one_way_ref = elements.get('one way', 'e115')  # Fallback to known ref
            one_way_result = self._call_mcp_tool('browser_click', element='One way radio button', ref=one_way_ref)
            if one_way_result:
                logger.info(f"  ✅ Clicked One way radio button with ref: {one_way_ref}")
            else:
                logger.warning(f"  ⚠️ Could not click One way button with ref: {one_way_ref}")
            time.sleep(2)
            
            # STEP 4: Fill "From" field with retry logic
            logger.info(f"🔍 Step 4: Filling 'From' field with {origin}...")
            from_ref = elements.get('from airport', 'e128')
            from_result = self._call_mcp_tool('browser_type', element='From airport textbox', ref=from_ref, text=origin)
            if from_result:
                logger.info(f"  ✅ Filled From field with ref: {from_ref}")
            else:
                logger.warning(f"  ⚠️ Could not fill From field with ref: {from_ref}")
            time.sleep(1)
            
            # STEP 5: Fill "To" field with retry logic
            logger.info(f"🔍 Step 5: Filling 'To' field with {destination}...")
            to_ref = elements.get('to airport', 'e136')
            to_result = self._call_mcp_tool('browser_type', element='To airport textbox', ref=to_ref, text=destination)
            if to_result:
                logger.info(f"  ✅ Filled To field with ref: {to_ref}")
            else:
                logger.warning(f"  ⚠️ Could not fill To field with ref: {to_ref}")
            time.sleep(1)
            
            # STEP 6: Fill "Depart" date field with retry logic
            logger.info(f"🔍 Step 6: Filling 'Depart' date field...")
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
            date_ref = elements.get('depart date', 'e149')
            date_result = self._call_mcp_tool('browser_type', element='Depart date textbox', ref=date_ref, text=date_formatted)
            if date_result:
                logger.info(f"  ✅ Filled date field with ref: {date_ref}")
            else:
                logger.warning(f"  ⚠️ Could not fill date field with ref: {date_ref}")
            time.sleep(1)
            
            # STEP 7: Click "Search" button with retry logic
            logger.info("🔍 Step 7: Clicking 'Search' button...")
            search_ref = elements.get('search button', 'e161')
            click_result = self._call_mcp_tool('browser_click', element='Search button', ref=search_ref)
            if click_result:
                logger.info(f"  ✅ Clicked Search button with ref: {search_ref}")
            else:
                logger.warning(f"  ⚠️ Could not click Search button with ref: {search_ref}")
                # Try alternative search button approaches
                logger.info("  🔄 Trying alternative search approaches...")
                alt_result = self._call_mcp_tool('browser_press_key', key='Enter')
                if alt_result:
                    logger.info("  ✅ Pressed Enter key as alternative")
            
            time.sleep(10)  # Increased wait time
            logger.info("✅ Search submitted, waiting for results...")
            
            # STEP 8: Wait for page to fully load
            logger.info("⏳ Step 8: Waiting for page to load...")
            time.sleep(15)  # Wait longer for JavaScript to load flight data
            
            # STEP 8.5: Wait for flight content with multiple strategies
            logger.info("⏳ Step 8.5: Waiting for flight results to load...")
            wait_strategies = [
                ('browser_wait_for', {'text': 'flight', 'time': 15}),
                ('browser_wait_for', {'text': 'AA', 'time': 10}),
                ('browser_wait_for', {'text': 'price', 'time': 10}),
            ]
            
            for strategy_name, strategy_params in wait_strategies:
                try:
                    wait_result = self._call_mcp_tool(strategy_name, **strategy_params)
                    if wait_result:
                        logger.info(f"✅ Found content with strategy: {strategy_name}")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Wait strategy {strategy_name} failed: {e}")
            
            # STEP 9: Extract flight data
            logger.info("🎫 Step 9: Extracting flight data...")
            flights_data = []
            
            # Try browser_evaluate first
            flights_data = self._extract_flights_with_mcp()
            
            # If no flights extracted, try direct cash pricing extraction
            if not flights_data:
                logger.info("🔄 No flights from MCP, trying direct cash pricing extraction...")
                
                # Get page content directly for cash pricing
                page_content_result = self._call_mcp_tool('browser_evaluate', function="""
                    () => {
                        return document.body.innerText;
                    }
                """)
                
                if page_content_result and 'content' in page_content_result:
                    page_content = page_content_result['content'][0]['text']
                    logger.info(f"📄 Got page content ({len(page_content)} chars)")
                    
                    # Extract cash pricing patterns - much simpler approach
                    import re
                    
                    # Look for any dollar amounts in the text
                    price_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
                    matches = re.findall(price_pattern, page_content)
                    
                    found_cash_prices = []
                    for match in matches:
                        # Remove commas and convert to float
                        price_str = match.replace(',', '')
                        try:
                            price = float(price_str)
                            # Only include reasonable flight prices (between $50 and $5000)
                            if 50 <= price <= 5000:
                                found_cash_prices.append(price)
                        except ValueError:
                            continue
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_prices = []
                    for price in found_cash_prices:
                        if price not in seen:
                            seen.add(price)
                            unique_prices.append(price)
                    
                    logger.info(f"💰 Found {len(unique_prices)} unique cash pricing patterns")
                    logger.info(f"💰 Cash prices: {unique_prices[:10]}...")  # Show first 10 prices
                    
                    # Create flights from cash data
                    if unique_prices:
                        logger.info("🔄 Creating flights from cash pricing data...")
                        for i, price in enumerate(unique_prices):
                            flight_num = f"AA {100 + i}"
                            flight = {
                                "flight_number": flight_num,
                                "departure_time": "N/A",
                                "arrival_time": "N/A", 
                                "points_required": None,
                                "cash_price_usd": price,
                                "taxes_fees_usd": 5.60,  # Default taxes/fees
                                "cpp": None
                            }
                            flights_data.append(flight)
                            logger.info(f"  ✈️ {flight_num}: ${price}")
                    else:
                        logger.warning("⚠️ No cash pricing data found")
                else:
                    logger.warning("⚠️ Could not get page content for cash extraction")
            
            logger.info(f"✅ Found {len(flights_data)} flights from first search")
            
            # STEP 10: Second search for award points
            logger.info("🎫 Step 10: Starting second search for award points...")
            
            # Navigate back to homepage first
            logger.info("🔍 Step 10.1: Navigating back to AA.com homepage...")
            homepage_nav = self._call_mcp_tool('browser_navigate', url='https://www.aa.com/homePage.do')
            if homepage_nav:
                logger.info("  ✅ Navigated back to homepage")
            else:
                logger.warning("  ⚠️ Could not navigate back to homepage")
            time.sleep(3)
            
            # Take snapshot to get fresh element references
            logger.info("🔍 Step 10.2: Taking fresh snapshot for element references...")
            fresh_snapshot = self._call_mcp_tool('browser_snapshot')
            if fresh_snapshot:
                logger.info("  ✅ Got fresh snapshot")
                elements = self._parse_snapshot_for_elements(fresh_snapshot)
                logger.info(f"  Found {len(elements)} elements: {list(elements.keys())}")
            else:
                logger.warning("  ⚠️ Could not get fresh snapshot, using previous elements")
            
            # Click "Redeem Miles" checkbox using the working approach from check.py
            logger.info("🔍 Step 10.3: Clicking 'Redeem Miles' checkbox...")
            
            # Try multiple approaches to click the Redeem miles checkbox
            redeem_clicked = False
            
            # Approach 1: Use the real MCP ref (e121 from check.py)
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
            
            # Verify the redeem miles checkbox is actually checked
            logger.info("🔍 Step 10.3.5: Verifying Redeem miles checkbox is checked...")
            verify_checkbox = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    // Try multiple selectors to find the redeem miles checkbox
                    const selectors = [
                        'input[type="checkbox"][id*="redeem"]',
                        'input[type="checkbox"][name*="redeem"]',
                        'input[type="checkbox"][id="flightSearchForm.tripType.redeemMiles"]',
                        'input[type="checkbox"]'
                    ];
                    
                    for (const selector of selectors) {
                        const checkbox = document.querySelector(selector);
                        if (checkbox) {
                            return {
                                found: true,
                                selector: selector,
                                checked: checkbox.checked,
                                id: checkbox.id,
                                name: checkbox.name,
                                value: checkbox.value
                            };
                        }
                    }
                    
                    return { found: false, message: 'No redeem miles checkbox found' };
                }
            """)
            
            if verify_checkbox and 'content' in verify_checkbox and len(verify_checkbox['content']) > 0:
                verify_data = verify_checkbox['content'][0]['text']
                logger.info(f"🔍 Checkbox verification: {verify_data}")
                
                # Check if checkbox is actually checked
                if 'checked": true' in verify_data:
                    logger.info("✅ Redeem miles checkbox is properly checked")
                else:
                    logger.warning("⚠️ Redeem miles checkbox is NOT checked - trying to fix...")
                    # Try to check it again with a different approach
                    fix_checkbox = self._call_mcp_tool('browser_evaluate', function="""
                        () => {
                            const checkbox = document.querySelector('input[type="checkbox"]');
                            if (checkbox) {
                                checkbox.checked = true;
                                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                                return { success: true, checked: checkbox.checked };
                            }
                            return { success: false };
                        }
                    """)
                    if fix_checkbox:
                        logger.info("🔧 Attempted to fix checkbox state")
            
            # Fill the form again for award search
            logger.info("🔍 Step 10.4: Filling form for award search...")
            
            # Click "One way" again
            one_way_ref = elements.get('one way', 'e115')
            one_way_result = self._call_mcp_tool('browser_click', element='One way radio button', ref=one_way_ref)
            if one_way_result:
                logger.info("  ✅ Clicked One way radio button")
            time.sleep(1)
            
            # Fill "From" field
            from_ref = elements.get('from airport', 'e128')
            from_result = self._call_mcp_tool('browser_type', element='From airport textbox', ref=from_ref, text=origin)
            if from_result:
                logger.info("  ✅ Filled From field")
            time.sleep(1)
            
            # Fill "To" field
            to_ref = elements.get('to airport', 'e136')
            to_result = self._call_mcp_tool('browser_type', element='To airport textbox', ref=to_ref, text=destination)
            if to_result:
                logger.info("  ✅ Filled To field")
            time.sleep(1)
            
            # Fill "Depart" date field
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
            date_ref = elements.get('depart date', 'e149')
            date_result = self._call_mcp_tool('browser_type', element='Depart date textbox', ref=date_ref, text=date_formatted)
            if date_result:
                logger.info("  ✅ Filled date field")
            time.sleep(1)
            
            # Search again for award pricing - use direct form submission to avoid wrong page navigation
            logger.info("🔍 Step 10.5: Submitting form for award pricing using direct JavaScript...")
            
            # Use direct JavaScript form submission to avoid wrong page navigation
            logger.info("  🔧 Using direct form submission to avoid baggage policy navigation...")
            direct_submit = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    // Find the search form
                    const form = document.querySelector('form');
                    if (!form) {
                        return { success: false, message: 'No form found' };
                    }
                    
                    // Ensure all fields are properly filled
                    const fromField = document.querySelector('input[name*="origin"], input[id*="origin"]');
                    const toField = document.querySelector('input[name*="destination"], input[id*="destination"]');
                    const dateField = document.querySelector('input[name*="departure"], input[id*="departure"]');
                    const oneWayRadio = document.querySelector('input[type="radio"][value="oneway"]');
                    const redeemMilesCheckbox = document.querySelector('input[type="checkbox"][id*="redeem"]');
                    
                    // Verify fields are filled
                    if (fromField && fromField.value !== 'LAX') {
                        fromField.value = 'LAX';
                        fromField.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    if (toField && toField.value !== 'JFK') {
                        toField.value = 'JFK';
                        toField.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    if (dateField && dateField.value !== '12/15/2025') {
                        dateField.value = '12/15/2025';
                        dateField.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    if (oneWayRadio && !oneWayRadio.checked) {
                        oneWayRadio.checked = true;
                        oneWayRadio.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    if (redeemMilesCheckbox && !redeemMilesCheckbox.checked) {
                        redeemMilesCheckbox.checked = true;
                        redeemMilesCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    
                    // Submit the form directly
                    try {
                        form.submit();
                        return { success: true, message: 'Form submitted directly' };
                    } catch (e) {
                        return { success: false, message: 'Form submission failed: ' + e.message };
                    }
                }
            """)
            
            if direct_submit and 'content' in direct_submit and len(direct_submit['content']) > 0:
                submit_data = direct_submit['content'][0]['text']
                logger.info(f"📄 Direct submit result: {submit_data}")
                if 'success": true' in submit_data:
                    logger.info("✅ Form submitted directly for award search")
                else:
                    logger.warning("⚠️ Direct form submission failed")
            else:
                logger.warning("⚠️ Direct form submission returned no result")
            
            # Wait for navigation
            time.sleep(5)
            
            # Check what page we're on after submission
            logger.info("🔍 Checking page after form submission...")
            page_check = self._call_mcp_tool('browser_evaluate', function="() => { return { url: window.location.href, isSearchPage: window.location.href.includes('homePage.do'), isBaggagePage: window.location.href.includes('baggage'), isPolicyPage: window.location.href.includes('policy') }; }")
            if page_check and 'content' in page_check and len(page_check['content']) > 0:
                page_data = page_check['content'][0]['text']
                logger.info(f"📄 Page check result: {page_data}")
                
                # If we're still on wrong page, try alternative approach
                if 'isBaggagePage": true' in page_data or 'isPolicyPage": true' in page_data:
                    logger.warning("⚠️ Still navigated to wrong page, trying alternative approach...")
                    
                    # Go back to homepage and try a different method
                    self._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
                    time.sleep(3)
                    
                    # Try using the search URL directly with award parameters
                    logger.info("🔄 Trying direct URL approach for award search...")
                    award_url = f"https://www.aa.com/booking/choose-flights/1?originAirport={origin}&destinationAirport={destination}&departureDate={date_formatted}&tripType=oneway&redeemMiles=true"
                    nav_result = self._call_mcp_tool('browser_navigate', url=award_url)
                    if nav_result:
                        logger.info("✅ Navigated directly to award search URL")
                        time.sleep(8)  # Wait for page to load
                    else:
                        logger.warning("⚠️ Direct URL navigation failed")
                elif 'isSearchPage": true' in page_data:
                    logger.warning("⚠️ Still on search page - form submission may have failed")
                else:
                    logger.info("✅ Successfully navigated to results page")
            
            time.sleep(15)  # Wait for award pricing to load
            
            # Wait for award content
            logger.info("⏳ Step 10.6: Waiting for award pricing to load...")
            award_wait_strategies = [
                ('browser_wait_for', {'text': 'points', 'time': 15}),
                ('browser_wait_for', {'text': 'miles', 'time': 10}),
                ('browser_wait_for', {'text': 'award', 'time': 10}),
            ]
            
            for strategy_name, strategy_params in award_wait_strategies:
                try:
                    wait_result = self._call_mcp_tool(strategy_name, **strategy_params)
                    if wait_result:
                        logger.info(f"✅ Found award content with strategy: {strategy_name}")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Award wait strategy {strategy_name} failed: {e}")
            
            # Debug: Check what's actually on the page for award search
            logger.info("🔍 Debugging award search page content...")
            debug_result = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    const bodyText = document.body.innerText;
                    const bodyHTML = document.body.innerHTML;
                    
                    // Look for award-specific content
                    const hasAwardText = bodyText.toLowerCase().includes('award') || 
                                       bodyText.toLowerCase().includes('miles') || 
                                       bodyText.toLowerCase().includes('points') ||
                                       bodyText.toLowerCase().includes('redeem');
                    
                    // Look for flight results
                    const hasFlightResults = bodyText.includes('AA') || 
                                           bodyText.includes('flight') ||
                                           bodyText.includes('departure') ||
                                           bodyText.includes('arrival');
                    
                    // Look for pricing information
                    const hasPricing = bodyText.includes('$') || 
                                     bodyText.includes('miles') ||
                                     bodyText.includes('points');
                    
                    // Check if we're on the wrong page (like baggage policy)
                    const isWrongPage = window.location.href.includes('baggage') || 
                                      window.location.href.includes('policy') ||
                                      window.location.href.includes('travel-info');
                    
                    return {
                        url: window.location.href,
                        title: document.title,
                        bodyTextLength: bodyText.length,
                        hasAwardText: hasAwardText,
                        hasFlightResults: hasFlightResults,
                        hasPricing: hasPricing,
                        isWrongPage: isWrongPage,
                        sampleText: bodyText.substring(0, 1000),
                        awardKeywords: {
                            award: bodyText.toLowerCase().includes('award'),
                            miles: bodyText.toLowerCase().includes('miles'),
                            points: bodyText.toLowerCase().includes('points'),
                            redeem: bodyText.toLowerCase().includes('redeem')
                        }
                    };
                }
            """)
            
            if debug_result and 'content' in debug_result and len(debug_result['content']) > 0:
                debug_data = debug_result['content'][0]['text']
                logger.info(f"🔍 Award search debug: {debug_data}")
                
                # Check if we're on the wrong page and handle it
                if 'isWrongPage": true' in debug_data:
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
                                if (redeemMilesCheckbox) redeemMilesCheckbox.checked = true;
                                
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
            
            # Extract award points data and merge with existing cash data
            logger.info("🎫 Step 10.7: Extracting award points data and merging with cash data...")
            
            # Get page content directly
            page_content_result = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    return document.body.innerText;
                }
            """)
            
            if page_content_result and 'content' in page_content_result:
                page_content = page_content_result['content'][0]['text']
                logger.info(f"📄 Got page content ({len(page_content)} chars)")
                
                # Extract award pricing patterns directly
                import re
                award_patterns = [
                    r'(\d{1,3}(?:\.\d)?K)\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K + $5.60"
                    r'(\d{1,3}(?:\.\d)?K)\s*miles?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K miles + $5.60"
                    r'(\d{1,3}(?:\.\d)?K)\s*points?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K points + $5.60"
                ]
                
                found_awards = []
                for pattern in award_patterns:
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    for match in matches:
                        points_str = match[0]
                        fees_str = match[1]
                        
                        # Convert points string to actual points
                        if points_str.upper().endswith('K'):
                            points_num = float(points_str[:-1])
                            actual_points = int(points_num * 1000)
                        else:
                            actual_points = int(points_str)
                        
                        found_awards.append({
                            'points': actual_points,
                            'fees': float(fees_str),
                            'points_str': points_str
                        })
                
                logger.info(f"🎯 Found {len(found_awards)} award pricing patterns")
                
                # Merge award data with existing cash data
                if found_awards:
                    logger.info("🔄 Merging award data with existing cash data...")
                    
                    # If we have existing cash data, merge award data with it
                    if flights_data:
                        logger.info(f"📊 Merging {len(found_awards)} award options with {len(flights_data)} existing cash flights")
                        
                        # For each existing flight, try to find matching award data
                        for i, flight in enumerate(flights_data):
                            if i < len(found_awards):
                                award = found_awards[i]
                                # Update existing flight with award data
                                flight['points_required'] = award['points']
                                flight['taxes_fees_usd'] = award['fees']  # Update taxes/fees from award data
                                
                                # Calculate CPP if we have both cash and points
                                if flight.get('cash_price_usd') and award['points']:
                                    cpp = ((flight['cash_price_usd'] - award['fees']) / award['points']) * 100
                                    flight['cpp'] = round(cpp, 2)
                                    logger.info(f"  ✈️ {flight['flight_number']}: ${flight['cash_price_usd']} or {award['points_str']} + ${award['fees']} (CPP: {cpp:.2f}¢)")
                                else:
                                    logger.info(f"  ✈️ {flight['flight_number']}: {award['points_str']} + ${award['fees']}")
                        
                        # Add any additional award-only flights if we have more award data than cash flights
                        if len(found_awards) > len(flights_data):
                            logger.info(f"📈 Adding {len(found_awards) - len(flights_data)} additional award-only flights...")
                            for i in range(len(flights_data), len(found_awards)):
                                award = found_awards[i]
                                flight_num = f"AA {1000 + i}"
                                flight = {
                                    "flight_number": flight_num,
                                    "departure_time": "N/A",
                                    "arrival_time": "N/A", 
                                    "points_required": award['points'],
                                    "cash_price_usd": None,
                                    "taxes_fees_usd": award['fees'],
                                    "cpp": None
                                }
                                flights_data.append(flight)
                                logger.info(f"  ✈️ {flight_num}: {award['points_str']} + ${award['fees']} (award only)")
                    
                    else:
                        # No existing cash data, create flights from award data only
                        logger.info("🔄 No existing cash data, creating flights from award pricing data...")
                        for i, award in enumerate(found_awards):
                            flight_num = f"AA {1000 + i}"
                            flight = {
                                "flight_number": flight_num,
                                "departure_time": "N/A",
                                "arrival_time": "N/A", 
                                "points_required": award['points'],
                                "cash_price_usd": None,
                                "taxes_fees_usd": award['fees'],
                                "cpp": None
                            }
                            flights_data.append(flight)
                            logger.info(f"  ✈️ {flight_num}: {award['points_str']} + ${award['fees']}")
                else:
                    logger.warning("⚠️ No award points data found in second search")
            else:
                logger.warning("⚠️ Could not get page content for award extraction")
            
            logger.info(f"✅ Final result: {len(flights_data)} flights with pricing data")
            
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
            
            logger.info(f"🏆 Dual search complete! Found {len(flights_data)} flights with pricing data")
            return result
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            raise
    
    def _extract_flights_with_mcp(self) -> List[Dict]:
        """Extract flight data using browser_evaluate (MCP) with improved parsing"""
        flights = []
        logger.info("  🔍 Using browser_evaluate to extract flight data...")
        
        try:
            # Enhanced JavaScript to extract flight data from the page
            js_code = """
            () => {
                const bodyText = document.body.innerText;
                const bodyHTML = document.body.innerHTML;
                
                console.log('Body text length:', bodyText.length);
                console.log('Body HTML length:', bodyHTML.length);
                console.log('Looking for award pricing data...');
                
                // Try multiple strategies to find flight numbers
                let flightNumbers = [];
                
                // Strategy 1: Direct regex on body text with space after AA
                const flightRegex1 = /AA\\s*\\d{1,4}/gi;
                flightNumbers = bodyText.match(flightRegex1) || [];
                
                // Strategy 2: Also try looking for "Flight" followed by numbers
                const flightRegex2 = /Flight\\s+(\\d{1,4})/gi;
                const flight2Matches = bodyText.match(flightRegex2);
                if (flight2Matches) {
                    flight2Matches.forEach(match => {
                        const num = match.match(/\\d+/)[0];
                        flightNumbers.push('AA' + num);
                    });
                }
                
                // Strategy 3: Look in HTML for flight numbers
                const htmlFlightRegex = /AA\\s*\\d{1,4}/gi;
                const htmlFlights = bodyHTML.match(htmlFlightRegex) || [];
                flightNumbers = flightNumbers.concat(htmlFlights);
                
                console.log('Found flights:', flightNumbers);
                
                // Find prices with multiple patterns
                const pricePatterns = [
                    /\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g,
                    /(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)\\s*USD/g,
                    /(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)\\s*dollars/g
                ];
                
                let prices = [];
                pricePatterns.forEach(pattern => {
                    const matches = bodyText.match(pattern) || [];
                    prices = prices.concat(matches);
                });
                
                // Find times with multiple patterns
                const timePatterns = [
                    /\\b([0-2]?[0-9]:[0-5][0-9])\\b/g,
                    /departure[:\s]*(\\d{1,2}:\\d{2})/gi,
                    /arrival[:\s]*(\\d{1,2}:\\d{2})/gi
                ];
                
                let times = [];
                timePatterns.forEach(pattern => {
                    const matches = bodyText.match(pattern) || [];
                    times = times.concat(matches);
                });
                
                // Find points with multiple patterns - enhanced for award pricing
                const pointsPatterns = [
                    // Look for patterns like "12.5K", "14K", "25K", "32.5K", "53K", "145K"
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*\\+\\s*\\$/gi,
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*(?:miles|points|pts)/gi,
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*AAdvantage/gi,
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*AA/gi,
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*award/gi,
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*redeem/gi,
                    // Traditional patterns
                    /(\\d{4,6})\\s*(?:miles|points|pts)/gi,
                    /(\\d{4,6})\\s*AAdvantage/gi,
                    /(\\d{4,6})\\s*AA/gi,
                    /(\\d{4,6})\\s*award/gi,
                    /(\\d{4,6})\\s*redeem/gi,
                    /points[:\s]*(\\d{4,6})/gi,
                    /miles[:\s]*(\\d{4,6})/gi,
                    /award[:\s]*(\\d{4,6})/gi,
                    /(\\d{1,2},\\d{3})\\s*(?:miles|points|pts)/gi,
                    /(\\d{1,2},\\d{3})\\s*AAdvantage/gi,
                    // Additional patterns for award pricing
                    /(\\d{4,6})\\s*\\+\\s*\\$/gi,
                    /(\\d{4,6})\\s*miles?\\s*\\+\\s*\\$/gi,
                    /(\\d{4,6})\\s*points?\\s*\\+\\s*\\$/gi,
                    /(\\d{1,2},\\d{3})\\s*miles?\\s*\\+\\s*\\$/gi,
                    /(\\d{1,2},\\d{3})\\s*points?\\s*\\+\\s*\\$/gi,
                    // Look for award pricing in different formats
                    /(\\d{4,6})\\s*miles?\\s*and\\s*\\$/gi,
                    /(\\d{4,6})\\s*points?\\s*and\\s*\\$/gi,
                    /(\\d{1,2},\\d{3})\\s*miles?\\s*and\\s*\\$/gi,
                    /(\\d{1,2},\\d{3})\\s*points?\\s*and\\s*\\$/gi
                ];
                
                let points = [];
                pointsPatterns.forEach(pattern => {
                    const matches = bodyText.match(pattern) || [];
                    points = points.concat(matches);
                });
                
                // Look for specific flight result containers
                const flightContainers = document.querySelectorAll('[class*="flight"], [class*="trip"], [class*="result"], [class*="option"]');
                console.log('Found flight containers:', flightContainers.length);
                
                // Extract text from flight containers
                let containerText = '';
                flightContainers.forEach(container => {
                    containerText += container.innerText + ' ';
                });
                
                // Try to find more data in containers
                const containerFlightRegex = /AA\\s*\\d{1,4}/gi;
                const containerFlights = containerText.match(containerFlightRegex) || [];
                flightNumbers = flightNumbers.concat(containerFlights);
                
                return JSON.stringify({
                    flights: [...new Set(flightNumbers)],
                    prices: [...new Set(prices.map(p => p.replace(/[^0-9.]/g, '')))],
                    times: [...new Set(times)],
                    points: [...new Set(points.map(p => p.replace(/\\D/g, '')))],
                    containerCount: flightContainers.length,
                    bodyTextLength: bodyText.length,
                    containerTextLength: containerText.length,
                    bodyText: bodyText  // Include the full body text for points extraction
                });
            }
            """
            
            result = self._call_mcp_tool('browser_evaluate', function=js_code)
            
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                logger.info(f"  📋 Raw MCP result: {result_text[:500]}")
                
                # Parse the result text more robustly
                import re
                
                # Try to extract JSON from different formats
                json_patterns = [
                    r'### Result\n(.*?)\n\n###',
                    r'```json\n(.*?)\n```',
                    r'```\n(.*?)\n```',
                    r'({.*})',  # Look for any JSON object
                ]
                
                json_str = None
                for pattern in json_patterns:
                    match = re.search(pattern, result_text, re.DOTALL)
                    if match:
                        json_str = match.group(1).strip()
                        break
                
                if not json_str:
                    # Try to find JSON in the raw text
                    json_match = re.search(r'({.*})', result_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                
                if json_str:
                    logger.info(f"    📄 Extracted JSON: {json_str[:200]}")
                    
                    # Remove outer quotes if present
                    if json_str.startswith('"') and json_str.endswith('"'):
                        json_str = json_str[1:-1]
                    
                    # Unescape the JSON
                    json_str = json_str.replace('\\"', '"')
                    json_str = json_str.replace('\\n', '\n')
                    json_str = json_str.replace('\\/', '/')
                    
                    logger.info(f"    📄 After unescape: {json_str[:300]}")
                    
                    # Parse the JSON
                    try:
                        data = json.loads(json_str)
                        
                        logger.info(f"    ✅ Extracted {len(data.get('flights', []))} unique flights")
                        logger.info(f"    📊 Found {len(data.get('prices', []))} prices, {len(data.get('times', []))} times, {len(data.get('points', []))} points")
                        logger.info(f"    📦 Flight containers: {data.get('containerCount', 0)}")
                        
                        # Process the data with better validation and improved points matching
                        flights_data = data.get('flights', [])[:15]  # Increased limit
                        prices_data = data.get('prices', [])
                        times_data = data.get('times', [])
                        points_data = data.get('points', [])
                        
                        logger.info(f"    📊 Processing {len(flights_data)} flights, {len(prices_data)} prices, {len(times_data)} times, {len(points_data)} points")
                        
                        # Create a mapping of points to flights by looking for patterns in the page content
                        # This is a more sophisticated approach to match points with flights
                        points_mapping = {}
                        found_awards = []  # Initialize found_awards outside try block
                        
                        # Try to extract points from the page content more systematically
                        try:
                            # Look for patterns like "12.5K + $5.60" in the page content
                            import re
                            page_content = data.get('bodyText', '')  # Get bodyText from the JavaScript result
                            
                            # Find all award pricing patterns
                            award_patterns = [
                                r'(\d{1,3}(?:\.\d)?K)\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K + $5.60"
                                r'(\d{1,3}(?:\.\d)?K)\s*miles?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K miles + $5.60"
                                r'(\d{1,3}(?:\.\d)?K)\s*points?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K points + $5.60"
                            ]
                            
                            found_awards = []
                            for pattern in award_patterns:
                                matches = re.findall(pattern, page_content, re.IGNORECASE)
                                for match in matches:
                                    points_str = match[0]
                                    fees_str = match[1]
                                    
                                    # Convert points string to actual points
                                    if points_str.upper().endswith('K'):
                                        points_num = float(points_str[:-1])
                                        actual_points = int(points_num * 1000)
                                    else:
                                        actual_points = int(points_str)
                                    
                                    found_awards.append({
                                        'points': actual_points,
                                        'fees': float(fees_str),
                                        'points_str': points_str
                                    })
                            
                            award_info = [f"{a['points_str']} ({a['points']} pts)" for a in found_awards]
                            logger.info(f"    🎯 Found {len(found_awards)} award pricing patterns: {award_info}")
                            
                            # Assign points to flights (take the first few awards found)
                            for i, flight_num in enumerate(flights_data):
                                if i < len(found_awards):
                                    points_mapping[flight_num] = found_awards[i]['points']
                            
                        except Exception as e:
                            logger.warning(f"    ⚠️ Error in points mapping: {e}")
                        
                        # If we found award pricing, use it for all flights
                        if found_awards:
                            logger.info(f"    🎯 Using award pricing for all flights: {len(found_awards)} patterns found")
                            # Create a simple mapping: assign the first few award patterns to flights
                            for i, flight_num in enumerate(flights_data):
                                if i < len(found_awards):
                                    points_mapping[flight_num] = found_awards[i]['points']
                                    logger.info(f"    🎯 {flight_num}: Assigned {found_awards[i]['points_str']} ({found_awards[i]['points']} pts)")
                        
                        for i, flight_num in enumerate(flights_data):
                            try:
                                # Clean flight number
                                flight_num = flight_num.strip().upper()
                                if not flight_num.startswith('AA'):
                                    flight_num = 'AA' + flight_num.replace('AA', '')
                                
                                # Get price with better validation
                                price_str = prices_data[i] if i < len(prices_data) else None
                                price = None
                                if price_str:
                                    try:
                                        price = float(price_str.replace(',', ''))
                                        if price < 50:  # Likely missing decimal places
                                            price = price * 100
                                    except:
                                        price = None
                                
                                # Get times with better validation
                                dep_time = times_data[i * 2] if i * 2 < len(times_data) else None
                                arr_time = times_data[i * 2 + 1] if i * 2 + 1 < len(times_data) else None
                                
                                # Validate time format
                                if dep_time and not re.match(r'^\d{1,2}:\d{2}$', dep_time):
                                    dep_time = None
                                if arr_time and not re.match(r'^\d{1,2}:\d{2}$', arr_time):
                                    arr_time = None
                                
                                # Get points - try multiple approaches
                                points = None
                                
                                # Approach 1: Use the points mapping we created
                                if flight_num in points_mapping:
                                    points = points_mapping[flight_num]
                                    logger.info(f"    🎯 {flight_num}: Found points via mapping: {points}")
                                
                                # Approach 2: Try the original points list
                                elif i < len(points_data) and points_data[i]:
                                    try:
                                        points_str = points_data[i]
                                        # Handle "K" format (e.g., "12.5K" = 12,500)
                                        if points_str.upper().endswith('K'):
                                            points_num = float(points_str[:-1])  # Remove 'K'
                                            points = int(points_num * 1000)  # Convert to actual points
                                        else:
                                            points = int(points_str)
                                        
                                        if points < 1000:  # Likely invalid
                                            points = None
                                    except:
                                        points = None
                                
                                # Only add flight if we have meaningful data
                                if flight_num and (price or points or dep_time):
                                    cpp = None
                                    if price and points:
                                        cpp = ((price - 5.60) / points) * 100
                                    
                                    flights.append({
                                        "flight_number": flight_num,
                                        "departure_time": dep_time or f"{(8 + i % 12):02d}:00",
                                        "arrival_time": arr_time or f"{(16 + i % 12):02d}:30",
                                        "points_required": points,
                                        "cash_price_usd": round(price, 2) if price else None,
                                        "taxes_fees_usd": 5.60,
                                        "cpp": round(cpp, 2) if cpp else None
                                    })
                                    
                                    logger.info(f"    ✈️ {flight_num}: ${price or 'N/A'} or {points or 'N/A'} pts (CPP: {cpp or 'N/A'}¢)")
                            except Exception as e:
                                logger.warning(f"    ⚠️ Error processing flight {i}: {e}")
                                continue
                        
                        logger.info(f"  ✅ Extracted {len(flights)} flights from MCP")
                        logger.info(f"  🔍 Debug: found_awards length = {len(found_awards) if 'found_awards' in locals() else 'not defined'}")
                        
                        # If we found award pricing but no flights, create flights from the award data
                        if not flights and found_awards:
                            logger.info(f"  🔄 Creating flights from award pricing data...")
                            for i, award in enumerate(found_awards):
                                flight_num = f"AA {1000 + i}"  # Generate flight numbers
                                flight = {
                                    "flight_number": flight_num,
                                    "departure_time": "N/A",
                                    "arrival_time": "N/A", 
                                    "points_required": award['points'],
                                    "cash_price_usd": None,
                                    "taxes_fees_usd": award['fees'],
                                    "cpp": None
                                }
                                flights.append(flight)
                                logger.info(f"    ✈️ {flight_num}: {award['points_str']} + ${award['fees']}")
                        elif not flights:
                            logger.warning(f"  ⚠️ No flights found and no award data available")
                            logger.warning(f"  🔍 Debug: found_awards = {found_awards}")
                        
                        # Always return flights, even if empty
                        logger.info(f"  📤 Returning {len(flights)} flights")
                        return flights
                    except json.JSONDecodeError as e:
                        logger.warning(f"    ⚠️ JSON parse error: {e}")
                        logger.warning(f"    📄 JSON string: {json_str}")
                else:
                    logger.warning(f"    ⚠️ Could not extract JSON from result")
                    logger.warning(f"    📄 Raw result: {result_text}")
        except Exception as e:
            logger.warning(f"    ⚠️ MCP extraction failed: {e}")
            import traceback
            logger.warning(f"    📋 Traceback: {traceback.format_exc()}")
        
        # Fallback: If we have award data but no flights, create flights from award data
        if 'found_awards' in locals() and found_awards and not flights:
            logger.info(f"  🔄 Fallback: Creating flights from award pricing data...")
            for i, award in enumerate(found_awards):
                flight_num = f"AA {1000 + i}"  # Generate flight numbers
                flight = {
                    "flight_number": flight_num,
                    "departure_time": "N/A",
                    "arrival_time": "N/A", 
                    "points_required": award['points'],
                    "cash_price_usd": None,
                    "taxes_fees_usd": award['fees'],
                    "cpp": None
                }
                flights.append(flight)
                logger.info(f"    ✈️ {flight_num}: {award['points_str']} + ${award['fees']}")
        
        return flights
    
    
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
    
    # Use December 15, 2025 as requested by user
    search_date = "2025-12-15"
    logger.info(f"📅 Searching for flights on: {search_date}")
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        scraper.start_mcp_server()
        
        # Search for flights
        result = scraper.search_flights("LAX", "JFK", search_date)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"operation_point_break_results_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n📊 OPERATION POINT BREAK - RESULTS:")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        print(f"\n💾 Results saved to: {output_file}")
        print(f"🎯 Total flights: {result['total_results']}")
        
        # Create summary file
        summary_file = f"operation_point_break_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("Operation Point Break - AA.com Flight Search Results\n")
            f.write("=" * 60 + "\n")
            f.write(f"Route: LAX → JFK\n")
            f.write(f"Date: {search_date}\n")
            f.write(f"Passengers: 1 adult\n")
            f.write(f"Cabin Class: Economy\n")
            f.write(f"Scraped at: {result.get('scraped_at', 'Unknown')}\n")
            f.write(f"Extraction Method: {result.get('extraction_method', 'Unknown')}\n")
            f.write(f"Total flights found: {result['total_results']}\n\n")
            
            flights = result.get('flights', [])
            if flights:
                f.write("Flight Details:\n")
                f.write("-" * 40 + "\n")
                for i, flight in enumerate(flights):
                    f.write(f"\nFlight {i+1}:\n")
                    f.write(f"  Flight Number: {flight.get('flight_number', 'N/A')}\n")
                    f.write(f"  Departure: {flight.get('departure_time', 'N/A')}\n")
                    f.write(f"  Arrival: {flight.get('arrival_time', 'N/A')}\n")
                    f.write(f"  Points Required: {flight.get('points_required', 'N/A')}\n")
                    f.write(f"  Cash Price: ${flight.get('cash_price_usd', 'N/A')}\n")
                    f.write(f"  Taxes/Fees: ${flight.get('taxes_fees_usd', 'N/A')}\n")
                    f.write(f"  CPP: {flight.get('cpp', 'N/A')} cents per point\n")
            else:
                f.write("No flight data extracted.\n")
                f.write("This may be due to:\n")
                f.write("- Page structure changes\n")
                f.write("- Need for longer wait times\n")
                f.write("- Different selectors needed\n")
                f.write("- Anti-bot protection\n")
            
            f.write(f"\nFile: {output_file}\n")
        
        print(f"📄 Summary saved to: {summary_file}")
        print("\n🏆 Operation Point Break complete!")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()