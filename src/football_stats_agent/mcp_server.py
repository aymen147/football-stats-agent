"""MCP server exposing the agent's tools to any MCP client, over stdio.

Usage:
    uv run football-mcp-server
"""

import functools
from collections.abc import Callable
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from football_stats_agent.config import CHARTS_DIR, DB_PATH
from football_stats_agent.toolset import RECOVERABLE_ERRORS, bind_tools

INSTRUCTIONS = (
    "Read-only statistics on French Ligue 1 matches, seasons 2023-2024 to 2025-2026. "
    "Team names use the database spelling, e.g. 'Paris SG'."
)


def _report_expected_errors(function: Callable[..., Any]) -> Callable[..., Any]:
    """MCPServer hides the message of unexpected exceptions from clients. ToolError is
    forwarded, so the client learns why a call was refused (e.g. read-only database)."""

    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return function(*args, **kwargs)
        except RECOVERABLE_ERRORS as error:
            raise ToolError(str(error)) from error

    return wrapper


def build_server(db_path: Path = DB_PATH, charts_dir: Path = CHARTS_DIR) -> MCPServer:
    server = MCPServer(name="football-stats", instructions=INSTRUCTIONS)
    for function in bind_tools(db_path, charts_dir):
        server.tool()(_report_expected_errors(function))
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()
