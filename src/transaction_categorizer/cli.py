from __future__ import annotations

import argparse

from .agent import OpenAITransactionAgent
from .processor import categorize_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Categorize bank transactions with rules and an optional AI agent."
    )
    parser.add_argument("input_csv", help="Bank CSV with date, description, and amount columns")
    parser.add_argument("output_csv", help="Where to write categorized transactions")
    parser.add_argument(
        "--use-agent",
        action="store_true",
        help="Send transactions not matched by rules to the OpenAI agent",
    )
    parser.add_argument(
        "--auto-accept-threshold",
        type=float,
        default=0.90,
        help="Minimum confidence for automatic categorization (default: 0.90)",
    )
    parser.add_argument(
        "--high-value-threshold",
        type=float,
        default=1000.0,
        help="Absolute amount requiring human review (default: 1000)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not 0 <= args.auto_accept_threshold <= 1:
        raise SystemExit("--auto-accept-threshold must be between 0 and 1")
    if args.high_value_threshold < 0:
        raise SystemExit("--high-value-threshold must be non-negative")

    agent = OpenAITransactionAgent() if args.use_agent else None
    summary = categorize_csv(
        args.input_csv,
        args.output_csv,
        agent=agent,
        auto_accept_threshold=args.auto_accept_threshold,
        high_value_threshold=args.high_value_threshold,
    )
    print(f"Processed: {summary['total']}")
    print(f"Automatically categorized: {summary['auto_categorized']}")
    print(f"Needs review: {summary['needs_review']}")
    print(f"Output: {args.output_csv}")


if __name__ == "__main__":
    main()

