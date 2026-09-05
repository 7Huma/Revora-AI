def recommend(
    source: str,
    root_cause: str | None = None,
    risk: dict | None = None,
    context: dict | None = None,
) -> dict:
    """
    Select the safest bounded recovery intervention.

    Returns:
        action, channel, priority, and reason.
    """

    source = (source or "").strip().lower()
    risk = risk or {}
    context = context or {}

    score = float(risk.get("score", 0))
    days_overdue = int(context.get("days_overdue", 0))

    if source == "payment_failure":
        return {
            "action": "retry_payment",
            "channel": "payment_gateway",
            "priority": "high" if score >= 70 else "medium",
            "reason": (
                "Retry a recoverable payment before escalating "
                "to customer outreach."
            ),
        }

    if source == "checkout_abandonment":
        return {
            "action": "send_checkout_recovery",
            "channel": "email",
            "priority": "high" if score >= 70 else "medium",
            "reason": (
                "Recover the abandoned checkout with a personalized "
                "payment link."
            ),
        }

    if source == "subscription_failure":
        return {
            "action": "subscription_recovery",
            "channel": "email",
            "priority": "high",
            "reason": (
                "Ask the customer to update payment details "
                "and retry billing."
            ),
        }

    if source == "overdue_invoice":
        return {
            "action": "receivables_chase",
            "channel": "email",
            "priority": "high" if days_overdue > 30 else "medium",
            "reason": (
                "Start a polite B2B payment follow-up "
                "based on invoice age."
            ),
        }

    if source == "mandate_retry":
        return {
            "action": "retry_mandate",
            "channel": "payment_gateway",
            "priority": "high",
            "reason": (
                "Retry the mandate using the configured retry sequence."
            ),
        }

    return {
        "action": "manual_review",
        "channel": "system",
        "priority": "medium",
        "reason": (
            "Insufficient evidence for an automated intervention."
        ),
    }