from typing import Any


SOURCE_CAUSES = {
    "payment_failure": "payment_degradation",
    "checkout_abandonment": "checkout_dropoff",
    "subscription_failure": "failed_subscription",
    "overdue_invoice": "overdue_receivable",
    "mandate_retry": "mandate_failure",
}


def diagnose(
    source: str,
    context: dict[str, Any] | None = None,
) -> dict:
    """
    Determine the likely revenue-loss root cause.

    This deterministic implementation can later be replaced or
    augmented with an LLM-based diagnosis layer.
    """

    source = (source or "").strip().lower()
    context = context or {}

    cause = SOURCE_CAUSES.get(
        source,
        "unknown_revenue_risk",
    )

    if (
        source == "payment_failure"
        and str(context.get("failure_reason", "")).lower()
        == "insufficient_funds"
    ):
        cause = "temporary_payment_failure"

    return {
        "cause": cause,
    }