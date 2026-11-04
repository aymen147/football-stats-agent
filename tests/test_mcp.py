"""MCP server tests, with the client connected in-process (no subprocess, no network)."""

import asyncio
from typing import Any

from conftest import SYNTHETIC_MATCHES
from mcp.client import Client

from football_stats_agent.mcp_server import build_server
from football_stats_agent.tools import run_sql


def call(server: Any, name: str, arguments: dict[str, Any]) -> Any:
    async def _call() -> Any:
        async with Client(server) as client:
            return await client.call_tool(name, arguments)

    return asyncio.run(_call())


def test_server_lists_the_same_three_tools_as_the_agent(db_path, tmp_path):
    async def _list() -> list[str]:
        async with Client(build_server(db_path, tmp_path)) as client:
            return sorted(tool.name for tool in (await client.list_tools()).tools)

    assert asyncio.run(_list()) == ["make_chart", "run_sql", "team_stats"]


def test_server_returns_structured_results(db_path, tmp_path):
    result = call(build_server(db_path, tmp_path), "team_stats", {"team": "Lyon"})

    assert not result.is_error
    assert result.structured_content["points"] == 4


def test_server_reports_a_refused_write_as_a_tool_error(db_path, tmp_path):
    result = call(build_server(db_path, tmp_path), "run_sql", {"query": "DELETE FROM matches"})

    assert result.is_error
    assert "readonly" in result.content[0].text
    assert run_sql("SELECT COUNT(*) FROM matches", db_path)["rows"] == [[len(SYNTHETIC_MATCHES)]]
