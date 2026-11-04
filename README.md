# football-stats-agent

An agent that answers natural-language questions about Ligue 1 match statistics.
A LangGraph graph lets an LLM (Groq) choose between three tools: a read-only SQL query
tool, a statistics tool and a chart tool. The same tools are exposed through an MCP
server, and a security layer guards them against prompt injection.

> **Status: work in progress.** Sections marked _TODO_ are filled in as each part is built
> and tested. Nothing below claims more than the code in this repository does.

## What is real and what is not

_TODO: filled in at the end, from the code and the test results only._

## Security evaluation

_TODO: table of the prompt-injection test set — attacks tried, attacks blocked._

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python scripts/prepare_data.py   # downloads 3 Ligue 1 seasons, builds data/football.db
uv run pytest
```

To run the agent you need a free Groq API key: copy `.env.example` to `.env` and fill in
`GROQ_API_KEY`. The tests do not need a key and never call an LLM.

## Data

Match results and statistics for Ligue 1 seasons 2023-2024 to 2025-2026 (918 matches) come
from [football-data.co.uk](https://www.football-data.co.uk/). The files are not
redistributed in this repository: `scripts/prepare_data.py` downloads them. Betting odds
columns are dropped. The tests run on a small synthetic database (`tests/conftest.py`).

## Project layout

```
src/football_stats_agent/   package (tools, agent, MCP server, security)
scripts/prepare_data.py     data download and SQLite build
tests/                      pytest suite, synthetic fixtures
docs/learning_log.md        who wrote what, and what was learned
```
