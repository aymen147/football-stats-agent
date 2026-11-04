"""Tools the agent can call. Each one returns plain, JSON-serialisable data."""

from pathlib import Path
from typing import Any

from football_stats_agent.db import connect_read_only

DEFAULT_MAX_ROWS = 50


def run_sql(query: str, db_path: Path, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Run one SQL query on the Ligue 1 database and return the result as a table.

    The connection is read-only: a query that tries to modify the data fails.
    At most `max_rows` rows are returned. `truncated` is True when the query produced
    more rows than that; narrow the query with filters, aggregates or LIMIT.
    """
    if max_rows < 1:
        raise ValueError("max_rows must be at least 1")
    conn = connect_read_only(db_path)
    try:
        cursor = conn.execute(query)
        columns = [column[0] for column in cursor.description or []]
        # One extra row tells us whether the result was cut, without loading it all.
        fetched = cursor.fetchmany(max_rows + 1)
    finally:
        conn.close()
    rows = [list(row) for row in fetched[:max_rows]]
    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": len(fetched) > max_rows,
    }
