"""Sanity checks on the synthetic test database itself."""

import sqlite3

from conftest import SYNTHETIC_MATCHES


def test_synthetic_db_holds_every_match(db_path):
    conn = sqlite3.connect(db_path)
    try:
        (count,) = conn.execute("SELECT COUNT(*) FROM matches").fetchone()
    finally:
        conn.close()
    assert count == len(SYNTHETIC_MATCHES)
