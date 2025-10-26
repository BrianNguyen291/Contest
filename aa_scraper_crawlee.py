#!/usr/bin/env python3
"""
AA.com Booking Page Scraper using Crawlee Python
This script uses Crawlee's PlaywrightCrawler with anti-detection features
to scrape the American Airlines booking page.
"""

import asyncio
import json
from datetime import datetime
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

class AACrawler:
    def __init__(self):
        self.results = {
            "scraped_at": datetime.now().isoformat(),
            "url": "",
            "title": "",
            "flights": [],
            "raw_content": ""
        }
    
    async def scrape_aa_booking_page(self, url):
        """
        Scrape AA.com booking page using Crawlee's PlaywrightCrawler
        """
        print(f"🚀 Starting AA.com booking page scrape with Crawlee...")
        print(f"📋 URL: {url}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Configure PlaywrightCrawler with anti-detection features
        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1,  # Only scrape the target URL
            browser_pool_options={
                "browser_options": {
                    "type": "chromium",
                    "launch_options": {
                        "headless": False,  # Set to True for production
                        "args": [
                            "--no-sandbox",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-features=VizDisplayCompositor",
                            "--disable-web-security",
                            "--disable-features=TranslateUI",
                            "--disable-ipc-flooding-protection",
                        ]
                    },
                },
                "context_options": {
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-US",
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }
        )
        
        # Define the request handler
        @crawler.router.default_handler
        async def request_handler(context: PlaywrightCrawlingContext) -> None:
            print(f"🔍 Processing {context.request.url}...")
            
            page = context.page
            
            # Add stealth measures
            await self.add_stealth_measures(page)
            
            # Wait for page to load
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(3000)  # Wait 3 seconds for dynamic content
            
            # Extract data
            await self.extract_flight_data(page, context.request.url)
            
            # Push data to dataset
            await context.push_data(self.results)
        
        try:
            # Run the crawler
            await crawler.run([url])
            print("✅ Crawling completed successfully!")
            
            # Save results
            self.save_results(url)
            
            return self.results
            
        except Exception as e:
            print(f"❌ Error during crawling: {str(e)}")
            self.results["error"] = str(e)
            return self.results
    
    async def add_stealth_measures(self, page):
        """
        Add stealth measures to avoid detection
        """
        print("🔧 Adding stealth measures...")
        
        try:
            # Override navigator properties
            await page.add_init_script("""
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
            
            # Set extra headers
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
        except Exception as e:
            print(f"⚠️  Warning: Could not add all stealth measures: {str(e)}")
    
    async def extract_flight_data(self, page, url):
        """
        Extract flight information from the page
        """
        print("🔍 Extracting flight data...")
        
        self.results["url"] = url
        
        try:
            # Get page title
            title = await page.title()
            self.results["title"] = title
            print(f"📄 Page title: {title}")
            
            # Look for flight information containers
            flight_selectors = [
                '.flight-option',
                '.flight-card', 
                '.flight-result',
                '.trip-option',
                '[data-testid*="flight"]',
                '.flight-details',
                '.trip-summary',
                '.flight-list',
                '.search-results',
                '.booking-options'
            ]
            
            flights_found = False
            
            for selector in flight_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"📊 Found {len(elements)} flight elements with selector: {selector}")
                        flights_found = True
                        
                        for i, element in enumerate(elements):
                            text_content = await element.inner_text()
                            html_content = await element.inner_html()
                            
                            flight_info = {
                                "index": i,
                                "selector_used": selector,
                                "text_content": text_content.strip(),
                                "html_content": html_content
                            }
                            self.results["flights"].append(flight_info)
                            
                except Exception as e:
                    print(f"⚠️  Error with selector {selector}: {str(e)}")
                    continue
            
            if not flights_found:
                print("⚠️  No flight elements found with standard selectors")
                
                # Try to find any structured data
                try:
                    all_divs = await page.query_selector_all('div')
                    print(f"📋 Found {len(all_divs)} div elements on page")
                    
                    # Look for elements with flight-related classes
                    potential_elements = await page.query_selector_all('[class*="flight"], [class*="trip"], [class*="option"]')
                    if potential_elements:
                        print(f"🔍 Found {len(potential_elements)} potential flight-related elements")
                        
                        for i, element in enumerate(potential_elements[:10]):  # Limit to first 10
                            try:
                                text_content = await element.inner_text()
                                class_name = await element.get_attribute('class')
                                
                                flight_info = {
                                    "index": i,
                                    "element_type": "potential_flight",
                                    "text_content": text_content.strip(),
                                    "class_name": class_name or ''
                                }
                                self.results["flights"].append(flight_info)
                            except Exception as e:
                                print(f"⚠️  Error processing element {i}: {str(e)}")
                                continue
                
                except Exception as e:
                    print(f"❌ Error finding alternative elements: {str(e)}")
            
            # Get raw HTML content
            try:
                self.results["raw_content"] = await page.content()
            except Exception as e:
                print(f"⚠️  Could not get raw content: {str(e)}")
            
            print(f"✅ Extracted data: {len(self.results['flights'])} flight elements found")
            
        except Exception as e:
            print(f"❌ Error extracting flight data: {str(e)}")
            self.results["extraction_error"] = str(e)
    
    def save_results(self, url):
        """
        Save the scraped data to files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aa_crawlee_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            
            # Save summary
            summary_filename = f"aa_crawlee_summary_{timestamp}.txt"
            with open(summary_filename, 'w', encoding='utf-8') as f:
                f.write(f"AA.com Scraping Summary (Crawlee)\n")
                f.write(f"==================================\n")
                f.write(f"URL: {url}\n")
                f.write(f"Scraped at: {self.results.get('scraped_at', 'Unknown')}\n")
                f.write(f"Page title: {self.results.get('title', 'Unknown')}\n")
                f.write(f"Flights found: {len(self.results.get('flights', []))}\n")
                f.write(f"File: {filename}\n")
            
            print(f"📄 Summary saved to: {summary_filename}")
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")

async def main():
    """
    Main function to run the crawler
    """
    url = "https://www.aa.com/booking/choose-flights/1?sid=4cefacb3-eedf-467e-bb94-90f7532ac7d8"
    
    print("=" * 60)
    print("🛫 AA.com Booking Page Scraper (Crawlee)")
    print("=" * 60)
    
    # Check if Crawlee is installed
    try:
        import crawlee
        print(f"✅ Crawlee version: {crawlee.__version__}")
    except ImportError:
        print("❌ Crawlee not installed. Please install it first:")
        print("   pip install crawlee")
        return
    
    # Create and run crawler
    crawler = AACrawler()
    result = await crawler.scrape_aa_booking_page(url)
    
    if result and not result.get("error"):
        print("\n" + "=" * 60)
        print("🎉 Scraping completed successfully!")
        print("=" * 60)
        print(f"📊 Flights found: {len(result.get('flights', []))}")
        print(f"📄 Page title: {result.get('title', 'Unknown')}")
    else:
        print("\n" + "=" * 60)
        print("❌ Scraping failed!")
        print("=" * 60)
        if result.get("error"):
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
