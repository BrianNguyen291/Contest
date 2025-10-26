#!/usr/bin/env python3
"""
Test AA.com Homepage with Scrapling
"""

from scrapling.fetchers import StealthyFetcher
import json
from datetime import datetime

def test_aa_homepage():
    print("🧪 Testing AA.com Homepage with Scrapling...")
    
    url = "https://www.aa.com/homePage.do"
    
    try:
        print(f"📋 Testing URL: {url}")
        
        page = StealthyFetcher.fetch(
            url,
            headless=True,  # Use headless for testing
            solve_cloudflare=True,
            humanize=2.0,
            geoip=True,
            os_randomize=True,
            disable_ads=True,
            google_search=True,
            block_webrtc=True,
            allow_webgl=False
        )
        
        print("✅ Successfully fetched page!")
        
        # Extract page information
        page_data = {
            "scraped_at": datetime.now().isoformat(),
            "url": url,
            "title": "",
            "content_summary": {},
            "raw_content": ""
        }
        
        # Get page title
        if hasattr(page, 'title'):
            page_data["title"] = page.title
        
        # Extract content
        if hasattr(page, 'css'):
            # Count different elements
            links = page.css('a')
            images = page.css('img')
            forms = page.css('form')
            inputs = page.css('input')
            buttons = page.css('button')
            
            page_data["content_summary"] = {
                "links_count": len(links),
                "images_count": len(images),
                "forms_count": len(forms),
                "inputs_count": len(inputs),
                "buttons_count": len(buttons)
            }
            
            print(f"📊 Content Summary:")
            print(f"  🔗 Links: {len(links)}")
            print(f"  🖼️  Images: {len(images)}")
            print(f"  📝 Forms: {len(forms)}")
            print(f"  ⌨️  Inputs: {len(inputs)}")
            print(f"  🔘 Buttons: {len(buttons)}")
            
            # Show first few links
            print(f"\n🔗 First 10 links found:")
            for i, link in enumerate(links[:10]):
                if hasattr(link, 'text'):
                    text = link.text.strip()[:50]
                    try:
                        href = link.get('href') if hasattr(link, 'get') else ''
                    except:
                        href = ''
                    print(f"  {i+1}. {text}... -> {href}")
            
            # Look for flight-related content
            flight_keywords = ['flight', 'book', 'search', 'trip', 'reservation']
            flight_elements = []
            
            for keyword in flight_keywords:
                elements = page.css(f'[class*="{keyword}"], [id*="{keyword}"], [data-testid*="{keyword}"]')
                if elements:
                    flight_elements.extend(elements)
            
            if flight_elements:
                print(f"\n✈️  Found {len(flight_elements)} flight-related elements")
                for i, element in enumerate(flight_elements[:5]):
                    if hasattr(element, 'text'):
                        print(f"  {i+1}. {element.text.strip()[:100]}...")
        
        # Get raw HTML
        if hasattr(page, 'html'):
            page_data["raw_content"] = page.html
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aa_homepage_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🛫 AA.com Homepage Test (Scrapling)")
    print("=" * 60)
    
    success = test_aa_homepage()
    
    if success:
        print("\n🎉 Homepage test successful!")
        print("✅ Scrapling can successfully access AA.com")
        print("💡 Ready to test booking pages with fresh session URLs")
    else:
        print("\n❌ Homepage test failed!")
