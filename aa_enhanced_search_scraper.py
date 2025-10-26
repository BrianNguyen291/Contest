#!/usr/bin/env python3
"""
Enhanced AA.com Flight Search Scraper with JavaScript Rendering
This script performs a flight search and waits for JavaScript to load the results
"""

import json
import time
from datetime import datetime, timedelta
from scrapling.fetchers import StealthyFetcher

def search_and_scrape_flights_enhanced(origin="LAX", destination="JFK", depart_date=None, return_date=None):
    """
    Search for flights and scrape the results with JavaScript rendering
    """
    print(f"✈️  Searching flights: {origin} → {destination}")
    
    if not depart_date:
        depart_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
    
    if not return_date:
        return_date = (datetime.now() + timedelta(days=4)).strftime("%m/%d/%Y")
    
    print(f"📅 Departure: {depart_date}")
    print(f"📅 Return: {return_date}")
    
    try:
        # Step 1: Go to AA.com homepage first
        print("🌐 Going to AA.com homepage...")
        homepage = StealthyFetcher.fetch(
            "https://www.aa.com/homePage.do",
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
        
        print("✅ Homepage loaded successfully!")
        time.sleep(2)  # Wait a bit
        
        # Step 2: Construct search URL
        print("🔗 Constructing search URL...")
        search_url = f"https://www.aa.com/booking/find-flights?origin={origin}&destination={destination}&departureDate={depart_date}&returnDate={return_date}&adults=1&children=0&infants=0&tripType=roundTrip"
        
        print(f"🎯 Search URL: {search_url}")
        
        # Step 3: Navigate to search results with longer wait time
        print("🔍 Navigating to search results (with JavaScript rendering)...")
        
        # Use a custom page action to wait for content to load
        def wait_for_content(page):
            print("⏳ Waiting for JavaScript to load flight results...")
            
            # Wait for the page to load
            time.sleep(5)
            
            # Try to execute JavaScript to check if content is loaded
            try:
                # Check if there are any flight elements
                js_check = """
                var flightElements = document.querySelectorAll('[class*="flight"], [class*="trip"], [class*="result"], [class*="option"]');
                var loadingElements = document.querySelectorAll('[class*="loading"], [class*="spinner"]');
                
                return {
                    flight_elements: flightElements.length,
                    loading_elements: loadingElements.length,
                    body_text: document.body.innerText.length,
                    ready_state: document.readyState
                };
                """
                
                result = page.execute_script(js_check)
                print(f"📊 Page status: {result}")
                
                # Wait a bit more if content is still loading
                if result.get('loading_elements', 0) > 0 or result.get('flight_elements', 0) == 0:
                    print("⏳ Content still loading, waiting more...")
                    time.sleep(5)
                
                return page
                
            except Exception as e:
                print(f"⚠️  JavaScript check failed: {str(e)}")
                return page
        
        search_page = StealthyFetcher.fetch(
            search_url,
            headless=False,
            solve_cloudflare=True,
            humanize=2.0,
            geoip=True,
            os_randomize=True,
            disable_ads=True,
            google_search=True,
            block_webrtc=True,
            allow_webgl=False,
            page_action=wait_for_content
        )
        
        print(f"📍 Final URL: {search_page.url}")
        
        # Step 4: Extract flight data with enhanced selectors
        flight_data = extract_flight_data_enhanced(search_page, search_url)
        
        return flight_data
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return None

def extract_flight_data_enhanced(page, url):
    """
    Extract flight information with enhanced selectors and JavaScript execution
    """
    print("🔍 Extracting flight data with enhanced methods...")
    
    flight_data = {
        "scraped_at": datetime.now().isoformat(),
        "search_url": url,
        "final_url": page.url if hasattr(page, 'url') else url,
        "title": "",
        "flights": [],
        "page_info": {},
        "javascript_data": {}
    }
    
    try:
        # Get page title
        if hasattr(page, 'title'):
            flight_data["title"] = page.title
        
        # Execute JavaScript to get page information
        try:
            js_info = """
            var info = {
                title: document.title,
                url: window.location.href,
                ready_state: document.readyState,
                body_text_length: document.body.innerText.length,
                all_elements: document.querySelectorAll('*').length,
                div_elements: document.querySelectorAll('div').length,
                span_elements: document.querySelectorAll('span').length,
                p_elements: document.querySelectorAll('p').length,
                flight_keywords: []
            };
            
            // Look for flight-related text
            var flightWords = ['flight', 'depart', 'arrive', 'price', 'fare', 'seat', 'gate', 'terminal', 'airline'];
            var bodyText = document.body.innerText.toLowerCase();
            
            flightWords.forEach(function(word) {
                if (bodyText.includes(word)) {
                    info.flight_keywords.push(word);
                }
            });
            
            return info;
            """
            
            js_result = page.execute_script(js_info)
            flight_data["javascript_data"] = js_result
            print(f"📊 JavaScript page info: {js_result}")
            
        except Exception as e:
            print(f"⚠️  JavaScript execution failed: {str(e)}")
        
        # Get page info using CSS selectors
        if hasattr(page, 'css'):
            links = page.css('a')
            images = page.css('img')
            forms = page.css('form')
            inputs = page.css('input')
            buttons = page.css('button')
            divs = page.css('div')
            spans = page.css('span')
            
            flight_data["page_info"] = {
                "links_count": len(links),
                "images_count": len(images),
                "forms_count": len(forms),
                "inputs_count": len(inputs),
                "buttons_count": len(buttons),
                "divs_count": len(divs),
                "spans_count": len(spans)
            }
            
            print(f"📊 Page elements found:")
            print(f"  🔗 Links: {len(links)}")
            print(f"  🖼️  Images: {len(images)}")
            print(f"  📝 Forms: {len(forms)}")
            print(f"  ⌨️  Inputs: {len(inputs)}")
            print(f"  🔘 Buttons: {len(buttons)}")
            print(f"  📦 Divs: {len(divs)}")
            print(f"  📝 Spans: {len(spans)}")
        
        # Enhanced flight selectors
        flight_selectors = [
            # Common flight result selectors
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
            
            # Data attributes
            '[data-testid*="flight"]',
            '[data-testid*="trip"]',
            '[data-testid*="option"]',
            '[data-testid*="result"]',
            
            # Class patterns
            '[class*="flight"]',
            '[class*="trip"]',
            '[class*="option"]',
            '[class*="result"]',
            '[class*="booking"]',
            '[class*="search"]',
            
            # ID patterns
            '[id*="flight"]',
            '[id*="trip"]',
            '[id*="option"]',
            '[id*="result"]',
            
            # Generic containers that might hold flight data
            '.result',
            '.option',
            '.item',
            '.card',
            '.tile'
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
                            
                            # Only include elements with substantial content
                            if len(text_content) > 10:
                                flight_info = {
                                    "index": i,
                                    "selector_used": selector,
                                    "text_content": text_content[:800],
                                    "element_type": "flight_element",
                                    "content_length": len(text_content)
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
            
            # Try to find any content with flight-related keywords
            try:
                all_elements = page.css('*')
                print(f"📋 Checking {len(all_elements)} total elements for flight content...")
                
                flight_keywords = ['flight', 'depart', 'arrive', 'price', 'fare', 'seat', 'gate', 'terminal', 'airline', 'time', 'duration']
                potential_elements = []
                
                for element in all_elements[:200]:  # Check first 200 elements
                    try:
                        if hasattr(element, 'text'):
                            text = element.text.strip()
                            if len(text) > 20 and any(keyword in text.lower() for keyword in flight_keywords):
                                potential_elements.append((element, text))
                    except:
                        continue
                
                if potential_elements:
                    print(f"🔍 Found {len(potential_elements)} potential flight-related elements")
                    
                    for i, (element, text) in enumerate(potential_elements[:30]):  # Limit to first 30
                        try:
                            flight_info = {
                                "index": i,
                                "element_type": "potential_flight",
                                "text_content": text[:500],
                                "reason": "contains flight keywords",
                                "content_length": len(text)
                            }
                            flight_data["flights"].append(flight_info)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing potential element {i}: {str(e)}")
                            continue
                
            except Exception as e:
                print(f"❌ Error finding alternative elements: {str(e)}")
        
        # Get raw HTML content (first 10000 characters)
        try:
            raw_content = page.html if hasattr(page, 'html') else str(page)
            flight_data["raw_content"] = raw_content[:10000]  # Limit size
        except Exception as e:
            print(f"⚠️  Could not get raw content: {str(e)}")
        
        print(f"✅ Extracted data: {len(flight_data['flights'])} flight elements found")
        
    except Exception as e:
        print(f"❌ Error extracting flight data: {str(e)}")
        flight_data["extraction_error"] = str(e)
    
    return flight_data

def save_results(flight_data, search_params):
    """
    Save the scraped data to files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aa_enhanced_search_results_{timestamp}.json"
    
    try:
        # Add search parameters to the data
        flight_data["search_parameters"] = search_params
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        
        # Save summary
        summary_filename = f"aa_enhanced_search_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"AA.com Enhanced Flight Search Results\n")
            f.write(f"=====================================\n")
            f.write(f"Search: {search_params['origin']} → {search_params['destination']}\n")
            f.write(f"Departure: {search_params['depart_date']}\n")
            f.write(f"Return: {search_params['return_date']}\n")
            f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Search URL: {flight_data.get('search_url', 'Unknown')}\n")
            f.write(f"Final URL: {flight_data.get('final_url', 'Unknown')}\n")
            f.write(f"Page title: {flight_data.get('title', 'Unknown')}\n")
            f.write(f"Flights found: {len(flight_data.get('flights', []))}\n")
            
            # Add JavaScript data summary
            js_data = flight_data.get('javascript_data', {})
            if js_data:
                f.write(f"\nJavaScript Data:\n")
                f.write(f"  Body text length: {js_data.get('body_text_length', 'Unknown')}\n")
                f.write(f"  All elements: {js_data.get('all_elements', 'Unknown')}\n")
                f.write(f"  Flight keywords found: {', '.join(js_data.get('flight_keywords', []))}\n")
            
            f.write(f"\nFile: {filename}\n")
        
        print(f"📄 Summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

def main():
    """
    Main function to run the enhanced flight search and scraping
    """
    print("=" * 70)
    print("🛫 AA.com Enhanced Flight Search & Scraper")
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
    
    # Perform search and scraping
    flight_data = search_and_scrape_flights_enhanced(**search_params)
    
    if flight_data:
        # Save results
        save_results(flight_data, search_params)
        
        print("\n" + "=" * 70)
        print("🎉 Enhanced search and scraping completed!")
        print("=" * 70)
        print(f"📊 Flights found: {len(flight_data.get('flights', []))}")
        print(f"📄 Page title: {flight_data.get('title', 'Unknown')}")
        print(f"🔗 Search URL: {flight_data.get('search_url', 'Unknown')}")
        print(f"📍 Final URL: {flight_data.get('final_url', 'Unknown')}")
        
        # Show JavaScript data summary
        js_data = flight_data.get('javascript_data', {})
        if js_data:
            print(f"📊 Page content: {js_data.get('body_text_length', 'Unknown')} characters")
            print(f"🔍 Flight keywords: {', '.join(js_data.get('flight_keywords', []))}")
    else:
        print("\n" + "=" * 70)
        print("❌ Enhanced search and scraping failed!")
        print("=" * 70)

if __name__ == "__main__":
    main()
