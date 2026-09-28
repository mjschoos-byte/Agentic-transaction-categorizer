from __future__ import annotations

import csv
from pathlib import Path
from typing import Protocol

from .models import Category, Classification, Transaction
from .rules import classify_by_rule


REQUIRED_COLUMNS = {"date", "description", "amount"}
OUTPUT_COLUMNS = [
    "date",
    "description",
    "amount",
    "merchant",
    "category",
    "confidence",
    "source",
    "status",
    "reason",
]


class TransactionAgent(Protocol):
    def classify(self, transaction: Transaction) -> Classification: ...


def _parse_transaction(row: dict[str, str], row_number: int) -> Transaction:
    date = row.get("date", "").strip()
    description = row.get("description", "").strip()
    raw_amount = row.get("amount", "").strip().replace(",", "")
    if not date or not description or not raw_amount:
        raise ValueError(f"Row {row_number}: date, description, and amount are required.")
    try:
        amount = float(raw_amount)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: amount must be a number, got {raw_amount!r}.") from exc
    return Transaction(date=date, description=description, amount=amount)


def categorize_transaction(
    transaction: Transaction,
    *,
    agent: TransactionAgent | None = None,
    auto_accept_threshold: float = 0.90,
    high_value_threshold: float = 1000.0,
) -> dict[str, str]:
    classification = classify_by_rule(transaction)
    if classification is None and agent is not None:
        classification = agent.classify(transaction)
    if classification is None:
        classification = Classification(
            category=Category.UNCATEGORIZED,
            confidence=0.0,
            merchant="Unknown",
            source="unclassified",
            reason="No approved rule matched and the agent was not enabled.",
        )

    needs_review = (
        classification.confidence < auto_accept_threshold
        or abs(transaction.amount) >= high_value_threshold
        or classification.category is Category.UNCATEGORIZED
    )

    return {
        "date": transaction.date,
        "description": transaction.description,
        "amount": f"{transaction.amount:.2f}",
        "merchant": classification.merchant,
        "category": classification.category.value,
        "confidence": f"{classification.confidence:.2f}",
        "source": classification.source,
        "status": "needs_review" if needs_review else "auto_categorized",
        "reason": classification.reason,
    }


def categorize_csv(
    input_path: str | Path,
    output_path: str | Path,
    *,
    agent: TransactionAgent | None = None,
    auto_accept_threshold: float = 0.90,
    high_value_threshold: float = 1000.0,
) -> dict[str, int]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    results: list[dict[str, str]] = []

    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"Input CSV is missing columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            transaction = _parse_transaction(row, row_number)
            results.append(
                categorize_transaction(
                    transaction,
                    agent=agent,
                    auto_accept_threshold=auto_accept_threshold,
                    high_value_threshold=high_value_threshold,
                )
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    review_count = sum(row["status"] == "needs_review" for row in results)
    return {
        "total": len(results),
        "auto_categorized": len(results) - review_count,
        "needs_review": review_count,
    }

