"""Functions for fetching match links from tournament pages."""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def accept_cookies(driver):
    """Accept cookie consent if present."""
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
    """Detect tournament surface from the header."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".headerLeague__title, .event__header"))
        )
        
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, ".headerLeague__title")
            text = f"{title_elem.get_attribute('title')} {title_elem.text}".lower()
        except NoSuchElementException:
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
    """Extract match links from tournament page, skipping qualification rounds."""
    try:
        driver.get(base_url)
        accept_cookies(driver)
        
        surface = get_tournament_surface(driver)
        print(f"  Detected Surface: {surface}")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sportName.tennis"))
        )
        
        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Click "Show more matches"
        try:
            more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'További meccsek')] | //span[contains(text(), 'További meccsek')]"))
            )
            print("  Found 'További meccsek' button, clicking...")
            driver.execute_script("arguments[0].scrollIntoView(true);", more_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", more_btn)
            time.sleep(5)
            print("  Loaded more matches.")
        except TimeoutException:
            try:
                more_btn = driver.find_element(By.CSS_SELECTOR, ".event__more")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(5)
            except:
                print("  No 'Show more matches' button found.")
        except Exception as e:
            print(f"  Error clicking show more: {e}")

        container = driver.find_element(By.CSS_SELECTOR, ".sportName.tennis")
        elements = container.find_elements(By.XPATH, "./*")
        
        match_links = []
        is_qualification = False
        
        print(f"  Scanning {len(elements)} list items for valid matches...")
        
        for elem in elements:
            class_name = elem.get_attribute("class")
            text = elem.text.replace("\n", " ").strip()
            
            if "event__header" in class_name:
                if "Selejtező" in text or "Qualifying" in text:
                    is_qualification = True
                else:
                    is_qualification = False
            
            elif "header" in class_name or "title" in class_name.lower():
                if "Selejtező" in text or "Qualifying" in text:
                    is_qualification = True

            elif "event__match" in class_name:
                lower_text = text.lower()
                if "törölt" in lower_text or "elmaradt" in lower_text:
                    continue

                if not is_qualification:
                    try:
                        link_el = elem.find_element(By.CSS_SELECTOR, "a.eventRowLink") 
                        href = link_el.get_attribute('href')
                        if href:
                            match_links.append(href)
                    except NoSuchElementException:
                        pass
        
        match_links = list(dict.fromkeys(match_links))
        return match_links, surface
        
    except Exception as e:
        print(f"Error getting match links: {e}")
        return [], "Unknown"
