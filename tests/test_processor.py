import csv

import pytest

from transaction_categorizer.models import Category, Classification, Transaction
from transaction_categorizer.processor import categorize_csv, categorize_transaction


class FakeAgent:
    def classify(self, transaction: Transaction) -> Classification:
        return Classification(
            category=Category.PROFESSIONAL_SERVICES,
            confidence=0.75,
            merchant="Northstar Consulting",
            source="agent",
            reason="Description appears to identify a consulting firm.",
        )


def test_unknown_transaction_without_agent_needs_review() -> None:
    result = categorize_transaction(Transaction("2026-08-08", "UNKNOWN VENDOR", -42.00))
    assert result["category"] == "Uncategorized"
    assert result["status"] == "needs_review"


def test_low_confidence_agent_result_needs_review() -> None:
    result = categorize_transaction(
        Transaction("2026-08-08", "NORTHSTAR CONSULTING LLC", -650.00),
        agent=FakeAgent(),
    )
    assert result["source"] == "agent"
    assert result["status"] == "needs_review"


def test_high_value_rule_match_still_needs_review() -> None:
    result = categorize_transaction(Transaction("2026-08-03", "STRIPE TRANSFER", 3200.00))
    assert result["category"] == "Revenue"
    assert result["status"] == "needs_review"


def test_categorize_csv(tmp_path) -> None:
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    input_path.write_text(
        "date,description,amount\n2026-08-01,AWS,-25.00\n2026-08-02,MYSTERY,-10.00\n",
        encoding="utf-8",
    )

    summary = categorize_csv(input_path, output_path)

    assert summary == {"total": 2, "auto_categorized": 1, "needs_review": 1}
    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["category"] == "Software"
    assert rows[1]["category"] == "Uncategorized"


def test_missing_columns_raise_clear_error(tmp_path) -> None:
    input_path = tmp_path / "input.csv"
    input_path.write_text("description,amount\nAWS,-25.00\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing columns: date"):
        categorize_csv(input_path, tmp_path / "output.csv")

