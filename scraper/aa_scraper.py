"""AA Flight Scraper with Bot Evasion Techniques"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth
from fake_useragent import UserAgent

from .models import SearchMetadata, Flight, ScraperResult
from .config import SELECTORS, ALT_SELECTORS, ERROR_MESSAGES, DEFAULT_VIEWPORT, DEFAULT_USER_AGENT
from .utils import (
    calculate_cpp, parse_price, parse_time, parse_flight_number,
    random_delay, match_flights, validate_date, format_airport_code
)


class AAScraper:
    """American Airlines flight scraper with bot evasion techniques"""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Initialize browser with stealth settings"""
        self.playwright = await async_playwright().start()
        
        # Configure browser launch options
        launch_options = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-http2",
                "--disable-quic",
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]
        }
        
        # Add proxy if provided
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        # Create context with realistic settings
        context_options = {
            "viewport": DEFAULT_VIEWPORT,
            "user_agent": DEFAULT_USER_AGENT,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
        }
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Apply stealth settings
        stealth = Stealth()
        await stealth.apply_stealth_async(self.page)
        
        # Add additional stealth measures
        await self._apply_stealth_measures()
    
    async def _apply_stealth_measures(self):
        """Apply additional stealth measures to avoid detection"""
        # Override navigator properties
        await self.page.add_init_script("""
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
    
    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def _human_like_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add human-like random delay"""
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)
    
    async def _human_like_typing(self, element, text: str):
        """Type text with human-like speed and randomness"""
        await element.click()
        await self._human_like_delay(100, 300)
        
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def _handle_cookies(self):
        """Handle cookie consent popup"""
        try:
            # Wait for cookie modal
            await self.page.wait_for_selector(SELECTORS["cookie_modal"], timeout=5000)
            
            # Click accept button
            accept_button = await self.page.query_selector(SELECTORS["cookie_accept"])
            if accept_button:
                await accept_button.click()
                await self._human_like_delay(1000, 2000)
        except:
            # Cookie modal not found or already handled
            pass
    
    async def _fill_search_form(self, origin: str, destination: str, date: str, passengers: int = 1):
        """Fill the flight search form with human-like behavior"""
        # Handle cookies first
        await self._handle_cookies()
        
        # Fill origin airport
        origin_input = await self.page.wait_for_selector(SELECTORS["origin_input"], timeout=10000)
        await self._human_like_typing(origin_input, origin)
        await self._human_like_delay(500, 1000)
        
        # Fill destination airport
        dest_input = await self.page.wait_for_selector(SELECTORS["destination_input"], timeout=10000)
        await self._human_like_typing(dest_input, destination)
        await self._human_like_delay(500, 1000)
        
        # Fill date
        date_input = await self.page.wait_for_selector(SELECTORS["date_input"], timeout=10000)
        await self._human_like_typing(date_input, date)
        await self._human_like_delay(500, 1000)
        
        # Set passengers if needed
        if passengers > 1:
            passengers_input = await self.page.wait_for_selector(SELECTORS["passengers_input"], timeout=10000)
            await passengers_input.click()
            await self._human_like_delay(300, 500)
            # Implementation would depend on AA's passenger selector UI
        
        await self._human_like_delay(1000, 2000)
    
    async def _search_award_flights(self, origin: str, destination: str, date: str, passengers: int = 1) -> List[Dict[str, Any]]:
        """Search for award flights and extract pricing data"""
        try:
            # Navigate to AA.com with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.page.goto("https://www.aa.com", wait_until="domcontentloaded", timeout=30000)
                    await self._human_like_delay(2000, 3000)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Retry {attempt + 1}/{max_retries} for AA.com navigation...")
                    await self._human_like_delay(5000, 10000)
            
            # Fill search form
            await self._fill_search_form(origin, destination, date, passengers)
            
            # Switch to award flights mode
            try:
                award_toggle = await self.page.wait_for_selector(SELECTORS["award_toggle"], timeout=5000)
                await award_toggle.click()
                await self._human_like_delay(1000, 2000)
            except:
                # Award toggle not found, try alternative approach
                pass
            
            # Click search button
            search_button = await self.page.wait_for_selector(SELECTORS["search_button"], timeout=10000)
            await search_button.click()
            await self._human_like_delay(3000, 5000)
            
            # Wait for results to load
            await self.page.wait_for_selector(SELECTORS["flight_cards"], timeout=30000)
            await self._human_like_delay(2000, 3000)
            
            # Extract flight data
            flights = await self._extract_flight_data(is_award=True)
            return flights
            
        except Exception as e:
            print(f"Error searching award flights: {e}")
            return []
    
    async def _search_cash_flights(self, origin: str, destination: str, date: str, passengers: int = 1) -> List[Dict[str, Any]]:
        """Search for cash flights and extract pricing data"""
        try:
            # Navigate to AA.com (fresh page) with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.page.goto("https://www.aa.com", wait_until="domcontentloaded", timeout=30000)
                    await self._human_like_delay(2000, 3000)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Retry {attempt + 1}/{max_retries} for AA.com navigation...")
                    await self._human_like_delay(5000, 10000)
            
            # Fill search form
            await self._fill_search_form(origin, destination, date, passengers)
            
            # Ensure we're in cash mode (default)
            try:
                cash_toggle = await self.page.wait_for_selector(SELECTORS["cash_toggle"], timeout=5000)
                await cash_toggle.click()
                await self._human_like_delay(1000, 2000)
            except:
                # Cash toggle not found, assume already in cash mode
                pass
            
            # Click search button
            search_button = await self.page.wait_for_selector(SELECTORS["search_button"], timeout=10000)
            await search_button.click()
            await self._human_like_delay(3000, 5000)
            
            # Wait for results to load
            await self.page.wait_for_selector(SELECTORS["flight_cards"], timeout=30000)
            await self._human_like_delay(2000, 3000)
            
            # Extract flight data
            flights = await self._extract_flight_data(is_award=False)
            return flights
            
        except Exception as e:
            print(f"Error searching cash flights: {e}")
            return []
    
    async def _extract_flight_data(self, is_award: bool) -> List[Dict[str, Any]]:
        """Extract flight data from search results"""
        flights = []
        
        try:
            # Get all flight cards
            flight_cards = await self.page.query_selector_all(SELECTORS["flight_cards"])
            
            for card in flight_cards:
                try:
                    flight_data = {}
                    
                    # Extract flight number
                    flight_number_elem = await card.query_selector(SELECTORS["flight_number"])
                    if flight_number_elem:
                        flight_text = await flight_number_elem.inner_text()
                        flight_data["flight_number"] = parse_flight_number(flight_text)
                    
                    # Extract departure time
                    dep_time_elem = await card.query_selector(SELECTORS["departure_time"])
                    if dep_time_elem:
                        dep_text = await dep_time_elem.inner_text()
                        flight_data["departure_time"] = parse_time(dep_text)
                    
                    # Extract arrival time
                    arr_time_elem = await card.query_selector(SELECTORS["arrival_time"])
                    if arr_time_elem:
                        arr_text = await arr_time_elem.inner_text()
                        flight_data["arrival_time"] = parse_time(arr_text)
                    
                    if is_award:
                        # Extract points and taxes for award flights
                        points_elem = await card.query_selector(SELECTORS["points_price"])
                        if points_elem:
                            points_text = await points_elem.inner_text()
                            flight_data["points_required"] = parse_price(points_text)
                        
                        taxes_elem = await card.query_selector(SELECTORS["taxes_fees"])
                        if taxes_elem:
                            taxes_text = await taxes_elem.inner_text()
                            flight_data["taxes_fees_usd"] = parse_price(taxes_text)
                    else:
                        # Extract cash price for cash flights
                        price_elem = await card.query_selector(SELECTORS["cash_price"])
                        if price_elem:
                            price_text = await price_elem.inner_text()
                            flight_data["cash_price_usd"] = parse_price(price_text)
                    
                    # Only add flight if we have essential data
                    if flight_data.get("flight_number") and flight_data.get("departure_time"):
                        flights.append(flight_data)
                        
                except Exception as e:
                    print(f"Error extracting flight data from card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error extracting flight data: {e}")
        
        return flights
    
    async def search_flights(self, search_metadata: SearchMetadata) -> ScraperResult:
        """Main method to search for flights and return results"""
        try:
            # Validate inputs
            if not validate_date(search_metadata.date):
                raise ValueError(f"Invalid date: {search_metadata.date}")
            
            origin = format_airport_code(search_metadata.origin)
            destination = format_airport_code(search_metadata.destination)
            
            # Search for award flights
            print("Searching for award flights...")
            award_flights = await self._search_award_flights(
                origin, destination, search_metadata.date, search_metadata.passengers
            )
            
            # Search for cash flights
            print("Searching for cash flights...")
            cash_flights = await self._search_cash_flights(
                origin, destination, search_metadata.date, search_metadata.passengers
            )
            
            # Match flights and calculate CPP
            matched_flights = match_flights(award_flights, cash_flights)
            
            # Convert to Flight objects
            flights = []
            for flight_data in matched_flights:
                flight = Flight(**flight_data)
                flights.append(flight)
            
            return ScraperResult(
                search_metadata=search_metadata,
                flights=flights,
                total_results=len(flights)
            )
            
        except Exception as e:
            print(f"Error in search_flights: {e}")
            return ScraperResult(
                search_metadata=search_metadata,
                flights=[],
                total_results=0
            )
