# Backend

Python scraper with modular architecture. Scrapes tennis match data and uploads directly to Supabase.

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

## Running the Scraper (GitHub Actions)

The scraper runs automatically via GitHub Actions (2x daily). It uploads directly to Supabase without creating local files.

## Running the API

```bash
pip install -r requirements.txt
python main.py
```

API runs on http://localhost:8000
