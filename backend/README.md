# Backend

Python backend with scraper and FastAPI.

## Structure

```
backend/
├── scraper/           # Modular scraper package
│   ├── config.py      # Tournament URLs
│   ├── driver.py      # Selenium WebDriver setup
│   ├── links.py       # Match link extraction
│   ├── extractor.py   # Match data extraction
│   ├── database.py    # Supabase operations
│   └── run.py         # Main orchestrator
├── main.py            # FastAPI server
└── schema.sql         # Database schema
```

## Running the Scraper

```bash
# Set environment variables
export SUPABASE_URL="your-url"
export SUPABASE_KEY="your-key"
export TOURNAMENT_URLS_JSON='{"australian_open": "https://..."}'

# Run scraper
python -m scraper.run australian_open
```

## Running the API

```bash
pip install -r requirements.txt
python main.py
```

API runs on http://localhost:8000
