from transaction_categorizer.models import Category, Transaction
from transaction_categorizer.rules import classify_by_rule, normalize_description


def test_normalize_description() -> None:
    assert normalize_description("  SQ *JOE'S   COFFEE #42 ") == "sq joe s coffee 42"


def test_aws_rule() -> None:
    result = classify_by_rule(Transaction("2026-08-01", "ACH PMT AWS EDI 2938", -245.19))
    assert result is not None
    assert result.category is Category.SOFTWARE
    assert result.source == "rule"


def test_stripe_inflow_is_revenue() -> None:
    result = classify_by_rule(Transaction("2026-08-03", "STRIPE TRANSFER", 3200.00))
    assert result is not None
    assert result.category is Category.REVENUE


def test_stripe_outflow_is_not_assumed_to_be_revenue() -> None:
    assert classify_by_rule(Transaction("2026-08-03", "STRIPE TRANSFER", -25.00)) is None

