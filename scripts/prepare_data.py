"""Download the Ligue 1 CSVs from football-data.co.uk and build data/football.db.

Usage:
    uv run python scripts/prepare_data.py [--force-download]
"""

import argparse
import sqlite3
import urllib.request
from pathlib import Path

import pandas as pd

from football_stats_agent.config import DB_PATH, LIGUE_1_CSV_URL, RAW_DIR, SEASONS
from football_stats_agent.schema import CREATE_MATCHES, CSV_TO_DB_COLUMNS, MATCHES_TABLE


def download(force: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for code in SEASONS:
        target = RAW_DIR / f"F1_{code}.csv"
        if target.exists() and not force:
            print(f"skip   {target.name} (already downloaded)")
            continue
        urllib.request.urlretrieve(LIGUE_1_CSV_URL.format(code=code), target)
        print(f"fetch  {target.name}")


def load_season(csv_path: Path, season: str) -> pd.DataFrame:
    # utf-8-sig strips the byte-order mark at the start of the files
    frame = pd.read_csv(csv_path, encoding="utf-8-sig", usecols=list(CSV_TO_DB_COLUMNS))
    frame = frame.rename(columns=CSV_TO_DB_COLUMNS)
    frame["match_date"] = pd.to_datetime(frame["match_date"], format="%d/%m/%Y").dt.strftime(
        "%Y-%m-%d"
    )
    frame.insert(0, "season", season)
    return frame


def build_database(db_path: Path = DB_PATH) -> int:
    matches = pd.concat(
        [load_season(RAW_DIR / f"F1_{code}.csv", label) for code, label in SEASONS.items()],
        ignore_index=True,
    )
    db_path.unlink(missing_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.execute(CREATE_MATCHES)
            matches.to_sql(MATCHES_TABLE, conn, if_exists="append", index=False)
    finally:
        conn.close()
    return len(matches)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()
    download(force=args.force_download)
    count = build_database()
    print(f"built  {DB_PATH} ({count} matches)")


if __name__ == "__main__":
    main()
