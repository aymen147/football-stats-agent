"""Command line: ask the agent one question and show which tools it used.

Usage:
    uv run football-agent "Which team won the most home games in 2025-2026?"
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

from football_stats_agent.agent import ask, build_agent
from football_stats_agent.config import CHARTS_DIR, DB_PATH

DEFAULT_MODEL = "openai/gpt-oss-120b"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question about Ligue 1 statistics.")
    parser.add_argument("question")
    args = parser.parse_args()

    # Windows consoles default to cp1252, which cannot print French typography (e.g. U+202F).
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    if not os.environ.get("GROQ_API_KEY"):
        sys.exit("GROQ_API_KEY is missing: copy .env.example to .env and add your key.")
    if not DB_PATH.exists():
        sys.exit("Database not found: run `uv run python scripts/prepare_data.py` first.")

    model = ChatGroq(model=os.environ.get("GROQ_MODEL", DEFAULT_MODEL), temperature=0)
    messages = ask(build_agent(model, DB_PATH, CHARTS_DIR), args.question)

    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                print(f"[tool] {call['name']}({call['args']})")
    print(messages[-1].content)


if __name__ == "__main__":
    main()
