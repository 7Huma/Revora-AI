from typing import Any


def analyze_outcome(
    case: Any,
    execution_result: dict,
) -> dict:
    """
    Analyze the result of a recovery intervention.

    Returns:
        outcome
        recovered_amount
        recovery_rate
        next_action
        learning_signal
    """

    result = execution_result.get("result", {})

    success = bool(
        result.get("success", False)
    )

    amount_at_risk = float(
        case.amount_at_risk or 0
    )

    if success:
        recovered_amount = amount_at_risk

        if amount_at_risk > 0:
            recovery_rate = round(
                recovered_amount / amount_at_risk,
                2,
            )
        else:
            recovery_rate = 0.0

        return {
            "outcome": "SUCCESS",
            "recovered_amount": recovered_amount,
            "recovery_rate": recovery_rate,
            "next_action": "close_case",
            "learning_signal": "positive",
        }

    # Failed intervention
    return {
        "outcome": "FAILED",
        "recovered_amount": 0.0,
        "recovery_rate": 0.0,
        "next_action": get_next_action(case),
        "learning_signal": "negative",
    }


def get_next_action(case: Any) -> str:
    """
    Decide what the autonomous agent should do
    after a failed intervention.
    """

    source = str(
        case.source or ""
    ).lower()

    risk = float(
        case.risk_score or 0
    )

    # Payment failures
    if source == "payment_failure":

        if risk >= 70:
            return "retry_payment"

        return "send_payment_reminder"

    # Checkout abandonment
    if source == "checkout_abandonment":
        return "send_checkout_recovery"

    # Subscription failure
    if source == "subscription_failure":
        return "retry_subscription"

    # Invoice
    if source == "overdue_invoice":

        if risk >= 70:
            return "escalate_receivables"

        return "send_receivables_followup"

    # Mandate
    if source == "mandate_retry":
        return "retry_mandate"

    return "manual_review"