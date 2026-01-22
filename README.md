# 🎾 Grand Slam Analyzer

Analyze tennis Grand Slam betting strategies with real match data and interactive visualizations.

## 🚀 Quick Start

```bash
# Start both backend and frontend
bash start.sh

# Or update the database with latest matches
bash update_db.sh
```

## 📁 Project Structure

- **`backend/`** - FastAPI server with web scraper
- **`frontend/`** - Vue 3 + Vite dashboard
- **`DEPLOY.md`** - Deployment guide (free tiers)
- **`SECURITY.md`** - Security review and recommendations

## 🔧 Setup

See individual README files in `backend/` and `frontend/` directories for detailed setup instructions.

## 📊 Features

- Real-time match data scraping from eredmenyek.com
- Underdog vs Favorite strategy comparison
- Interactive balance charts with match-by-match breakdown
- Support for both ATP and WTA divisions
- Automatic database updates via GitHub Actions

## 🔐 Security

- API key authentication
- Rate limiting (60 req/min per IP)
- CORS protection
- Environment-based configuration

## 📝 License

MIT
# Trigger Actions
