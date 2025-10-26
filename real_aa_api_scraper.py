#!/usr/bin/env python3
"""
Real AA.com API Scraper - Using Actual API Format
Based on captured network requests from AA.com
"""

import requests
import json
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealAAApiScraper:
    """Real AA.com API scraper using actual captured API format"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.aa.com"
        
        # Set up session with realistic headers from captured request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Origin': 'https://www.aa.com',
            'Referer': 'https://www.aa.com/booking/choose-flights/1',
            'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=1, i'
        })
        
        # Track search results for CPP calculation
        self.cash_flights = []
        self.award_flights = []
    
    def _add_random_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _build_search_payload(self, origin: str, destination: str, date: str, passengers: int = 1, award_search: bool = False) -> Dict:
        """
        Build the exact API payload format captured from AA.com
        """
        # Convert date format from YYYY-MM-DD to YYYY-MM-DD (already correct)
        departure_date = date
        
        payload = {
            "metadata": {
                "selectedProducts": [],
                "tripType": "OneWay",
                "udo": {
                    "search_method": "Lowest"
                }
            },
            "passengers": [
                {
                    "type": "adult",
                    "count": passengers
                }
            ],
            "requestHeader": {
                "clientId": "AAcom"
            },
            "slices": [
                {
                    "allCarriers": True,
                    "cabin": "",
                    "departureDate": departure_date,
                    "destination": destination.upper(),
                    "destinationNearbyAirports": False,
                    "maxStops": None,
                    "origin": origin.upper(),
                    "originNearbyAirports": False
                }
            ],
            "tripOptions": {
                "corporateBooking": False,
                "fareType": "Lowest",
                "locale": "en_US",
                "pointOfSale": None,
                "searchType": "Revenue" if not award_search else "Award"
            },
            "loyaltyInfo": None,
            "version": "cfr",
            "queryParams": {
                "sliceIndex": 0,
                "sessionId": "",
                "solutionSet": "",
                "solutionId": "",
                "sort": "CARRIER"
            }
        }
        
        return payload
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1, award_search: bool = False) -> List[Dict]:
        """
        Search flights using the real AA.com API format
        """
        logger.info(f"🔍 Searching flights: {origin} → {destination} on {date}")
        logger.info(f"   Passengers: {passengers}, Award search: {award_search}")
        
        # Add random delay
        self._add_random_delay(1.0, 2.5)
        
        # Build the exact payload format
        payload = self._build_search_payload(origin, destination, date, passengers, award_search)
        
        # API endpoint
        url = f"{self.base_url}/booking/api/search/weekly"
        
        try:
            logger.info("📡 Making API request to AA.com...")
            logger.info(f"   Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, json=payload, timeout=30)
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API response received: {len(data.get('flights', []))} flights")
                
                flights = self._parse_flights(data, award_search)
                logger.info(f"🎯 Parsed {len(flights)} flights")
                
                # Store results for CPP calculation
                if award_search:
                    self.award_flights = flights
                else:
                    self.cash_flights = flights
                
                return flights
            else:
                logger.warning(f"⚠️ API returned status {response.status_code}")
                logger.warning(f"   Response: {response.text[:500]}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def _parse_flights(self, data: Dict, award_search: bool) -> List[Dict]:
        """Parse flight data from real AA.com API response"""
        flights = []
        
        try:
            # Try to find flight data in various possible structures
            flight_list = []
            
            # Look for flights in different possible locations
            if 'flights' in data:
                flight_list = data['flights']
            elif 'results' in data:
                flight_list = data['results']
            elif 'data' in data and isinstance(data['data'], list):
                flight_list = data['data']
            elif isinstance(data, list):
                flight_list = data
            
            if not flight_list:
                logger.warning("⚠️ No flight data found in response")
                logger.info(f"   Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return flights
            
            logger.info(f"📋 Processing {len(flight_list)} flights from API response")
            
            for i, flight in enumerate(flight_list):
                try:
                    # Extract flight information with multiple fallbacks
                    flight_number = self._extract_flight_number(flight, i)
                    departure_time = self._extract_departure_time(flight)
                    arrival_time = self._extract_arrival_time(flight)
                    
                    # Extract pricing information
                    if award_search:
                        points_required, taxes_fees = self._extract_award_pricing(flight)
                        cash_price = 0.0
                    else:
                        cash_price, taxes_fees = self._extract_cash_pricing(flight)
                        points_required = 0
                    
                    flight_data = {
                        "flight_number": flight_number,
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "points_required": int(points_required) if points_required else 0,
                        "cash_price_usd": round(float(cash_price), 2),
                        "taxes_fees_usd": round(float(taxes_fees), 2),
                        "cpp": 0.0  # Will be calculated later
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
    
    def _extract_flight_number(self, flight: Dict, index: int) -> str:
        """Extract flight number with multiple fallbacks"""
        # Try various possible keys for flight number
        possible_keys = ['flightNumber', 'flight_number', 'number', 'flightId', 'id']
        
        for key in possible_keys:
            if key in flight and flight[key]:
                return str(flight[key])
        
        # Fallback to generated number
        return f"AA{index+1:03d}"
    
    def _extract_departure_time(self, flight: Dict) -> str:
        """Extract departure time with multiple fallbacks"""
        # Try various possible keys for departure time
        possible_keys = ['departureTime', 'departure_time', 'departure', 'depTime', 'depart']
        
        for key in possible_keys:
            if key in flight and flight[key]:
                return str(flight[key])
        
        return 'N/A'
    
    def _extract_arrival_time(self, flight: Dict) -> str:
        """Extract arrival time with multiple fallbacks"""
        # Try various possible keys for arrival time
        possible_keys = ['arrivalTime', 'arrival_time', 'arrival', 'arrTime', 'arrive']
        
        for key in possible_keys:
            if key in flight and flight[key]:
                return str(flight[key])
        
        return 'N/A'
    
    def _extract_award_pricing(self, flight: Dict) -> tuple:
        """Extract award pricing (points and taxes)"""
        points_required = 0
        taxes_fees = 5.60  # Default AA fees
        
        # Look for award pricing in various structures
        pricing_keys = ['awardPricing', 'award_pricing', 'milesPricing', 'pricing']
        
        for pricing_key in pricing_keys:
            if pricing_key in flight and isinstance(flight[pricing_key], dict):
                pricing = flight[pricing_key]
                
                # Look for points/miles
                points_keys = ['miles', 'points', 'awardMiles', 'totalMiles', 'requiredMiles']
                for points_key in points_keys:
                    if points_key in pricing and pricing[points_key]:
                        points_required = pricing[points_key]
                        break
                
                # Look for taxes/fees
                taxes_keys = ['taxes', 'fees', 'taxesAndFees', 'totalFees']
                for taxes_key in taxes_keys:
                    if taxes_key in pricing and pricing[taxes_key]:
                        taxes_fees = pricing[taxes_key]
                        break
                
                break
        
        return points_required, taxes_fees
    
    def _extract_cash_pricing(self, flight: Dict) -> tuple:
        """Extract cash pricing (price and taxes)"""
        cash_price = 0.0
        taxes_fees = 5.60  # Default AA fees
        
        # Look for cash pricing in various structures
        pricing_keys = ['cashPricing', 'cash_pricing', 'revenuePricing', 'pricing']
        
        for pricing_key in pricing_keys:
            if pricing_key in flight and isinstance(flight[pricing_key], dict):
                pricing = flight[pricing_key]
                
                # Look for total price
                price_keys = ['totalPrice', 'total_price', 'basePrice', 'price', 'fare']
                for price_key in price_keys:
                    if price_key in pricing and pricing[price_key]:
                        cash_price = pricing[price_key]
                        break
                
                # Look for taxes/fees
                taxes_keys = ['taxes', 'fees', 'taxesAndFees', 'totalFees']
                for taxes_key in taxes_keys:
                    if taxes_key in pricing and pricing[taxes_key]:
                        taxes_fees = pricing[taxes_key]
                        break
                
                break
        
        return cash_price, taxes_fees
    
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
    """Main function - Test the real AA.com API scraper"""
    print("🚀 Real AA.com API Scraper - Using Captured API Format")
    print("=" * 70)
    print("🎯 Testing with actual AA.com API structure")
    print("📡 Using captured request format from network inspection")
    print("=" * 70)
    print()
    
    scraper = RealAAApiScraper()
    
    # Test with the route from your captured data: PGA → BFS on 2025-11-17
    origin = "PGA"
    destination = "BFS"
    date = "2025-11-17"
    passengers = 1
    
    logger.info(f"📅 Testing with captured route: {origin} → {destination} on {date}")
    
    try:
        # First search: CASH prices
        logger.info("\n💰 Starting CASH price search...")
        cash_flights = scraper.search_flights(origin, destination, date, passengers, award_search=False)
        logger.info(f"💰 Found {len(cash_flights)} cash flights")
        
        # Add delay between searches
        logger.info("⏳ Waiting between searches...")
        time.sleep(random.uniform(2, 4))
        
        # Second search: AWARD prices
        logger.info("\n💎 Starting AWARD price search...")
        award_flights = scraper.search_flights(origin, destination, date, passengers, award_search=True)
        logger.info(f"💎 Found {len(award_flights)} award flights")
        
        # Calculate CPP by matching award and cash flights
        logger.info("\n🧮 Calculating CPP (Cents Per Point)...")
        enhanced_flights = scraper.calculate_cpp()
        
        # Format results
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
        output_file = "real_aa_api_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n📊 REAL AA.COM API - RESULTS:")
        print("=" * 70)
        print(json.dumps(results, indent=2))
        print(f"\n💾 Results saved to: {output_file}")
        print(f"🎯 Total flights with CPP: {results['total_results']}")
        print(f"💰 Cash flights found: {len(cash_flights)}")
        print(f"💎 Award flights found: {len(award_flights)}")
        print(f"🧮 Flights with CPP calculated: {len(enhanced_flights)}")
        
        print("\n🏆 Real AA.com API scraper test complete!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"\n❌ Real AA.com API scraper test failed: {e}")
        return None

if __name__ == "__main__":
    main()
