# Learning log

This project was built as a guided exercise. This log records, phase by phase, what was
prepared with help, what Aymen reviewed, and what was learned.

## Phase 0 — scaffolding (prepared with help, reviewed by Aymen)

- Repository layout, `pyproject.toml`, `.gitignore`, `.env.example`
- `scripts/prepare_data.py`: download of the football-data.co.uk CSVs, SQLite build
- `src/football_stats_agent/schema.py`, `config.py`
- `tests/conftest.py`: synthetic test database
- GitHub Actions workflow (`.github/workflows/ci.yml`)

## Phase 1 — read-only connection and SQL tool (prepared with help, reviewed by Aymen)

- `db.py`: `connect_read_only` opens SQLite with the `mode=ro` URI flag, so the engine
  itself refuses writes, whatever the wording of the query. A missing file raises an error
  instead of creating an empty database (the default behaviour of `sqlite3.connect`).
- `tools.py`: `run_sql` returns `columns`, `rows`, `row_count`, `truncated`. It fetches
  `max_rows + 1` rows to know whether the result was cut without loading all of it, and
  always closes the connection.
- `tests/test_tools.py`: writes (`DELETE`, `UPDATE`, `INSERT`, `DROP`, `CREATE`) are
  refused and leave the data intact; truncation, including the exact-limit edge case.

Finding: read-only mode does **not** block `ATTACH DATABASE`, which creates an empty file at
a path chosen by whoever writes the query. Kept as an expected-failure test until the
security layer (phase 4) denies it.

## Phase 2 — statistics and chart tools, LangGraph agent (prepared with help, reviewed by Aymen)

- `tools.py`: `team_stats` uses parameterised SQL (`?` placeholders), never string
  concatenation, and turns home/away columns into the team's point of view. An unknown team
  raises an error that lists the valid names, so the model can correct itself ('PSG' ->
  'Paris SG'). `make_chart` uses matplotlib's `Figure` directly (no GUI backend, works in
  CI) and reduces the title to safe characters so it can never write outside `charts/`.
- `agent.py`: an explicit `StateGraph` — `agent` node (model with tools bound) ->
  `tools_condition` -> `ToolNode` -> back to `agent`, until the model answers without a tool
  call. The model never sees file paths: the tools are wrapped in closures. SQL and
  validation errors go back to the model as tool messages (`handle_tool_errors`); in
  LangGraph 1.x the default re-raises them. `recursion_limit` caps a run at 12 steps.
- `tests/test_agent.py`: a scripted fake model (no API key) checks tool routing, error
  recovery after a refused `DELETE`, and the step cap.

Finding: a fake model that returns the *same* message object loops only once — LangGraph's
`add_messages` replaces a message whose id it has already seen instead of appending it.
