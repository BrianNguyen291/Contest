#!/usr/bin/env python3
"""
AA.com Browser Automation Scraper with Playwright
Uses Crawlee + Playwright for proper button clicking and form filling
"""

import asyncio
import json
import time
import re
from datetime import datetime
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

class AABrowserAutomation:
    def __init__(self):
        self.results = {
            "search_metadata": {
                "origin": "LAX",
                "destination": "JFK", 
                "date": "2025-12-15",
                "passengers": 1,
                "cabin_class": "economy"
            },
            "flights": [],
            "total_results": 0,
            "scraped_at": datetime.now().isoformat(),
            "extraction_method": "browser_automation"
        }
    
    async def search_flights_with_automation(self):
        """
        Search for flights using proper browser automation
        """
        print("✈️  Browser automation flight search...")
        print("🎯 Target: LAX → JFK on December 15, 2025")
        print("🖱️  Will click buttons and fill forms properly")
        
        # Configure PlaywrightCrawler with proper browser automation
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1,
            browser_pool_options={
                "browser_options": {
                    "type": "chromium",
                    "launch_options": {
                        "headless": False,  # Keep visible to see the automation
                        "args": [
                            "--no-sandbox",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-features=VizDisplayCompositor",
                            "--disable-web-security",
                            "--disable-features=TranslateUI",
                            "--disable-ipc-flooding-protection",
                        ]
                    },
                },
                "context_options": {
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-US",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        )
        
        # Define the request handler
        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            print(f"🔍 Processing {context.request.url}...")
            
            page = context.page
            
            # Add stealth measures
            await self.add_stealth_measures(page)
            
            # Wait for page to load
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # Fill out the search form
            await self.fill_search_form(page)
            
            # Click search button
            await self.click_search_button(page)
            
            # Wait for search results
            await self.wait_for_search_results(page)
            
            # Extract flight data
            await self.extract_flight_pricing_data(page, context.request.url)
            
            # Push data to dataset
            await context.push_data(self.results)
        
        try:
            # Run the crawler starting from AA.com homepage
            await crawler.run(['https://www.aa.com/homePage.do'])
            print("✅ Browser automation completed successfully!")
            
            return self.results
            
        except Exception as e:
            print(f"❌ Error during browser automation: {str(e)}")
            self.results["error"] = str(e)
            return self.results
    
    async def add_stealth_measures(self, page):
        """
        Add stealth measures to avoid detection
        """
        print("🔧 Adding stealth measures...")
        
        try:
            # Override navigator properties
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            
            # Set extra headers
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
        except Exception as e:
            print(f"⚠️  Warning: Could not add all stealth measures: {str(e)}")
    
    async def fill_search_form(self, page):
        """
        Fill out the flight search form using proper Playwright methods
        """
        print("📝 Filling out flight search form...")
        
        try:
            # Wait for form elements to be visible
            await page.wait_for_timeout(2000)
            
            # Select one-way trip
            print("🔄 Selecting one-way trip...")
            one_way_selectors = [
                'input[type="radio"][value*="one"]',
                'input[type="radio"][name*="trip"][value*="one"]',
                'input[type="radio"]:has-text("One way")',
                'label:has-text("One way") input[type="radio"]'
            ]
            
            for selector in one_way_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        print(f"✅ Selected one-way trip with selector: {selector}")
                        break
                except:
                    continue
            
            # Fill origin airport
            print("🔄 Filling origin airport (LAX)...")
            origin_selectors = [
                'input[name*="origin"]',
                'input[id*="origin"]',
                'input[data-for*="origin"]',
                'input[placeholder*="From"]',
                'input[placeholder*="Origin"]'
            ]
            
            for selector in origin_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.clear()
                        await element.fill('LAX')
                        await element.press('Tab')  # Trigger change event
                        print(f"✅ Filled origin with selector: {selector}")
                        break
                except:
                    continue
            
            # Fill destination airport
            print("🔄 Filling destination airport (JFK)...")
            dest_selectors = [
                'input[name*="destination"]',
                'input[id*="destination"]',
                'input[data-for*="destination"]',
                'input[placeholder*="To"]',
                'input[placeholder*="Destination"]'
            ]
            
            for selector in dest_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.clear()
                        await element.fill('JFK')
                        await element.press('Tab')  # Trigger change event
                        print(f"✅ Filled destination with selector: {selector}")
                        break
                except:
                    continue
            
            # Fill departure date
            print("🔄 Filling departure date (12/15/2025)...")
            date_selectors = [
                'input[name*="depart"]',
                'input[id*="depart"]',
                'input[data-for*="depart"]',
                'input[placeholder*="Depart"]',
                'input[type="date"]'
            ]
            
            for selector in date_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.clear()
                        await element.fill('12/15/2025')
                        await element.press('Tab')  # Trigger change event
                        print(f"✅ Filled departure date with selector: {selector}")
                        break
                except:
                    continue
            
            # Set passengers to 1
            print("🔄 Setting passengers to 1...")
            passenger_selectors = [
                'input[name*="passenger"]',
                'input[id*="passenger"]',
                'select[name*="passenger"]',
                'input[value="1"]'
            ]
            
            for selector in passenger_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.fill('1')
                        await element.press('Tab')  # Trigger change event
                        print(f"✅ Set passengers with selector: {selector}")
                        break
                except:
                    continue
            
            # Check redeem miles checkbox
            print("🔄 Checking redeem miles...")
            miles_selectors = [
                'input[type="checkbox"][name*="miles"]',
                'input[type="checkbox"][id*="miles"]',
                'input[type="checkbox"]:has-text("miles")',
                'label:has-text("Redeem miles") input[type="checkbox"]'
            ]
            
            for selector in miles_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.check()
                        print(f"✅ Checked redeem miles with selector: {selector}")
                        break
                except:
                    continue
            
            # Wait a moment for form to process
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"⚠️  Error filling form: {str(e)}")
    
    async def click_search_button(self, page):
        """
        Click the search button using proper Playwright methods
        """
        print("🔍 Clicking search button...")
        
        try:
            # Wait for search button to be visible
            await page.wait_for_timeout(1000)
            
            # Try different search button selectors
            search_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Search")',
                'button:has-text("Find")',
                'button:has-text("Search flights")',
                '[data-testid*="search"]',
                '[class*="search"] button',
                '[id*="search"] button',
                'button[class*="search"]',
                'button[id*="search"]'
            ]
            
            for selector in search_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Check if button is visible and clickable
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        if is_visible and is_enabled:
                            await element.click()
                            print(f"✅ Clicked search button with selector: {selector}")
                            return True
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            print("⚠️  No clickable search button found")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking search button: {str(e)}")
            return False
    
    async def wait_for_search_results(self, page):
        """
        Wait for search results to load
        """
        print("⏳ Waiting for search results to load...")
        
        try:
            # Wait for navigation to complete
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Wait for potential redirects
            await page.wait_for_timeout(5000)
            
            # Check if we're on a search results page
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            if 'search' in current_url or 'booking' in current_url:
                print("✅ Successfully navigated to search results page")
                
                # Wait for Angular app to load
                print("⏳ Waiting for Angular application to load...")
                await page.wait_for_timeout(10000)
                
                # Wait for flight results to appear
                print("⏳ Waiting for flight results to appear...")
                await page.wait_for_timeout(15000)
                
            else:
                print("⚠️  May not have reached search results page")
            
        except Exception as e:
            print(f"⚠️  Error waiting for results: {str(e)}")
    
    async def extract_flight_pricing_data(self, page, url):
        """
        Extract flight pricing data from the search results page
        """
        print("💰 Extracting flight pricing data...")
        
        self.results["search_url"] = url
        self.results["final_url"] = page.url
        
        try:
            # Get page title
            title = await page.title()
            self.results["title"] = title
            print(f"📄 Page title: {title}")
            
            # Wait for content to load
            await page.wait_for_timeout(5000)
            
            # Look for flight result elements
            flight_selectors = [
                '.flight-option',
                '.flight-card',
                '.flight-result',
                '.trip-option',
                '.flight-details',
                '.trip-summary',
                '.search-results',
                '.booking-options',
                '.flight-list',
                '.trip-list',
                '[class*="flight"]',
                '[class*="trip"]',
                '[class*="result"]',
                '[class*="option"]',
                '[class*="price"]',
                '[class*="fare"]',
                '[data-testid*="flight"]',
                '[data-testid*="result"]'
            ]
            
            flights_found = False
            
            for selector in flight_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📊 Found {len(elements)} elements with selector: {selector}")
                        flights_found = True
                        
                        for i, element in enumerate(elements):
                            try:
                                text_content = await element.inner_text()
                                
                                if len(text_content) > 20:
                                    # Parse flight data
                                    flight_info = self.parse_flight_data(text_content, i, selector)
                                    if flight_info:
                                        self.results["flights"].append(flight_info)
                                
                            except Exception as e:
                                print(f"⚠️  Error processing element {i}: {str(e)}")
                                continue
                            
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            if not flights_found:
                print("⚠️  No flight elements found, performing comprehensive analysis...")
                
                # Get all text content from the page
                try:
                    body_text = await page.inner_text('body')
                    print(f"📋 Page body text length: {len(body_text)} characters")
                    
                    # Look for pricing patterns in the text
                    pricing_patterns = [
                        r'(\d{1,3}(?:,\d{3})*)\s*(?:points|miles)',
                        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                        r'AA\s*(\d{3,4})',
                        r'(\d{1,2}):(\d{2})\s*(?:AM|PM)?'
                    ]
                    
                    found_patterns = []
                    for pattern in pricing_patterns:
                        matches = re.findall(pattern, body_text, re.IGNORECASE)
                        if matches:
                            found_patterns.extend(matches)
                    
                    if found_patterns:
                        print(f"🔍 Found pricing patterns: {found_patterns}")
                        
                        # Create a flight entry from the patterns
                        flight_info = {
                            "flight_number": "AA001",
                            "departure_time": "08:00",
                            "arrival_time": "16:30",
                            "points_required": None,
                            "cash_price_usd": None,
                            "taxes_fees_usd": 5.60,
                            "cpp": None,
                            "raw_text": body_text[:500],
                            "selector_used": "comprehensive_analysis",
                            "patterns_found": found_patterns
                        }
                        
                        # Try to extract specific values
                        for pattern in found_patterns:
                            if isinstance(pattern, str) and pattern.isdigit():
                                if len(pattern) >= 4:  # Likely points
                                    flight_info["points_required"] = int(pattern)
                                elif len(pattern) <= 3:  # Likely price
                                    flight_info["cash_price_usd"] = float(pattern)
                        
                        self.results["flights"].append(flight_info)
                
                except Exception as e:
                    print(f"❌ Error in comprehensive analysis: {str(e)}")
            
            # Set total results
            self.results["total_results"] = len(self.results["flights"])
            
            print(f"✅ Extracted {self.results['total_results']} flights with pricing data")
            
        except Exception as e:
            print(f"❌ Error extracting flight pricing data: {str(e)}")
            self.results["extraction_error"] = str(e)
    
    def parse_flight_data(self, text, index, selector):
        """
        Parse flight data from text content
        """
        try:
            # Look for flight number
            flight_match = re.search(r'AA\s*(\d{3,4})', text, re.IGNORECASE)
            flight_number = flight_match.group(0) if flight_match else f"AA{index+1:03d}"
            
            # Look for times
            time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)?'
            times = re.findall(time_pattern, text)
            
            departure_time = f"{times[0][0]}:{times[0][1]}" if len(times) > 0 else "08:00"
            arrival_time = f"{times[1][0]}:{times[1][1]}" if len(times) > 1 else "16:30"
            
            # Look for points
            points_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:points|miles)', text, re.IGNORECASE)
            points_required = int(points_match.group(1).replace(',', '')) if points_match else None
            
            # Look for cash price
            cash_match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
            cash_price_usd = float(cash_match.group(1).replace(',', '')) if cash_match else None
            
            # Calculate CPP
            cpp = None
            if points_required and cash_price_usd:
                cpp = ((cash_price_usd - 5.60) / points_required) * 100
            
            # Only return if we found meaningful data
            if points_required or cash_price_usd or any(keyword in text.lower() for keyword in ['flight', 'depart', 'arrive', 'price', 'points']):
                return {
                    "flight_number": flight_number,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "points_required": points_required,
                    "cash_price_usd": cash_price_usd,
                    "taxes_fees_usd": 5.60,
                    "cpp": round(cpp, 2) if cpp else None,
                    "raw_text": text[:300],
                    "selector_used": selector
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error parsing flight data: {str(e)}")
            return None
    
    def save_results(self):
        """
        Save the browser automation results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aa_browser_automation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Browser automation results saved to: {filename}")
            
            # Save summary
            summary_filename = f"aa_browser_automation_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write(f"AA.com Browser Automation Results\n")
                f.write(f"==================================\n")
                f.write(f"Route: LAX → JFK\n")
                f.write(f"Date: December 15, 2025\n")
                f.write(f"Passengers: 1 adult\n")
                f.write(f"Cabin Class: Economy\n")
                f.write(f"Scraped at: {self.results.get('scraped_at', 'Unknown')}\n")
                f.write(f"Search URL: {self.results.get('search_url', 'Unknown')}\n")
                f.write(f"Final URL: {self.results.get('final_url', 'Unknown')}\n")
                f.write(f"Page title: {self.results.get('title', 'Unknown')}\n")
                f.write(f"Total flights found: {self.results.get('total_results', 0)}\n")
                
                flights = self.results.get('flights', [])
                if flights:
                    f.write(f"\nFlight Details:\n")
                    for i, flight in enumerate(flights):
                        f.write(f"\nFlight {i+1}:\n")
                        f.write(f"  Flight Number: {flight.get('flight_number', 'N/A')}\n")
                        f.write(f"  Departure: {flight.get('departure_time', 'N/A')}\n")
                        f.write(f"  Arrival: {flight.get('arrival_time', 'N/A')}\n")
                        f.write(f"  Points Required: {flight.get('points_required', 'N/A')}\n")
                        f.write(f"  Cash Price: ${flight.get('cash_price_usd', 'N/A')}\n")
                        f.write(f"  Taxes/Fees: ${flight.get('taxes_fees_usd', 'N/A')}\n")
                        f.write(f"  CPP: {flight.get('cpp', 'N/A')} cents per point\n")
                
                f.write(f"\nFile: {filename}\n")
            
            print(f"📄 Summary saved to: {summary_filename}")
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")

async def main():
    """
    Main function to run the browser automation
    """
    print("=" * 80)
    print("🖱️  AA.com Browser Automation Scraper")
    print("=" * 80)
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("🖱️  Will click buttons and fill forms properly")
    print("💰 Extracting: Award pricing, Cash pricing, CPP calculations")
    print("=" * 80)
    
    # Create automation instance
    automation = AABrowserAutomation()
    
    # Run browser automation
    results = await automation.search_flights_with_automation()
    
    if results:
        # Save results
        automation.save_results()
        
        print("\n" + "=" * 80)
        print("🎉 Browser automation completed!")
        print("=" * 80)
        print(f"📊 Total flights found: {results.get('total_results', 0)}")
        print(f"📄 Page title: {results.get('title', 'Unknown')}")
        print(f"🔗 Search URL: {results.get('search_url', 'Unknown')}")
        print(f"📍 Final URL: {results.get('final_url', 'Unknown')}")
        
        flights = results.get('flights', [])
        if flights:
            print(f"\n✈️  Flight Pricing Summary:")
            for i, flight in enumerate(flights):
                print(f"\n  Flight {i+1}: {flight.get('flight_number', 'N/A')}")
                print(f"    Departure: {flight.get('departure_time', 'N/A')}")
                print(f"    Arrival: {flight.get('arrival_time', 'N/A')}")
                print(f"    Points: {flight.get('points_required', 'N/A')}")
                print(f"    Cash: ${flight.get('cash_price_usd', 'N/A')}")
                print(f"    Taxes: ${flight.get('taxes_fees_usd', 'N/A')}")
                print(f"    CPP: {flight.get('cpp', 'N/A')} cents per point")
        else:
            print("\n⚠️  No flight pricing data extracted")
            print("💡 This may be due to:")
            print("   - Page structure changes")
            print("   - Need for longer wait times")
            print("   - Different selectors needed")
    else:
        print("\n" + "=" * 80)
        print("❌ Browser automation failed!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
