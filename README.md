# AA Flight Scraper

A Python-based web scraper that extracts both award and cash pricing from American Airlines (AA.com) and calculates Cents Per Point (CPP) values. Built with Playwright and advanced bot evasion techniques.

## Features

- **Dual Pricing Extraction**: Scrapes both award miles and cash prices for the same flights
- **CPP Calculation**: Automatically calculates Cents Per Point value for each flight
- **Bot Evasion**: Advanced stealth techniques to avoid detection
- **Flexible Parameters**: Support for different routes, dates, and passenger counts
- **Docker Support**: Easy deployment with Docker containerization
- **JSON Output**: Structured data output for easy integration

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Run the scraper:**
```bash
python main.py --origin LAX --destination JFK --date 2025-12-15
```

### Docker Deployment

1. **Build the image:**
```bash
docker build -t aa-flight-scraper .
```

2. **Run the container:**
```bash
docker run --rm aa-flight-scraper --origin LAX --destination JFK --date 2025-12-15
```

## Usage

```bash
python main.py [OPTIONS]

Options:
  --origin TEXT           Origin airport code (default: LAX)
  --destination TEXT      Destination airport code (default: JFK)
  --date TEXT             Flight date in YYYY-MM-DD format (default: 2025-12-15)
  --passengers INTEGER    Number of passengers (default: 1)
  --output TEXT           Output JSON file path (default: stdout)
  --proxy TEXT            Proxy URL (e.g., http://proxy:8080)
  --no-headless          Run browser in visible mode (default: headless)
  --verbose               Enable verbose logging
```

## Examples

**Basic search:**
```bash
python main.py --origin LAX --destination JFK --date 2025-12-15
```

**Save to file:**
```bash
python main.py --origin SFO --destination BOS --date 2025-12-20 --output results.json
```

**With proxy:**
```bash
python main.py --origin LAX --destination JFK --date 2025-12-15 --proxy http://proxy:8080
```

## Output Format

```json
{
  "search_metadata": {
    "origin": "LAX",
    "destination": "JFK",
    "date": "2025-12-15",
    "passengers": 1,
    "cabin_class": "economy"
  },
  "flights": [
    {
      "flight_number": "AA123",
      "departure_time": "08:00",
      "arrival_time": "16:30",
      "points_required": 12500,
      "cash_price_usd": 289.00,
      "taxes_fees_usd": 5.60,
      "cpp": 2.27
    }
  ],
  "total_results": 1
}
```

## CPP Calculation

Cents Per Point (CPP) is calculated as:
```
CPP = (Cash Price - Taxes & Fees) / Points Required × 100
```

## Bot Evasion Techniques

The scraper implements multiple layers of bot evasion:

- **Playwright Stealth**: Automatic fingerprint randomization
- **Human-like Behavior**: Random delays, mouse movements, natural typing
- **Realistic Browser Context**: Proper viewport, user-agent, locale settings
- **Request Header Randomization**: Varied headers to mimic real browsers
- **Retry Logic**: Exponential backoff for failed requests

## Legal Notice

This tool is for educational and personal use only. Users are responsible for complying with American Airlines' Terms of Service and applicable laws.

## License

This project is provided as-is for educational purposes. Use at your own risk.