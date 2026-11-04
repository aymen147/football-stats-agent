"""The tool set shared by the LangGraph agent and the MCP server.

Each function closes over the database and chart paths, so neither the LLM nor an MCP
client can choose a file path. The docstrings are the descriptions the model reads.
"""

import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

from football_stats_agent import tools
from football_stats_agent.security import sanitize

# Expected failures (refused or invalid query, unknown team...): their message is shown to
# the model or MCP client so it can correct the call. Any other exception is a bug.
RECOVERABLE_ERRORS: tuple[type[Exception], ...] = (sqlite3.Error, ValueError)


def bind_tools(db_path: Path, charts_dir: Path) -> list[Callable[..., Any]]:
    def run_sql(query: str) -> dict[str, Any]:
        """Run one read-only SQL query on the `matches` table. Returns columns and at
        most 50 rows; if `truncated` is true, refine the query (WHERE, GROUP BY, LIMIT)."""
        return sanitize(tools.run_sql(query, db_path))

    def team_stats(team: str, season: str | None = None) -> dict[str, Any]:
        """Summary for one team: played, wins, draws, losses, points, goals for and
        against, average shots, cards. `season` like '2024-2025'; omit it for all seasons."""
        return sanitize(tools.team_stats(team, db_path, season))

    def make_chart(
        title: str, labels: list[str], values: list[float], kind: str = "bar"
    ) -> dict[str, str]:
        """Draw a 'bar' or 'line' chart (1 to 30 points) and return the PNG path."""
        return tools.make_chart(title, labels, values, charts_dir, kind)

    return [run_sql, team_stats, make_chart]
