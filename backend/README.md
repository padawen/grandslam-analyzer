# Grand Slam Analyzer - Backend

FastAPI backend for analyzing tennis Grand Slam betting strategies.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables
Copy `.env.example` to `.env` and configure:
- `API_KEY`: Secret key for API authentication
- `DATABASE_URL`: PostgreSQL connection string (optional, uses SQLite if not set)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend URLs

## Run
```bash
python3 main.py
```

API will be available at `http://localhost:8000`
