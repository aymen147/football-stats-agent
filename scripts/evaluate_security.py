"""Run the prompt-injection test set and print the results as Markdown.

Usage:
    uv run python scripts/evaluate_security.py
"""

import sys
import tempfile
from pathlib import Path

from football_stats_agent.evaluation import evaluate, summary_table


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # attack texts contain French accents
    with tempfile.TemporaryDirectory() as workdir:
        outcomes = evaluate(Path(workdir))
    print(summary_table(outcomes))
    print("\nNot blocked:")
    for outcome in outcomes:
        if not outcome.blocked:
            print(f"- {outcome.category} / {outcome.attack_id}: {outcome.description}")


if __name__ == "__main__":
    main()
