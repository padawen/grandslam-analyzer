"""Main scraper orchestrator - entry point for scraping tournaments."""
import os
import sys
import json

from .config import TOURNAMENT_URLS
from .driver import setup_driver
from .links import get_match_links
from .extractor import extract_match_data
from .database import get_existing_match_ids_from_supabase, save_to_db


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def scrape_tournament(tournament_key):
    """Scrape matches for a specific tournament."""
    if tournament_key not in TOURNAMENT_URLS:
        print(f"Error: Tournament '{tournament_key}' not supported.")
        print(f"Available: {list(TOURNAMENT_URLS.keys())}")
        return False
    
    base_url = TOURNAMENT_URLS[tournament_key]
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    output_file = f"data/matches_{tournament_key}.json"
    driver = None
    
    try:
        print(f"\n{'='*60}")
        print(f"Tournament Scraper: {tournament_key}")
        print(f"{'='*60}\n")
        
        print("Initializing Chrome driver...")
        driver = setup_driver()
        
        print(f"Fetching match links from: {base_url}")
        match_links, surface = get_match_links(driver, base_url)
        
        if not match_links:
            print("No matches found!")
            return False
        
        print(f"Found {len(match_links)} matches\n")
        
        matches = []
        successful = 0
        skipped = 0
        already_in_db = 0
        
        # Get existing IDs from Supabase to skip
        existing_ids = get_existing_match_ids_from_supabase()
        
        for i, match_url in enumerate(match_links, 1):
            if match_url in existing_ids:
                already_in_db += 1
                continue
            
            print(f"[{i}/{len(match_links)}] Processing...")
            
            match_data = extract_match_data(driver, match_url)
            
            if match_data:
                matches.append(match_data)
                successful += 1
                print(f"  ✓ {match_data['playerA']} ({match_data['oddsA']}) vs {match_data['playerB']} ({match_data['oddsB']}) - {match_data['round']}")
            else:
                skipped += 1
                print(f"  ✗ Skipped (no odds/walkover)")
        
        # Save to JSON
        output_data = {
            "tournament_key": tournament_key,
            "tournament": f"{tournament_key.replace('_', ' ').title()}",
            "surface": surface,
            "matches": matches
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE - {tournament_key}")
        print(f"Total processed: {len(match_links)}")
        print(f"Already in DB: {already_in_db} (skipped)")
        print(f"Newly scraped: {successful}")
        print(f"Skipped (error): {skipped}")
        print(f"Data saved to: {output_file}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m scraper.run <tournament_key>")
        print(f"Available tournaments: {list(TOURNAMENT_URLS.keys())}")
        sys.exit(1)
    
    tournament_key = sys.argv[1]
    success = scrape_tournament(tournament_key)
    
    if success:
        try:
            with open(f"data/matches_{tournament_key}.json", "r") as f:
                data = json.load(f)
                save_to_db(data)
        except Exception as e:
            print(f"Failed to save to DB: {e}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
