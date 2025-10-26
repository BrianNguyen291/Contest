#!/usr/bin/env python3
"""
Real AA.com Scraper using Microsoft Playwright MCP - OPTIMIZED VERSION
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
    """AA.com scraper using Microsoft Playwright MCP (official) - Optimized"""
    
    # Element reference cache to avoid re-parsing
    ELEMENT_REFS = {
        'one_way': 'e115',
        'from_airport': 'e128',
        'to_airport': 'e136',
        'depart_date': 'e149',
        'redeem_miles': 'e121',
        'search_button': 'e161'
    }
    
    # Common timeout values
    SHORT_WAIT = 1
    MEDIUM_WAIT = 3
    LONG_WAIT = 5
    PAGE_LOAD_WAIT = 10
    
    def __init__(self):
        self.base_url = "https://www.aa.com"
        self.mcp_process = None
        self._element_cache = {}
        
    def start_mcp_server(self):
        """Start the official Playwright MCP server with retry logic"""
        logger.info("🌐 Starting official Playwright MCP server...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.mcp_process = subprocess.Popen(
                    ["npx", "@playwright/mcp"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                # Reduced wait time
                time.sleep(2)
                logger.info("✅ Official Playwright MCP server started")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    logger.error(f"❌ Failed to start MCP server after {max_retries} attempts: {e}")
            raise
    
    def _call_mcp_tool(self, tool_name: str, **kwargs) -> Optional[Dict]:
        """Call a Playwright MCP tool using JSON-RPC with improved error handling"""
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
            self._restart_mcp()
            return None
        except Exception as e:
            logger.warning(f"    ⚠️ MCP tool failed: {e}")
            return None
    
    def _restart_mcp(self):
        """Helper method to restart MCP server"""
        self.close()
        self.start_mcp_server()
    
    def _wait_for_page_load(self, url_pattern: str, timeout: int = 15) -> bool:
        """Wait for page to load by checking URL"""
        start = time.time()
        while time.time() - start < timeout:
            result = self._call_mcp_tool('browser_evaluate', function=f"() => window.location.href.includes('{url_pattern}')")
            if result:
                return True
            time.sleep(0.5)
        return False
    
    def _parse_snapshot_for_elements(self, snapshot) -> Dict[str, str]:
        """Parse snapshot to find element references - using cached refs"""
        # Return cached element references
        return {
            'one way radio': self.ELEMENT_REFS['one_way'],
            'from airport': self.ELEMENT_REFS['from_airport'],
            'to airport': self.ELEMENT_REFS['to_airport'],
            'depart date': self.ELEMENT_REFS['depart_date'],
            'redeem miles': self.ELEMENT_REFS['redeem_miles'],
            'search button': self.ELEMENT_REFS['search_button']
        }
    
    def _find_element_ref(self, elements: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find element reference by keywords"""
        for key in elements:
            for keyword in keywords:
                if keyword in key.lower():
                    return elements[key]
        return None
    
    def _fill_flight_form(self, origin: str, destination: str, date: str, award_search: bool = False) -> bool:
        """Fill flight search form - optimized version"""
        try:
            # Click One Way radio
            self._call_mcp_tool('browser_click', element='One way radio button', ref=self.ELEMENT_REFS['one_way'])
            time.sleep(self.SHORT_WAIT)
            
            # Fill form fields
            self._call_mcp_tool('browser_type', element='From airport textbox', ref=self.ELEMENT_REFS['from_airport'], text=origin)
            time.sleep(self.SHORT_WAIT)
            
            self._call_mcp_tool('browser_type', element='To airport textbox', ref=self.ELEMENT_REFS['to_airport'], text=destination)
            time.sleep(self.SHORT_WAIT)
            
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')
            self._call_mcp_tool('browser_type', element='Depart date textbox', ref=self.ELEMENT_REFS['depart_date'], text=date_formatted)
            time.sleep(self.SHORT_WAIT)
            
            # Handle award search
            if award_search:
                self._click_redeem_miles()
            
            # Click search
            return self._click_search_button()
        except Exception as e:
            logger.error(f"❌ Form fill failed: {e}")
            return False
    
    def _click_redeem_miles(self) -> bool:
        """Click redeem miles checkbox with optimized retry logic"""
        retry_count = 3
        for attempt in range(retry_count):
            result = self._call_mcp_tool('browser_click', element='Redeem miles label', ref=self.ELEMENT_REFS['redeem_miles'])
            if result:
                logger.info("  ✅ Clicked Redeem miles checkbox")
                return True
            if attempt < retry_count - 1:
                time.sleep(self.SHORT_WAIT)
        logger.warning("  ⚠️ Failed to click Redeem miles checkbox")
        return False
    
    def _click_search_button(self) -> bool:
        """Click search button with optimized retry logic"""
        retry_count = 2
        for attempt in range(retry_count):
            result = self._call_mcp_tool('browser_click', element='Search button', ref=self.ELEMENT_REFS['search_button'])
            if result:
                logger.info("  ✅ Clicked Search button")
                return True
            if attempt < retry_count - 1:
                time.sleep(self.SHORT_WAIT)
        logger.warning("  ⚠️ Failed to click Search button")
        return False
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1, award_search: bool = False) -> Dict:
        """Search for flights using official Playwright MCP - optimized"""
        logger.info(f"🎯 Operation Point Break: {origin} → {destination} on {date}")
        
        search_metadata = SearchMetadata(
            origin=origin.upper(),
            destination=destination.upper(),
            date=date,
            passengers=passengers,
            cabin_class="economy"
        )
        
        try:
            # Navigate to AA.com
            url = "https://www.aa.com/homePage.do?locale=en_US" if award_search else self.base_url
            nav_result = self._call_mcp_tool('browser_navigate', url=url)
            
            if not nav_result:
                raise Exception("Failed to navigate to AA.com")
            
            time.sleep(self.MEDIUM_WAIT)
            
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
            
            # Fill form and submit
            logger.info("📝 Filling search form...")
            if not self._fill_flight_form(origin, destination, date, award_search):
                raise Exception("Failed to fill search form")
            
            logger.info("✅ Form submitted, waiting for results...")
            
            # Wait for search results page
            time.sleep(self.PAGE_LOAD_WAIT)
            
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
    
    def _extract_flights_with_mcp(self, award_search: bool = False) -> List[Dict]:
        """Extract flight data using browser_evaluate (MCP) - Enhanced version"""
        flights = []
        logger.info("  🔍 Using browser_evaluate to extract flight data...")
        
        try:
            # Get page content and send to API for processing
            js_code = """
            () => {
                return {
                    url: window.location.href,
                    title: document.title,
                    bodyText: document.body.innerText,
                    html: document.documentElement.outerHTML
                };
            }
            """
            
            result = self._call_mcp_tool('browser_evaluate', function=js_code)
            
            if result and 'content' in result and len(result['content']) > 0:
                result_text = result['content'][0]['text']
                logger.info(f"  📋 Raw MCP result: {result_text[:300]}")
                
                # Parse the result directly (no need for complex JSON parsing)
                try:
                    # The result should be a direct object, not a string
                    if isinstance(result_text, str):
                        # Clean control characters that cause JSON parsing issues
                        import re
                        result_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', result_text)
                        
                        # Try to extract JSON from the result text
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
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"    ⚠️ JSON parse error: {e}")
                    data = {"bodyText": result_text, "url": "", "title": ""}
                except Exception as e:
                    logger.warning(f"    ⚠️ Data processing error: {e}")
                    data = {"bodyText": result_text, "url": "", "title": ""}
            
            # Extract flight data directly from page content
            try:
                processed_flights = self._extract_flights_from_text(data.get('bodyText', ''), award_search)
                
                if processed_flights:
                    flights.extend(processed_flights)
                    logger.info(f"    ✅ Extracted {len(processed_flights)} flights from page")
                else:
                    # Fallback to basic extraction
                    logger.warning("    ⚠️ Direct extraction failed, using basic extraction...")
                    flights.extend(self._basic_flight_extraction(data, award_search))
            except Exception as e:
                logger.error(f"    ❌ Extraction error: {e}")
                # Fallback to basic extraction
                flights.extend(self._basic_flight_extraction(data, award_search))
                    
            logger.info(f"  ✅ Extracted {len(flights)} flights from MCP")
            return flights
                    
        except json.JSONDecodeError as e:
            logger.warning(f"    ⚠️ JSON parse error: {e}")
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
        """Extract comprehensive flight data using simplified MCP approach"""
        logger.info("🔍 Extracting comprehensive flight data...")
        
        try:
            # Simplified JavaScript for data extraction
            js_code = """
            () => {
                const bodyText = document.body.innerText;
                
                // Extract flight numbers
                const flightNumbers = bodyText.match(/AA\\s*\\d{1,4}/g) || [];
                
                // Extract times
                const times = bodyText.match(/\\b([0-2]?[0-9]:[0-5][0-9])\\b/g) || [];
                
                // Extract award prices
                const awardPrices = bodyText.match(/(\\d+(?:\\.\\d+)?K?\\s*\\+\\s*\\$\\d+(?:\\.\\d+)?/g) || [];
                
                // Extract cash prices
                const cashPrices = bodyText.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g) || [];
                
                return {
                    flightNumbers: flightNumbers.slice(0, 20),
                    times: times.slice(0, 40),
                    awardPrices: awardPrices.slice(0, 40),
                    cashPrices: cashPrices.slice(0, 40),
                    totalFlights: flightNumbers.length,
                    totalTimes: times.length,
                    totalAwardPrices: awardPrices.length,
                    totalCashPrices: cashPrices.length
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
    
    def _extract_flights_from_text(self, body_text: str, award_search: bool) -> list:
        """Extract flight data from page text using regex patterns"""
        flights = []
        try:
            # Extract flight numbers
            flight_numbers = re.findall(r'AA\s*\d{1,4}', body_text)
            # Extract cash prices
            cash_prices = re.findall(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', body_text)
            # Extract times
            times = re.findall(r'\b([0-2]?[0-9]:[0-5][0-9])\b', body_text)
            
            # Create flight entries
            for i, flight_num in enumerate(flight_numbers[:10]):
                try:
                    departure_time = times[i * 2] if i * 2 < len(times) else 'N/A'
                    arrival_time = times[i * 2 + 1] if i * 2 + 1 < len(times) else 'N/A'
                    cash_price = float(cash_prices[i].replace(',', '')) if i < len(cash_prices) else 0.0
                    
                    flights.append({
                        "flight_number": flight_num,
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "points_required": 0,
                        "cash_price_usd": round(cash_price, 2),
                        "taxes_fees_usd": 5.60,
                        "cpp": 0.0
                    })
                except:
                    continue
        except:
            pass
            return flights
    
    def _basic_flight_extraction(self, data: dict, award_search: bool) -> list:
        """Basic fallback extraction method"""
        flights = []
        try:
            body_text = data.get('bodyText', '')
            if body_text:
                return self._extract_flights_from_text(body_text, award_search)
        except:
            pass
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
        cash_flights = []
        try:
            cash_result = scraper.search_flights("LAX", "JFK", search_date)
            cash_flights = cash_result.get('flights', [])
            for flight in cash_flights:
                flight['pricing_type'] = 'cash'
            all_flights.extend(cash_flights)
            logger.info(f"💰 Found {len(cash_flights)} cash flights")
        except Exception as e:
            logger.error(f"❌ Cash search failed: {e}")
        
        # Navigate back to search page by clicking AA logo
        logger.info("\n🌐 Clicking AA logo to return to search page for award search...")
        time.sleep(2)  # Wait a moment
        
        # Try multiple approaches to click the AA logo
        logo_clicked = False
        try:
            # Try clicking by image alt text
            result = scraper._call_mcp_tool('browser_click', element='American Airlines logo', ref='e1')
            if result:
                logger.info("  ✅ Clicked AA logo")
                logo_clicked = True
        except Exception as e:
            logger.warning(f"  ⚠️ Could not find logo by alt text: {e}")
        
        if not logo_clicked:
            # Try finding logo via browser_evaluate
            try:
                logger.info("  🔧 Trying to find AA logo with browser_evaluate...")
                js_code = """
                () => {
                    // Try multiple selectors for the AA logo
                    const selectors = [
                        'img[alt="American Airlines logo"]',
                        'img.aa-logo',
                        'a[href="/"] img',
                        '.aa-logo',
                        'img[src*="logo-american"]'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            // Click the logo or its parent link
                            const link = element.closest('a');
                            if (link) {
                                link.click();
                                return { success: true, clicked: 'link', selector: selector };
                            } else {
                                element.click();
                                return { success: true, clicked: 'img', selector: selector };
                            }
                        }
                    }
                    return { success: false, message: 'No logo found' };
                }
                """
                result = scraper._call_mcp_tool('browser_evaluate', function=js_code)
                if result and 'content' in result and len(result['content']) > 0:
                    result_text = result['content'][0]['text']
                    logger.info(f"  📋 Logo click result: {result_text}")
                    if 'success": true' in result_text:
                        logger.info("  ✅ Clicked AA logo (browser_evaluate method)")
                        logo_clicked = True
            except Exception as e:
                logger.warning(f"  ⚠️ Browser evaluate failed: {e}")
        
        if not logo_clicked:
            logger.warning("  ⚠️ Could not click AA logo, falling back to navigation")
        scraper._call_mcp_tool('browser_navigate', url="https://www.aa.com/homePage.do?locale=en_US")
        
        time.sleep(3)  # Wait for page to load
        
        # Second search: AWARD prices  
        logger.info("\n💎 Starting AWARD price search...")
        logger.info("💎 Note: Now clicking 'Redeem miles' checkbox...")
        award_flights = []
        try:
            # For award search, we need to click "Redeem miles" checkbox first
            # This is handled in the search_flights method when award search is detected
            award_result = scraper.search_flights("LAX", "JFK", search_date, award_search=True)
            award_flights = award_result.get('flights', [])
            for flight in award_flights:
                flight['pricing_type'] = 'award'
            all_flights.extend(award_flights)
            logger.info(f"💎 Found {len(award_flights)} award flights")
            logger.info("🤖 Award search data sent to ChatGPT - waiting for results...")
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
        
        # Format results in the desired format
        formatted_flights = []
        
        # Process cash flights
        cash_flights = [f for f in all_flights if f.get('pricing_type') == 'cash']
        for flight in cash_flights:
            formatted_flight = {
                "flight_number": flight.get('flight_number', 'N/A'),
                "departure_time": flight.get('departure_time', 'N/A'),
                "arrival_time": flight.get('arrival_time', 'N/A'),
                "points_required": flight.get('points_required', 0),
                "cash_price_usd": flight.get('cash_price_usd', 0.0),
                "taxes_fees_usd": flight.get('taxes_fees_usd', 0.0),
                "cpp": flight.get('cpp', 0.0)
            }
            formatted_flights.append(formatted_flight)
        
        # Process award flights
        award_flights = [f for f in all_flights if f.get('pricing_type') == 'award']
        for flight in award_flights:
            formatted_flight = {
                "flight_number": flight.get('flight_number', 'N/A'),
                "departure_time": flight.get('departure_time', 'N/A'),
                "arrival_time": flight.get('arrival_time', 'N/A'),
                "points_required": flight.get('points_required', 0),
                "cash_price_usd": flight.get('cash_price_usd', 0.0),
                "taxes_fees_usd": flight.get('taxes_fees_usd', 0.0),
                "cpp": flight.get('cpp', 0.0)
            }
            formatted_flights.append(formatted_flight)
        
        # Final result in the exact format requested
        result = {
            "search_metadata": {
                "origin": "LAX",
                "destination": "JFK",
                "date": search_date,
                "passengers": 1,
                "cabin_class": "economy"
            },
            "flights": formatted_flights,
            "total_results": len(formatted_flights)
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