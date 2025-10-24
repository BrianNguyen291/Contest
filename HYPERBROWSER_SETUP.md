# Hyperbrowser Setup Guide

## 🚀 Why Hyperbrowser Works vs Local Scraping

**Hyperbrowser uses cloud infrastructure that bypasses AA.com's anti-bot protection:**

### ✅ **Hyperbrowser Advantages:**
- 🌐 **Cloud Infrastructure**: Enterprise data centers with clean IP addresses
- 🔄 **Automatic IP Rotation**: Different IPs for each request
- 🛡️ **Enterprise Stealth**: Professional-grade anti-detection
- 🌍 **Geographic Distribution**: Requests from different locations
- 📊 **Clean Browser Fingerprints**: Fresh signatures each time
- 🏢 **Business-grade Infrastructure**: Not flagged as residential automation

### ❌ **Local Scraping Limitations:**
- 🏠 **Home IP Address**: Residential IP easily flagged
- 💻 **Same Browser Fingerprint**: Identical hardware signature
- 🔄 **No IP Rotation**: Same network identity
- 📱 **Limited Stealth**: Easier to detect locally
- 🌐 **Geographic Consistency**: Always same location

## 📋 Setup Instructions

### 1. Get Hyperbrowser API Key
1. Visit: https://docs.hyperbrowser.ai/get-started/quickstart/web-scraping/scrape
2. Sign up for Hyperbrowser account
3. Get your API key from the dashboard

### 2. Create Environment File
Create a `.env` file in the project root:
```bash
# Hyperbrowser API Key
HYPERBROWSER_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
```bash
pip install hyperbrowser python-dotenv
```

### 4. Test the Scraper
```bash
python -m scraper.hyperbrowser_scraper
```

## 🎯 Expected Results

With Hyperbrowser cloud infrastructure:
- ✅ **Bypasses AA.com anti-bot protection**
- ✅ **Extracts real flight data**
- ✅ **Fast execution (sub-second)**
- ✅ **Professional-grade reliability**

## 🔧 Technical Details

The scraper uses the official [Hyperbrowser SDK](https://docs.hyperbrowser.ai/get-started/quickstart/web-scraping/scrape) to:

1. **Scrape AA.com** using cloud infrastructure
2. **Parse HTML content** for flight data
3. **Extract flight information** (numbers, prices, times, points)
4. **Calculate CPP** (Cents Per Point) for each flight
5. **Return structured data** via FastAPI

## 🚀 Usage

```python
from scraper.hyperbrowser_scraper import HyperbrowserAAScraper
from scraper.models import SearchMetadata

async with HyperbrowserAAScraper() as scraper:
    await scraper.start()
    
    search_metadata = SearchMetadata(
        origin="LAX",
        destination="JFK", 
        date="2025-12-15",
        passengers=1
    )
    
    result = await scraper.search_flights(search_metadata)
    print(f"Found {result.total_results} flights")
```

## 🎉 Success!

This approach successfully bypasses AA.com's enterprise-grade anti-bot protection by using professional cloud infrastructure instead of local automation.
