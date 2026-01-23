"""Functions for extracting match data from individual match pages."""
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException
)


def extract_match_data(driver, match_url):
    """Extract match data from individual match page with retries for stability."""
    for attempt in range(2):
        try:
            driver.get(match_url)
            time.sleep(1)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".participant__participantNameWrapper"))
            )
            
            player_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".participant__participantNameWrapper"))
            )
            
            if len(player_elements) < 2:
                print(f"  Warning: Less than 2 players found at {match_url}")
                return None
            
            player_a = player_elements[0].text.strip()
            player_b = player_elements[1].text.strip()
            
            # Check for Walkover
            is_walkover = False
            winner_index = -1
            
            if "Továbbjutó" in player_a:
                is_walkover = True
                winner_index = 0
                player_a = player_a.replace("Továbbjutó", "").strip(" -()")
            elif "Továbbjutó" in player_b:
                is_walkover = True
                winner_index = 1
                player_b = player_b.replace("Továbbjutó", "").strip(" -()")
            
            # Extract round from breadcrumb
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
                return None

            # Extract match time
            match_time = None
            try:
                time_elem = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__startTime")
                time_text = time_elem.text.strip()
                if time_text:
                    match_time = datetime.strptime(time_text, "%d.%m.%Y %H:%M")
            except (NoSuchElementException, ValueError):
                pass

            odds_a = 1.0
            odds_b = 1.0
            player_a_won = False
            player_b_won = False
            
            if is_walkover:
                print(f"  Walkover detected: {player_a} vs {player_b}")
                if winner_index == 0:
                    player_a_won = True
                else:
                    player_b_won = True
            else:
                # Try to get odds from TippmixPro
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
                
                # Fallback winner detection
                if not player_a_won and not player_b_won:
                    try:
                        home = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__home")
                        if "duelParticipant--winner" in home.get_attribute("class"):
                            player_a_won = True
                        away = driver.find_element(By.CSS_SELECTOR, ".duelParticipant__away")
                        if "duelParticipant--winner" in away.get_attribute("class"):
                            player_b_won = True
                    except NoSuchElementException:
                        pass

                if not is_walkover and odds_a == 1.0 and odds_b == 1.0 and not player_a_won and not player_b_won:
                    return None

            # Determine underdog/favorite
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
                print(f"  Stale element detected, retrying...")
                continue
            return None
        except TimeoutException:
            print(f"  Timeout processing {match_url}")
            return None
        except NoSuchElementException:
            return None
        except Exception as e:
            if attempt == 0:
                print(f"  Error, retrying...")
                continue
            print(f"  Error extracting match data: {e}")
            return None
    
    return None
