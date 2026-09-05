from typing import Any


def calculate_risk(
    source: str,
    amount: float,
    context: dict[str, Any] | None = None,
) -> dict:
    """
    Calculate a deterministic recovery risk score from 0 to 100.

    Factors:
    - amount at risk
    - previous payment failures
    - customer lifetime value
    - recovery source
    - invoice age
    """

    if amount < 0:
        raise ValueError("amount cannot be negative")

    source = (source or "").strip().lower()
    context = context or {}

    score = 40

    if amount >= 10000:
        score += 20
    elif amount >= 5000:
        score += 10

    if context.get("previous_failures", 0) >= 1:
        score += 10

    if context.get("customer_ltv", 0) >= 30000:
        score += 15

    if source in {
        "payment_failure",
        "subscription_failure",
    }:
        score += 10

    if (
        source == "overdue_invoice"
        and context.get("days_overdue", 0) > 30
    ):
        score += 10

    return {
        "score": min(score, 100),
    }
