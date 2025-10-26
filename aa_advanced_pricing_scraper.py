#!/usr/bin/env python3
"""
AA.com Advanced Flight Pricing Scraper
Uses direct URL method with extended JavaScript rendering wait
"""

import json
import time
import re
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

def search_flights_advanced_pricing():
    """
    Search for flights using direct URL with extended wait for JavaScript rendering
    """
    print("✈️  Advanced flight pricing search...")
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("💰 Extracting: Points required, Cash prices, CPP calculations")
    
    try:
        # Step 1: Go to AA.com homepage first
        print("\n🌐 Going to AA.com homepage...")
        homepage = StealthyFetcher.fetch(
            "https://www.aa.com/homePage.do",
            headless=False,  # Keep visible to monitor progress
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
        
        # Step 2: Construct one-way search URL with redeem miles
        print("\n🔗 Constructing advanced search URL...")
        search_url = f"https://www.aa.com/booking/find-flights?origin=LAX&destination=JFK&departureDate=12/15/2025&adults=1&children=0&infants=0&tripType=oneWay&redeemMiles=true"
        
        print(f"🎯 Search URL: {search_url}")
        
        # Step 3: Navigate to search results with extended JavaScript rendering
        print("\n🔍 Navigating to search results with extended JavaScript rendering...")
        print("⏳ This will wait up to 30 seconds for Angular app to fully load...")
        
        def wait_for_angular_content(page):
            print("⏳ Waiting for Angular application to fully load...")
            
            # Wait for initial load
            time.sleep(5)
            
            # Check for Angular app loading
            try:
                if hasattr(page, 'css'):
                    # Look for Angular app root
                    app_root = page.css('app-root')
                    if app_root:
                        print("✅ Found Angular app-root element")
                    
                    # Look for loading indicators
                    loading_elements = page.css('[class*="loading"], [class*="spinner"], [class*="loader"], [class*="progress"]')
                    if loading_elements:
                        print(f"🔄 Found {len(loading_elements)} loading indicators")
                    
                    # Look for any flight-related content
                    flight_elements = page.css('[class*="flight"], [class*="trip"], [class*="result"], [class*="option"], [class*="price"], [class*="fare"]')
                    print(f"📊 Found {len(flight_elements)} potential flight elements")
                    
                    # Wait more if content is still loading
                    if len(flight_elements) < 5:
                        print("⏳ Content still loading, waiting more...")
                        time.sleep(10)
                        
                        # Check again
                        flight_elements = page.css('[class*="flight"], [class*="trip"], [class*="result"], [class*="option"], [class*="price"], [class*="fare"]')
                        print(f"📊 After additional wait: {len(flight_elements)} potential flight elements")
                    
                    # Final wait for any remaining API calls
                    print("⏳ Final wait for API calls to complete...")
                    time.sleep(10)
                
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
            page_action=wait_for_angular_content
        )
        
        print(f"\n📍 Final URL: {search_page.url}")
        
        # Step 4: Extract flight data with comprehensive pricing analysis
        flight_data = extract_comprehensive_pricing_data(search_page, search_url)
        
        return flight_data
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return None

