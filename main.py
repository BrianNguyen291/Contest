#!/usr/bin/env python3
"""AA Flight Scraper CLI Entry Point"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, date
from pathlib import Path

from scraper.aa_scraper import AAScraper
from scraper.models import SearchMetadata


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AA Flight Scraper - Extract award and cash pricing with CPP calculation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --origin LAX --destination JFK --date 2025-12-15
  python main.py --origin SFO --destination BOS --date 2025-12-20 --passengers 2
  python main.py --origin LAX --destination JFK --date 2025-12-15 --output results.json
  python main.py --origin LAX --destination JFK --date 2025-12-15 --proxy http://proxy:8080
        """
    )
    
    parser.add_argument(
        "--origin",
        type=str,
        default="LAX",
        help="Origin airport code (default: LAX)"
    )
    
    parser.add_argument(
        "--destination", 
        type=str,
        default="JFK",
        help="Destination airport code (default: JFK)"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        default="2025-12-15",
        help="Flight date in YYYY-MM-DD format (default: 2025-12-15)"
    )
    
    parser.add_argument(
        "--passengers",
        type=int,
        default=1,
        help="Number of passengers (default: 1)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path (default: stdout)"
    )
    
    parser.add_argument(
        "--proxy",
        type=str,
        help="Proxy URL (e.g., http://proxy:8080)"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (default: headless)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def validate_date_format(date_str: str) -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_airport_code(code: str) -> bool:
    """Validate airport code format"""
    return len(code) == 3 and code.isalpha()


async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Validate inputs
    if not validate_date_format(args.date):
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD format.")
        sys.exit(1)
    
    if not validate_airport_code(args.origin.upper()):
        print(f"Error: Invalid origin airport code '{args.origin}'. Use 3-letter code.")
        sys.exit(1)
    
    if not validate_airport_code(args.destination.upper()):
        print(f"Error: Invalid destination airport code '{args.destination}'. Use 3-letter code.")
        sys.exit(1)
    
    if args.passengers < 1 or args.passengers > 9:
        print(f"Error: Invalid passenger count '{args.passengers}'. Must be 1-9.")
        sys.exit(1)
    
    # Create search metadata
    search_metadata = SearchMetadata(
        origin=args.origin.upper(),
        destination=args.destination.upper(),
        date=args.date,
        passengers=args.passengers,
        cabin_class="economy"
    )
    
    if args.verbose:
        print(f"Searching flights: {search_metadata.origin} → {search_metadata.destination}")
        print(f"Date: {search_metadata.date}")
        print(f"Passengers: {search_metadata.passengers}")
        if args.proxy:
            print(f"Using proxy: {args.proxy}")
    
    try:
        # Initialize scraper
        async with AAScraper(headless=not args.no_headless, proxy=args.proxy) as scraper:
            # Search for flights
            result = await scraper.search_flights(search_metadata)
            
            # Convert to JSON
            result_json = result.model_dump()
            
            # Output results
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    json.dump(result_json, f, indent=2)
                print(f"Results saved to: {output_path}")
            else:
                print(json.dumps(result_json, indent=2))
            
            # Print summary
            if args.verbose:
                print(f"\nSummary:")
                print(f"Total flights found: {result.total_results}")
                if result.flights:
                    print(f"Flights with CPP data: {len([f for f in result.flights if f.cpp is not None])}")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
