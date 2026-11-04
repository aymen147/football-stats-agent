"""Example MCP client: starts the server as a subprocess and calls its tools over stdio.

Usage:
    uv run football-mcp-demo
"""

import asyncio
import json
import sys

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

SERVER = StdioServerParameters(
    command=sys.executable, args=["-m", "football_stats_agent.mcp_server"]
)


async def demo() -> None:
    async with Client(SERVER) as client:
        listing = await client.list_tools()
        print("tools:", ", ".join(tool.name for tool in listing.tools))

        stats = await client.call_tool("team_stats", {"team": "Lens", "season": "2025-2026"})
        print("team_stats(Lens, 2025-2026):")
        print(json.dumps(stats.structured_content, ensure_ascii=False, indent=2))

        refused = await client.call_tool("run_sql", {"query": "DELETE FROM matches"})
        print("run_sql(DELETE FROM matches) ->", "error:" if refused.is_error else "accepted:",
              refused.content[0].text)


def main() -> None:
    asyncio.run(demo())


if __name__ == "__main__":
    main()
