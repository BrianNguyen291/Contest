#!/usr/bin/env python3
"""
Debug script to analyze what's actually on the AA.com page
"""

import json
import logging
from real_mcp_aa_scraper import RealMCPPlaywrightScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_page_content():
    """Debug what's actually on the AA.com page"""
    print("🔍 Debugging AA.com Page Content")
    print("=" * 50)
    
    scraper = RealMCPPlaywrightScraper()
    
    try:
        # Start MCP server
        print("🌐 Starting MCP server...")
        scraper.start_mcp_server()
        
        # Navigate to AA.com
        print("🌐 Navigating to AA.com...")
        nav_result = scraper._call_mcp_tool('browser_navigate', url='https://www.aa.com/homePage.do')
        if nav_result:
            print("✅ Successfully navigated to AA.com")
        else:
            print("❌ Failed to navigate to AA.com")
            return
        
        # Wait for page to load
        import time
        time.sleep(5)
        
        # Get page content for analysis
        print("📄 Getting page content...")
        page_content_result = scraper._call_mcp_tool('browser_evaluate', function="""
            () => {
                const bodyText = document.body.innerText;
                const bodyHTML = document.body.innerHTML;
                
                // Look for specific patterns
                const patterns = {
                    flightNumbers: (bodyText.match(/AA\\s*\\d{1,4}/gi) || []).slice(0, 10),
                    prices: (bodyText.match(/\\$\\s*(\\d+(?:,\\d{3})*(?:\\.\\d{2})?)/g) || []).slice(0, 10),
                    points: (bodyText.match(/(\\d{1,3}(?:\\.\\d)?K)\\s*(?:miles|points|pts)/gi) || []).slice(0, 10),
                    awardPatterns: (bodyText.match(/(\\d{1,3}(?:\\.\\d)?K)\\s*\\+\\s*\\$/gi) || []).slice(0, 10),
                    redeemText: bodyText.toLowerCase().includes('redeem'),
                    milesText: bodyText.toLowerCase().includes('miles'),
                    pointsText: bodyText.toLowerCase().includes('points')
                };
                
                return {
                    url: window.location.href,
                    title: document.title,
                    bodyTextLength: bodyText.length,
                    patterns: patterns,
                    sampleText: bodyText.substring(0, 2000),
                    hasForm: !!document.querySelector('form'),
                    hasSearchButton: !!document.querySelector('input[type="submit"], button[type="submit"]'),
                    formFields: Array.from(document.querySelectorAll('input')).map(input => ({
                        type: input.type,
                        name: input.name,
                        id: input.id,
                        placeholder: input.placeholder
                    }))
                };
            }
        """)
        
        if page_content_result and 'content' in page_content_result:
            debug_data = page_content_result['content'][0]['text']
            print("📊 Page Analysis Results:")
            print("=" * 50)
            print(debug_data)
            
            # Save debug data
            with open('debug_page_content.json', 'w') as f:
                json.dump(debug_data, f, indent=2)
            print("\n💾 Debug data saved to: debug_page_content.json")
            
        else:
            print("❌ Could not get page content")
            
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
    finally:
        scraper.close()
        print("\n✅ Debug complete!")

if __name__ == "__main__":
    debug_page_content()
