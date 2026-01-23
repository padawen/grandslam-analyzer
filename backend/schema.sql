-- Database Schema for Grand Slam Analyzer

-- 1. Tournaments Table
CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    surface VARCHAR(50),
    division VARCHAR(10) DEFAULT 'ATP', -- 'ATP' or 'WTA'
    external_id VARCHAR(100) UNIQUE, -- ID from the scraper (tournament key)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, year, division)
);

-- 2. Rounds Table
-- Normalized rounds to avoid repeating string data and allow proper sorting
CREATE TABLE IF NOT EXISTS rounds (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL, -- e.g., "1/64 Final", "Final"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, name)
);

-- 3. Matches Table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    round_id INTEGER REFERENCES rounds(id) ON DELETE CASCADE,
    
    player_a VARCHAR(100) NOT NULL,
    player_b VARCHAR(100) NOT NULL,
    
    odds_a NUMERIC(5, 2), -- e.g., 1.55
    odds_b NUMERIC(5, 2),
    
    winner VARCHAR(100), -- Winner player name or NULL if not finished
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'finished', 'live'
    
    match_time TIMESTAMP, -- When the match was played
    match_url TEXT, -- Full URL to the match page
    external_id VARCHAR(100) UNIQUE, -- ID from the scraper (URL or ID)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_matches_round_id ON matches(round_id);
CREATE INDEX IF NOT EXISTS idx_matches_match_time ON matches(match_time);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS idx_rounds_tournament_id ON rounds(tournament_id);
CREATE INDEX IF NOT EXISTS idx_tournaments_year_division ON tournaments(year, division);
