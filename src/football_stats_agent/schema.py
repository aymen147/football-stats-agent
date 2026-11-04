"""SQLite schema, shared by the data build script and the test fixtures."""

MATCHES_TABLE = "matches"

# football-data.co.uk CSV column -> database column.
# The CSV short names (HS, AS, ...) are renamed: AS is an SQL keyword, and
# readable names make it easier for the LLM to write correct queries.
CSV_TO_DB_COLUMNS = {
    "Date": "match_date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
    "HTHG": "ht_home_goals",
    "HTAG": "ht_away_goals",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",
    "HF": "home_fouls",
    "AF": "away_fouls",
    "HC": "home_corners",
    "AC": "away_corners",
    "HY": "home_yellow_cards",
    "AY": "away_yellow_cards",
    "HR": "home_red_cards",
    "AR": "away_red_cards",
}

CREATE_MATCHES = f"""
CREATE TABLE {MATCHES_TABLE} (
    id INTEGER PRIMARY KEY,
    season TEXT NOT NULL,                 -- e.g. '2024-2025'
    match_date TEXT NOT NULL,             -- ISO 8601, e.g. '2024-08-16'
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_goals INTEGER NOT NULL,          -- full time
    away_goals INTEGER NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('H', 'D', 'A')),  -- home win, draw, away win
    ht_home_goals INTEGER,                -- half time
    ht_away_goals INTEGER,
    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,
    home_fouls INTEGER,
    away_fouls INTEGER,
    home_corners INTEGER,
    away_corners INTEGER,
    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,
    home_red_cards INTEGER,
    away_red_cards INTEGER
)
"""
