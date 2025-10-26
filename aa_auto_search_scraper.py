#!/usr/bin/env python3
"""
Enhanced AA.com Scraper with Automatic Flight Search
This script automatically performs a flight search to get fresh booking URLs,
then scrapes the flight results.
"""

import json
import time
from datetime import datetime, timedelta
from scrapling.fetchers import StealthyFetcher, StealthySession

class AAFlightSearcher:
    def __init__(self):
        self.session = None
        self.search_results = []
        
    def setup_session(self):
        """Setup a persistent session for multiple requests"""
        print("🔧 Setting up persistent session...")
        self.session = StealthySession(
            headless=False,  # Set to True for production
            solve_cloudflare=True,
            humanize=2.0,
            geoip=True,
            os_randomize=True,
            disable_ads=True,
            google_search=True,
            block_webrtc=True,
            allow_webgl=False
        )
        return self.session
    
    def perform_flight_search(self, origin="LAX", destination="JFK", depart_date=None, return_date=None):
        """
        Perform a flight search on AA.com to get fresh booking URLs
        """
        print(f"✈️  Starting flight search: {origin} → {destination}")
        
        if not depart_date:
            # Default to tomorrow
            depart_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        
        if not return_date:
            # Default to 3 days later
            return_date = (datetime.now() + timedelta(days=4)).strftime("%m/%d/%Y")
        
        print(f"📅 Departure: {depart_date}")
        print(f"📅 Return: {return_date}")
        
        try:
            # Step 1: Go to AA.com homepage
            print("🌐 Navigating to AA.com homepage...")
            homepage = self.session.fetch("https://www.aa.com/homePage.do")
            
            # Step 2: Fill out the flight search form
            print("📝 Filling out flight search form...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to find and fill the search form
            search_data = {
                "origin": origin,
                "destination": destination,
                "depart_date": depart_date,
                "return_date": return_date,
                "passengers": "1"
            }
            
            # Look for form elements
            origin_inputs = homepage.css('input[name*="origin"], input[id*="origin"], input[data-for*="origin"]')
            dest_inputs = homepage.css('input[name*="destination"], input[id*="destination"], input[data-for*="destination"]')
            depart_inputs = homepage.css('input[name*="depart"], input[id*="depart"], input[data-for*="depart"]')
            return_inputs = homepage.css('input[name*="return"], input[id*="return"], input[data-for*="return"]')
            search_buttons = homepage.css('button[type="submit"], input[type="submit"], button:contains("Search"), button:contains("Find")')
            
            print(f"🔍 Found form elements:")
            print(f"  Origin inputs: {len(origin_inputs)}")
            print(f"  Destination inputs: {len(dest_inputs)}")
            print(f"  Departure inputs: {len(depart_inputs)}")
            print(f"  Return inputs: {len(return_inputs)}")
            print(f"  Search buttons: {len(search_buttons)}")
            
            # Try to interact with the form using JavaScript
            print("🔧 Attempting form interaction...")
            
            # Execute JavaScript to fill the form
            js_code = f"""
            // Try to find and fill form elements
            var originInputs = document.querySelectorAll('input[name*="origin"], input[id*="origin"], input[data-for*="origin"]');
            var destInputs = document.querySelectorAll('input[name*="destination"], input[id*="destination"], input[data-for*="destination"]');
            var departInputs = document.querySelectorAll('input[name*="depart"], input[id*="depart"], input[data-for*="depart"]');
            var returnInputs = document.querySelectorAll('input[name*="return"], input[id*="return"], input[data-for*="return"]');
            
            // Fill origin
            if (originInputs.length > 0) {{
                originInputs[0].value = '{origin}';
                originInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                originInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            // Fill destination
            if (destInputs.length > 0) {{
                destInputs[0].value = '{destination}';
                destInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                destInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            // Fill departure date
            if (departInputs.length > 0) {{
                departInputs[0].value = '{depart_date}';
                departInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                departInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            // Fill return date
            if (returnInputs.length > 0) {{
                returnInputs[0].value = '{return_date}';
                returnInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                returnInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            
            // Return form data
            return {{
                origin_filled: originInputs.length > 0,
                dest_filled: destInputs.length > 0,
                depart_filled: departInputs.length > 0,
                return_filled: returnInputs.length > 0,
                form_elements: {{
                    origin: originInputs.length,
                    destination: destInputs.length,
                    depart: departInputs.length,
                    return: returnInputs.length
                }}
            }};
            """
            
            # Execute the JavaScript
            form_result = homepage.execute_script(js_code)
            print(f"📋 Form filling result: {form_result}")
            
            # Wait a moment for the form to process
            time.sleep(2)
            
            # Try to submit the form
            print("🚀 Attempting to submit search form...")
            
            submit_js = """
            // Find and click search button
            var searchButtons = document.querySelectorAll('button[type="submit"], input[type="submit"], button:contains("Search"), button:contains("Find")');
            if (searchButtons.length > 0) {
                searchButtons[0].click();
                return { submitted: true, button_text: searchButtons[0].textContent || searchButtons[0].value };
            }
            
            // Try alternative selectors
            var altButtons = document.querySelectorAll('[data-testid*="search"], [class*="search"], [id*="search"]');
            if (altButtons.length > 0) {
                altButtons[0].click();
                return { submitted: true, button_text: altButtons[0].textContent || altButtons[0].value, method: "alternative" };
            }
            
            return { submitted: false, error: "No search button found" };
            """
            
            submit_result = homepage.execute_script(submit_js)
            print(f"🎯 Submit result: {submit_result}")
            
            # Wait for search results to load
            print("⏳ Waiting for search results...")
            time.sleep(5)
            
            # Check if we got redirected to search results
            current_url = homepage.url
            print(f"📍 Current URL after search: {current_url}")
            
            if "booking" in current_url or "search" in current_url or "results" in current_url:
                print("✅ Successfully navigated to search results!")
                return current_url, homepage
            else:
                print("⚠️  May not have reached search results page")
                return current_url, homepage
                
        except Exception as e:
            print(f"❌ Error during flight search: {str(e)}")
            return None, None
    
    def scrape_search_results(self, results_url, page):
        """
        Scrape flight search results from the booking page
        """
        print(f"🔍 Scraping search results from: {results_url}")
        
        flight_data = {
            "scraped_at": datetime.now().isoformat(),
            "search_url": results_url,
            "title": "",
            "flights": [],
            "raw_content": ""
        }
        
        try:
            # Get page title
            if hasattr(page, 'title'):
                flight_data["title"] = page.title
            
            # Look for flight results
            flight_selectors = [
                '.flight-option',
                '.flight-card',
                '.flight-result',
                '.trip-option',
                '.flight-details',
                '.trip-summary',
                '.search-results',
                '.booking-options',
                '[data-testid*="flight"]',
                '[class*="flight"]',
                '[class*="trip"]',
                '[class*="option"]'
            ]
            
            flights_found = False
            
            for selector in flight_selectors:
                try:
                    elements = page.css(selector)
                    if elements:
                        print(f"📊 Found {len(elements)} elements with selector: {selector}")
                        flights_found = True
                        
                        for i, element in enumerate(elements):
                            try:
                                text_content = element.text.strip() if hasattr(element, 'text') else str(element)
                                html_content = str(element)
                                
                                flight_info = {
                                    "index": i,
                                    "selector_used": selector,
                                    "text_content": text_content[:500],  # Limit text length
                                    "html_content": html_content[:1000]  # Limit HTML length
                                }
                                flight_data["flights"].append(flight_info)
                                
                            except Exception as e:
                                print(f"⚠️  Error processing element {i}: {str(e)}")
                                continue
                                
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            if not flights_found:
                print("⚠️  No flight elements found with standard selectors")
                
                # Try to get any structured data
                try:
                    all_divs = page.css('div')
                    print(f"📋 Found {len(all_divs)} div elements on page")
                    
                    # Look for any elements that might contain flight info
                    potential_elements = page.css('[class*="flight"], [class*="trip"], [class*="option"], [class*="result"]')
                    if potential_elements:
                        print(f"🔍 Found {len(potential_elements)} potential flight-related elements")
                        
                        for i, element in enumerate(potential_elements[:20]):  # Limit to first 20
                            try:
                                text_content = element.text.strip() if hasattr(element, 'text') else str(element)
                                class_name = element.get('class') if hasattr(element, 'get') else ''
                                
                                flight_info = {
                                    "index": i,
                                    "element_type": "potential_flight",
                                    "text_content": text_content[:300],
                                    "class_name": class_name
                                }
                                flight_data["flights"].append(flight_info)
                                
                            except Exception as e:
                                print(f"⚠️  Error processing potential element {i}: {str(e)}")
                                continue
                
                except Exception as e:
                    print(f"❌ Error finding alternative elements: {str(e)}")
            
            # Get raw HTML content
            try:
                flight_data["raw_content"] = page.html if hasattr(page, 'html') else str(page)
            except Exception as e:
                print(f"⚠️  Could not get raw content: {str(e)}")
            
            print(f"✅ Extracted data: {len(flight_data['flights'])} flight elements found")
            
        except Exception as e:
            print(f"❌ Error extracting flight data: {str(e)}")
            flight_data["extraction_error"] = str(e)
        
        return flight_data
    
    def save_results(self, flight_data, search_params):
        """
        Save the scraped data to files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aa_auto_search_results_{timestamp}.json"
        
        try:
            # Add search parameters to the data
            flight_data["search_parameters"] = search_params
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(flight_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            
            # Save summary
            summary_filename = f"aa_auto_search_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write(f"AA.com Automatic Flight Search Results\n")
                f.write(f"=====================================\n")
                f.write(f"Search: {search_params['origin']} → {search_params['destination']}\n")
                f.write(f"Departure: {search_params['depart_date']}\n")
                f.write(f"Return: {search_params['return_date']}\n")
                f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
                f.write(f"Search URL: {flight_data.get('search_url', 'Unknown')}\n")
                f.write(f"Page title: {flight_data.get('title', 'Unknown')}\n")
                f.write(f"Flights found: {len(flight_data.get('flights', []))}\n")
                f.write(f"File: {filename}\n")
            
            print(f"📄 Summary saved to: {summary_filename}")
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")

def main():
    """
    Main function to run the automatic flight search and scraping
    """
    print("=" * 70)
    print("🛫 AA.com Automatic Flight Search & Scraper")
    print("=" * 70)
    
    # Search parameters
    search_params = {
        "origin": "LAX",  # Los Angeles
        "destination": "JFK",  # New York JFK
        "depart_date": (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y"),
        "return_date": (datetime.now() + timedelta(days=4)).strftime("%m/%d/%Y")
    }
    
    print(f"🔍 Search Parameters:")
    print(f"  From: {search_params['origin']}")
    print(f"  To: {search_params['destination']}")
    print(f"  Depart: {search_params['depart_date']}")
    print(f"  Return: {search_params['return_date']}")
    
    # Create searcher instance
    searcher = AAFlightSearcher()
    
    try:
        # Setup session
        searcher.setup_session()
        
        # Perform flight search
        results_url, results_page = searcher.perform_flight_search(**search_params)
        
        if results_url and results_page:
            # Scrape the results
            flight_data = searcher.scrape_search_results(results_url, results_page)
            
            # Save results
            searcher.save_results(flight_data, search_params)
            
            print("\n" + "=" * 70)
            print("🎉 Automatic search and scraping completed!")
            print("=" * 70)
            print(f"📊 Flights found: {len(flight_data.get('flights', []))}")
            print(f"📄 Page title: {flight_data.get('title', 'Unknown')}")
            print(f"🔗 Search URL: {results_url}")
        else:
            print("\n" + "=" * 70)
            print("❌ Flight search failed!")
            print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    finally:
        # Close session
        if searcher.session:
            print("🔒 Closing session...")
            searcher.session.close()

if __name__ == "__main__":
    main()
