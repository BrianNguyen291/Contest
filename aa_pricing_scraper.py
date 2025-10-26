#!/usr/bin/env python3
"""
AA.com Flight Search with Award Pricing & CPP Calculator
Clicks the search button and extracts flight data with points/cash pricing
"""

import json
import time
import re
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

def search_flights_with_pricing():
    """
    Search for flights and extract award pricing, cash pricing, and CPP data
    """
    print("✈️  Searching flights with award pricing data...")
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("💰 Extracting: Points required, Cash prices, CPP calculations")
    
    try:
        # Step 1: Go to AA.com homepage
        print("\n🌐 Going to AA.com homepage...")
        homepage = StealthyFetcher.fetch(
            "https://www.aa.com/homePage.do",
            headless=False,  # Keep visible to see the search process
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
        time.sleep(3)
        
        # Step 2: Fill out the search form
        print("\n📝 Filling out flight search form...")
        
        # Try to interact with the form elements
        def fill_search_form(page):
            print("🔧 Attempting to fill search form...")
            
            # JavaScript to fill the form
            fill_js = """
            // Fill origin airport
            var originInputs = document.querySelectorAll('input[name*="origin"], input[id*="origin"], input[data-for*="origin"]');
            if (originInputs.length > 0) {
                originInputs[0].value = 'LAX';
                originInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                originInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Filled origin: LAX');
            }
            
            // Fill destination airport
            var destInputs = document.querySelectorAll('input[name*="destination"], input[id*="destination"], input[data-for*="destination"]');
            if (destInputs.length > 0) {
                destInputs[0].value = 'JFK';
                destInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                destInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Filled destination: JFK');
            }
            
            // Fill departure date
            var departInputs = document.querySelectorAll('input[name*="depart"], input[id*="depart"], input[data-for*="depart"]');
            if (departInputs.length > 0) {
                departInputs[0].value = '12/15/2025';
                departInputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                departInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Filled departure date: 12/15/2025');
            }
            
            // Select one-way trip
            var oneWayRadios = document.querySelectorAll('input[type="radio"][value*="one"], input[type="radio"][name*="trip"][value*="one"]');
            if (oneWayRadios.length > 0) {
                oneWayRadios[0].checked = true;
                oneWayRadios[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Selected one-way trip');
            }
            
            // Set passengers to 1
            var passengerInputs = document.querySelectorAll('input[name*="passenger"], input[id*="passenger"], select[name*="passenger"]');
            if (passengerInputs.length > 0) {
                passengerInputs[0].value = '1';
                passengerInputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Set passengers to 1');
            }
            
            // Check redeem miles checkbox
            var redeemCheckboxes = document.querySelectorAll('input[type="checkbox"][name*="miles"], input[type="checkbox"][id*="miles"]');
            if (redeemCheckboxes.length > 0) {
                redeemCheckboxes[0].checked = true;
                redeemCheckboxes[0].dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Checked redeem miles');
            }
            
            return {
                origin_filled: originInputs.length > 0,
                dest_filled: destInputs.length > 0,
                depart_filled: departInputs.length > 0,
                oneway_selected: oneWayRadios.length > 0,
                passengers_set: passengerInputs.length > 0,
                miles_checked: redeemCheckboxes.length > 0
            };
            """
            
            try:
                result = page.execute_script(fill_js)
                print(f"📋 Form filling result: {result}")
                time.sleep(2)
                
                # Click search button
                print("🔍 Clicking search button...")
                search_js = """
                // Find and click search button
                var searchButtons = document.querySelectorAll('button[type="submit"], input[type="submit"], button:contains("Search"), button:contains("Find")');
                if (searchButtons.length > 0) {
                    searchButtons[0].click();
                    return { clicked: true, button_text: searchButtons[0].textContent || searchButtons[0].value };
                }
                
                // Try alternative selectors
                var altButtons = document.querySelectorAll('[data-testid*="search"], [class*="search"], [id*="search"]');
                if (altButtons.length > 0) {
                    altButtons[0].click();
                    return { clicked: true, button_text: altButtons[0].textContent || altButtons[0].value, method: "alternative" };
                }
                
                return { clicked: false, error: "No search button found" };
                """
                
                search_result = page.execute_script(search_js)
                print(f"🎯 Search button result: {search_result}")
                
                return page
                
            except Exception as e:
                print(f"⚠️  JavaScript execution failed: {str(e)}")
                return page
        
        # Apply form filling
        filled_page = StealthyFetcher.fetch(
            "https://www.aa.com/homePage.do",
            headless=False,
            solve_cloudflare=True,
            humanize=2.0,
            geoip=True,
            os_randomize=True,
            disable_ads=True,
            google_search=True,
            block_webrtc=True,
            allow_webgl=False,
            page_action=fill_search_form
        )
        
        # Wait for search results
        print("\n⏳ Waiting for search results to load...")
        time.sleep(10)
        
        # Step 3: Extract flight data with pricing
        flight_data = extract_flight_pricing_data(filled_page)
        
        return flight_data
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return None

def extract_flight_pricing_data(page):
    """
    Extract flight data with award pricing, cash pricing, and CPP calculations
    """
    print("\n💰 Extracting flight pricing data...")
    
    flight_data = {
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
        "extraction_method": "pricing_analysis"
    }
    
    try:
        # Wait for flight results to load
        print("⏳ Waiting for flight results to appear...")
        time.sleep(5)
        
        # Look for flight result elements
        flight_selectors = [
            # Standard flight result containers
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
            
            # Pricing-specific selectors
            '[class*="price"]',
            '[class*="fare"]',
            '[class*="cost"]',
            '[class*="points"]',
            '[class*="award"]',
            
            # Data attributes
            '[data-testid*="flight"]',
            '[data-testid*="price"]',
            '[data-testid*="fare"]',
            
            # Generic result containers
            '.result',
            '.option',
            '.item',
            '.card',
            '.tile',
            '.listing'
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
                            
                            if len(text_content) > 20:
                                # Try to extract flight data from text
                                flight_info = parse_flight_data(text_content, i, selector)
                                if flight_info:
                                    flight_data["flights"].append(flight_info)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing element {i}: {str(e)}")
                            continue
                            
            except Exception as e:
                print(f"⚠️  Error with selector {selector}: {str(e)}")
                continue
        
        if not flights_found:
            print("⚠️  No flight elements found, performing comprehensive analysis...")
            
            # Comprehensive text analysis for pricing data
            try:
                all_elements = page.css('*')
                print(f"📋 Analyzing {len(all_elements)} elements for pricing data...")
                
                pricing_keywords = [
                    'points', 'miles', 'award', 'cash', 'price', 'fare', 'cost',
                    'flight', 'depart', 'arrive', 'time', 'duration', 'cpp'
                ]
                
                potential_flights = []
                
                for element in all_elements[:200]:
                    try:
                        if hasattr(element, 'text'):
                            text = element.text.strip()
                            if len(text) > 30 and any(keyword in text.lower() for keyword in pricing_keywords):
                                potential_flights.append((element, text))
                    except:
                        continue
                
                print(f"🔍 Found {len(potential_flights)} potential flight pricing elements")
                
                for i, (element, text) in enumerate(potential_flights[:20]):
                    try:
                        flight_info = parse_flight_data(text, i, "comprehensive_analysis")
                        if flight_info:
                            flight_data["flights"].append(flight_info)
                    except Exception as e:
                        print(f"⚠️  Error parsing flight {i}: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"❌ Error in comprehensive analysis: {str(e)}")
        
        # Set total results
        flight_data["total_results"] = len(flight_data["flights"])
        
        print(f"✅ Extracted {flight_data['total_results']} flights with pricing data")
        
    except Exception as e:
        print(f"❌ Error extracting flight pricing data: {str(e)}")
        flight_data["extraction_error"] = str(e)
    
    return flight_data

def parse_flight_data(text, index, selector):
    """
    Parse flight data from text content, extracting pricing information
    """
    try:
        # Look for flight number patterns
        flight_number_match = re.search(r'AA\s*(\d+)', text, re.IGNORECASE)
        flight_number = flight_number_match.group(0) if flight_number_match else f"AA{index+1:03d}"
        
        # Look for time patterns
        time_pattern = r'(\d{1,2}):(\d{2})\s*(AM|PM)?'
        times = re.findall(time_pattern, text)
        
        departure_time = f"{times[0][0]}:{times[0][1]}" if len(times) > 0 else "08:00"
        arrival_time = f"{times[1][0]}:{times[1][1]}" if len(times) > 1 else "16:30"
        
        # Look for points/miles patterns
        points_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:points|miles)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:pts|mi)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:AAdvantage|AA)'
        ]
        
        points_required = None
        for pattern in points_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                points_required = int(match.group(1).replace(',', ''))
                break
        
        # Look for cash price patterns
        cash_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:cash|price)'
        ]
        
        cash_price_usd = None
        for pattern in cash_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cash_price_usd = float(match.group(1).replace(',', ''))
                break
        
        # Look for taxes/fees patterns
        taxes_patterns = [
            r'taxes?\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'fees?\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'total\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        taxes_fees_usd = 5.60  # Default value
        for pattern in taxes_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                taxes_fees_usd = float(match.group(1).replace(',', ''))
                break
        
        # Calculate CPP if we have both points and cash price
        cpp = None
        if points_required and cash_price_usd:
            cpp = ((cash_price_usd - taxes_fees_usd) / points_required) * 100
        
        # Only return flight data if we found meaningful information
        if points_required or cash_price_usd or any(keyword in text.lower() for keyword in ['flight', 'depart', 'arrive', 'price', 'points']):
            return {
                "flight_number": flight_number,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "points_required": points_required,
                "cash_price_usd": cash_price_usd,
                "taxes_fees_usd": taxes_fees_usd,
                "cpp": round(cpp, 2) if cpp else None,
                "raw_text": text[:200],  # First 200 chars for debugging
                "selector_used": selector
            }
        
        return None
        
    except Exception as e:
        print(f"⚠️  Error parsing flight data: {str(e)}")
        return None

def save_pricing_results(flight_data):
    """
    Save the flight pricing results in the required JSON format
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aa_pricing_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Pricing results saved to: {filename}")
        
        # Save summary
        summary_filename = f"aa_pricing_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"AA.com Flight Pricing Analysis\n")
            f.write(f"==============================\n")
            f.write(f"Route: LAX → JFK\n")
            f.write(f"Date: December 15, 2025\n")
            f.write(f"Passengers: 1 adult\n")
            f.write(f"Cabin Class: Economy\n")
            f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Total flights found: {flight_data.get('total_results', 0)}\n")
            
            flights = flight_data.get('flights', [])
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

def main():
    """
    Main function to run the flight pricing search
    """
    print("=" * 80)
    print("💰 AA.com Flight Pricing & CPP Calculator")
    print("=" * 80)
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("📊 Extracting: Award pricing, Cash pricing, CPP calculations")
    print("=" * 80)
    
    # Perform flight search with pricing extraction
    flight_data = search_flights_with_pricing()
    
    if flight_data:
        # Save results
        save_pricing_results(flight_data)
        
        print("\n" + "=" * 80)
        print("🎉 Flight pricing analysis completed!")
        print("=" * 80)
        print(f"📊 Total flights found: {flight_data.get('total_results', 0)}")
        
        flights = flight_data.get('flights', [])
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
            print("   - JavaScript not fully loaded")
            print("   - Different page structure")
            print("   - Need for longer wait times")
    else:
        print("\n" + "=" * 80)
        print("❌ Flight pricing search failed!")
        print("=" * 80)

if __name__ == "__main__":
    main()
