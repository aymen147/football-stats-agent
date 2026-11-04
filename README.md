# football-stats-agent

Goal: an agent that answers natural-language questions about Ligue 1 match statistics.
A LangGraph graph will let an LLM (Groq) choose between three tools: a read-only SQL query
tool, a statistics tool and a chart tool. The same tools will be exposed through an MCP
server, and a security layer will guard them against prompt injection.

> **Status: work in progress, built step by step.** The roadmap shows what exists today.
> This README only describes what the code in this repository does.

## Roadmap

- [x] Data pipeline: Ligue 1 statistics downloaded and loaded into SQLite
- [x] Test suite on a synthetic database, CI with GitHub Actions
- [x] Read-only SQL tool (known gap: `ATTACH` can still create an empty file, fixed in the
      security layer below)
- [x] Statistics and chart tools
- [x] LangGraph agent choosing between the tools (graph tested in CI with a scripted model;
      live run with Groq not yet recorded here)
- [ ] MCP server exposing the same tools, with an example client
- [ ] Security layer: allow-listed tables, output checks, prompt-injection test set
- [ ] Evaluation: attacks tried and attacks blocked, with an honest list of limits

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python scripts/prepare_data.py   # downloads 3 Ligue 1 seasons, builds data/football.db
uv run pytest
```

The tests run on a synthetic database: they need no API key and no network access.

To ask the agent a question, copy `.env.example` to `.env`, add a free Groq API key, then:

```bash
uv run football-agent "Which team won the most home games in 2025-2026?"
```

The command prints each tool the model chose (`[tool] run_sql(...)`) before the answer.

## Data

Match results and statistics for Ligue 1 seasons 2023-2024 to 2025-2026 (918 matches) come
from [football-data.co.uk](https://www.football-data.co.uk/). The files are not
redistributed in this repository: `scripts/prepare_data.py` downloads them. Betting odds
columns are dropped. The tests use a small synthetic database (`tests/conftest.py`).

## Project layout

```
src/football_stats_agent/   package: read-only database access, tools, agent, CLI
scripts/prepare_data.py     data download and SQLite build
tests/                      pytest suite, synthetic fixtures
docs/learning_log.md        who wrote what, and what was learned
```
