"""Database operations for Supabase REST API."""
import os
import requests


def get_existing_match_ids_from_supabase():
    """Fetch all external_ids from Supabase to skip already processed matches."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Supabase not configured, cannot fetch existing IDs.")
        return set()
    
    url = f"{supabase_url}/rest/v1/matches?select=external_id"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            ids = {item['external_id'] for item in data if item.get('external_id')}
            print(f"  Found {len(ids)} matches already in Supabase (will be skipped).")
            return ids
        else:
            print(f"  Warning: Could not fetch existing IDs: {response.text}")
            return set()
    except Exception as e:
        print(f"  Error fetching existing IDs: {e}")
        return set()


def save_to_db(data):
    """Save scraped data to Supabase via REST API."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set.")
        return False
    
    print("Saving to Supabase REST API...")
    
    t_key = data['tournament_key']
    t_division = 'WTA' if '_wta' in t_key.lower() else 'ATP'
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }
    
    # Upsert Tournament
    t_data = {
        "name": data['tournament'],
        "year": 2026,
        "division": t_division,
        "surface": data.get('surface', 'Unknown'),
        "external_id": t_key
    }
    
    try:
        url = f"{supabase_url}/rest/v1/tournaments?on_conflict=external_id"
        response = requests.post(url, headers=headers, json=t_data)
        res = response.json()
        if not res or not isinstance(res, list) or len(res) == 0:
            print(f"Supabase tournament upsert failed: {response.text}")
            return False
        t_id = res[0]['id']
    except Exception as e:
        print(f"Error upserting tournament: {e}")
        return False
    
    # Group matches by round
    matches_by_round = {}
    for m in data.get('matches', []):
        r_name = m.get('round', 'Unknown')
        if r_name not in matches_by_round:
            matches_by_round[r_name] = []
        matches_by_round[r_name].append(m)

    for r_name, round_matches in matches_by_round.items():
        # Upsert Round
        r_url = f"{supabase_url}/rest/v1/rounds?on_conflict=tournament_id,name"
        r_data = {"tournament_id": t_id, "name": r_name}
        res_r = requests.post(r_url, headers=headers, json=r_data).json()
        if not res_r or len(res_r) == 0:
            continue
        r_id = res_r[0]['id']
        
        # Build match payloads
        match_payloads = []
        for m in round_matches:
            m_time = m.get('matchTime')
            if m_time and hasattr(m_time, 'isoformat'):
                m_time = m_time.isoformat()
            
            winner = None
            if m.get('underdogWon'):
                winner = m.get('underdog')
            elif m.get('favoriteWon'):
                winner = m.get('favorite')
            
            match_payloads.append({
                "round_id": r_id,
                "player_a": m['playerA'],
                "player_b": m['playerB'],
                "odds_a": m['oddsA'],
                "odds_b": m['oddsB'],
                "winner": winner,
                "status": "finished",
                "match_time": m_time,
                "match_url": m['id'],
                "external_id": m['id']
            })
        
        if match_payloads:
            m_url = f"{supabase_url}/rest/v1/matches?on_conflict=external_id"
            requests.post(m_url, headers=headers, json=match_payloads)
    
    print(f"Successfully saved {data['tournament']} to Supabase.")
    return True
