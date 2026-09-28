# Agent-Assisted Bank Transaction Categorizer

A small finance automation project that converts a bank-export CSV into a categorized transaction report. Known merchants are handled by deterministic rules. Unknown merchants can be sent to an OpenAI-powered classification agent, and uncertain or high-value transactions are held for human review.

This is a portfolio project, not an accounting system. It does not move money, post journal entries, or replace professional review.

## The problem

Finance and accounting teams often receive bank data with descriptions such as `SQ *JOES COFFEE` or `ACH PMT AWS EDI 2938`. A person must interpret each description, choose a category, and investigate unclear entries. That work is repetitive, inconsistent, and difficult to audit at scale.

This project uses exception-based processing:

1. Apply approved rules to familiar merchants.
2. Ask an agent for a structured suggestion when no rule matches.
3. Automatically accept only high-confidence, ordinary-value suggestions.
4. Route uncertain and high-value items to human review.
5. Preserve the reason, confidence, source, and final status in the output.

## Architecture

```text
Bank CSV
   |
   v
Input validation -> Merchant rules -> Optional AI agent -> Review controls -> Output CSV
                                           |                   |
                                           v                   v
                                  category + reason     low confidence or
                                  + confidence          high value = review
```

ServiceNow is intentionally not required. The output could later be connected to ServiceNow, a spreadsheet, or another workflow system, but the current version is a standalone Python project suitable for demonstrating automation in an internship application.

## Categories

- Revenue
- Rent
- Payroll
- Travel
- Meals
- Software
- Office Supplies
- Utilities
- Professional Services
- Bank Fees
- Transfer
- Uncategorized

These are management-reporting categories for a demonstration. They are not a complete chart of accounts and do not determine tax treatment.

## Quick start

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Run the rules-only version (no API key required):

```bash
categorize-transactions data/sample_transactions.csv output/categorized.csv
```

Run the agent-assisted version:

```bash
export OPENAI_API_KEY="your-key"
categorize-transactions data/sample_transactions.csv output/categorized.csv --use-agent
```

The optional model can be changed with `OPENAI_MODEL`. The default is `gpt-4o-mini`.

Run tests:

```bash
pytest
```

## Input format

The CSV must contain these exact columns:

```csv
date,description,amount
2026-08-01,ACH PMT AWS EDI 2938,-245.19
2026-08-02,STRIPE TRANSFER 8291,3200.00
```

Positive amounts are money entering the account. Negative amounts are money leaving it.

## Output fields

| Field | Meaning |
|---|---|
| `category` | Suggested reporting category |
| `confidence` | A value from 0 to 1 |
| `source` | `rule`, `agent`, or `unclassified` |
| `status` | `auto_categorized` or `needs_review` |
| `reason` | Short, auditable explanation |

The default controls require review when confidence is below 0.90 or the absolute transaction amount is at least $1,000. Both thresholds can be changed from the command line.

## Why use both rules and an agent?

Rules are best for known, repeatable cases: `AWS` should not require a model call every month. An agent is helpful for ambiguous descriptions that rules have not seen. Human review remains necessary because a merchant name alone often cannot reveal the correct accounting treatment.

The agent uses structured output, so its category must be one of the allowed values and its response includes a confidence score and explanation. Transaction descriptions are treated as untrusted data, not as instructions.

## Suggested demo

1. Run the sample file without the agent and show that known merchants are categorized.
2. Show that unknown merchants are routed to review.
3. Enable the agent and show structured suggestions for the unknown merchants.
4. Explain why high-value transactions still require review.
5. Compare the number of manually reviewed rows with the total row count.

## What this demonstrates

- Finance operations and transaction classification
- Python, CSV processing, validation, and testing
- A hybrid rules-and-AI architecture
- Human-in-the-loop controls and an audit trail
- Practical awareness of AI limitations

Possible résumé bullet after measuring the final demo dataset:

> Built a Python transaction-classification workflow combining deterministic merchant rules with structured AI recommendations, confidence thresholds, and human review controls for ambiguous and high-value transactions.

## Next improvements

- Add a simple Streamlit interface
- Save reviewer corrections as new approved rules
- Add duplicate-transaction detection
- Measure accuracy against a labeled test dataset
- Add a database and review dashboard
- Connect review items to ServiceNow only if a future use case calls for it

