import pytest

from app.agents.revenue_agent import analyze_case


def test_payment_failure_pipeline():
    result = analyze_case(
        source="payment_failure",
        amount=1000,
        context={},
    )

    assert result["risk_score"] == 50
    assert result["root_cause"] == "payment_degradation"
    assert result["recommended_action"] == "retry_payment"
    assert result["channel"] == "payment_gateway"
    assert result["priority"] == "medium"


def test_high_value_payment_failure():
    result = analyze_case(
        source="payment_failure",
        amount=10000,
        context={
            "previous_failures": 1,
            "customer_ltv": 50000,
        },
    )

    assert result["risk_score"] == 95
    assert result["root_cause"] == "payment_degradation"
    assert result["recommended_action"] == "retry_payment"
    assert result["priority"] == "high"


def test_insufficient_funds_pipeline():
    result = analyze_case(
        source="payment_failure",
        amount=2000,
        context={
            "failure_reason": "insufficient_funds",
        },
    )

    assert result["root_cause"] == "temporary_payment_failure"
    assert result["recommended_action"] == "retry_payment"


def test_checkout_pipeline():
    result = analyze_case(
        source="checkout_abandonment",
        amount=3000,
        context={},
    )

    assert result["root_cause"] == "checkout_dropoff"
    assert result["recommended_action"] == "send_checkout_recovery"
    assert result["channel"] == "email"


def test_subscription_pipeline():
    result = analyze_case(
        source="subscription_failure",
        amount=6000,
        context={},
    )

    assert result["root_cause"] == "failed_subscription"
    assert result["recommended_action"] == "subscription_recovery"
    assert result["channel"] == "email"


def test_overdue_invoice_pipeline():
    result = analyze_case(
        source="overdue_invoice",
        amount=8000,
        context={
            "days_overdue": 45,
        },
    )

    assert result["root_cause"] == "overdue_receivable"
    assert result["recommended_action"] == "receivables_chase"
    assert result["channel"] == "email"
    assert result["priority"] == "high"


def test_mandate_pipeline():
    result = analyze_case(
        source="mandate_retry",
        amount=4000,
        context={},
    )

    assert result["root_cause"] == "mandate_failure"
    assert result["recommended_action"] == "retry_mandate"
    assert result["channel"] == "payment_gateway"


def test_unknown_source_pipeline():
    result = analyze_case(
        source="unknown",
        amount=1000,
        context={},
    )

    assert result["root_cause"] == "unknown_revenue_risk"
    assert result["recommended_action"] == "manual_review"
    assert result["channel"] == "system"


def test_context_can_be_omitted():
    result = analyze_case(
        source="payment_failure",
        amount=1000,
    )

    assert result["risk_score"] == 50


def test_negative_amount_rejected():
    with pytest.raises(ValueError):
        analyze_case(
            source="payment_failure",
            amount=-100,
            context={},
        )