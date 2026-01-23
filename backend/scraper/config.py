"""Configuration for the scraper."""
import os
import json

# Try to load from local config.py first (for local development)
TOURNAMENT_URLS = {}

try:
    from config import TOURNAMENT_URLS as LOCAL_URLS
    TOURNAMENT_URLS.update(LOCAL_URLS)
except ImportError:
    pass

# Override/extend with environment variable (for CI/CD)
urls_json = os.environ.get("TOURNAMENT_URLS_JSON")
if urls_json:
    try:
        TOURNAMENT_URLS.update(json.loads(urls_json))
    except Exception as e:
        print(f"Error parsing TOURNAMENT_URLS_JSON: {e}")

if not TOURNAMENT_URLS:
    print("Error: No tournament URLs found. Please set TOURNAMENT_URLS_JSON secret or create local config.py.")
