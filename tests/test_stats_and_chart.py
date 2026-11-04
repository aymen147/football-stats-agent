"""Tests for the team_stats and make_chart tools."""

from pathlib import Path

import pytest

from football_stats_agent.tools import make_chart, team_stats

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def test_team_stats_combines_home_and_away_games(db_path):
    # Synthetic data: Marseille 2-2 Lyon (away draw), Lyon 2-1 Lille (home win).
    stats = team_stats("Lyon", db_path)

    assert stats == {
        "team": "Lyon",
        "season": "all",
        "played": 2,
        "wins": 1,
        "draws": 1,
        "losses": 0,
        "points": 4,
        "goals_for": 4,
        "goals_against": 3,
        "avg_shots": 10.0,
        "avg_shots_on_target": 4.0,
        "yellow_cards": 4,
        "red_cards": 0,
    }


def test_team_stats_filters_by_season_and_reads_away_columns(db_path):
    # Synthetic data: Le Havre 1-4 Paris SG, with 14 away shots.
    stats = team_stats("Paris SG", db_path, season="2024-2025")

    assert stats["played"] == 1
    assert stats["wins"] == 1
    assert stats["goals_for"] == 4
    assert stats["avg_shots"] == 14.0


def test_team_stats_lists_valid_names_for_an_unknown_team(db_path):
    with pytest.raises(ValueError, match="Valid teams: .*Paris SG"):
        team_stats("PSG", db_path)


def test_make_chart_saves_a_png(tmp_path):
    result = make_chart("Wins per team", ["Lens", "Lyon"], [14, 12], tmp_path)

    path = Path(result["path"])
    assert path.parent == tmp_path
    assert path.read_bytes().startswith(PNG_SIGNATURE)


def test_make_chart_title_cannot_escape_the_output_folder(tmp_path):
    result = make_chart("../../outside/evil", ["a"], [1], tmp_path)

    assert Path(result["path"]).parent == tmp_path


@pytest.mark.parametrize(
    ("labels", "values", "kind"),
    [
        (["a", "b"], [1], "bar"),
        ([], [], "bar"),
        (["a"] * 31, [1] * 31, "bar"),
        (["a"], [1], "pie"),
    ],
)
def test_make_chart_rejects_invalid_input(tmp_path, labels, values, kind):
    with pytest.raises(ValueError):
        make_chart("chart", labels, values, tmp_path, kind=kind)
