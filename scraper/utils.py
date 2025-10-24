"""Utility functions for AA scraper"""

import re
import random
import time
from typing import Optional, Dict, Any
from datetime import datetime


def calculate_cpp(cash_price: float, taxes_fees: float, points_required: int) -> Optional[float]:
    """
    Calculate Cents Per Point (CPP) value.
    
    Args:
        cash_price: Cash price in USD
        taxes_fees: Taxes and fees in USD
        points_required: Points required for award booking
        
    Returns:
        CPP value or None if calculation not possible
    """
    if not all([cash_price, taxes_fees is not None, points_required]):
        return None
    
    try:
        cpp = ((cash_price - taxes_fees) / points_required) * 100
        return round(cpp, 2)
    except (ZeroDivisionError, TypeError):
        return None


def parse_price(price_text: str) -> Optional[float]:
    """
    Parse price from text string.
    
    Args:
        price_text: Price text like "$289.00" or "12,500 points"
        
    Returns:
        Price as float or None if parsing fails
    """
    if not price_text:
        return None
    
    # Remove common currency symbols and text
    cleaned = re.sub(r'[^\d.,]', '', price_text)
    
    # Handle comma-separated thousands
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_time(time_text: str) -> Optional[str]:
    """
    Parse time from text and return in HH:MM format.
    
    Args:
        time_text: Time text like "8:00 AM" or "16:30"
        
    Returns:
        Time in HH:MM format or None if parsing fails
    """
    if not time_text:
        return None
    
    # Clean the text
    time_text = time_text.strip().upper()
    
    # Try to match various time formats
    patterns = [
        r'(\d{1,2}):(\d{2})\s*(AM|PM)?',  # 8:00 AM or 16:30
        r'(\d{1,2})\s*(AM|PM)',           # 8 AM
    ]
    
    for pattern in patterns:
        match = re.search(pattern, time_text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            ampm = match.group(3) if len(match.groups()) > 2 else None
            
            # Convert to 24-hour format if needed
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute:02d}"
    
    return None


def parse_flight_number(flight_text: str) -> Optional[str]:
    """
    Parse flight number from text.
    
    Args:
        flight_text: Flight text like "AA123" or "American 123"
        
    Returns:
        Flight number or None if parsing fails
    """
    if not flight_text:
        return None
    
    # Look for pattern like AA123, AA 123, etc.
    match = re.search(r'([A-Z]{2,3})\s*(\d{1,4})', flight_text.upper())
    if match:
        return f"{match.group(1)}{match.group(2)}"
    
    return None


def random_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
    """
    Add random delay to simulate human behavior.
    
    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    delay = random.randint(min_ms, max_ms) / 1000.0
    time.sleep(delay)


def match_flights(award_flights: list, cash_flights: list) -> list:
    """
    Match award flights with cash flights based on flight number and departure time.
    
    Args:
        award_flights: List of award flight data
        cash_flights: List of cash flight data
        
    Returns:
        List of matched flights with both award and cash data
    """
    matched_flights = []
    
    for award_flight in award_flights:
        flight_number = award_flight.get('flight_number')
        departure_time = award_flight.get('departure_time')
        
        if not flight_number or not departure_time:
            continue
        
        # Find matching cash flight
        matching_cash = None
        for cash_flight in cash_flights:
            if (cash_flight.get('flight_number') == flight_number and 
                cash_flight.get('departure_time') == departure_time):
                matching_cash = cash_flight
                break
        
        # Create combined flight data
        combined_flight = {
            'flight_number': flight_number,
            'departure_time': departure_time,
            'arrival_time': award_flight.get('arrival_time'),
            'points_required': award_flight.get('points_required'),
            'cash_price_usd': matching_cash.get('cash_price_usd') if matching_cash else None,
            'taxes_fees_usd': award_flight.get('taxes_fees_usd'),
        }
        
        # Calculate CPP if we have all required data
        if (combined_flight['cash_price_usd'] and 
            combined_flight['taxes_fees_usd'] is not None and 
            combined_flight['points_required']):
            combined_flight['cpp'] = calculate_cpp(
                combined_flight['cash_price_usd'],
                combined_flight['taxes_fees_usd'],
                combined_flight['points_required']
            )
        
        matched_flights.append(combined_flight)
    
    return matched_flights


def validate_date(date_str: str) -> bool:
    """
    Validate date string format and ensure it's in the future.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        True if valid future date, False otherwise
    """
    try:
        flight_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return flight_date >= today
    except ValueError:
        return False


def format_airport_code(code: str) -> str:
    """
    Format airport code to uppercase and validate format.
    
    Args:
        code: Airport code string
        
    Returns:
        Formatted airport code or raises ValueError
    """
    if not code or len(code) != 3:
        raise ValueError(f"Invalid airport code: {code}")
    
    return code.upper()
