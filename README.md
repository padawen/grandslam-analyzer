# Grand Slam Analyzer

A tennis betting analytics tool that scrapes match data from eredmenyek.com and calculates ROI for underdog betting strategies.

## Project Structure

```
grandslam-analyzer/
├── frontend/          # Vue.js dashboard
├── backend/           # Python scraper + FastAPI
└── .github/workflows/ # Automated scraping via GitHub Actions
```

## Live Demo

- **Frontend**: Deployed on Vercel
- **Database**: Supabase (PostgreSQL)
- **Scraper**: Runs automatically via GitHub Actions (2x daily)

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend API
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Environment Variables

Set in GitHub Secrets for automated scraping:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key
- `TOURNAMENT_URLS_JSON` - JSON with tournament URLs
