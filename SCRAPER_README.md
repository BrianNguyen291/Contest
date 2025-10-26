# AA.com Booking Page Scraper

This project provides multiple approaches to scrape American Airlines booking pages using advanced web scraping tools that can bypass anti-bot protection and handle JavaScript-rendered content.

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
./setup_scrapers.sh

# Or manually install dependencies
pip install -r scraper_requirements.txt
playwright install
```

### 2. Run Scrapers
```bash
# Activate virtual environment
source venv/bin/activate

# Run Scrapling scraper (Recommended)
python3 aa_scraper_scrapling.py

# Run Crawlee scraper (Alternative)
python3 aa_scraper_crawlee.py
```

## 🛠️ Available Scrapers

### 1. Scrapling Scraper (`aa_scraper_scrapling.py`)
**Best for: Anti-bot bypass, Cloudflare protection**

Features:
- ✅ Automatic Cloudflare challenge solving
- ✅ Human-like mouse movements and behavior
- ✅ Canvas fingerprinting protection
- ✅ WebRTC blocking
- ✅ OS fingerprint randomization
- ✅ GeoIP spoofing
- ✅ Ad blocking

### 2. Crawlee Scraper (`aa_scraper_crawlee.py`)
**Best for: Advanced browser automation, Playwright integration**

Features:
- ✅ Playwright-based browser automation
- ✅ Advanced stealth measures
- ✅ Navigator property overrides
- ✅ Custom headers and user agents
- ✅ Viewport and locale configuration
- ✅ Anti-detection techniques

## 🔧 Configuration

### Scrapling Configuration
```python
page = StealthyFetcher.fetch(
    url,
    headless=False,  # Set to True for production
    solve_cloudflare=True,  # Solve Cloudflare challenges
    humanize=True,  # Human-like behavior
    geoip=True,  # IP-based geo spoofing
    os_randomize=True,  # Randomize OS fingerprints
    disable_ads=True,  # Block advertisements
    google_search=True,  # Use Google referrer
    block_webrtc=True,  # Block WebRTC
    allow_webgl=False,  # Disable WebGL
    hide_canvas=True,  # Canvas fingerprinting protection
    humanize=2.0  # Max cursor movement time
)
```

### Crawlee Configuration
```python
crawler = PlaywrightCrawler(
    max_requests_per_crawl=1,
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
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    }
)
```

## 📊 Output

Both scrapers generate:
- **JSON file**: Complete scraped data with timestamps
- **Summary file**: Human-readable summary of results
- **Console output**: Real-time progress and status updates

### Example Output Structure
```json
{
  "scraped_at": "2024-01-15T10:30:00",
  "url": "https://www.aa.com/booking/choose-flights/1?sid=...",
  "title": "Choose Flights - American Airlines",
  "flights": [
    {
      "index": 0,
      "selector_used": ".flight-option",
      "text_content": "Flight details...",
      "html_content": "<div>...</div>"
    }
  ],
  "raw_content": "<html>...</html>"
}
```

## ⚠️ Important Notes

### Session Requirements
- The URL contains a session ID (`sid`) that may expire
- You may need to get a fresh URL from a real browser session
- Some pages require authentication or specific cookies

### Legal Considerations
- Always respect robots.txt and terms of service
- Use reasonable request rates to avoid overloading servers
- Consider the legal implications of scraping commercial websites
- This is for educational/research purposes only

### Performance Tips
- Set `headless=True` for production use
- Use proxy rotation for large-scale scraping
- Implement delays between requests
- Monitor for rate limiting

## 🔍 Troubleshooting

### Common Issues

1. **Empty Results**
   - Session ID may have expired
   - Page requires JavaScript execution
   - Anti-bot protection is blocking requests

2. **Installation Errors**
   - Ensure Python 3.8+ is installed
   - Use virtual environment
   - Install Playwright browsers: `playwright install`

3. **Browser Issues**
   - Update browser drivers
   - Check system permissions
   - Try different browser types (chromium, firefox, webkit)

### Debug Mode
Enable debug mode by setting `headless=False` to see the browser in action and debug issues visually.

## 📚 Dependencies

- **scrapling**: Advanced anti-bot bypass library
- **crawlee**: Web scraping and browser automation framework
- **playwright**: Browser automation library
- **requests**: HTTP library
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation
- **numpy**: Numerical computing

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the scrapers.

## 📄 License

This project is for educational purposes only. Please respect website terms of service and applicable laws.
