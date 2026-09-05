from app.agents.root_cause_agent import diagnose


def test_payment_failure():
    result = diagnose(
        "payment_failure",
        {},
    )

    assert result["cause"] == "payment_degradation"


def test_insufficient_funds_payment_failure():
    result = diagnose(
        "payment_failure",
        {"failure_reason": "insufficient_funds"},
    )

    assert result["cause"] == "temporary_payment_failure"


def test_insufficient_funds_is_case_insensitive():
    result = diagnose(
        "payment_failure",
        {"failure_reason": "INSUFFICIENT_FUNDS"},
    )

    assert result["cause"] == "temporary_payment_failure"


def test_checkout_abandonment():
    result = diagnose(
        "checkout_abandonment",
        {},
    )

    assert result["cause"] == "checkout_dropoff"


def test_subscription_failure():
    result = diagnose(
        "subscription_failure",
        {},
    )

    assert result["cause"] == "failed_subscription"


def test_overdue_invoice():
    result = diagnose(
        "overdue_invoice",
        {},
    )

    assert result["cause"] == "overdue_receivable"


def test_mandate_retry():
    result = diagnose(
        "mandate_retry",
        {},
    )

    assert result["cause"] == "mandate_failure"


def test_unknown_source():
    result = diagnose(
        "something_unknown",
        {},
    )

    assert result["cause"] == "unknown_revenue_risk"


def test_context_can_be_omitted():
    result = diagnose("payment_failure")

    assert result["cause"] == "payment_degradation"


def test_source_is_normalized():
    result = diagnose(
        " PAYMENT_FAILURE ",
        {},
    )

    assert result["cause"] == "payment_degradation"