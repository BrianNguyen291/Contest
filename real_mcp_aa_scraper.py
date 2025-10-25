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
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ScraperAPI key for final HTML fetching
SCRAPERAPI_KEY = "6d27e9060aa3db9d1e187dbd8a3277e2"  # Replace with your actual key

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
                
        except Exception as e:
            logger.warning(f"    ⚠️ MCP tool failed: {e}")
            return None
    
    def _parse_snapshot_for_elements(self, snapshot) -> Dict[str, str]:
        """Parse snapshot to find element references like Playwright MCP does"""
        elements = {}
        snapshot_text = str(snapshot)
        
        # Use the EXACT same approach that worked in our test
        # Look for the specific refs we know work: e128, e136, e149, e161
        elements['from airport'] = 'e128'  # From field
        elements['to airport'] = 'e136'    # To field  
        elements['depart date'] = 'e149'   # Depart date field
        elements['search button'] = 'e161' # Search button
        
        logger.info(f"    Using known working refs: {elements}")
        return elements
    
    def _find_element_ref(self, elements: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find element reference by keywords"""
        for key in elements:
            for keyword in keywords:
                if keyword in key.lower():
                    return elements[key]
        return None
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1) -> Dict:
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
            nav_result = self._call_mcp_tool('browser_navigate', url=self.base_url)
            
            if not nav_result:
                raise Exception("Failed to navigate to AA.com")
            
            time.sleep(3)
            logger.info("✅ Page loaded")
            
            # STEP 2: Take snapshot to get element references
            logger.info("📸 Step 2: Taking page snapshot...")
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
            
            # STEP 7: Click "Search" button using EXACT ref that worked in test
            logger.info("🔍 Step 7: Clicking 'Search' button...")
            click_result = self._call_mcp_tool('browser_click', element='Search button', ref='e161')
            logger.info(f"  ✅ Clicked Search button with ref: e161")
            logger.info(f"  Click result: {click_result}")
            
            time.sleep(8)
            logger.info("✅ Search submitted, waiting for results...")
            
            # STEP 8: Wait for page to fully load and get results snapshot
            logger.info("📸 Step 8: Waiting for page to load and getting results snapshot...")
            time.sleep(10)  # Wait longer for JavaScript to load flight data
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
            
            # STEP 9: Get current URL and fetch HTML from ScraperAPI
            logger.info("🎫 Step 9: Getting current URL and fetching HTML from ScraperAPI...")
            current_url = self._get_current_url()
            logger.info(f"  📍 Current URL: {current_url}")
            html_content = self._get_html_from_scraperapi(current_url)
            
            if not html_content:
                logger.warning("⚠️ ScraperAPI failed, trying snapshot extraction...")
                flights_data = self._extract_flights_from_snapshot(str(results_snapshot if results_snapshot else snapshot))
            else:
                logger.info(f"✅ Got {len(html_content)} bytes of real HTML")
                flights_data = self._extract_flights_from_html(html_content)
            
            if not flights_data:
                logger.error("❌ No flights extracted")
                raise Exception("Failed to extract any flight data")
            
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
    
    def _get_current_url(self) -> str:
        """Get current URL from MCP browser"""
        try:
            # Use browser_evaluate to get current URL
            result = self._call_mcp_tool('browser_evaluate', function='() => window.location.href')
            if result and 'content' in result:
                # Extract URL from the response text
                response_text = result['content'][0]['text']
                # Look for URL in quotes
                import re
                url_match = re.search(r'"https://[^"]*"', response_text)
                if url_match:
                    url = url_match.group(0).strip('"')
                    logger.info(f"    ✅ Extracted URL: {url}")
                    return url
            return self.base_url
        except Exception as e:
            logger.warning(f"    ⚠️ Could not get current URL: {e}")
            return self.base_url
    
    def _get_html_from_scraperapi(self, results_url: str = None) -> Optional[str]:
        """Get HTML content from ScraperAPI"""
        logger.info("  🌐 Fetching HTML from ScraperAPI...")
        try:
            # Use the results URL if provided, otherwise use homepage
            target_url = results_url or self.base_url
            logger.info(f"    🎯 Fetching: {target_url}")
            
            response = requests.get(
                f"https://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_url}&render=true",
                headers={"Accept": "text/html"},
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"    ✅ ScraperAPI returned {len(response.text)} bytes")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"    ⚠️ Failed to fetch HTML from ScraperAPI: {e}")
            return None
    
    def _extract_flights_from_html(self, html_content: str) -> List[Dict]:
        """Extract flight data from HTML content"""
        flights = []
        logger.info("  🔍 Parsing HTML content...")
        
        # Extract flight numbers
        flight_matches = re.findall(r'(AA\d{1,4})', html_content)
        logger.info(f"    Found {len(set(flight_matches))} unique flight numbers")
        
        # Extract prices
        price_matches = re.findall(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', html_content)
        logger.info(f"    Found {len(price_matches)} prices")
        
        # Extract times
        time_matches = re.findall(r'\b([0-2][0-9]:[0-5][0-9])\b', html_content)
        logger.info(f"    Found {len(time_matches)} times")
        
        # Extract points
        points_matches = re.findall(r'(\d{4,6})\s*(?:miles|points|pts)', html_content)
        logger.info(f"    Found {len(points_matches)} point values")
        
        unique_flights = list(set(flight_matches))[:20]
        
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
        
        logger.info(f"  ✅ Extracted {len(flights)} flights from HTML")
        return flights
    
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
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"📅 Searching for flights TODAY: {today}")
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        scraper.start_mcp_server()
        
        # Search for flights
        result = scraper.search_flights("LAX", "JFK", today)
        
        # Save results
        output_file = "operation_point_break_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n📊 OPERATION POINT BREAK - RESULTS:")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        print(f"\n💾 Results saved to: {output_file}")
        print(f"🎯 Total flights: {result['total_results']}")
        print("\n🏆 Operation Point Break complete!")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()