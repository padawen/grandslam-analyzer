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
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Return a dict of external_id -> has_winner_assigned
            # This allows the runner to decide if a match needs re-scraping
            matches = {item['external_id']: False for item in data if item.get('external_id')}
            
            # Now check which ones actually have a winner
            url_winners = f"{supabase_url}/rest/v1/matches?select=external_id,winner"
            winners_res = requests.get(url_winners, headers=headers, timeout=10)
            if winners_res.status_code == 200:
                for item in winners_res.json():
                    if item.get('external_id') and item.get('winner'):
                        matches[item['external_id']] = True
            
            print(f"  Found {len(matches)} matches already in Supabase ({sum(matches.values())} finished).")
            return matches
        else:
            print(f"  Warning: Could not fetch existing IDs: {response.text}")
            return {}
    except Exception as e:
        print(f"  Error fetching existing IDs: {e}")
        return {}


def is_tournament_finished(tournament_key):
    """Check if the tournament is completely finished (has a finished match in the Döntő/Final round).
       Returns True if finished, False otherwise or on error."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return False
        
    url = f"{supabase_url}/rest/v1/tournaments?external_id=eq.{tournament_key}&select=id,rounds(name,matches(winner,status))"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return False  # Tournament not even in DB yet
            
            t_data = data[0]
            rounds = t_data.get('rounds') or []
            
            for r in rounds:
                r_name = str(r.get('name', '')).lower()
                if 'döntő' in r_name or 'final' in r_name:
                    matches = r.get('matches') or []
                    for m in matches:
                        if m.get('winner') and m.get('status') == 'finished':
                            return True  # Found a finished final match!
                            
            return False
        else:
            print(f"  Warning: Could not check if tournament is finished: {response.text}")
            return False
    except Exception as e:
        print(f"  Error checking if tournament is finished: {e}")
        return False


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
    
    # Classify tournament category
    masters_keys = {'miami_atp', 'miami_wta', 'indian_wells_atp', 'indian_wells_wta'}
    t_category = 'masters' if t_key in masters_keys else 'grand_slam'
    
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
        "category": t_category,
        "surface": data.get('surface', 'Unknown'),
        "external_id": t_key
    }
    
    try:
        url = f"{supabase_url}/rest/v1/tournaments?on_conflict=external_id"
        response = requests.post(url, headers=headers, json=t_data, timeout=10)
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
        res_r = requests.post(r_url, headers=headers, json=r_data, timeout=10).json()
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
            print(f"  Uploading {len(match_payloads)} matches for round '{r_name}'...")
            m_url = f"{supabase_url}/rest/v1/matches?on_conflict=external_id"
            m_res = requests.post(m_url, headers=headers, json=match_payloads, timeout=10)
            if m_res.status_code not in [200, 201]:
                print(f"  Warning: Failed to upload matches for round '{r_name}': {m_res.text}")
            else:
                print(f"  ✓ Uploaded {len(match_payloads)} matches.")
    
    print(f"Successfully saved {data['tournament']} to Supabase.")
    return True
