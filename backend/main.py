from fastapi import FastAPI, HTTPException, Request, Depends
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Optional
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import httpx
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://fnrfsdgtkuieypwenqcy.supabase.com")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Grand Slam Analyzer API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# API Key authentication
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
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()

@app.get("/matches", response_model=List[Match])
@limiter.limit("60/minute")
async def get_matches(
    request: Request,
    limit: int = 1000,
    year: Optional[int] = None,
    division: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """Get matches with optional filters"""
    
    # Build query
    select_query = "id,player_a,player_b,odds_a,odds_b,winner,status,match_time,updated_at,rounds!inner(name,tournaments!inner(year,division,surface))"
    params = {"select": select_query, "limit": limit}
    
    # Add filters as separate query params (PostgREST nested resource syntax)
    if year:
        params["rounds.tournaments.year"] = f"eq.{year}"
    if division:
        params["rounds.tournaments.division"] = f"eq.{division}"
    
    try:
        data = await supabase_request("GET", "matches", params)
        print("DEBUG DATA[0]:", data[0] if data else "No data")
        
        if not data:
            return []
            
        # Transform response
        matches = []
        for row in data:
            try:
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
                    "surface": row["rounds"]["tournaments"].get("surface") if row.get("rounds") and row["rounds"].get("tournaments") else "Unknown"
                })
            except (KeyError, TypeError) as e:
                print(f"Skipping malformed row: {e}")
                continue
        
        return matches
    except Exception as e:
        print(f"Supabase error: {e}")
        return [] # Return empty list instead of 500


@app.get("/divisions")
@limiter.limit("60/minute")
async def get_divisions(
    request: Request,
    year: Optional[int] = None,
    api_key: str = Depends(get_api_key)
):
    """Get available divisions"""
    params = {"select": "division"}
    if year:
        params["year"] = f"eq.{year}"
    
    try:
        data = await supabase_request("GET", "tournaments", params)
        divisions = list(set([row["division"] for row in data]))
        return divisions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
