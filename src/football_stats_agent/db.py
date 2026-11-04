"""Database access. Every connection the agent uses is read-only."""

import sqlite3
from pathlib import Path

from football_stats_agent.security import install_guards


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open an existing SQLite database in read-only mode.

    Read-only is enforced by SQLite itself, so no query sent through this connection
    can modify the data, however it is worded. A missing file raises
    sqlite3.OperationalError instead of silently creating an empty database.
    """
    uri = f"{Path(db_path).resolve().as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def connect_for_tools(db_path: Path) -> sqlite3.Connection:
    """Read-only connection plus the security guards: the one every tool uses."""
    conn = connect_read_only(db_path)
    install_guards(conn)
    return conn
