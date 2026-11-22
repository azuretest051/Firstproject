"""CLI: python -m src.recommend '{...json prefs...}'"""

from __future__ import annotations

import argparse
import json
import sys

from src.recommend.engine import recommend


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run restaurant recommendations")
    parser.add_argument(
        "preferences_json",
        nargs="?",
        help="JSON object with location, budget, cuisine, min_rating, additional_preferences",
    )
    parser.add_argument("--top-n", type=int, default=None)
    args = parser.parse_args(argv)

    if not args.preferences_json:
        args.preferences_json = json.dumps(
            {
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": "family-friendly",
            }
        )

    prefs = json.loads(args.preferences_json)
    result = recommend(prefs, top_n=args.top_n)
    json.dump(result, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
