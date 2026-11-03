"""Command-line entry point for the natural-language reminder agent."""

import argparse
import json
import sys
from collections.abc import Sequence

from src.reminder_agent import parse_reminder
from src.reminder_agent.errors import ReminderAgentError


def serialize_response(response: dict[str, str | None]) -> str:
    return json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interpret one reminder sentence.")
    parser.add_argument("sentence", help="one natural-language reminder sentence")
    args = parser.parse_args(argv)
    try:
        response = parse_reminder(args.sentence)
    except ReminderAgentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(serialize_response(response), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
