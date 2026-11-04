"""Shared fixtures. Tests never touch the real database or the network."""

import sqlite3
from pathlib import Path

import pytest

from football_stats_agent.schema import CREATE_MATCHES, MATCHES_TABLE

# Invented values: only the column layout mirrors the real data.
_DEFAULT_STATS = {
    "ht_home_goals": 0,
    "ht_away_goals": 0,
    "home_shots": 10,
    "away_shots": 10,
    "home_shots_on_target": 4,
    "away_shots_on_target": 4,
    "home_fouls": 12,
    "away_fouls": 12,
    "home_corners": 5,
    "away_corners": 5,
    "home_yellow_cards": 2,
    "away_yellow_cards": 2,
    "home_red_cards": 0,
    "away_red_cards": 0,
}

SYNTHETIC_MATCHES = [
    {"season": "2024-2025", "match_date": "2024-08-16", "home_team": "Le Havre",
     "away_team": "Paris SG", "home_goals": 1, "away_goals": 4, "result": "A",
     "home_shots": 5, "away_shots": 14},
    {"season": "2024-2025", "match_date": "2024-08-17", "home_team": "Marseille",
     "away_team": "Lyon", "home_goals": 2, "away_goals": 2, "result": "D"},
    {"season": "2024-2025", "match_date": "2024-08-18", "home_team": "Lille",
     "away_team": "Nice", "home_goals": 3, "away_goals": 0, "result": "H",
     "home_red_cards": 1},
    {"season": "2025-2026", "match_date": "2025-08-15", "home_team": "Paris SG",
     "away_team": "Marseille", "home_goals": 0, "away_goals": 1, "result": "A"},
    {"season": "2025-2026", "match_date": "2025-08-16", "home_team": "Lyon",
     "away_team": "Lille", "home_goals": 2, "away_goals": 1, "result": "H",
     "home_corners": 9},
    {"season": "2025-2026", "match_date": "2025-08-17", "home_team": "Nice",
     "away_team": "Le Havre", "home_goals": 1, "away_goals": 1, "result": "D"},
]


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Path to a fresh SQLite database holding SYNTHETIC_MATCHES."""
    path = tmp_path / "football_test.db"
    rows = [{**_DEFAULT_STATS, **match} for match in SYNTHETIC_MATCHES]
    columns = list(rows[0])
    placeholders = ", ".join(f":{name}" for name in columns)
    conn = sqlite3.connect(path)
    try:
        with conn:
            conn.execute(CREATE_MATCHES)
            conn.executemany(
                f"INSERT INTO {MATCHES_TABLE} ({', '.join(columns)}) VALUES ({placeholders})",
                rows,
            )
    finally:
        conn.close()
    return path
