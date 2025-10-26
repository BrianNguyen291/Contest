#!/usr/bin/env python3
"""
Quick test of Scrapling with AA.com
"""

from scrapling.fetchers import StealthyFetcher

def test_scrapling():
    print("🧪 Testing Scrapling with AA.com...")
    
    # Test with main AA.com page first
    url = "https://www.aa.com"
    
    try:
        print(f"📋 Testing URL: {url}")
        
        page = StealthyFetcher.fetch(
            url,
            headless=True,  # Use headless for testing
            solve_cloudflare=True,
            humanize=True,
            geoip=True,
            os_randomize=True,
            disable_ads=True
        )
        
        print("✅ Successfully fetched page!")
        print(f"📄 Page title: {page.title if hasattr(page, 'title') else 'Unknown'}")
        
        # Try to find some content
        if hasattr(page, 'css'):
            links = page.css('a')
            print(f"🔗 Found {len(links)} links on the page")
            
            # Show first few links
            for i, link in enumerate(links[:5]):
                if hasattr(link, 'text'):
                    print(f"  {i+1}. {link.text.strip()[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_scrapling()
    if success:
        print("\n🎉 Scrapling test successful! Ready to scrape AA.com booking page.")
    else:
        print("\n❌ Scrapling test failed. Check the error above.")
