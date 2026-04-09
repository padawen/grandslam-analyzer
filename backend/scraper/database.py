import os
import requests
import sys


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
            matches = {item['external_id']: False for item in data if item.get('external_id')}
            
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
                return False
            
            t_data = data[0]
            rounds = t_data.get('rounds') or []
            
            for r in rounds:
                r_name = str(r.get('name', '')).strip()
                r_name_lower = r_name.lower()
                is_final = r_name_lower in ('döntő', 'final', 'the final') or r_name_lower == 'final'
                if is_final:
                    matches = r.get('matches') or []
                    for m in matches:
                        if m.get('winner') and m.get('status') == 'finished':
                            return True
                            
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

    try:
        if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from config import get_category
        t_category = get_category(t_key)
    except Exception:
        t_category = 'masters'

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }
    
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
    
    matches_by_round = {}
    for m in data.get('matches', []):
        r_name = m.get('round', 'Unknown')
        if r_name not in matches_by_round:
            matches_by_round[r_name] = []
        matches_by_round[r_name].append(m)

    for r_name, round_matches in matches_by_round.items():
        r_url = f"{supabase_url}/rest/v1/rounds?on_conflict=tournament_id,name"
        r_data = {"tournament_id": t_id, "name": r_name}
        res_r = requests.post(r_url, headers=headers, json=r_data, timeout=10).json()
        if not res_r or len(res_r) == 0:
            continue
        r_id = res_r[0]['id']
        
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
                "status": "finished" if winner else "upcoming",
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
