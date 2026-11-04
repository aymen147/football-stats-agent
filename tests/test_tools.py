"""Tests for the read-only connection and the run_sql tool."""

import sqlite3

import pytest
from conftest import SYNTHETIC_MATCHES

from football_stats_agent.db import connect_read_only
from football_stats_agent.tools import run_sql


def test_run_sql_returns_columns_and_rows(db_path):
    result = run_sql(
        "SELECT home_team, home_goals FROM matches "
        "WHERE season = '2025-2026' ORDER BY match_date LIMIT 2",
        db_path,
    )

    assert result == {
        "columns": ["home_team", "home_goals"],
        "rows": [["Paris SG", 0], ["Lyon", 2]],
        "row_count": 2,
        "truncated": False,
    }


@pytest.mark.parametrize(
    "statement",
    [
        "DELETE FROM matches",
        "UPDATE matches SET home_goals = 99",
        "INSERT INTO matches (season, match_date, home_team, away_team, home_goals, "
        "away_goals, result) VALUES ('x', 'x', 'x', 'x', 0, 0, 'D')",
        "DROP TABLE matches",
        "CREATE TABLE stolen (secret TEXT)",
    ],
)
def test_run_sql_cannot_modify_the_database(db_path, statement):
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        run_sql(statement, db_path)

    count = run_sql("SELECT COUNT(*) FROM matches", db_path)
    assert count["rows"] == [[len(SYNTHETIC_MATCHES)]]


def test_run_sql_truncates_long_results(db_path):
    result = run_sql("SELECT id FROM matches", db_path, max_rows=2)

    assert result["row_count"] == 2
    assert result["truncated"] is True


def test_run_sql_is_not_truncated_at_the_exact_limit(db_path):
    result = run_sql("SELECT id FROM matches", db_path, max_rows=len(SYNTHETIC_MATCHES))

    assert result["row_count"] == len(SYNTHETIC_MATCHES)
    assert result["truncated"] is False


def test_run_sql_rejects_a_non_positive_row_limit(db_path):
    with pytest.raises(ValueError):
        run_sql("SELECT id FROM matches", db_path, max_rows=0)


def test_connect_read_only_does_not_create_a_missing_file(tmp_path):
    missing = tmp_path / "missing.db"

    with pytest.raises(sqlite3.OperationalError):
        connect_read_only(missing)

    assert not missing.exists()


@pytest.mark.xfail(
    strict=True,
    reason="mode=ro does not stop ATTACH from creating a file; the phase 4 authorizer will",
)
def test_run_sql_cannot_create_files_with_attach(db_path, tmp_path):
    target = tmp_path / "attached.db"

    with pytest.raises(sqlite3.DatabaseError):
        run_sql(f"ATTACH DATABASE '{target}' AS other", db_path)

    assert not target.exists()
