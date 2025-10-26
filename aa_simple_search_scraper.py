#!/usr/bin/env python3
"""
Simple AA.com Flight Search Scraper
This script performs a basic flight search and scrapes results
"""

import json
import time
from datetime import datetime, timedelta
from scrapling.fetchers import StealthyFetcher

def search_and_scrape_flights(origin="LAX", destination="JFK", depart_date=None, return_date=None):
    """
    Search for flights and scrape the results
    """
    print(f"✈️  Searching flights: {origin} → {destination}")
    
    if not depart_date:
        depart_date = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
    
    if not return_date:
        return_date = (datetime.now() + timedelta(days=4)).strftime("%m/%d/%Y")
    
    print(f"📅 Departure: {depart_date}")
    print(f"📅 Return: {return_date}")
    
    try:
        # Step 1: Go to AA.com homepage
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
        
        # Step 2: Try to construct a search URL directly
        print("🔗 Constructing direct search URL...")
        
        # AA.com search URL pattern
        search_url = f"https://www.aa.com/booking/find-flights?origin={origin}&destination={destination}&departureDate={depart_date}&returnDate={return_date}&adults=1&children=0&infants=0&tripType=roundTrip"
        
        print(f"🎯 Search URL: {search_url}")
        
        # Step 3: Navigate to search results
        print("🔍 Navigating to search results...")
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
            allow_webgl=False
        )
        
        print(f"📍 Final URL: {search_page.url}")
        
        # Step 4: Extract flight data
        flight_data = extract_flight_data(search_page, search_url)
        
        return flight_data
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return None

def extract_flight_data(page, url):
    """
    Extract flight information from the search results page
    """
    print("🔍 Extracting flight data...")
    
    flight_data = {
        "scraped_at": datetime.now().isoformat(),
        "search_url": url,
        "final_url": page.url if hasattr(page, 'url') else url,
        "title": "",
        "flights": [],
        "page_info": {}
    }
    
    try:
        # Get page title
        if hasattr(page, 'title'):
            flight_data["title"] = page.title
        
        # Get page info
        if hasattr(page, 'css'):
            links = page.css('a')
            images = page.css('img')
            forms = page.css('form')
            inputs = page.css('input')
            buttons = page.css('button')
            
            flight_data["page_info"] = {
                "links_count": len(links),
                "images_count": len(images),
                "forms_count": len(forms),
                "inputs_count": len(inputs),
                "buttons_count": len(buttons)
            }
            
            print(f"📊 Page elements found:")
            print(f"  🔗 Links: {len(links)}")
            print(f"  🖼️  Images: {len(images)}")
            print(f"  📝 Forms: {len(forms)}")
            print(f"  ⌨️  Inputs: {len(inputs)}")
            print(f"  🔘 Buttons: {len(buttons)}")
        
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
            '[class*="option"]',
            '[class*="result"]'
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
                            
                            flight_info = {
                                "index": i,
                                "selector_used": selector,
                                "text_content": text_content[:500],
                                "element_type": "flight_element"
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
            
            # Try to find any content that might be flight-related
            try:
                all_elements = page.css('*')
                print(f"📋 Found {len(all_elements)} total elements on page")
                
                # Look for elements with flight-related text
                flight_keywords = ['flight', 'depart', 'arrive', 'price', 'fare', 'seat', 'gate']
                potential_elements = []
                
                for element in all_elements[:100]:  # Check first 100 elements
                    try:
                        if hasattr(element, 'text'):
                            text = element.text.strip().lower()
                            if any(keyword in text for keyword in flight_keywords):
                                potential_elements.append(element)
                    except:
                        continue
                
                if potential_elements:
                    print(f"🔍 Found {len(potential_elements)} potential flight-related elements")
                    
                    for i, element in enumerate(potential_elements[:20]):  # Limit to first 20
                        try:
                            text_content = element.text.strip() if hasattr(element, 'text') else str(element)
                            
                            flight_info = {
                                "index": i,
                                "element_type": "potential_flight",
                                "text_content": text_content[:300],
                                "reason": "contains flight keywords"
                            }
                            flight_data["flights"].append(flight_info)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing potential element {i}: {str(e)}")
                            continue
                
            except Exception as e:
                print(f"❌ Error finding alternative elements: {str(e)}")
        
        # Get raw HTML content (first 5000 characters)
        try:
            raw_content = page.html if hasattr(page, 'html') else str(page)
            flight_data["raw_content"] = raw_content[:5000]  # Limit size
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
    filename = f"aa_simple_search_results_{timestamp}.json"
    
    try:
        # Add search parameters to the data
        flight_data["search_parameters"] = search_params
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        
        # Save summary
        summary_filename = f"aa_simple_search_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"AA.com Simple Flight Search Results\n")
            f.write(f"===================================\n")
            f.write(f"Search: {search_params['origin']} → {search_params['destination']}\n")
            f.write(f"Departure: {search_params['depart_date']}\n")
            f.write(f"Return: {search_params['return_date']}\n")
            f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Search URL: {flight_data.get('search_url', 'Unknown')}\n")
            f.write(f"Final URL: {flight_data.get('final_url', 'Unknown')}\n")
            f.write(f"Page title: {flight_data.get('title', 'Unknown')}\n")
            f.write(f"Flights found: {len(flight_data.get('flights', []))}\n")
            f.write(f"File: {filename}\n")
        
        print(f"📄 Summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

def main():
    """
    Main function to run the simple flight search and scraping
    """
    print("=" * 60)
    print("🛫 AA.com Simple Flight Search & Scraper")
    print("=" * 60)
    
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
    flight_data = search_and_scrape_flights(**search_params)
    
    if flight_data:
        # Save results
        save_results(flight_data, search_params)
        
        print("\n" + "=" * 60)
        print("🎉 Search and scraping completed!")
        print("=" * 60)
        print(f"📊 Flights found: {len(flight_data.get('flights', []))}")
        print(f"📄 Page title: {flight_data.get('title', 'Unknown')}")
        print(f"🔗 Search URL: {flight_data.get('search_url', 'Unknown')}")
        print(f"📍 Final URL: {flight_data.get('final_url', 'Unknown')}")
    else:
        print("\n" + "=" * 60)
        print("❌ Search and scraping failed!")
        print("=" * 60)

if __name__ == "__main__":
    main()
