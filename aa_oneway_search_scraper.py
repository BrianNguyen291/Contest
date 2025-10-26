#!/usr/bin/env python3
"""
AA.com One-Way Flight Search Scraper
Searches for: LAX → JFK on December 15, 2025, 1 adult, Economy
"""

import json
import time
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

def search_one_way_flights():
    """
    Search for one-way flights: LAX → JFK on December 15, 2025
    """
    print("✈️  Searching ONE-WAY flights: LAX → JFK")
    print("📅 Date: December 15, 2025")
    print("👤 Passengers: 1 adult")
    print("💺 Class: Economy (Main Cabin)")
    
    # Search parameters
    origin = "LAX"
    destination = "JFK" 
    depart_date = "12/15/2025"
    trip_type = "oneWay"  # One-way flight
    
    try:
        # Step 1: Go to AA.com homepage
        print("\n🌐 Going to AA.com homepage...")
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
        time.sleep(3)  # Wait for page to fully load
        
        # Step 2: Construct one-way search URL
        print("\n🔗 Constructing ONE-WAY search URL...")
        search_url = f"https://www.aa.com/booking/find-flights?origin={origin}&destination={destination}&departureDate={depart_date}&adults=1&children=0&infants=0&tripType={trip_type}"
        
        print(f"🎯 Search URL: {search_url}")
        
        # Step 3: Navigate to search results with extended wait for JavaScript
        print("\n🔍 Navigating to ONE-WAY search results...")
        print("⏳ Waiting for JavaScript to load flight results (this may take 10-15 seconds)...")
        
        def wait_for_flight_content(page):
            print("⏳ Waiting for Angular app to load flight results...")
            
            # Wait longer for JavaScript to load
            time.sleep(10)
            
            # Try to check if content is loading
            try:
                # Look for any signs of flight content
                if hasattr(page, 'css'):
                    # Check for loading indicators
                    loading_elements = page.css('[class*="loading"], [class*="spinner"], [class*="loader"]')
                    if loading_elements:
                        print(f"🔄 Found {len(loading_elements)} loading indicators, waiting more...")
                        time.sleep(5)
                    
                    # Check for any flight-related elements
                    flight_elements = page.css('[class*="flight"], [class*="trip"], [class*="result"], [class*="option"]')
                    print(f"📊 Found {len(flight_elements)} potential flight elements")
                    
                    # Check for any content with flight keywords
                    all_elements = page.css('*')
                    flight_keywords = ['flight', 'depart', 'arrive', 'price', 'fare', 'seat', 'gate', 'terminal']
                    content_found = False
                    
                    for element in all_elements[:100]:
                        try:
                            if hasattr(element, 'text'):
                                text = element.text.strip().lower()
                                if any(keyword in text for keyword in flight_keywords) and len(text) > 10:
                                    content_found = True
                                    break
                        except:
                            continue
                    
                    if content_found:
                        print("✅ Found flight-related content!")
                    else:
                        print("⚠️  No flight content detected yet, waiting more...")
                        time.sleep(5)
                
                return page
                
            except Exception as e:
                print(f"⚠️  Content check failed: {str(e)}")
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
            page_action=wait_for_flight_content
        )
        
        print(f"\n📍 Final URL: {search_page.url}")
        
        # Step 4: Extract flight data with comprehensive analysis
        flight_data = extract_one_way_flight_data(search_page, search_url)
        
        return flight_data
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return None

