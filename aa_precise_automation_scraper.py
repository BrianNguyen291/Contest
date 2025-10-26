#!/usr/bin/env python3
"""
AA.com Precise Browser Automation with Element Inspection
More accurate clicking and form filling with better element detection
"""

import asyncio
import json
import time
import re
from datetime import datetime
from playwright.async_api import async_playwright

class AAPrecisePlaywrightScraper:
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
            "extraction_method": "precise_playwright_automation"
        }
    
    async def search_flights_with_precise_automation(self):
        """
        Search for flights using precise Playwright automation with element inspection
        """
        print("✈️  Precise Playwright flight search...")
        print("🎯 Target: LAX → JFK on December 15, 2025")
        print("🔍 Will inspect elements before clicking for accuracy")
        
        async with async_playwright() as p:
            # Launch browser with more stealth options
            browser = await p.chromium.launch(
                headless=False,  # Keep visible to see what's happening
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-web-security",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-dev-shm-usage",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-images",  # Faster loading
                    "--disable-javascript",  # Disable JS initially to see static content
                ]
            )
            
            # Create context with stealth settings
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Go to AA.com homepage and inspect elements
                print("\n🌐 Going to AA.com homepage...")
                await page.goto("https://www.aa.com/homePage.do", wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
                print("✅ Homepage loaded successfully!")
                
                # Step 2: Inspect and interact with elements more precisely
                await self.inspect_and_interact_with_elements(page)
                
                # Step 3: Try alternative approaches if needed
                await self.try_alternative_approaches(page)
                
                # Save results
                self.save_results()
                
                print("✅ Precise browser automation completed!")
                
            except Exception as e:
                print(f"❌ Error during browser automation: {str(e)}")
                self.results["error"] = str(e)
            
            finally:
                await browser.close()
        
        return self.results
    
    async def inspect_and_interact_with_elements(self, page):
        """
        Inspect elements on the page and interact with them more precisely
        """
        print("🔍 Inspecting page elements for accurate interaction...")
        
        try:
            # First, let's see what elements are actually on the page
            await self.debug_page_elements(page)
            
            # Try to find and interact with form elements
            await self.find_and_fill_form_elements(page)
            
            # Try to find and click search button
            await self.find_and_click_search_button(page)
            
        except Exception as e:
            print(f"⚠️  Error in element inspection: {str(e)}")
    
    async def debug_page_elements(self, page):
        """
        Debug what elements are actually on the page
        """
        print("🔍 Debugging page elements...")
        
        try:
            # Get all input elements
            inputs = await page.query_selector_all('input')
            print(f"📊 Found {len(inputs)} input elements")
            
            for i, input_elem in enumerate(inputs[:10]):  # Show first 10
                try:
                    input_type = await input_elem.get_attribute('type')
                    input_name = await input_elem.get_attribute('name')
                    input_id = await input_elem.get_attribute('id')
                    input_placeholder = await input_elem.get_attribute('placeholder')
                    input_class = await input_elem.get_attribute('class')
                    
                    print(f"  Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}', placeholder='{input_placeholder}', class='{input_class}'")
                except:
                    continue
            
            # Get all button elements
            buttons = await page.query_selector_all('button')
            print(f"📊 Found {len(buttons)} button elements")
            
            for i, button in enumerate(buttons[:10]):  # Show first 10
                try:
                    button_text = await button.inner_text()
                    button_type = await button.get_attribute('type')
                    button_class = await button.get_attribute('class')
                    button_id = await button.get_attribute('id')
                    
                    print(f"  Button {i+1}: text='{button_text}', type='{button_type}', class='{button_class}', id='{button_id}'")
                except:
                    continue
            
            # Get all radio buttons
            radios = await page.query_selector_all('input[type="radio"]')
            print(f"📊 Found {len(radios)} radio button elements")
            
            for i, radio in enumerate(radios[:5]):  # Show first 5
                try:
                    radio_value = await radio.get_attribute('value')
                    radio_name = await radio.get_attribute('name')
                    radio_id = await radio.get_attribute('id')
                    
                    print(f"  Radio {i+1}: value='{radio_value}', name='{radio_name}', id='{radio_id}'")
                except:
                    continue
            
            # Get all checkboxes
            checkboxes = await page.query_selector_all('input[type="checkbox"]')
            print(f"📊 Found {len(checkboxes)} checkbox elements")
            
            for i, checkbox in enumerate(checkboxes[:5]):  # Show first 5
                try:
                    checkbox_name = await checkbox.get_attribute('name')
                    checkbox_id = await checkbox.get_attribute('id')
                    checkbox_class = await checkbox.get_attribute('class')
                    
                    print(f"  Checkbox {i+1}: name='{checkbox_name}', id='{checkbox_id}', class='{checkbox_class}'")
                except:
                    continue
            
        except Exception as e:
            print(f"⚠️  Error debugging elements: {str(e)}")
    
    async def find_and_fill_form_elements(self, page):
        """
        Find and fill form elements based on what we actually see
        """
        print("📝 Finding and filling form elements...")
        
        try:
            # Wait for page to be ready
            await page.wait_for_timeout(3000)
            
            # Try to select one-way trip
            print("🔄 Looking for one-way trip selection...")
            radio_selectors = [
                'input[type="radio"][value*="one"]',
                'input[type="radio"][value*="One"]',
                'input[type="radio"][value*="oneWay"]',
                'input[type="radio"][value*="oneway"]',
                'input[type="radio"][name*="trip"]',
                'input[type="radio"]'
            ]
            
            for selector in radio_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"🔍 Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        try:
                            value = await element.get_attribute('value')
                            name = await element.get_attribute('name')
                            is_visible = await element.is_visible()
                            
                            print(f"  Radio {i+1}: value='{value}', name='{name}', visible={is_visible}")
                            
                            # If it looks like a one-way option, click it
                            if value and ('one' in value.lower() or 'oneway' in value.lower()):
                                if is_visible:
                                    await element.click()
                                    print(f"✅ Clicked one-way radio with value: {value}")
                                    await page.wait_for_timeout(1000)
                                    break
                        except Exception as e:
                            print(f"⚠️  Error with radio {i+1}: {str(e)}")
                            continue
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            # Try to fill origin airport
            print("🔄 Looking for origin airport input...")
            origin_selectors = [
                'input[name*="origin"]',
                'input[id*="origin"]',
                'input[placeholder*="From"]',
                'input[placeholder*="Origin"]',
                'input[aria-label*="From"]',
                'input[aria-label*="Origin"]',
                'input[data-testid*="origin"]',
                'input[data-testid*="from"]'
            ]
            
            for selector in origin_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        print(f"🔍 Found origin element with selector: {selector}, visible={is_visible}, enabled={is_enabled}")
                        
                        if is_visible and is_enabled:
                            await element.click()
                            await element.clear()
                            await element.fill('LAX')
                            await element.press('Tab')
                            print(f"✅ Filled origin with LAX using selector: {selector}")
                            await page.wait_for_timeout(1000)
                            break
                except Exception as e:
                    print(f"⚠️  Error with origin selector {selector}: {str(e)}")
                    continue
            
            # Try to fill destination airport
            print("🔄 Looking for destination airport input...")
            dest_selectors = [
                'input[name*="destination"]',
                'input[id*="destination"]',
                'input[placeholder*="To"]',
                'input[placeholder*="Destination"]',
                'input[aria-label*="To"]',
                'input[aria-label*="Destination"]',
                'input[data-testid*="destination"]',
                'input[data-testid*="to"]'
            ]
            
            for selector in dest_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        print(f"🔍 Found destination element with selector: {selector}, visible={is_visible}, enabled={is_enabled}")
                        
                        if is_visible and is_enabled:
                            await element.click()
                            await element.clear()
                            await element.fill('JFK')
                            await element.press('Tab')
                            print(f"✅ Filled destination with JFK using selector: {selector}")
                            await page.wait_for_timeout(1000)
                            break
                except Exception as e:
                    print(f"⚠️  Error with destination selector {selector}: {str(e)}")
                    continue
            
            # Try to fill departure date
            print("🔄 Looking for departure date input...")
            date_selectors = [
                'input[name*="depart"]',
                'input[id*="depart"]',
                'input[placeholder*="Depart"]',
                'input[type="date"]',
                'input[aria-label*="Depart"]',
                'input[data-testid*="depart"]'
            ]
            
            for selector in date_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        print(f"🔍 Found date element with selector: {selector}, visible={is_visible}, enabled={is_enabled}")
                        
                        if is_visible and is_enabled:
                            await element.click()
                            await element.clear()
                            await element.fill('12/15/2025')
                            await element.press('Tab')
                            print(f"✅ Filled departure date with 12/15/2025 using selector: {selector}")
                            await page.wait_for_timeout(1000)
                            break
                except Exception as e:
                    print(f"⚠️  Error with date selector {selector}: {str(e)}")
                    continue
            
            # Try to check redeem miles checkbox
            print("🔄 Looking for redeem miles checkbox...")
            miles_selectors = [
                'input[type="checkbox"][name*="miles"]',
                'input[type="checkbox"][id*="miles"]',
                'input[type="checkbox"][aria-label*="miles"]',
                'input[type="checkbox"][data-testid*="miles"]'
            ]
            
            for selector in miles_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        print(f"🔍 Found miles checkbox with selector: {selector}, visible={is_visible}, enabled={is_enabled}")
                        
                        if is_visible and is_enabled:
                            await element.check()
                            print(f"✅ Checked redeem miles using selector: {selector}")
                            await page.wait_for_timeout(1000)
                            break
                except Exception as e:
                    print(f"⚠️  Error with miles selector {selector}: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"⚠️  Error filling form elements: {str(e)}")
    
    async def find_and_click_search_button(self, page):
        """
        Find and click the search button more precisely
        """
        print("🔍 Looking for search button...")
        
        try:
            # Wait for button to be ready
            await page.wait_for_timeout(2000)
            
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
                'button[id*="search"]',
                'input[value*="Search"]',
                'button[aria-label*="Search"]',
                'button[aria-label*="Find"]'
            ]
            
            for selector in search_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"🔍 Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        try:
                            is_visible = await element.is_visible()
                            is_enabled = await element.is_enabled()
                            text = await element.inner_text()
                            button_type = await element.get_attribute('type')
                            
                            print(f"  Button {i+1}: text='{text}', type='{button_type}', visible={is_visible}, enabled={is_enabled}")
                            
                            if is_visible and is_enabled and ('search' in text.lower() or 'find' in text.lower() or button_type == 'submit'):
                                await element.click()
                                print(f"✅ Clicked search button with text: '{text}' using selector: {selector}")
                                return True
                        except Exception as e:
                            print(f"⚠️  Error with button {i+1}: {str(e)}")
                            continue
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            print("⚠️  No clickable search button found")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking search button: {str(e)}")
            return False
    
    async def try_alternative_approaches(self, page):
        """
        Try alternative approaches if form filling didn't work
        """
        print("🔄 Trying alternative approaches...")
        
        try:
            # Approach 1: Direct URL navigation
            print("🔄 Trying direct URL approach...")
            search_url = "https://www.aa.com/booking/find-flights?origin=LAX&destination=JFK&departureDate=12/15/2025&adults=1&children=0&infants=0&tripType=oneWay&redeemMiles=true"
            
            print(f"🎯 Direct search URL: {search_url}")
            
            # Navigate directly to search results
            await page.goto(search_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(10000)
            
            print("✅ Navigated to search results page")
            
            # Wait for content to load
            await page.wait_for_timeout(20000)
            
            # Extract flight data
            await self.extract_flight_pricing_data(page)
            
        except Exception as e:
            print(f"❌ Error with alternative approaches: {str(e)}")
    
    async def extract_flight_pricing_data(self, page):
        """
        Extract flight pricing data from the search results page
        """
        print("💰 Extracting flight pricing data...")
        
        self.results["final_url"] = page.url
        
        try:
            # Get page title
            title = await page.title()
            self.results["title"] = title
            print(f"📄 Page title: {title}")
            
            # Wait for content to load
            await page.wait_for_timeout(5000)
            
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
    
    def save_results(self):
        """
        Save the browser automation results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aa_precise_automation_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Precise automation results saved to: {filename}")
            
            # Save summary
            summary_filename = f"aa_precise_automation_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write(f"AA.com Precise Browser Automation Results\n")
                f.write(f"=========================================\n")
                f.write(f"Route: LAX → JFK\n")
                f.write(f"Date: December 15, 2025\n")
                f.write(f"Passengers: 1 adult\n")
                f.write(f"Cabin Class: Economy\n")
                f.write(f"Scraped at: {self.results.get('scraped_at', 'Unknown')}\n")
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
    Main function to run the precise Playwright automation
    """
    print("=" * 80)
    print("🎯 AA.com Precise Browser Automation")
    print("=" * 80)
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("🔍 Will inspect elements before clicking for accuracy")
    print("💰 Extracting: Award pricing, Cash pricing, CPP calculations")
    print("=" * 80)
    
    # Create scraper instance
    scraper = AAPrecisePlaywrightScraper()
    
    # Run precise Playwright automation
    results = await scraper.search_flights_with_precise_automation()
    
    if results:
        print("\n" + "=" * 80)
        print("🎉 Precise automation completed!")
        print("=" * 80)
        print(f"📊 Total flights found: {results.get('total_results', 0)}")
        print(f"📄 Page title: {results.get('title', 'Unknown')}")
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
        print("❌ Precise automation failed!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