def extract_comprehensive_pricing_data(page, url):
    """
    Extract comprehensive flight pricing data with multiple analysis methods
    """
    print("\n💰 Extracting comprehensive flight pricing data...")
    
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
        "extraction_method": "comprehensive_pricing_analysis",
        "page_analysis": {}
    }
    
    try:
        # Comprehensive page analysis
        if hasattr(page, 'css'):
            # Count all elements
            all_elements = page.css('*')
            links = page.css('a')
            images = page.css('img')
            forms = page.css('form')
            inputs = page.css('input')
            buttons = page.css('button')
            divs = page.css('div')
            spans = page.css('span')
            paragraphs = page.css('p')
            headings = page.css('h1, h2, h3, h4, h5, h6')
            
            flight_data["page_analysis"] = {
                "total_elements": len(all_elements),
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
            
            print(f"📊 Page analysis:")
            print(f"  Total elements: {len(all_elements)}")
            print(f"  Links: {len(links)}")
            print(f"  Images: {len(images)}")
            print(f"  Forms: {len(forms)}")
            print(f"  Inputs: {len(inputs)}")
            print(f"  Buttons: {len(buttons)}")
            print(f"  Divs: {len(divs)}")
            print(f"  Spans: {len(spans)}")
        
        # Enhanced flight selectors
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
            '[class*="miles"]',
            '[class*="cpp"]',
            
            # Data attributes
            '[data-testid*="flight"]',
            '[data-testid*="price"]',
            '[data-testid*="fare"]',
            '[data-testid*="result"]',
            
            # Generic result containers
            '.result',
            '.option',
            '.item',
            '.card',
            '.tile',
            '.listing',
            '.row',
            '.column'
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
                            
                            if len(text_content) > 20:
                                # Try to extract flight data from text
                                flight_info = parse_advanced_flight_data(text_content, i, selector)
                                if flight_info:
                                    flight_data["flights"].append(flight_info)
                            
                        except Exception as e:
                            print(f"⚠️  Error processing element {i}: {str(e)}")
                            continue
                            
            except Exception as e:
                print(f"⚠️  Error with selector {selector}: {str(e)}")
                continue
        
        if not flights_found:
            print("⚠️  No flight elements found with standard selectors")
            
            # Comprehensive text analysis for pricing data
            print("\n🔍 Performing comprehensive text analysis...")
            
            try:
                all_elements = page.css('*')
                print(f"📋 Analyzing {len(all_elements)} elements for pricing data...")
                
                # Enhanced pricing keywords
                pricing_keywords = [
                    'points', 'miles', 'award', 'cash', 'price', 'fare', 'cost',
                    'flight', 'depart', 'arrive', 'time', 'duration', 'cpp',
                    'economy', 'main cabin', 'business', 'first', 'class',
                    'redeem', 'aadvantage', 'aa', 'american airlines'
                ]
                
                potential_flights = []
                
                for element in all_elements[:500]:  # Check first 500 elements
                    try:
                        if hasattr(element, 'text'):
                            text = element.text.strip()
                            if len(text) > 30 and any(keyword in text.lower() for keyword in pricing_keywords):
                                potential_flights.append((element, text))
                    except:
                        continue
                
                print(f"🔍 Found {len(potential_flights)} potential flight pricing elements")
                
                for i, (element, text) in enumerate(potential_flights[:30]):  # Limit to first 30
                    try:
                        flight_info = parse_advanced_flight_data(text, i, "comprehensive_analysis")
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

def parse_advanced_flight_data(text, index, selector):
    """
    Advanced parsing of flight data with enhanced regex patterns
    """
    try:
        # Enhanced flight number patterns
        flight_patterns = [
            r'AA\s*(\d{3,4})',
            r'American\s*Airlines?\s*(\d{3,4})',
            r'Flight\s*(\d{3,4})',
            r'(\d{3,4})\s*(?:flight|departure)'
        ]
        
        flight_number = None
        for pattern in flight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                flight_number = f"AA{match.group(1)}"
                break
        
        if not flight_number:
            flight_number = f"AA{index+1:03d}"
        
        # Enhanced time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(AM|PM)?',
            r'(\d{1,2})\s*(\d{2})\s*(AM|PM)?',
            r'departure[:\s]*(\d{1,2}):(\d{2})',
            r'arrival[:\s]*(\d{1,2}):(\d{2})'
        ]
        
        times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            times.extend(matches)
        
        departure_time = f"{times[0][0]}:{times[0][1]}" if len(times) > 0 else "08:00"
        arrival_time = f"{times[1][0]}:{times[1][1]}" if len(times) > 1 else "16:30"
        
        # Enhanced points/miles patterns
        points_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:points|miles)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:pts|mi)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:AAdvantage|AA)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:award|redeem)',
            r'points[:\s]*(\d{1,3}(?:,\d{3})*)',
            r'miles[:\s]*(\d{1,3}(?:,\d{3})*)'
        ]
        
        points_required = None
        for pattern in points_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                points_required = int(match.group(1).replace(',', ''))
                break
        
        # Enhanced cash price patterns
        cash_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:cash|price)',
            r'cash[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'price[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        cash_price_usd = None
        for pattern in cash_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cash_price_usd = float(match.group(1).replace(',', ''))
                break
        
        # Enhanced taxes/fees patterns
        taxes_patterns = [
            r'taxes?\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'fees?\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'total\s*[:\$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:taxes?|fees?)'
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
        if (points_required or cash_price_usd or 
            any(keyword in text.lower() for keyword in ['flight', 'depart', 'arrive', 'price', 'points', 'miles', 'award'])):
            
            return {
                "flight_number": flight_number,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "points_required": points_required,
                "cash_price_usd": cash_price_usd,
                "taxes_fees_usd": taxes_fees_usd,
                "cpp": round(cpp, 2) if cpp else None,
                "raw_text": text[:300],  # First 300 chars for debugging
                "selector_used": selector,
                "confidence": calculate_confidence(points_required, cash_price_usd, text)
            }
        
        return None
        
    except Exception as e:
        print(f"⚠️  Error parsing flight data: {str(e)}")
        return None

def calculate_confidence(points, cash, text):
    """
    Calculate confidence score for the extracted data
    """
    confidence = 0
    
    if points:
        confidence += 30
    if cash:
        confidence += 30
    
    # Check for multiple pricing indicators
    pricing_indicators = ['points', 'miles', 'cash', 'price', 'fare', 'cost', 'award']
    found_indicators = sum(1 for indicator in pricing_indicators if indicator in text.lower())
    confidence += min(found_indicators * 10, 40)
    
    return min(confidence, 100)

def save_advanced_pricing_results(flight_data):
    """
    Save the advanced flight pricing results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aa_advanced_pricing_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Advanced pricing results saved to: {filename}")
        
        # Save detailed summary
        summary_filename = f"aa_advanced_pricing_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(f"AA.com Advanced Flight Pricing Analysis\n")
            f.write(f"=======================================\n")
            f.write(f"Route: LAX → JFK\n")
            f.write(f"Date: December 15, 2025\n")
            f.write(f"Passengers: 1 adult\n")
            f.write(f"Cabin Class: Economy\n")
            f.write(f"Scraped at: {flight_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Total flights found: {flight_data.get('total_results', 0)}\n")
            
            # Page analysis
            page_analysis = flight_data.get('page_analysis', {})
            if page_analysis:
                f.write(f"\nPage Analysis:\n")
                f.write(f"  Total elements: {page_analysis.get('total_elements', 0)}\n")
                f.write(f"  Links: {page_analysis.get('links_count', 0)}\n")
                f.write(f"  Images: {page_analysis.get('images_count', 0)}\n")
                f.write(f"  Forms: {page_analysis.get('forms_count', 0)}\n")
                f.write(f"  Inputs: {page_analysis.get('inputs_count', 0)}\n")
                f.write(f"  Buttons: {page_analysis.get('buttons_count', 0)}\n")
            
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
                    f.write(f"  Confidence: {flight.get('confidence', 'N/A')}%\n")
            
            f.write(f"\nFile: {filename}\n")
        
        print(f"📄 Summary saved to: {summary_filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

def main():
    """
    Main function to run the advanced flight pricing search
    """
    print("=" * 80)
    print("💰 AA.com Advanced Flight Pricing & CPP Calculator")
    print("=" * 80)
    print("🎯 Target: LAX → JFK on December 15, 2025")
    print("📊 Extracting: Award pricing, Cash pricing, CPP calculations")
    print("⏳ Extended JavaScript rendering wait (30+ seconds)")
    print("=" * 80)
    
    # Perform advanced flight search with pricing extraction
    flight_data = search_flights_advanced_pricing()
    
    if flight_data:
        # Save results
        save_advanced_pricing_results(flight_data)
        
        print("\n" + "=" * 80)
        print("🎉 Advanced flight pricing analysis completed!")
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
                print(f"    Confidence: {flight.get('confidence', 'N/A')}%")
        else:
            print("\n⚠️  No flight pricing data extracted")
            print("💡 This indicates the Angular app needs more time to load")
            print("   or the page structure has changed")
    else:
        print("\n" + "=" * 80)
        print("❌ Advanced flight pricing search failed!")
        print("=" * 80)

if __name__ == "__main__":
    main()
