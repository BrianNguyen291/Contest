# AA Flight Scraper

A Python-based web scraper that extracts both award and cash pricing from American Airlines (AA.com) and calculates Cents Per Point (CPP) values. Built with Playwright and advanced bot evasion techniques.

## Features

- **Dual Pricing Extraction**: Scrapes both award miles and cash prices for the same flights
- **CPP Calculation**: Automatically calculates Cents Per Point value for each flight
- **Bot Evasion**: Advanced stealth techniques to avoid detection
- **Flexible Parameters**: Support for different routes, dates, and passenger counts
- **Docker Support**: Easy deployment with Docker containerization
- **JSON Output**: Structured data output for easy integration

## Bot Evasion Techniques

The scraper implements multiple layers of bot evasion:

- **Playwright Stealth**: Automatic fingerprint randomization
- **Human-like Behavior**: Random delays, mouse movements, natural typing
- **Realistic Browser Context**: Proper viewport, user-agent, locale settings
- **Request Header Randomization**: Varied headers to mimic real browsers
- **Proxy Support**: Optional residential proxy rotation
- **Retry Logic**: Exponential backoff for failed requests

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd aa-flight-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Run the scraper:
```bash
python main.py --origin LAX --destination JFK --date 2025-12-15
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t aa-flight-scraper .
```

2. Run the container:
```bash
docker run --rm aa-flight-scraper --origin LAX --destination JFK --date 2025-12-15
```

3. Or use docker-compose:
```bash
docker-compose up
```

## Usage

### Command Line Interface

```bash
python main.py [OPTIONS]

Options:
  --origin TEXT           Origin airport code (default: LAX)
  --destination TEXT      Destination airport code (default: JFK)
  --date TEXT             Flight date in YYYY-MM-DD format (default: 2025-12-15)
  --passengers INTEGER    Number of passengers (default: 1)
  --output TEXT           Output JSON file path (default: stdout)
  --proxy TEXT            Proxy URL (e.g., http://proxy:8080)
  --headless              Run browser in headless mode (default: True)
  --verbose               Enable verbose logging
  --help                  Show help message
```

### Examples

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

**Multiple passengers:**
```bash
python main.py --origin LAX --destination JFK --date 2025-12-15 --passengers 2
```

### Docker Examples

**Basic Docker run:**
```bash
docker run --rm aa-flight-scraper --origin LAX --destination JFK --date 2025-12-15
```

**Docker with volume for output:**
```bash
docker run --rm -v $(pwd)/output:/app/output aa-flight-scraper \
  --origin LAX --destination JFK --date 2025-12-15 \
  --output /app/output/results.json
```

**Docker Compose:**
```bash
# Edit docker-compose.yml to set your parameters
docker-compose up
```

## Output Format

The scraper outputs structured JSON data:

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

### CPP Calculation

Cents Per Point (CPP) is calculated as:
```
CPP = (Cash Price - Taxes & Fees) / Points Required × 100
```

Example: If a flight costs $289 cash or 12,500 points + $5.60 fees:
```
CPP = ($289 - $5.60) / 12,500 × 100 = 2.27 cents per point
```

## Configuration

### Environment Variables

- `PROXY_URL`: Set proxy URL for all requests
- `HEADLESS`: Set to `false` to run browser in visible mode
- `VERBOSE`: Enable detailed logging

### Proxy Support

The scraper supports HTTP/HTTPS proxies:

```bash
python main.py --proxy http://username:password@proxy.example.com:8080
```

## Error Handling

The scraper handles various error scenarios:

- **No flights found**: Returns empty results gracefully
- **Network timeouts**: Implements retry logic with exponential backoff
- **CAPTCHA detection**: Logs warning and continues
- **Rate limiting**: Automatic delays between requests
- **Invalid dates**: Validates date format and future dates only

## Troubleshooting

### Common Issues

1. **Browser not found**: Run `playwright install chromium`
2. **Permission denied**: Check Docker permissions or run with `sudo`
3. **Proxy errors**: Verify proxy URL and credentials
4. **No results**: Check if flights exist for the given date/route

### Debug Mode

Run with `--verbose` flag for detailed logging:

```bash
python main.py --origin LAX --destination JFK --date 2025-12-15 --verbose
```

### Non-headless Mode

For debugging, run browser in visible mode:

```bash
python main.py --origin LAX --destination JFK --date 2025-12-15 --headless=false
```

## Development

### Project Structure

```
aa-flight-scraper/
├── scraper/
│   ├── __init__.py
│   ├── aa_scraper.py      # Main scraper class
│   ├── models.py          # Pydantic data models
│   ├── utils.py           # Utility functions
│   └── config.py          # Configuration constants
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container build instructions
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore        # Docker build exclusions
└── README.md            # This file
```

### Adding New Features

1. **New selectors**: Update `scraper/config.py`
2. **New data fields**: Modify `scraper/models.py`
3. **New parsing logic**: Extend `scraper/utils.py`
4. **New CLI options**: Update `main.py`

## Legal Notice

This tool is for educational and personal use only. Users are responsible for complying with American Airlines' Terms of Service and applicable laws. The authors are not responsible for any misuse of this tool.

## License

This project is provided as-is for educational purposes. Use at your own risk.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages with `--verbose` flag
3. Test with different dates/routes
4. Check network connectivity and proxy settings
