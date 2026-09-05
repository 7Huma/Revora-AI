import pytest

from app.agents.risk_detector import calculate_risk


def test_base_risk():
    result = calculate_risk(
        source="checkout_abandonment",
        amount=1000,
        context={},
    )

    assert result["score"] == 40


def test_medium_amount_increases_risk():
    result = calculate_risk(
        source="checkout_abandonment",
        amount=5000,
        context={},
    )

    assert result["score"] == 50


def test_high_amount_increases_risk():
    result = calculate_risk(
        source="checkout_abandonment",
        amount=10000,
        context={},
    )

    assert result["score"] == 60


def test_previous_failure_increases_risk():
    result = calculate_risk(
        source="checkout_abandonment",
        amount=1000,
        context={"previous_failures": 1},
    )

    assert result["score"] == 50


def test_high_ltv_increases_risk():
    result = calculate_risk(
        source="checkout_abandonment",
        amount=1000,
        context={"customer_ltv": 30000},
    )

    assert result["score"] == 55


def test_payment_failure_adds_risk():
    result = calculate_risk(
        source="payment_failure",
        amount=1000,
        context={},
    )

    assert result["score"] == 50


def test_subscription_failure_adds_risk():
    result = calculate_risk(
        source="subscription_failure",
        amount=1000,
        context={},
    )

    assert result["score"] == 50


def test_old_invoice_adds_risk():
    result = calculate_risk(
        source="overdue_invoice",
        amount=1000,
        context={"days_overdue": 31},
    )

    assert result["score"] == 50


def test_score_never_exceeds_100():
    result = calculate_risk(
        source="payment_failure",
        amount=10000,
        context={
            "previous_failures": 100,
            "customer_ltv": 100000,
        },
    )

    assert 0 <= result["score"] <= 100


def test_negative_amount_rejected():
    with pytest.raises(ValueError):
        calculate_risk(
            source="payment_failure",
            amount=-100,
            context={},
        )


def test_context_can_be_omitted():
    result = calculate_risk(
        source="payment_failure",
        amount=1000,
    )

    assert result["score"] == 50


def test_source_is_normalized():
    result = calculate_risk(
        source=" PAYMENT_FAILURE ",
        amount=1000,
    )

    assert result["score"] == 50