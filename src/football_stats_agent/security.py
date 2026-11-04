"""Security layer around the tools.

Deterministic guards (enforced by SQLite, cannot be talked around):
- an authorizer: only SELECT, only on allow-listed tables; ATTACH, PRAGMA, schema tables
  and every write are denied;
- a step budget that interrupts runaway queries.

Pattern-based checks (heuristics, can be evaded, measured in evaluation.py):
- tool results: text that looks like an instruction is removed before the model reads it;
- final answers: external URLs and secret-looking strings are flagged.
"""

import re
import sqlite3
from typing import Any

ALLOWED_TABLES = frozenset({"matches"})

# The progress handler runs every PROGRESS_INTERVAL SQLite VM instructions; a query is
# interrupted after MAX_VM_INSTRUCTIONS. Real questions on 918 matches stay far below.
PROGRESS_INTERVAL = 10_000
MAX_VM_INSTRUCTIONS = 20_000_000

REMOVED_TEXT = "[removed: text that looks like an instruction]"

INJECTION_PATTERN = re.compile(
    "|".join([
        r"\b(ignore|disregard|forget)\b.{0,40}\b(instructions?|rules|prompts?)\b",
        r"\b(ignorer?|ignorez|oublier?|oubliez)\b.{0,40}\b(instructions?|consignes?|règles)\b",
        r"\byou are now\b|\btu es maintenant\b",
        r"\bsystem prompt\b|\bprompt système\b",
        r"<\|[^|>]*\|>",
        r"\b(new|nouvelles?) instructions?\b",
        r"\b(drop\s+table|delete\s+from|insert\s+into|attach\s+database|update\s+\w+\s+set)\b",
        r"https?://",
    ]),
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
SECRET_PATTERNS = {
    # Canary token planted in a forbidden table by the security evaluation.
    "canary token": re.compile(r"CANARY-[0-9a-f]{6,}", re.IGNORECASE),
    "Groq API key": re.compile(r"\bgsk_[A-Za-z0-9]{20,}"),
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
}


def _authorize(action: int, arg1: str | None, arg2: str | None, *_: Any) -> int:
    """SQLite calls this while compiling each statement; anything not listed is denied."""
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ:  # arg1 is the table, arg2 the column
        return sqlite3.SQLITE_OK if arg1 in ALLOWED_TABLES else sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:  # built-in functions: COUNT, AVG, ROUND...
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def install_guards(conn: sqlite3.Connection) -> None:
    """Add the authorizer and the step budget to a connection."""
    conn.set_authorizer(_authorize)
    calls = 0

    def stop_runaway_query() -> int:
        nonlocal calls
        calls += 1
        return int(calls * PROGRESS_INTERVAL > MAX_VM_INSTRUCTIONS)  # non-zero aborts

    conn.set_progress_handler(stop_runaway_query, PROGRESS_INTERVAL)


def sanitize(value: Any) -> Any:
    """Copy of a tool result where text that looks like an instruction is removed."""
    if isinstance(value, str):
        return REMOVED_TEXT if INJECTION_PATTERN.search(value) else value
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    return value


def check_answer(text: str) -> list[str]:
    """Reasons to withhold a final answer; an empty list means it can be shown.

    The agent has no reason to output a URL: a link or a markdown image pointing outside
    is a classic way to exfiltrate data, so any URL is flagged.
    """
    problems = ["external URL"] if URL_PATTERN.search(text) else []
    problems += [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]
    return problems
