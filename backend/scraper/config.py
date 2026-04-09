import os
import json
from dotenv import load_dotenv

load_dotenv()

urls_json = os.environ.get("TOURNAMENT_URLS_JSON")
TOURNAMENT_URLS = {}

if urls_json:
    try:
        TOURNAMENT_URLS = json.loads(urls_json)
    except Exception as e:
        print(f"Error parsing TOURNAMENT_URLS_JSON: {e}")

if not TOURNAMENT_URLS:
    print("Error: No tournament URLs found. Please set TOURNAMENT_URLS_JSON in your .env or GitHub Actions secrets.")
