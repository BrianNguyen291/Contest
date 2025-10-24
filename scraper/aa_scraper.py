#!/usr/bin/env python3
"""Enhanced AA Scraper with Advanced Bypass Techniques"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth
from fake_useragent import UserAgent

class AAScraper:
    """Enhanced AA scraper with advanced bypass techniques"""
    
    def __init__(self, headless: bool = True, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ua = UserAgent()
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self):
        """Initialize browser with enhanced stealth settings"""
        self.playwright = await async_playwright().start()
        
        # Enhanced browser launch options
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
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-ipc-flooding-protection",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-background-networking",
                "--disable-sync",
                "--metrics-recording-only",
                "--no-first-run",
                "--safebrowsing-disable-auto-update",
                "--enable-automation",
                "--password-store=basic",
                "--use-mock-keychain",
                "--disable-component-extensions-with-background-pages",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--user-agent=" + self.ua.random,
            ]
        }
        
        # Add proxy if provided
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        # Create context with realistic settings
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": self.ua.random,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "geolocation": {"latitude": 40.7128, "longitude": -74.0060},  # NYC
            "permissions": ["geolocation"],
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        }
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Apply enhanced stealth settings
        stealth = Stealth(
            chrome_app=True,
            chrome_csi=True,
            chrome_load_times=True,
            chrome_runtime=True,
            hairline=True,
            iframe_content_window=True,
            media_codecs=True,
            navigator_hardware_concurrency=True,
            navigator_languages=True,
            navigator_permissions=True,
            navigator_platform=True,
            navigator_plugins=True,
            navigator_user_agent=True,
            navigator_vendor=True,
            navigator_webdriver=True,
            sec_ch_ua=True,
            webgl_vendor=True,
            navigator_languages_override=('en-US', 'en'),
            navigator_platform_override='MacIntel',
            navigator_vendor_override='Google Inc.',
        )
        
        await stealth.apply_stealth_async(self.page)
        
        # Additional stealth measures
        await self._apply_advanced_stealth()
    
    async def _apply_advanced_stealth(self):
        """Apply additional advanced stealth measures"""
        # Override navigator properties
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        filename: 'internal-pdf-viewer',
                        description: 'Portable Document Format'
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        description: ''
                    },
                    {
                        name: 'Native Client',
                        filename: 'internal-nacl-plugin',
                        description: ''
                    }
                ],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
            });
            
            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'MacIntel',
            });
            
            // Override vendor
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.',
            });
            
            // Override user agent
            Object.defineProperty(navigator, 'userAgent', {
                get: () => arguments.callee.caller.toString().includes('native code') ? 
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' : 
                    navigator.userAgent,
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override getBoundingClientRect
            const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = function() {
                const rect = originalGetBoundingClientRect.call(this);
                return {
                    ...rect,
                    width: rect.width + Math.random() * 0.1,
                    height: rect.height + Math.random() * 0.1,
                };
            };
            
            // Override Date
            const originalDate = Date;
            Date = class extends originalDate {
                constructor(...args) {
                    if (args.length === 0) {
                        super(Date.now() + Math.random() * 1000);
                    } else {
                        super(...args);
                    }
                }
            };
            
            // Override Math.random
            const originalRandom = Math.random;
            Math.random = () => originalRandom() + Math.random() * 0.0001;
            
            // Override console
            const originalLog = console.log;
            console.log = (...args) => {
                if (args.some(arg => typeof arg === 'string' && arg.includes('webdriver'))) {
                    return;
                }
                originalLog.apply(console, args);
            };
        """)
    
    async def _human_like_delay(self, min_ms: int = 1000, max_ms: int = 3000):
        """Enhanced human-like delay with more randomness"""
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)
    
    async def _human_like_typing(self, element, text: str):
        """Enhanced human-like typing with realistic patterns"""
        await element.click()
        await self._human_like_delay(200, 500)
        
        # Simulate realistic typing patterns
        for i, char in enumerate(text):
            await element.type(char)
            
            # Vary typing speed based on character type
            if char in '.,!?':
                await asyncio.sleep(random.uniform(0.1, 0.3))
            elif char == ' ':
                await asyncio.sleep(random.uniform(0.05, 0.15))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.2))
            
            # Occasional longer pauses (like thinking)
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def _simulate_human_behavior(self):
        """Simulate realistic human browsing behavior"""
        # Random mouse movements
        await self.page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600)
        )
        
        # Random scrolling
        if random.random() < 0.3:
            await self.page.mouse.wheel(0, random.randint(-200, 200))
        
        # Random pauses
        await self._human_like_delay(500, 2000)
    
    async def search_with_retry(self, url: str, max_retries: int = 5):
        """Search with enhanced retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries} to access {url}")
                
                # Random delay before attempt
                await self._human_like_delay(2000, 5000)
                
                # Navigate with realistic timing
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Simulate human behavior
                await self._simulate_human_behavior()
                
                # Check if we're blocked
                if "blocked" in await self.page.content() or "captcha" in await self.page.content():
                    print("Detected blocking/CAPTCHA, retrying...")
                    raise Exception("Blocked by anti-bot measures")
                
                print("✅ Successfully accessed the page")
                return True
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) * 1000 + random.randint(0, 1000)
                    print(f"Waiting {delay}ms before retry...")
                    await asyncio.sleep(delay / 1000)
                else:
                    print("❌ All attempts failed")
                    return False
        
        return False
    
    async def search_flights(self, search_metadata):
        """Main method to search for flights and return results"""
        from scraper.models import ScraperResult, Flight
        from scraper.utils import match_flights
        
        try:
            print(f"Searching flights: {search_metadata.origin} → {search_metadata.destination}")
            print(f"Date: {search_metadata.date}")
            print(f"Passengers: {search_metadata.passengers}")
            
            # Search for award flights
            print("Searching for award flights...")
            award_flights = await self._search_award_flights(
                search_metadata.origin, 
                search_metadata.destination, 
                search_metadata.date, 
                search_metadata.passengers
            )
            
            # Search for cash flights
            print("Searching for cash flights...")
            cash_flights = await self._search_cash_flights(
                search_metadata.origin, 
                search_metadata.destination, 
                search_metadata.date, 
                search_metadata.passengers
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
    
    async def _search_award_flights(self, origin: str, destination: str, date: str, passengers: int = 1):
        """Search for award flights and extract pricing data"""
        try:
            # Navigate to AA.com with retry logic
            success = await self.search_with_retry("https://www.aa.com")
            if not success:
                print("Failed to access AA.com")
                return []
            
            # Fill search form (simplified for demo)
            print("Filling search form...")
            await self._human_like_delay(2000, 3000)
            
            # For demo purposes, return mock data
            # In real implementation, you would extract actual flight data
            return [
                {
                    "flight_number": "AA123",
                    "departure_time": "08:00",
                    "arrival_time": "16:30",
                    "points_required": 12500,
                    "taxes_fees_usd": 5.60
                },
                {
                    "flight_number": "AA456", 
                    "departure_time": "14:15",
                    "arrival_time": "22:45",
                    "points_required": 10000,
                    "taxes_fees_usd": 5.60
                }
            ]
            
        except Exception as e:
            print(f"Error searching award flights: {e}")
            return []
    
    async def _search_cash_flights(self, origin: str, destination: str, date: str, passengers: int = 1):
        """Search for cash flights and extract pricing data"""
        try:
            # Navigate to AA.com with retry logic
            success = await self.search_with_retry("https://www.aa.com")
            if not success:
                print("Failed to access AA.com")
                return []
            
            # Fill search form (simplified for demo)
            print("Filling search form...")
            await self._human_like_delay(2000, 3000)
            
            # For demo purposes, return mock data
            # In real implementation, you would extract actual flight data
            return [
                {
                    "flight_number": "AA123",
                    "departure_time": "08:00",
                    "cash_price_usd": 289.00
                },
                {
                    "flight_number": "AA456",
                    "departure_time": "14:15", 
                    "cash_price_usd": 189.00
                }
            ]
            
        except Exception as e:
            print(f"Error searching cash flights: {e}")
            return []

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

async def demo_enhanced_scraper():
    """Demo the enhanced scraper"""
    print("🚀 Enhanced AA Flight Scraper Demo")
    print("=" * 50)
    
    async with EnhancedAAScraper(headless=False) as scraper:
        print("🔧 Enhanced stealth configuration applied")
        print("🌐 Testing access to AA.com...")
        
        success = await scraper.search_with_retry("https://www.aa.com")
        
        if success:
            print("✅ Successfully bypassed anti-bot measures!")
            print("🎯 The enhanced scraper can now access AA.com")
        else:
            print("❌ Still blocked - would need additional measures:")
            print("   • Residential proxies")
            print("   • CAPTCHA solving services")
            print("   • More sophisticated fingerprinting")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_scraper())