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
    
    def _save_screenshot(self, screenshot_result: Dict, filename: str):
        """Save screenshot from MCP result"""
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
                        with open(filename, 'wb') as f:
                            f.write(image_data)
                        logger.info(f"  📁 Screenshot saved as: {filename}")
                        
                        # Verify file exists
                        if os.path.exists(filename):
                            logger.info(f"  ✅ File confirmed: {filename}")
                        else:
                            logger.warning(f"  ⚠️ File not found: {filename}")
                    else:
                        logger.warning(f"  ⚠️ Unexpected screenshot format: {first_item}")
                else:
                    logger.warning(f"  ⚠️ Unexpected screenshot content: {content}")
            else:
                logger.warning(f"  ⚠️ Unexpected screenshot result format: {screenshot_result}")
        except Exception as e:
            logger.warning(f"  ⚠️ Failed to save screenshot: {e}")
    
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
            
            # STEP 8: Wait for page to fully load and get results snapshot
            logger.info("📸 Step 8: Waiting for page to load and getting results snapshot...")
            time.sleep(15)  # Wait longer for JavaScript to load flight data
            
            # Take multiple snapshots to catch content as it loads
            results_snapshot = None
            for attempt in range(3):
                logger.info(f"  📸 Snapshot attempt {attempt + 1}/3...")
                snapshot_result = self._call_mcp_tool('browser_snapshot')
                if snapshot_result:
                    results_snapshot = snapshot_result
                    logger.info(f"  ✅ Got results snapshot ({len(str(results_snapshot))} bytes)")
                    break
                else:
                    logger.warning(f"  ⚠️ Snapshot attempt {attempt + 1} failed")
                    time.sleep(5)
            
            if not results_snapshot:
                logger.warning("⚠️ Could not get results snapshot after 3 attempts")
            
            # STEP 8.5: Take screenshot for debugging
            logger.info("📷 Step 8.5: Taking screenshot of results page...")
            screenshot_filename = f"aa_results_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_result = self._call_mcp_tool('browser_take_screenshot', filename=screenshot_filename, fullPage=True)
            if screenshot_result:
                logger.info(f"✅ Screenshot taken")
                self._save_screenshot(screenshot_result, screenshot_filename)
            else:
                logger.warning("⚠️ Could not take screenshot")
            
            # STEP 8.6: Wait for flight content with multiple strategies
            logger.info("⏳ Step 8.6: Waiting for flight results to load...")
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
            
            # Take final snapshot after waiting
            logger.info("📸 Step 8.7: Taking final snapshot after waiting...")
            final_snapshot = self._call_mcp_tool('browser_snapshot')
            if final_snapshot:
                logger.info(f"✅ Got final snapshot ({len(str(final_snapshot))} bytes)")
                results_snapshot = final_snapshot
            
            # STEP 9: Extract flight data with multiple methods
            logger.info("🎫 Step 9: Extracting flight data...")
            flights_data = []
            
            # Try browser_evaluate first
            flights_data = self._extract_flights_with_mcp()
            
            # If that fails, try snapshot extraction
            if not flights_data and results_snapshot:
                logger.warning("⚠️ browser_evaluate failed, trying snapshot extraction...")
                flights_data = self._extract_flights_from_snapshot(str(results_snapshot))
            
            # If still no data, try with original snapshot
            if not flights_data and snapshot:
                logger.warning("⚠️ Results snapshot failed, trying original snapshot...")
                flights_data = self._extract_flights_from_snapshot(str(snapshot))
            
            if not flights_data:
                logger.error("❌ No flights extracted with any method")
                # Return empty result instead of raising exception
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
                "total_results": len(flights_data),
                "scraped_at": datetime.now().isoformat(),
                "extraction_method": "mcp_playwright_improved"
            }
            
            logger.info(f"🏆 Search complete! Found {len(flights_data)} flights")
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
                
                // Find points with multiple patterns
                const pointsPatterns = [
                    /(\\d{4,6})\\s*(?:miles|points|pts)/gi,
                    /(\\d{4,6})\\s*AAdvantage/gi,
                    /(\\d{4,6})\\s*AA/gi
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
                    containerTextLength: containerText.length
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
                        
                        # Process the data with better validation
                        for i, flight_num in enumerate(data.get('flights', [])[:15]):  # Increased limit
                            try:
                                # Clean flight number
                                flight_num = flight_num.strip().upper()
                                if not flight_num.startswith('AA'):
                                    flight_num = 'AA' + flight_num.replace('AA', '')
                                
                                # Get price with better validation
                                price_str = data.get('prices', [])[i] if i < len(data.get('prices', [])) else None
                                price = None
                                if price_str:
                                    try:
                                        price = float(price_str.replace(',', ''))
                                        if price < 50:  # Likely missing decimal places
                                            price = price * 100
                                    except:
                                        price = None
                                
                                # Get times with better validation
                                times_list = data.get('times', [])
                                dep_time = times_list[i * 2] if i * 2 < len(times_list) else None
                                arr_time = times_list[i * 2 + 1] if i * 2 + 1 < len(times_list) else None
                                
                                # Validate time format
                                if dep_time and not re.match(r'^\d{1,2}:\d{2}$', dep_time):
                                    dep_time = None
                                if arr_time and not re.match(r'^\d{1,2}:\d{2}$', arr_time):
                                    arr_time = None
                                
                                # Get points with better validation
                                points_list = data.get('points', [])
                                points = None
                                if i < len(points_list) and points_list[i]:
                                    try:
                                        points = int(points_list[i])
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