def extract_one_way_flight_data(page, url):
    """
    Extract one-way flight information with comprehensive analysis
    """
    print("\n🔍 Extracting ONE-WAY flight data...")
    
    flight_data = {
        "scraped_at": datetime.now().isoformat(),
        "search_type": "one_way",
        "search_url": url,
        "final_url": page.url if hasattr(page, 'url') else url,
        "title": "",
        "flights": [],
        "page_info": {},
        "content_analysis": {}
    }
    
    try:
        # Get page title
        if hasattr(page, 'title'):
            flight_data["title"] = page.title
        
        # Comprehensive page analysis
        if hasattr(page, 'css'):
            # Count all elements
            links = page.css('a')
            images = page.css('img')
            forms = page.css('form')
            inputs = page.css('input')
            buttons = page.css('button')
            divs = page.css('div')
            spans = page.css('span')
            paragraphs = page.css('p')
            headings = page.css('h1, h2, h3, h4, h5, h6')
            
            flight_data["page_info"] = {
                "links_count": len(links),
                "images_count": len(images),
                "forms_count": len(forms),
                "inputs_count": len(inputs),
                "buttons_count": len(buttons),
                "divs_count": len(divs),
                "spans_count": len(spans),
                "paragraphs_count": len(paragraphs),
                "headings_count": len(headings)
            }
            
            print(f"📊 Page elements found:")
            print(f"  🔗 Links: {len(links)}")
            print(f"  🖼️  Images: {len(images)}")
            print(f"  📝 Forms: {len(forms)}")
            print(f"  ⌨️  Inputs: {len(inputs)}")
            print(f"  🔘 Buttons: {len(buttons)}")
            print(f"  📦 Divs: {len(divs)}")
            print(f"  📝 Spans: {len(spans)}")
            print(f"  📄 Paragraphs: {len(paragraphs)}")
            print(f"  📋 Headings: {len(headings)}")
        
        # Enhanced flight selectors for one-way flights
        flight_selectors = [
            # Standard flight result selectors
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
            '.one-way-result',
            '.single-trip',
            
            # Data attributes
            '[data-testid*="flight"]',
            '[data-testid*="trip"]',
            '[data-testid*="option"]',
            '[data-testid*="result"]',
            '[data-testid*="oneway"]',
            
            # Class patterns
            '[class*="flight"]',
            '[class*="trip"]',
            '[class*="option"]',
            '[class*="result"]',
            '[class*="booking"]',
            '[class*="search"]',
            '[class*="oneway"]',
            '[class*="single"]',
            
            # ID patterns
            '[id*="flight"]',
            '[id*="trip"]',
            '[id*="option"]',
            '[id*="result"]',
            '[id*="oneway"]',
            
            # Generic containers
            '.result',
            '.option',
            '.item',
            '.card',
            '.tile',
            '.listing'
        ]
        
        flights_found = False
        
        print(f"\n🔍 Searching for flight elements with {len(flight_selectors)} selectors...")
        
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
                            if len(text_content) > 20:
                                flight_info = {
                                    "index": i,
                                    "selector_used": selector,
                                    "text_content": text_content[:1000],
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
            
            # Comprehensive content analysis
            print("\n🔍 Performing comprehensive content analysis...")
            
            try:
                all_elements = page.css('*')
                print(f"📋 Analyzing {len(all_elements)} total elements...")
                
                # Flight-related keywords
                flight_keywords = [
                    'flight', 'depart', 'arrive', 'price', 'fare', 'seat', 'gate', 'terminal', 
                    'airline', 'time', 'duration', 'departure', 'arrival', 'aircraft', 'route',
                    'economy', 'main cabin', 'business', 'first', 'class', 'booking', 'reservation'
                ]
                
                # One-way specific keywords
                oneway_keywords = ['one way', 'oneway', 'single', 'direct', 'nonstop']
                
                potential_elements = []
                oneway_elements = []
                
                for element in all_elements[:300]:  # Check first 300 elements
                    try:
                        if hasattr(element, 'text'):
                            text = element.text.strip()
                            text_lower = text.lower()
                            
                            # Check for flight keywords
                            if len(text) > 15 and any(keyword in text_lower for keyword in flight_keywords):
                                potential_elements.append((element, text))
                            
                            # Check for one-way specific keywords
                            if any(keyword in text_lower for keyword in oneway_keywords):
                                oneway_elements.append((element, text))
                                
                    except:
                        continue
                
                print(f"🔍 Found {len(potential_elements)} potential flight-related elements")
                print(f"🔍 Found {len(oneway_elements)} one-way specific elements")
                
                # Add potential flight elements
                for i, (element, text) in enumerate(potential_elements[:25]):  # Limit to first 25
                    try:
                        flight_info = {
                            "index": i,
                            "element_type": "potential_flight",
                            "text_content": text[:600],
                            "reason": "contains flight keywords",
                            "content_length": len(text)
                        }
                        flight_data["flights"].append(flight_info)
                        
                    except Exception as e:
                        print(f"⚠️  Error processing potential element {i}: {str(e)}")
                        continue
                
                # Add one-way specific elements
                for i, (element, text) in enumerate(oneway_elements[:10]):  # Limit to first 10
                    try:
                        flight_info = {
                            "index": i,
                            "element_type": "oneway_specific",
                            "text_content": text[:400],
                            "reason": "contains one-way keywords",
                            "content_length": len(text)
                        }
                        flight_data["flights"].append(flight_info)
                        
                    except Exception as e:
                        print(f"⚠️  Error processing one-way element {i}: {str(e)}")
                        continue
                
                # Content analysis summary
                flight_data["content_analysis"] = {
                    "total_elements": len(all_elements),
                    "potential_flight_elements": len(potential_elements),
                    "oneway_specific_elements": len(oneway_elements),
                    "flight_keywords_found": [kw for kw in flight_keywords if any(kw in str(all_elements).lower())],
                    "oneway_keywords_found": [kw for kw in oneway_keywords if any(kw in str(all_elements).lower())]
                }
                
            except Exception as e:
                print(f"❌ Error in comprehensive analysis: {str(e)}")
        
        # Get raw HTML content (first 15000 characters)
        try:
            raw_content = page.html if hasattr(page, 'html') else str(page)
            flight_data["raw_content"] = raw_content[:15000]  # Limit size
        except Exception as e:
            print(f"⚠️  Could not get raw content: {str(e)}")
        
        print(f"\n✅ Extraction complete: {len(flight_data['flights'])} flight elements found")
        
    except Exception as e:
        print(f"❌ Error extracting flight data: {str(e)}")
        flight_data["extraction_error"] = str(e)
    
    return flight_data

def save_one_way_results(flight_data):
    """
    Save the one-way flight search results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aa_oneway_search_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Save detailed summary
        summary_filename = f"aa_oneway_search_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"AA.com One-Way Flight Search Results\n")
            f.write(f"====================================\n")
            f.write(f"Route: Los Angeles (LAX) → New York (JFK)\n")
            f.write(f"Date: December 15, 2025\n")
            f.write(f"Passengers: 1 adult\n")
            f.write(f"Class: Economy (Main Cabin)\n")
            f.write(f"Trip Type: One-Way\n")
            f.write(f"\nSearch Details:\n")
            f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Search URL: {flight_data.get('search_url', 'Unknown')}\n")
            f.write(f"Final URL: {flight_data.get('final_url', 'Unknown')}\n")
            f.write(f"Page title: {flight_data.get('title', 'Unknown')}\n")
            f.write(f"Flights found: {len(flight_data.get('flights', []))}\n")
            
            # Add page info
            page_info = flight_data.get('page_info', {})
            if page_info:
                f.write(f"\nPage Elements:\n")
                f.write(f"  Links: {page_info.get('links_count', 0)}\n")
                f.write(f"  Images: {page_info.get('images_count', 0)}\n")
                f.write(f"  Forms: {page_info.get('forms_count', 0)}\n")
                f.write(f"  Inputs: {page_info.get('inputs_count', 0)}\n")
                f.write(f"  Buttons: {page_info.get('buttons_count', 0)}\n")
                f.write(f"  Divs: {page_info.get('divs_count', 0)}\n")
                f.write(f"  Spans: {page_info.get('spans_count', 0)}\n")
            
            # Add content analysis
            content_analysis = flight_data.get('content_analysis', {})
            if content_analysis:
                f.write(f"\nContent Analysis:\n")
                f.write(f"  Total elements: {content_analysis.get('total_elements', 0)}\n")
                f.write(f"  Potential flight elements: {content_analysis.get('potential_flight_elements', 0)}\n")
                f.write(f"  One-way specific elements: {content_analysis.get('oneway_specific_elements', 0)}\n")
                f.write(f"  Flight keywords found: {', '.join(content_analysis.get('flight_keywords_found', []))}\n")
                f.write(f"  One-way keywords found: {', '.join(content_analysis.get('oneway_keywords_found', []))}\n")
            
            f.write(f"\nFile: {filename}\n")
        
        print(f"📄 Summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

def main():
    """
    Main function to run the one-way flight search
    """
    print("=" * 80)
    print("🛫 AA.com ONE-WAY Flight Search Scraper")
    print("=" * 80)
    print("Route: Los Angeles (LAX) → New York (JFK)")
    print("Date: December 15, 2025")
    print("Passengers: 1 adult")
    print("Class: Economy (Main Cabin)")
    print("Trip Type: ONE-WAY")
    print("=" * 80)
    
    # Perform one-way flight search
    flight_data = search_one_way_flights()
    
    if flight_data:
        # Save results
        save_one_way_results(flight_data)
        
        print("\n" + "=" * 80)
        print("🎉 ONE-WAY flight search completed!")
        print("=" * 80)
        print(f"📊 Flights found: {len(flight_data.get('flights', []))}")
        print(f"📄 Page title: {flight_data.get('title', 'Unknown')}")
        print(f"🔗 Search URL: {flight_data.get('search_url', 'Unknown')}")
        print(f"📍 Final URL: {flight_data.get('final_url', 'Unknown')}")
        
        # Show content analysis
        content_analysis = flight_data.get('content_analysis', {})
        if content_analysis:
            print(f"\n📊 Content Analysis:")
            print(f"  Total elements: {content_analysis.get('total_elements', 0)}")
            print(f"  Potential flight elements: {content_analysis.get('potential_flight_elements', 0)}")
            print(f"  One-way specific elements: {content_analysis.get('oneway_specific_elements', 0)}")
        
        # Show first few flight elements
        flights = flight_data.get('flights', [])
        if flights:
            print(f"\n✈️  First few flight elements found:")
            for i, flight in enumerate(flights[:3]):
                print(f"  {i+1}. {flight.get('element_type', 'unknown')}: {flight.get('text_content', '')[:100]}...")
    else:
        print("\n" + "=" * 80)
        print("❌ ONE-WAY flight search failed!")
        print("=" * 80)

if __name__ == "__main__":
    main()
