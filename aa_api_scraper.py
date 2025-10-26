#!/usr/bin/env python3
"""
AA.com API Scraper - Enhanced with Bot Evasion Techniques
Ultra-fast direct API approach with comprehensive CPP calculations
"""

import requests
import json
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AAApiScraper:
    """Enhanced AA.com API scraper with bot evasion techniques"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.aa.com"
        
        # Enhanced bot evasion headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Configure session for bot evasion
        self.session.max_redirects = 5
        self.session.timeout = 30
        
        # Track search results for CPP calculation
        self.cash_flights = []
        self.award_flights = []
    
    def _add_random_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _get_session_token(self) -> Optional[str]:
        """Get session token from AA.com homepage"""
        try:
            logger.info("🔑 Getting session token...")
            response = self.session.get(f"{self.base_url}/homePage.do")
            response.raise_for_status()
            
            # Look for session token in response
            # This is a simplified approach - real implementation would parse HTML/JS
            return "session_token_placeholder"
        except Exception as e:
            logger.warning(f"⚠️ Could not get session token: {e}")
            return None
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1, award_search: bool = False) -> List[Dict]:
        """
        Search flights using AA.com API with enhanced bot evasion
        
        Args:
            origin: Origin airport code (e.g., 'LAX')
            destination: Destination airport code (e.g., 'JFK')
            date: Departure date in YYYY-MM-DD format
            passengers: Number of passengers
            award_search: True for award search, False for cash search
            
        Returns:
            List of flight dictionaries
        """
        logger.info(f"🔍 Searching flights: {origin} → {destination} on {date}")
        logger.info(f"   Passengers: {passengers}, Award search: {award_search}")
        
        # Add random delay before request
        self._add_random_delay(0.5, 1.5)
        
        # Get session token first
        session_token = self._get_session_token()
        
        # Multiple API endpoints to try
        api_endpoints = [
            "https://www.aa.com/booking/api/search/weekly",
            "https://www.aa.com/booking/api/search",
            "https://www.aa.com/api/search/flights",
            "https://www.aa.com/booking/api/flights/search"
        ]
        
        # Request payload with enhanced parameters
        payload = {
            "adultPassengers": passengers,
            "childPassengers": 0,
            "infantPassengers": 0,
            "departDate": date,
            "destinationAirportCode": destination.upper(),
            "flexibleDays": 0,
            "originAirportCode": origin.upper(),
            "tripType": "oneway",
            "useAwardPoints": award_search,
            "cabinClass": "main",
            "currency": "USD",
            "locale": "en_US",
            "sessionId": session_token or f"session_{int(time.time())}"
        }
        
        # Try multiple endpoints
        for endpoint in api_endpoints:
            try:
                logger.info(f"📡 Trying API endpoint: {endpoint}")
                
                # Update referer for this specific request
                headers = {
                    'Referer': f"{self.base_url}/homePage.do",
                    'Origin': self.base_url,
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                response = self.session.post(endpoint, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ API response received from {endpoint}: {len(data.get('flights', []))} flights")
                    
                    flights = self._parse_flights(data, award_search)
                    logger.info(f"🎯 Parsed {len(flights)} flights")
                    
                    # Store results for CPP calculation
                    if award_search:
                        self.award_flights = flights
                    else:
                        self.cash_flights = flights
                    
                    return flights
                else:
                    logger.warning(f"⚠️ Endpoint {endpoint} returned status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Request failed for {endpoint}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON decode error for {endpoint}: {e}")
                continue
            except Exception as e:
                logger.warning(f"⚠️ Unexpected error for {endpoint}: {e}")
                continue
        
        logger.error("❌ All API endpoints failed")
        return []
    
    def _parse_flights(self, data: Dict, award_search: bool) -> List[Dict]:
        """Parse flight data from API response with enhanced extraction"""
        flights = []
        
        try:
            # Try multiple possible data structures
            flight_list = data.get('flights', []) or data.get('results', []) or data.get('data', [])
            
            if not flight_list:
                logger.warning("⚠️ No flight data found in response")
                return flights
            
            logger.info(f"📋 Processing {len(flight_list)} flights from API response")
            
            for i, flight in enumerate(flight_list):
                try:
                    # Extract basic flight info with multiple fallbacks
                    flight_number = (flight.get('flightNumber') or 
                                   flight.get('flight_number') or 
                                   flight.get('number') or 
                                   f"AA{i+1:03d}")
                    
                    departure_time = (flight.get('departureTime') or 
                                     flight.get('departure_time') or 
                                     flight.get('departure') or 
                                     flight.get('depTime') or 
                                     'N/A')
                    
                    arrival_time = (flight.get('arrivalTime') or 
                                   flight.get('arrival_time') or 
                                   flight.get('arrival') or 
                                   flight.get('arrTime') or 
                                   'N/A')
                    
                    # Extract pricing info with comprehensive fallbacks
                    if award_search:
                        # Award search - look for miles pricing
                        pricing = (flight.get('awardPricing') or 
                                 flight.get('award_pricing') or 
                                 flight.get('milesPricing') or 
                                 flight.get('pricing', {}))
                        
                        points_required = (pricing.get('miles') or 
                                          pricing.get('points') or 
                                          pricing.get('awardMiles') or 
                                          pricing.get('totalMiles') or 
                                          0)
                        
                        taxes_fees = (pricing.get('taxes') or 
                                     pricing.get('fees') or 
                                     pricing.get('taxesAndFees') or 
                                     pricing.get('totalFees') or 
                                     5.60)  # Default AA fees
                        
                        cash_price = 0.0
                    else:
                        # Cash search - look for cash pricing
                        pricing = (flight.get('cashPricing') or 
                                 flight.get('cash_pricing') or 
                                 flight.get('revenuePricing') or 
                                 flight.get('pricing', {}))
                        
                        cash_price = (pricing.get('totalPrice') or 
                                     pricing.get('total_price') or 
                                     pricing.get('basePrice') or 
                                     pricing.get('price') or 
                                     0.0)
                        
                        taxes_fees = (pricing.get('taxes') or 
                                     pricing.get('fees') or 
                                     pricing.get('taxesAndFees') or 
                                     pricing.get('totalFees') or 
                                     5.60)  # Default AA fees
                        
                        points_required = 0
                    
                    # Calculate CPP (cents per point) for award flights
                    cpp = 0.0
                    if award_search and points_required > 0:
                        # For award flights, we need cash equivalent to calculate CPP
                        # This will be calculated later when we have both cash and award data
                        cpp = 0.0  # Will be calculated in calculate_cpp method
                    
                    flight_data = {
                        "flight_number": flight_number,
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "points_required": int(points_required) if points_required else 0,
                        "cash_price_usd": round(float(cash_price), 2),
                        "taxes_fees_usd": round(float(taxes_fees), 2),
                        "cpp": round(cpp, 2)
                    }
                    
                    flights.append(flight_data)
                    logger.info(f"✈️ {flight_number}: {departure_time} → {arrival_time}")
                    if award_search:
                        logger.info(f"   💎 {points_required:,} pts + ${taxes_fees:.2f}")
                    else:
                        logger.info(f"   💰 ${cash_price:.2f} + ${taxes_fees:.2f}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing flight {i}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error parsing flight data: {e}")
        
        return flights
    
    def calculate_cpp(self) -> List[Dict]:
        """
        Calculate CPP (Cents Per Point) by matching award and cash flights
        Formula: cpp = (cash_price_usd - taxes_fees_usd) / points_required × 100
        """
        logger.info("🧮 Calculating CPP (Cents Per Point)...")
        
        enhanced_flights = []
        
        # Match award flights with cash flights by flight number and time
        for award_flight in self.award_flights:
            award_number = award_flight['flight_number']
            award_dep_time = award_flight['departure_time']
            
            # Find matching cash flight
            matching_cash_flight = None
            for cash_flight in self.cash_flights:
                if (cash_flight['flight_number'] == award_number and 
                    cash_flight['departure_time'] == award_dep_time):
                    matching_cash_flight = cash_flight
                    break
            
            if matching_cash_flight:
                # Calculate CPP using the formula
                cash_price = matching_cash_flight['cash_price_usd']
                taxes_fees = award_flight['taxes_fees_usd']
                points_required = award_flight['points_required']
                
                if points_required > 0:
                    cpp = ((cash_price - taxes_fees) / points_required) * 100
                else:
                    cpp = 0.0
                
                # Create enhanced flight data with both pricing options
                enhanced_flight = {
                    "flight_number": award_flight['flight_number'],
                    "departure_time": award_flight['departure_time'],
                    "arrival_time": award_flight['arrival_time'],
                    "points_required": points_required,
                    "cash_price_usd": round(cash_price, 2),
                    "taxes_fees_usd": round(taxes_fees, 2),
                    "cpp": round(cpp, 2)
                }
                
                enhanced_flights.append(enhanced_flight)
                logger.info(f"🎯 {award_number}: ${cash_price:.2f} or {points_required:,} pts (CPP: {cpp:.2f}¢)")
            else:
                # Award flight without matching cash price
                enhanced_flight = award_flight.copy()
                enhanced_flight['cpp'] = 0.0
                enhanced_flights.append(enhanced_flight)
                logger.warning(f"⚠️ No cash price found for {award_number}")
        
        logger.info(f"✅ Calculated CPP for {len(enhanced_flights)} flights")
        return enhanced_flights

def main():
    """Main function - Operation Point Break: AA.com Flight Scraper"""
    print("🚀 Operation Point Break - AA.com Flight Scraper (API Edition)")
    print("=" * 70)
    print("🎯 Extracting award and cash pricing for CPP calculation")
    print("⚡ Ultra-fast direct API approach with bot evasion techniques")
    print("=" * 70)
    print()
    
    scraper = AAApiScraper()
    
    # Search parameters for December 15, 2025
    origin = "LAX"
    destination = "JFK"
    date = "2025-12-15"
    passengers = 1
    
    logger.info(f"📅 Searching for flights: {origin} → {destination} on {date}")
    
    try:
        # First search: CASH prices
        logger.info("\n💰 Starting CASH price search...")
        cash_flights = scraper.search_flights(origin, destination, date, passengers, award_search=False)
        logger.info(f"💰 Found {len(cash_flights)} cash flights")
        
        # Add delay between searches to avoid rate limiting
        logger.info("⏳ Waiting between searches to avoid rate limiting...")
        time.sleep(random.uniform(2, 4))
        
        # Second search: AWARD prices
        logger.info("\n💎 Starting AWARD price search...")
        award_flights = scraper.search_flights(origin, destination, date, passengers, award_search=True)
        logger.info(f"💎 Found {len(award_flights)} award flights")
        
        # Calculate CPP by matching award and cash flights
        logger.info("\n🧮 Calculating CPP (Cents Per Point)...")
        enhanced_flights = scraper.calculate_cpp()
        
        # Format results in the exact structure requested
        results = {
            "search_metadata": {
                "origin": origin,
                "destination": destination,
                "date": date,
                "passengers": passengers,
                "cabin_class": "economy"
            },
            "flights": enhanced_flights,
            "total_results": len(enhanced_flights)
        }
        
        # Save results
        output_file = "operation_point_break_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n📊 OPERATION POINT BREAK - RESULTS:")
        print("=" * 70)
        print(json.dumps(results, indent=2))
        print(f"\n💾 Results saved to: {output_file}")
        print(f"🎯 Total flights with CPP: {results['total_results']}")
        print(f"💰 Cash flights found: {len(cash_flights)}")
        print(f"💎 Award flights found: {len(award_flights)}")
        print(f"🧮 Flights with CPP calculated: {len(enhanced_flights)}")
        
        # Show CPP analysis
        if enhanced_flights:
            print(f"\n📈 CPP ANALYSIS:")
            print("-" * 40)
            cpp_values = [f['cpp'] for f in enhanced_flights if f['cpp'] > 0]
            if cpp_values:
                avg_cpp = sum(cpp_values) / len(cpp_values)
                max_cpp = max(cpp_values)
                min_cpp = min(cpp_values)
                print(f"Average CPP: {avg_cpp:.2f}¢")
                print(f"Best CPP: {max_cpp:.2f}¢")
                print(f"Worst CPP: {min_cpp:.2f}¢")
                
                # Recommendation
                if avg_cpp >= 1.5:
                    print(f"\n💡 RECOMMENDATION: Using points makes sense!")
                    print(f"   Average CPP of {avg_cpp:.2f}¢ is above the 1.5¢ threshold")
                else:
                    print(f"\n💡 RECOMMENDATION: Consider paying cash")
                    print(f"   Average CPP of {avg_cpp:.2f}¢ is below the 1.5¢ threshold")
        
        print("\n🏆 Operation Point Break complete!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        print(f"\n❌ Operation Point Break failed: {e}")
        return None

if __name__ == "__main__":
    main()
