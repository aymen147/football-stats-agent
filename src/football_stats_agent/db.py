"""Database access. Every connection the agent uses is read-only."""

import sqlite3
from pathlib import Path


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open an existing SQLite database in read-only mode.

    Read-only is enforced by SQLite itself, so no query sent through this connection
    can modify the data, however it is worded. A missing file raises
    sqlite3.OperationalError instead of silently creating an empty database.
    """
    uri = f"{Path(db_path).resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)
