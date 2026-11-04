"""Project paths and data settings."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "football.db"
CHARTS_DIR = PROJECT_ROOT / "charts"

# football-data.co.uk season code -> season label stored in the database
SEASONS = {
    "2324": "2023-2024",
    "2425": "2024-2025",
    "2526": "2025-2026",
}
LIGUE_1_CSV_URL = "https://www.football-data.co.uk/mmz4281/{code}/F1.csv"
