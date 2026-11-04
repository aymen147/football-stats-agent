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
