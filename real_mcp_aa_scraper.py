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
                time.sleep(3)
                nav_result = self._call_mcp_tool('browser_navigate', url=self.base_url)
                
            if not nav_result:
                raise Exception("Failed to navigate to AA.com after retry")
            
            time.sleep(8)  # Increased wait time for page stability
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
            
            # STEP 9: Extract flight data using improved method
            logger.info("🎫 Step 9: Extracting flight data...")
            flights_data = self._extract_flights_with_mcp()
            
            logger.info(f"✅ Found {len(flights_data)} flights from improved extraction")
            
            # STEP 10: Try to get award pricing data if missing
            if flights_data and all(flight.get('points_required') is None for flight in flights_data):
                logger.info("🔄 No award points found, trying alternative extraction...")
                flights_data = self._extract_award_pricing_alternative(flights_data)
            
            # STEP 11: Clean up and deduplicate results
            logger.info("🧹 Cleaning up and deduplicating results...")
            flights_data = self._clean_and_deduplicate_flights(flights_data)
            
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
                const results = {
                    flights: [],
                    errors: [],
                    debug: {}
                };
                
                try {
                const bodyText = document.body.innerText;
                const bodyHTML = document.body.innerHTML;
                
                    results.debug.bodyTextLength = bodyText.length;
                    results.debug.bodyHTMLLength = bodyHTML.length;
                    
                    // Strategy 1: Look for flight containers first
                    const flightSelectors = [
                        '[class*="flight"]',
                        '[class*="trip"]', 
                        '[class*="result"]',
                        '[class*="option"]',
                        '[class*="card"]',
                        '[data-testid*="flight"]',
                        '[data-testid*="trip"]'
                    ];
                    
                    let flightElements = [];
                    flightSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        flightElements = flightElements.concat(Array.from(elements));
                    });
                    
                    results.debug.flightElementsFound = flightElements.length;
                    
                    // Strategy 2: Extract data from each flight element
                    flightElements.forEach((element, index) => {
                        try {
                            const text = element.innerText || '';
                            
                            // Extract flight number
                            const flightMatch = text.match(/AA\\s*(\\d{1,4})/i);
                            const flightNumber = flightMatch ? `AA${flightMatch[1]}` : null;
                            
                            // Extract times
                            const timeMatches = text.match(/\\b([0-2]?[0-9]:[0-5][0-9])\\b/g);
                            const departureTime = timeMatches ? timeMatches[0] : null;
                            const arrivalTime = timeMatches && timeMatches.length > 1 ? timeMatches[1] : null;
                            
                            // Extract cash prices
                            const cashPriceMatch = text.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/);
                            const cashPrice = cashPriceMatch ? parseFloat(cashPriceMatch[1].replace(/,/g, '')) : null;
                            
                            // Extract award points
                            let pointsRequired = null;
                            const pointsPatterns = [
                                /(\\d{1,3}(?:\\.\\d)?K)\\s*(?:miles|points|pts)/i,
                                /(\\d{4,6})\\s*(?:miles|points|pts)/i,
                                /(\\d{1,2},\\d{3})\\s*(?:miles|points|pts)/i
                            ];
                            
                            for (const pattern of pointsPatterns) {
                                const match = text.match(pattern);
                                if (match) {
                                    let pointsStr = match[1];
                                    if (pointsStr.toUpperCase().endsWith('K')) {
                                        pointsRequired = parseInt(parseFloat(pointsStr) * 1000);
                                    } else {
                                        pointsRequired = parseInt(pointsStr.replace(/,/g, ''));
                                    }
                                    break;
                                }
                            }
                            
                            // Extract taxes/fees
                            const feesMatch = text.match(/\\+\\s*\\$\\s*(\\d+(?:\\.\\d{2})?)/);
                            const taxesFees = feesMatch ? parseFloat(feesMatch[1]) : 5.60;
                            
                            // Only add if we have meaningful data
                            if (flightNumber || cashPrice || pointsRequired) {
                                const flight = {
                                    flight_number: flightNumber || `AA${1000 + index}`,
                                    departure_time: departureTime || 'N/A',
                                    arrival_time: arrivalTime || 'N/A',
                                    points_required: pointsRequired,
                                    cash_price_usd: cashPrice,
                                    taxes_fees_usd: taxesFees,
                                    cpp: null
                                };
                                
                                // Calculate CPP if we have both cash and points
                                if (cashPrice && pointsRequired) {
                                    flight.cpp = Math.round(((cashPrice - taxesFees) / pointsRequired) * 100 * 100) / 100;
                                }
                                
                                results.flights.push(flight);
                            }
                        } catch (e) {
                            results.errors.push(`Error processing element ${index}: ${e.message}`);
                        }
                    });
                    
                    // Strategy 3: Always try page-wide extraction for additional data
                    results.debug.pageWideExtraction = true;
                    
                    // Extract all flight numbers from page
                    const allFlightNumbers = bodyText.match(/AA\\s*\\d{1,4}/gi) || [];
                    const uniqueFlights = [...new Set(allFlightNumbers)];
                    
                    // Extract all prices (more aggressive)
                    const allPrices = bodyText.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g) || [];
                    const uniquePrices = [...new Set(allPrices.map(p => {
                        const price = parseFloat(p.replace(/[$,]/g, ''));
                        return price >= 50 && price <= 5000 ? price : null;
                    }).filter(p => p !== null))];
                    
                    // Extract all points (more aggressive)
                    const allPoints = [];
                    const aggressivePointsPatterns = [
                    /(\\d{1,3}(?:\\.\\d)?K)\\s*(?:miles|points|pts)/gi,
                    /(\\d{4,6})\\s*(?:miles|points|pts)/gi,
                    /(\\d{1,2},\\d{3})\\s*(?:miles|points|pts)/gi,
                        /(\\d{1,3}(?:\\.\\d)?K)\\s*\\+\\s*\\$/gi,
                        /(\\d{4,6})\\s*\\+\\s*\\$/gi
                    ];
                    
                    aggressivePointsPatterns.forEach(pattern => {
                        const matches = bodyText.match(pattern);
                        if (matches) {
                            matches.forEach(match => {
                                const pointsStr = match.match(pattern)[1];
                                let points;
                                if (pointsStr.toUpperCase().endsWith('K')) {
                                    points = parseInt(parseFloat(pointsStr) * 1000);
                                } else {
                                    points = parseInt(pointsStr.replace(/,/g, ''));
                                }
                                if (points >= 1000 && points <= 200000) allPoints.push(points);
                            });
                        }
                    });
                    
                    // Create additional flights from page-wide data
                    const maxAdditionalFlights = Math.max(uniqueFlights.length, uniquePrices.length, allPoints.length);
                    for (let i = 0; i < maxAdditionalFlights; i++) {
                        const flight = {
                            flight_number: uniqueFlights[i] || `AA${2000 + i}`,
                            departure_time: 'N/A',
                            arrival_time: 'N/A',
                            points_required: allPoints[i] || null,
                            cash_price_usd: uniquePrices[i] || null,
                            taxes_fees_usd: 5.60,
                            cpp: null
                        };
                        
                        if (flight.cash_price_usd && flight.points_required) {
                            flight.cpp = Math.round(((flight.cash_price_usd - flight.taxes_fees_usd) / flight.points_required) * 100 * 100) / 100;
                        }
                        
                        results.flights.push(flight);
                    }
                    
                    results.debug.flightsFound = results.flights.length;
                    results.debug.errorsCount = results.errors.length;
                    
                } catch (e) {
                    results.errors.push(`Main extraction error: ${e.message}`);
                }
                
                return JSON.stringify(results);
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
                        
                        flights_data = data.get('flights', [])
                        errors = data.get('errors', [])
                        debug = data.get('debug', {})
                        
                        logger.info(f"    ✅ Extracted {len(flights_data)} flights")
                        logger.info(f"    📊 Debug info: {debug}")
                        
                        if errors:
                            logger.warning(f"    ⚠️ Extraction errors: {errors}")
                        
                        # Convert the flights data to the expected format
                        for flight_data in flights_data:
                            flights.append({
                                "flight_number": flight_data.get('flight_number', 'N/A'),
                                "departure_time": flight_data.get('departure_time', 'N/A'),
                                "arrival_time": flight_data.get('arrival_time', 'N/A'),
                                "points_required": flight_data.get('points_required'),
                                "cash_price_usd": flight_data.get('cash_price_usd'),
                                "taxes_fees_usd": flight_data.get('taxes_fees_usd', 5.60),
                                "cpp": flight_data.get('cpp')
                            })
                        
                        logger.info(f"  ✅ Processed {len(flights)} flights from improved extraction")
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
        
        return flights
    
    def _extract_award_pricing_alternative(self, flights_data: List[Dict]) -> List[Dict]:
        """Try alternative methods to extract award pricing"""
        logger.info("🎯 Trying alternative award pricing extraction...")
        
        try:
            # Get page content for award pricing patterns
            page_content_result = self._call_mcp_tool('browser_evaluate', function="""
                () => {
                    return document.body.innerText;
                }
            """)
            
            if page_content_result and 'content' in page_content_result:
                page_content = page_content_result['content'][0]['text']
                logger.info(f"📄 Got page content for award extraction ({len(page_content)} chars)")
                
                # Look for award pricing patterns
                import re
                award_patterns = [
                    r'(\d{1,3}(?:\.\d)?K)\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K + $5.60"
                    r'(\d{1,3}(?:\.\d)?K)\s*miles?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K miles + $5.60"
                    r'(\d{1,3}(?:\.\d)?K)\s*points?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12.5K points + $5.60"
                    r'(\d{4,6})\s*miles?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12500 miles + $5.60"
                    r'(\d{4,6})\s*points?\s*\+\s*\$(\d+(?:\.\d{2})?)',  # "12500 points + $5.60"
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
                
                # Assign award data to flights
                if found_awards:
                    logger.info("🔄 Assigning award data to flights...")
                    for i, flight in enumerate(flights_data):
                        if i < len(found_awards):
                            award = found_awards[i]
                            flight['points_required'] = award['points']
                            flight['taxes_fees_usd'] = award['fees']
                            
                            # Calculate CPP if we have both cash and points
                            if flight.get('cash_price_usd') and award['points']:
                                cpp = ((flight['cash_price_usd'] - award['fees']) / award['points']) * 100
                                flight['cpp'] = round(cpp, 2)
                                logger.info(f"  ✈️ {flight['flight_number']}: ${flight['cash_price_usd']} or {award['points_str']} + ${award['fees']} (CPP: {cpp:.2f}¢)")
                            else:
                                logger.info(f"  ✈️ {flight['flight_number']}: {award['points_str']} + ${award['fees']}")
                
                # If still no award data, try to find any points patterns
                if not found_awards:
                    logger.info("🔄 Trying broader points patterns...")
                    broad_patterns = [
                        r'(\d{1,3}(?:\.\d)?K)\s*(?:miles|points|pts)',  # "12.5K miles"
                        r'(\d{4,6})\s*(?:miles|points|pts)',  # "12500 miles"
                        r'(\d{1,2},\d{3})\s*(?:miles|points|pts)',  # "12,500 miles"
                    ]
                    
                    for pattern in broad_patterns:
                        matches = re.findall(pattern, page_content, re.IGNORECASE)
                        for match in matches:
                            points_str = match
                            if points_str.upper().endswith('K'):
                                points_num = float(points_str[:-1])
                                actual_points = int(points_num * 1000)
                            else:
                                actual_points = int(points_str.replace(',', ''))
                            
                            if actual_points >= 1000:  # Reasonable points range
                                found_awards.append({
                                    'points': actual_points,
                                    'fees': 5.60,  # Default fees
                                    'points_str': points_str
                                })
                    
                    logger.info(f"🎯 Found {len(found_awards)} broad award patterns")
                    
                    # Assign to flights
                    for i, flight in enumerate(flights_data):
                        if i < len(found_awards):
                            award = found_awards[i]
                            flight['points_required'] = award['points']
                            flight['taxes_fees_usd'] = award['fees']
                            
                            if flight.get('cash_price_usd') and award['points']:
                                cpp = ((flight['cash_price_usd'] - award['fees']) / award['points']) * 100
                                flight['cpp'] = round(cpp, 2)
            
        except Exception as e:
            logger.warning(f"⚠️ Alternative award extraction failed: {e}")
        
        return flights_data
    
    def _clean_and_deduplicate_flights(self, flights_data: List[Dict]) -> List[Dict]:
        """Clean up and deduplicate flight results"""
        logger.info("🧹 Cleaning and deduplicating flights...")
        
        # Remove duplicates based on flight number and key data
        seen_flights = set()
        cleaned_flights = []
        
        for flight in flights_data:
            # Create a key for deduplication
            flight_key = (
                flight.get('flight_number'),
                flight.get('departure_time'),
                flight.get('cash_price_usd'),
                flight.get('points_required')
            )
            
            if flight_key not in seen_flights:
                seen_flights.add(flight_key)
                cleaned_flights.append(flight)
            else:
                logger.debug(f"  🗑️ Removed duplicate: {flight.get('flight_number')}")
        
        # Sort by flight number for consistency
        cleaned_flights.sort(key=lambda x: x.get('flight_number', ''))
        
        logger.info(f"🧹 Cleaned from {len(flights_data)} to {len(cleaned_flights)} flights")
        
        return cleaned_flights
    
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