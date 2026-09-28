from __future__ import annotations

import re

from .models import Category, Classification, Transaction


# In a production system these mappings would live in a reviewed configuration
# table. Keeping them here makes the learning project transparent and testable.
MERCHANT_RULES: tuple[tuple[tuple[str, ...], str, Category], ...] = (
    (("aws", "amazon web services"), "Amazon Web Services", Category.SOFTWARE),
    (("adobe",), "Adobe", Category.SOFTWARE),
    (("microsoft", "msft"), "Microsoft", Category.SOFTWARE),
    (("staples", "office depot"), "Office supply store", Category.OFFICE_SUPPLIES),
    (("uber", "lyft"), "Rideshare", Category.TRAVEL),
    (("delta air", "united airlines", "southwest"), "Airline", Category.TRAVEL),
    (("starbucks", "coffee", "restaurant"), "Food merchant", Category.MEALS),
    (("adp", "gusto payroll"), "Payroll provider", Category.PAYROLL),
    (("comcast", "verizon", "at&t"), "Utility provider", Category.UTILITIES),
    (("bank fee", "service charge", "overdraft"), "Bank", Category.BANK_FEES),
    (("landlord", "office rent", "property mgmt"), "Property manager", Category.RENT),
    (("legal", "law office", "accounting firm"), "Professional firm", Category.PROFESSIONAL_SERVICES),
)


def normalize_description(description: str) -> str:
    cleaned = re.sub(r"[^a-z0-9& ]+", " ", description.lower())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def classify_by_rule(transaction: Transaction) -> Classification | None:
    description = normalize_description(transaction.description)

    # Direction matters for payment processors: an incoming Stripe transfer is
    # treated as revenue, while an outgoing amount remains ambiguous.
    if "stripe" in description and transaction.amount > 0:
        return Classification(
            category=Category.REVENUE,
            confidence=0.99,
            merchant="Stripe",
            source="rule",
            reason="Incoming Stripe transfer matched the approved revenue rule.",
        )

    if any(term in description for term in ("internal transfer", "account transfer")):
        return Classification(
            category=Category.TRANSFER,
            confidence=0.99,
            merchant="Internal transfer",
            source="rule",
            reason="Description matched the approved internal-transfer rule.",
        )

    for keywords, merchant, category in MERCHANT_RULES:
        match = next((keyword for keyword in keywords if keyword in description), None)
        if match:
            return Classification(
                category=category,
                confidence=0.99,
                merchant=merchant,
                source="rule",
                reason=f"Description matched the approved '{match}' merchant rule.",
            )

    return None

