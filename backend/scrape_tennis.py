#!/usr/bin/env python3
"""
PDC Darts Year-Specific Scraper with Round Information
Usage: python3 scrape_year.py 2026
       python3 scrape_year.py 2025
"""

import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    WebDriverException
)

# Import URL configuration
TOURNAMENT_URLS = {}
try:
    from config import TOURNAMENT_URLS as CONFIG_URLS
    TOURNAMENT_URLS.update(CONFIG_URLS)
except ImportError:
    # If config.py is missing (e.g. in GitHub Actions), we'll rely on environment variables
    pass

# Update from environment variable if available
import os
urls_json = os.environ.get("TOURNAMENT_URLS_JSON")
if urls_json:
    try:
        import json
        TOURNAMENT_URLS.update(json.loads(urls_json))
    except Exception as e:
        print(f"Error parsing TOURNAMENT_URLS_JSON: {e}")

if not TOURNAMENT_URLS:
    print("Error: No tournament URLs found. Please set TOURNAMENT_URLS_JSON secret or create local config.py.")
    sys.exit(1)


def setup_driver():
    """Initialize Chrome driver with optimized options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    chrome_options.page_load_strategy = 'eager'
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(0)
    
    return driver


def accept_cookies(driver):
    """Accept cookie consent if present"""
    try:
        cookie_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_btn.click()
        WebDriverWait(driver, 2).until(
            EC.invisibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
        )
    except (TimeoutException, NoSuchElementException):
        pass



def get_tournament_surface(driver):
    """Detect tournament surface from the header"""
    try:
        # Wait for header
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".headerLeague__title, .event__header"))
        )
        
        # Try finding the designated header title element first
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, ".headerLeague__title")
            text = f"{title_elem.get_attribute('title')} {title_elem.text}".lower()
        except NoSuchElementException:
            # Fallback to the first event header
            header = driver.find_element(By.CSS_SELECTOR, ".event__header")
            text = header.text.lower()
            
        print(f"  Analysing surface from: '{text}'")
        
        if "kemény" in text or "hard" in text:
            return "Hard"
        elif "salak" in text or "clay" in text:
            return "Clay"
        elif "fű" in text or "grass" in text:
            return "Grass"
        elif "fedett" in text or "indoor" in text:
            return "Indoor Hard"
            
    except Exception as e:
        print(f"  Warning: Could not detect surface: {e}")
    
    return "Unknown"


def get_match_links(driver, base_url):
    """Extract match match links, skipping qualification rounds based on headers"""
    try:
        driver.get(base_url)
        accept_cookies(driver)
        
        # 1. Detect Surface ONCE
        surface = get_tournament_surface(driver)
        print(f"  Detected Surface: {surface}")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sportName.tennis"))
        )
        
        # Scroll down to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        import time
        time.sleep(2)
        
        # Click "Show more matches" - Robust method checking text content
        try:
            more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'További meccsek')] | //span[contains(text(), 'További meccsek')]"))
            )
            print("  Found 'További meccsek' button, clicking...")
            driver.execute_script("arguments[0].scrollIntoView(true);", more_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", more_btn)
            
            # Wait for more items to load
            time.sleep(5)
            print("  Loaded more matches.")
            
        except TimeoutException:
            try:
                more_btn = driver.find_element(By.CSS_SELECTOR, ".event__more")
                print("  Found '.event__more' button, clicking...")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(5)
            except:
                print("  No 'Show more matches' button found or clickable.")
        except Exception as e:
            print(f"  Error clicking show more: {e}")

        # Locate the container for matches
        container = driver.find_element(By.CSS_SELECTOR, ".sportName.tennis")
        
        # Get all direct children (headers and matches)
        elements = container.find_elements(By.XPATH, "./*")
        
        match_links = []
        is_qualification = False
        
        print(f"  Scanning {len(elements)} list items for valid matches...")
        
        for i, elem in enumerate(elements):
            class_name = elem.get_attribute("class")
            text = elem.text.replace("\n", " ").strip()
            
            if "event__header" in class_name:
                print(f"  [HEADER FOUND] '{text}'")
                
                if "Selejtező" in text or "Qualifying" in text:
                    is_qualification = True
                    print(f"    -> MARKING AS QUALIFICATION (skipping)")
                else:
                    is_qualification = False
                    print(f"    -> MARKING AS MAIN DRAW")
            
            elif "header" in class_name or "title" in class_name.lower():
                 if "Selejtező" in text or "Qualifying" in text:
                     print(f"  [POTENTIAL HEADER] Class: {class_name}, Text: {text}")
                     is_qualification = True

            elif "event__match" in class_name:
                # Check for Cancelled keywords (Törölt, Elmaradt)
                # User requested to KEEP 'Feladta' (Retired) and 'Visszalépett' (Walkover) if they have a winner.
                # Usually 'Header' has surface.
                
                lower_text = text.lower()
                # Only skip strictly cancelled matches that definitely have no result
                if "törölt" in lower_text or "elmaradt" in lower_text:
                    print(f"  Skipping cancelled match: {text[:50]}...")
                    continue

                if not is_qualification:
                    try:
                        # Find the link inside this match row
                        link_el = elem.find_element(By.CSS_SELECTOR, "a.eventRowLink") 
                        href = link_el.get_attribute('href')
                        if href:
                            match_links.append(href)
                    except NoSuchElementException:
                        pass
        
        # Deduplicate links just in case
        match_links = list(dict.fromkeys(match_links))
        
        print(f"  Detected Surface: {surface}")
        return match_links, surface
        
    except Exception as e:
        print(f"Error getting match links: {e}")
        return []


def extract_match_data(driver, match_url):
    """Extract match data from individual match page with retries for stability"""
    from selenium.common.exceptions import StaleElementReferenceException
    import time

    for attempt in range(2): # Try twice
        try:
            driver.get(match_url)
            
            # Additional wait for stability on very dynamic pages
            time.sleep(1)
            
            # Wait for player names
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".participant__participantNameWrapper"))
            )
            
            # Extract player names - re-find elements to avoid stale references
            player_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".participant__participantNameWrapper"))
            )
            
            if len(player_elements) < 2:
                print(f"  Warning: Less than 2 players found at {match_url}")
                return None
            
            player_a = player_elements[0].text.strip()
            player_b = player_elements[1].text.strip()
            
            # Check for Walkover based on player names
            is_walkover = False
            winner_index = -1 # 0 for Player A, 1 for Player B
            
            if "Továbbjutó" in player_a:
                is_walkover = True
                winner_index = 0
                player_a = player_a.replace("Továbbjutó", "").strip(" -()")
            elif "Továbbjutó" in player_b:
                is_walkover = True
                winner_index = 1
                player_b = player_b.replace("Továbbjutó", "").strip(" -()")
            
            # Extract round information from breadcrumb
            round_name = "Unknown"
            try:
                breadcrumb_elems = driver.find_elements(By.CSS_SELECTOR, '[class*="breadcrumbItemLabel"]')
                if breadcrumb_elems:
                    breadcrumb_text = breadcrumb_elems[-1].get_attribute('textContent').strip()
                    if " - " in breadcrumb_text:
                        round_name = breadcrumb_text.split(" - ")[1].strip()
                    else:
                        round_name = breadcrumb_text
            except (NoSuchElementException, IndexError):
                pass
            
            if "Selejtező" in round_name or "Qualifying" in round_name:
                print(f"  Skipping Qualification match: {player_a} vs {player_b} ({round_name})")
                return None

            # Extract match start time
            match_time = None
            try:
                time_elem = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__startTime")
                time_text = time_elem.text.strip()
                if time_text:
                    from datetime import datetime
                    match_time = datetime.strptime(time_text, "%d.%m.%Y %H:%M")
            except (NoSuchElementException, ValueError):
                pass

            odds_a = 1.0
            odds_b = 1.0
            player_a_won = False
            player_b_won = False
            
            if is_walkover:
                print(f"  Walkover detected: {player_a} vs {player_b}")
                odds_a = 1.0
                odds_b = 1.0
                if winner_index == 0:
                    player_a_won = True
                else:
                    player_b_won = True
            else:
                # Try to get real odds
                try:
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a.prematchLink"))
                        )
                    except TimeoutException:
                        pass

                    tippmix_links = driver.find_elements(By.CSS_SELECTOR, 'a[title="TippmixPro"]')
                    
                    if tippmix_links:
                        tippmix_link = tippmix_links[0]
                        try:
                            odds_row = tippmix_link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'odds')]")
                        except NoSuchElementException:
                            try:
                                odds_row = tippmix_link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'row')]")
                            except NoSuchElementException:
                                odds_row = driver.execute_script("return arguments[0].parentElement.parentElement;", tippmix_link)
                        
                        odds_cells = odds_row.find_elements(By.CSS_SELECTOR, "button[class*='oddsCell']")
                        
                        if len(odds_cells) >= 2:
                            odds_a_text = odds_cells[0].text.strip()
                            odds_b_text = odds_cells[1].text.strip()
                            
                            if odds_a_text and odds_b_text:
                                try:
                                    odds_a = float(odds_a_text.replace(',', '.'))
                                    odds_b = float(odds_b_text.replace(',', '.'))
                                    cell_a_classes = odds_cells[0].get_attribute('class') or ''
                                    cell_b_classes = odds_cells[1].get_attribute('class') or ''
                                    player_a_won = 'wcl-win' in cell_a_classes
                                    player_b_won = 'wcl-win' in cell_b_classes
                                except ValueError:
                                    pass
                except Exception as e:
                    print(f"  Error parsing odds: {e}")
                
                if not player_a_won and not player_b_won:
                    try:
                        home_participant = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__home")
                        if "duelParticipant--winner" in home_participant.get_attribute("class"):
                            player_a_won = True
                        away_participant = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__away")
                        if "duelParticipant--winner" in away_participant.get_attribute("class"):
                            player_b_won = True
                    except NoSuchElementException:
                        pass

                if not is_walkover and odds_a == 1.0 and odds_b == 1.0 and not player_a_won and not player_b_won:
                    return None

            # Determine underdog and favorite
            if odds_a > odds_b:
                underdog, underdog_odds, underdog_won = player_a, odds_a, player_a_won
                favorite, favorite_odds, favorite_won = player_b, odds_b, player_b_won
            elif odds_b > odds_a:
                underdog, underdog_odds, underdog_won = player_b, odds_b, player_b_won
                favorite, favorite_odds, favorite_won = player_a, odds_a, player_a_won
            else:
                underdog, underdog_odds, underdog_won = player_a, odds_a, player_a_won
                favorite, favorite_odds, favorite_won = player_b, odds_b, player_b_won
            
            return {
                "playerA": player_a,
                "playerB": player_b,
                "oddsA": odds_a,
                "oddsB": odds_b,
                "underdog": underdog,
                "underdogOdds": underdog_odds,
                "underdogWon": underdog_won,
                "favorite": favorite,
                "favoriteOdds": favorite_odds,
                "favoriteWon": favorite_won,
                "round": round_name,
                "matchTime": match_time,
                "id": match_url
            }
            
        except StaleElementReferenceException:
            if attempt == 0:
                print(f"  Stale element detected, retrying {match_url}...")
                continue
            else:
                print(f"  Stale element on retry, skipping {match_url}")
                return None
        except TimeoutException:
            print(f"  Timeout processing {match_url}")
            return None
        except NoSuchElementException:
            return None
        except Exception as e:
            if attempt == 0:
                print(f"  Error on attempt 1 for {match_url}: {e}, retrying...")
                continue
            else:
                print(f"  Error extracting match data: {e}")
                return None
    
    return None  # If all retries failed



def scrape_tournament(tournament_key):
    """Scrape matches for a specific tournament"""
    if tournament_key not in TOURNAMENT_URLS:
        print(f"Error: Tournament '{tournament_key}' not supported. Available: {list(TOURNAMENT_URLS.keys())}")
        return False
    
    base_url = TOURNAMENT_URLS[tournament_key]
    # Ensure data directory exists
    import os
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
        
        # Optional: limit for testing
        MAX_MATCHES = None  # Set to None for all matches
        if MAX_MATCHES:
            match_links = match_links[:MAX_MATCHES]
            print(f"Found {len(match_links)} matches (limited to {MAX_MATCHES} for testing)\n")
        else:
            print(f"Found {len(match_links)} matches\n")

        
        matches = []
        successful = 0
        skipped = 0
        already_in_db = 0
        
        # Get existing IDs from Supabase to skip already processed matches
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
        
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                from datetime import datetime
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        print("\n" + "="*60)
        print(f"SCRAPING COMPLETE - {tournament_key}")
        print(f"Total processed: {len(match_links)}")
        print(f"Already in DB: {already_in_db} (skipped)")
        print(f"Newly scraped: {successful}")
        print(f"Skipped (error): {skipped}")
        print(f"Data saved to: {output_file}")
        print("="*60 + "\n")
        
        return True
        
    except WebDriverException as e:
        print(f"\nWebDriver error: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

import os
import requests

def get_existing_match_ids_from_supabase():
    """Fetch all external_ids from the matches table in Supabase to skip already processed matches"""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Supabase not configured, cannot fetch existing IDs.")
        return set()
    
    url = f"{supabase_url}/rest/v1/matches?select=external_id"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            ids = {item['external_id'] for item in data if item.get('external_id')}
            print(f"  Found {len(ids)} matches already in Supabase (will be skipped).")
            return ids
        else:
            print(f"  Warning: Could not fetch existing IDs from Supabase: {response.text}")
            return set()
    except Exception as e:
        print(f"  Error fetching existing IDs from Supabase: {e}")
        return set()

def save_to_supabase(table, data, on_conflict="id"):
    """Helper to save to Supabase via REST API"""
    url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/{table}"
    headers = {
        "apikey": os.environ.get("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}",
        "Content-Type": "application/json",
        "Prefer": f"resolution=merge-duplicates,return=representation"
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code not in [200, 201]:
            print(f"Supabase error ({table}): {r.text}")
            return None
        return r.json()
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        return None

def save_to_db(data):
    """Save scraped data to Database (SQLite, Postgres, or Supabase REST)"""
    
    # 1. Try Supabase REST API if configured
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        print("Saving to Supabase REST API...")
        
        t_key = data['tournament_key']
        t_division = 'WTA' if '_wta' in t_key.lower() else 'ATP'
        
        # Upsert Tournament
        t_data = {
            "name": data['tournament'],
            "year": 2026,
            "division": t_division,
            "surface": data.get('surface', 'Unknown'),
            "external_id": t_key
        }
        
        # We need a way to handle UPSERT on a specific field via REST
        # Supabase uses 'on_conflict' in query params
        url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/tournaments?on_conflict=external_id"
        headers = {
            "apikey": os.environ.get("SUPABASE_KEY"),
            "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation"
        }
        
        try:
            response = requests.post(url, headers=headers, json=t_data)
            res = response.json()
            if not res or not isinstance(res, list) or len(res) == 0:
                print(f"Supabase tournament upsert failed. Response: {response.text}")
                return False
            t_id = res[0]['id']
        except Exception as e:
            print(f"Error upserting tournament to Supabase: {e}")
            return False
        
        # Group matches by round for processing
        matches_by_round = {}
        for m in data.get('matches', []):
            r_name = m.get('round', 'Unknown')
            if r_name not in matches_by_round:
                matches_by_round[r_name] = []
            matches_by_round[r_name].append(m)

        for r_name, round_matches in matches_by_round.items():
            # Round
            r_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/rounds?on_conflict=tournament_id,name"
            r_data = {"tournament_id": t_id, "name": r_name}
            res_r = requests.post(r_url, headers=headers, json=r_data).json()
            if not res_r or len(res_r) == 0: continue
            r_id = res_r[0]['id']
            
            match_payloads = []
            for m in round_matches:
                # Helper to format match_time robustly
                m_time = m.get('matchTime')
                if m_time and hasattr(m_time, 'isoformat'):
                    m_time = m_time.isoformat()
                
                # Winner logic based on extraction keys
                winner = None
                if m.get('underdogWon'):
                    winner = m.get('underdog')
                elif m.get('favoriteWon'):
                    winner = m.get('favorite')
                
                match_payloads.append({
                    "round_id": r_id,
                    "player_a": m['playerA'],
                    "player_b": m['playerB'],
                    "odds_a": m['oddsA'],
                    "odds_b": m['oddsB'],
                    "winner": winner,
                    "status": "finished",
                    "match_time": m_time,
                    "match_url": m['id'],
                    "external_id": m['id']
                })
            
            if match_payloads:
                m_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/matches?on_conflict=external_id"
                requests.post(m_url, headers=headers, json=match_payloads)
        
        print(f"Successfully saved {data['tournament']} to Supabase.")
        return True
    
    # If Supabase is not configured, fail
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scrape_tennis.py <tournament_key>")
        print(f"Available tournaments: {list(TOURNAMENT_URLS.keys())}")
        sys.exit(1)
    
    key = sys.argv[1]
    success = scrape_tournament(key)
    
    if success:
        # Load the JSON we just finished to save it to DB
        # Or refactor scrape_tournament to return data. 
        # For now, let's just read the file back
        try:
            with open(f"data/matches_{key}.json", "r") as f:
                 data = json.load(f)
                 save_to_db(data)
        except Exception as e:
            print(f"Failed to load/save JSON to DB: {e}")
            
    sys.exit(0 if success else 1)
