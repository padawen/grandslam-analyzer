from fastapi import FastAPI, HTTPException, Request, Depends
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Optional
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Grand Slam Analyzer API", root_path="/api")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

API_KEY = os.environ.get("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if API_KEY and api_key_header != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    return api_key_header

class Match(BaseModel):
    id: int
    round_name: str
    player_a: str
    player_b: str
    odds_a: Optional[float]
    odds_b: Optional[float]
    winner: Optional[str]
    status: str
    match_time: Optional[str]
    updated_at: Optional[str]
    surface: Optional[str]
    category: Optional[str]

async def supabase_request(method: str, endpoint: str, params: dict = None):
    """Make a request to Supabase REST API"""
    if not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    if method == "GET":
        response = await client.get(url, headers=headers, params=params)
    elif method == "POST":
        response = await client.post(url, headers=headers, json=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()

@app.get("/tournaments_list")
@limiter.limit("60/minute")
async def get_tournaments_list(
    request: Request,
    year: Optional[int] = None,
    division: Optional[str] = None,
    category: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """Get list of tournaments for the given filters"""
    params = {"select": "id,name,surface,category,division,year"}
    if year:
        params["year"] = f"eq.{year}"
    if division:
        params["division"] = f"eq.{division}"
    if category:
        params["category"] = f"eq.{category}"

    try:
        data = await supabase_request("GET", "tournaments", params)
        return data if data else []
    except Exception as e:
        print(f"Supabase error fetching tournaments: {e}")
        return []

@app.get("/matches", response_model=List[Match])
@limiter.limit("60/minute")
async def get_matches(
    request: Request,
    limit: int = 1000,
    year: Optional[int] = None,
    division: Optional[str] = None,
    category: Optional[str] = None,
    tournament_id: Optional[int] = None,
    api_key: str = Depends(get_api_key)
):
    """Get matches with optional filters"""

    select_query = "id,player_a,player_b,odds_a,odds_b,winner,status,match_time,updated_at,rounds!inner(name,tournaments!inner(id,name,year,division,surface,category))"
    params = {"select": select_query, "limit": limit}

    if tournament_id:
        params["rounds.tournaments.id"] = f"eq.{tournament_id}"
    else:
        if year:
            params["rounds.tournaments.year"] = f"eq.{year}"
        if division:
            params["rounds.tournaments.division"] = f"eq.{division}"
        if category:
            params["rounds.tournaments.category"] = f"eq.{category}"

    try:
        data = await supabase_request("GET", "matches", params)
        print("DEBUG DATA len:", len(data) if data else 0)

        if not data:
            return []

        matches = []
        for row in data:
            try:
                tournament = row["rounds"]["tournaments"] if row.get("rounds") and row["rounds"].get("tournaments") else {}
                matches.append({
                    "id": row["id"],
                    "round_name": row["rounds"]["name"] if row.get("rounds") else "Unknown",
                    "player_a": row["player_a"],
                    "player_b": row["player_b"],
                    "odds_a": row.get("odds_a"),
                    "odds_b": row.get("odds_b"),
                    "winner": row.get("winner"),
                    "status": row["status"],
                    "match_time": row.get("match_time"),
                    "updated_at": row.get("updated_at"),
                    "surface": tournament.get("surface", "Unknown"),
                    "category": tournament.get("category", "grand_slam"),
                })
            except (KeyError, TypeError) as e:
                print(f"Skipping malformed row: {e}")
                continue

        return matches
    except Exception as e:
        print(f"Supabase error: {e}")
        return []

@app.get("/divisions", response_model=List[str])
@limiter.limit("60/minute")
async def get_divisions(
    request: Request,
    year: Optional[int] = None,
    category: Optional[str] = None,
    tournament_id: Optional[int] = None,
    name: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """Get available divisions"""
    params = {"select": "division"}
    if year:
        params["year"] = f"eq.{year}"
    if category:
        params["category"] = f"eq.{category}"
    if tournament_id:
        params["id"] = f"eq.{tournament_id}"
    if name:
        params["name"] = f"eq.{name}"

    try:
        data = await supabase_request("GET", "tournaments", params)
        divisions = list(set([row["division"] for row in data]))
        divisions.sort(key=lambda x: (x != "ATP", x))
        return divisions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
@limiter.limit("60/minute")
async def get_categories(
    request: Request,
    year: Optional[int] = None,
    api_key: str = Depends(get_api_key)
):
    """Get available tournament categories (grand_slam, masters) for a given year"""
    params = {"select": "category"}
    if year:
        params["year"] = f"eq.{year}"

    try:
        data = await supabase_request("GET", "tournaments", params)
        categories = list(set([row["category"] for row in data if row.get("category")]))
        if not categories:
            categories = ["grand_slam"]
        return categories
    except Exception as e:
        return ["grand_slam"]

@app.get("/years")
@limiter.limit("60/minute")
async def get_years(request: Request, api_key: str = Depends(get_api_key)):
    """Get available years"""
    params = {"select": "year", "order": "year.desc"}

    try:
        data = await supabase_request("GET", "tournaments", params)
        years = list(set([row["year"] for row in data]))
        return sorted(years, reverse=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "database": "supabase"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
