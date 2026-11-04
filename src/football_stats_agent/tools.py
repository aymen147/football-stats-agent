"""Tools the agent can call. Each one returns plain, JSON-serialisable data."""

import re
from pathlib import Path
from typing import Any

import pandas as pd
from matplotlib.figure import Figure

from football_stats_agent.db import connect_read_only

DEFAULT_MAX_ROWS = 50
MAX_CHART_POINTS = 30
CHART_KINDS = ("bar", "line")


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


def team_stats(team: str, db_path: Path, season: str | None = None) -> dict[str, Any]:
    """Season summary for one team: record, points, goals, shots and cards.

    `team` must match the database spelling (e.g. 'Paris SG'). `season` looks like
    '2024-2025'; leave it empty to cover every season. Unknown names raise a
    ValueError that lists the valid teams and seasons.
    """
    query = "SELECT * FROM matches WHERE (home_team = ? OR away_team = ?)"
    params: list[str] = [team, team]
    if season:
        query += " AND season = ?"
        params.append(season)
    conn = connect_read_only(db_path)
    try:
        games = pd.read_sql_query(query, conn, params=params)
        if games.empty:
            teams = [row[0] for row in conn.execute(
                "SELECT DISTINCT home_team FROM matches ORDER BY home_team")]
            seasons = [row[0] for row in conn.execute(
                "SELECT DISTINCT season FROM matches ORDER BY season")]
            raise ValueError(
                f"No matches for team {team!r} in season {season or 'any'}. "
                f"Valid teams: {', '.join(teams)}. Valid seasons: {', '.join(seasons)}."
            )
    finally:
        conn.close()

    # Turn home/away columns into the team's own point of view.
    at_home = games["home_team"] == team
    goals_for = games["home_goals"].where(at_home, games["away_goals"])
    goals_against = games["away_goals"].where(at_home, games["home_goals"])
    shots = games["home_shots"].where(at_home, games["away_shots"])
    on_target = games["home_shots_on_target"].where(at_home, games["away_shots_on_target"])
    yellows = games["home_yellow_cards"].where(at_home, games["away_yellow_cards"])
    reds = games["home_red_cards"].where(at_home, games["away_red_cards"])

    wins = int((goals_for > goals_against).sum())
    draws = int((goals_for == goals_against).sum())
    return {
        "team": team,
        "season": season or "all",
        "played": len(games),
        "wins": wins,
        "draws": draws,
        "losses": len(games) - wins - draws,
        "points": 3 * wins + draws,
        "goals_for": int(goals_for.sum()),
        "goals_against": int(goals_against.sum()),
        "avg_shots": round(float(shots.mean()), 2),
        "avg_shots_on_target": round(float(on_target.mean()), 2),
        "yellow_cards": int(yellows.sum()),
        "red_cards": int(reds.sum()),
    }


def make_chart(
    title: str,
    labels: list[str],
    values: list[float],
    output_dir: Path,
    kind: str = "bar",
) -> dict[str, str]:
    """Draw a bar or line chart and save it as a PNG file.

    `labels` and `values` must have the same length (1 to 30 points). Returns the
    path of the saved image.
    """
    if kind not in CHART_KINDS:
        raise ValueError(f"kind must be one of {CHART_KINDS}")
    if not 1 <= len(labels) <= MAX_CHART_POINTS:
        raise ValueError(f"a chart needs between 1 and {MAX_CHART_POINTS} points")
    if len(labels) != len(values):
        raise ValueError("labels and values must have the same length")

    # The title comes from the LLM: keep only safe characters so it can never
    # point the file outside output_dir (e.g. '../../somewhere').
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "chart"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{slug}.png"

    figure = Figure(figsize=(8, 4.5), layout="constrained")
    axes = figure.subplots()
    if kind == "bar":
        axes.bar(labels, values)
    else:
        axes.plot(labels, values, marker="o")
    axes.set_title(title)
    axes.tick_params(axis="x", labelrotation=45)
    figure.savefig(path, dpi=120)
    return {"path": str(path)}
