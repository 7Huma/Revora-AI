from app.agents.intervention_agent import recommend


def test_payment_failure_low_risk():
    result = recommend(
        source="payment_failure",
        root_cause="PAYMENT_GATEWAY",
        risk={"score": 35},
        context={},
    )

    assert result["action"] == "retry_payment"
    assert result["channel"] == "payment_gateway"
    assert result["priority"] == "medium"


def test_payment_failure_high_risk():
    result = recommend(
        source="payment_failure",
        risk={"score": 75},
        context={},
    )

    assert result["priority"] == "high"


def test_checkout_abandonment():
    result = recommend(
        source="checkout_abandonment",
        risk={"score": 50},
        context={},
    )

    assert result["action"] == "send_checkout_recovery"
    assert result["channel"] == "email"


def test_subscription_failure():
    result = recommend(
        source="subscription_failure",
        risk={"score": 60},
        context={},
    )

    assert result["action"] == "subscription_recovery"
    assert result["priority"] == "high"


def test_overdue_invoice_under_30_days():
    result = recommend(
        source="overdue_invoice",
        risk={"score": 80},
        context={"days_overdue": 15},
    )

    assert result["action"] == "receivables_chase"
    assert result["priority"] == "medium"


def test_overdue_invoice_over_30_days():
    result = recommend(
        source="overdue_invoice",
        risk={"score": 80},
        context={"days_overdue": 45},
    )

    assert result["priority"] == "high"


def test_mandate_retry():
    result = recommend(
        source="mandate_retry",
        risk={"score": 60},
        context={},
    )

    assert result["action"] == "retry_mandate"
    assert result["channel"] == "payment_gateway"
    assert result["priority"] == "high"


def test_unknown_source_goes_to_manual_review():
    result = recommend(
        source="unknown",
        risk={"score": 90},
        context={},
    )

    assert result["action"] == "manual_review"
    assert result["channel"] == "system"


def test_missing_risk_and_context_do_not_crash():
    result = recommend(
        source="payment_failure",
    )

    assert result["action"] == "retry_payment"
    assert result["priority"] == "medium"