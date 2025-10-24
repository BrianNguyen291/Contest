"""Configuration constants for AA scraper"""

# AA.com URLs
BASE_URL = "https://www.aa.com"
SEARCH_URL = "https://www.aa.com/booking/find-flights"

# Browser settings
DEFAULT_VIEWPORT = {"width": 1920, "height": 1080}
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Timing settings (in milliseconds)
MIN_DELAY = 500
MAX_DELAY = 2000
PAGE_LOAD_TIMEOUT = 30000
ELEMENT_WAIT_TIMEOUT = 10000

# CSS Selectors for AA.com
SELECTORS = {
    # Cookie consent
    "cookie_accept": "button[data-testid='cookie-accept']",
    "cookie_modal": "[data-testid='cookie-modal']",
    
    # Search form
    "origin_input": "input[data-testid='origin-airport']",
    "destination_input": "input[data-testid='destination-airport']",
    "date_input": "input[data-testid='departure-date']",
    "passengers_input": "input[data-testid='passengers']",
    "search_button": "button[data-testid='search-flights']",
    
    # Award vs Cash toggle
    "award_toggle": "button[data-testid='award-flights']",
    "cash_toggle": "button[data-testid='cash-flights']",
    
    # Results
    "flight_cards": "[data-testid='flight-card']",
    "flight_number": "[data-testid='flight-number']",
    "departure_time": "[data-testid='departure-time']",
    "arrival_time": "[data-testid='arrival-time']",
    "points_price": "[data-testid='points-price']",
    "cash_price": "[data-testid='cash-price']",
    "taxes_fees": "[data-testid='taxes-fees']",
}

# Alternative selectors (fallback)
ALT_SELECTORS = {
    "origin_input": "input[name='origin']",
    "destination_input": "input[name='destination']",
    "date_input": "input[name='departureDate']",
    "search_button": "button[type='submit']",
    "flight_cards": ".flight-card, .flight-option",
    "flight_number": ".flight-number, .flight-id",
    "departure_time": ".departure-time, .dep-time",
    "arrival_time": ".arrival-time, .arr-time",
    "points_price": ".points, .miles",
    "cash_price": ".price, .fare",
}

# Error messages
ERROR_MESSAGES = {
    "no_flights": "No flights found for the given criteria",
    "timeout": "Page load timeout - site may be slow or blocking requests",
    "captcha": "CAPTCHA detected - manual intervention required",
    "rate_limit": "Rate limited - too many requests",
    "network": "Network error - check connection",
}
