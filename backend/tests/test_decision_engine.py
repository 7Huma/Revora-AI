import pytest

from app.ai.decision_engine import DecisionEngine


def test_payment_failure_decision():
    engine = DecisionEngine()

    result = engine.decide(
        "payment_failure",
        1000,
        {},
    )

    assert result["risk_score"] == 50
    assert result["root_cause"] == "payment_degradation"
    assert result["recommended_action"] == "retry_payment"


def test_checkout_decision():
    engine = DecisionEngine()

    result = engine.decide(
        "checkout_abandonment",
        3000,
    )

    assert result["root_cause"] == "checkout_dropoff"
    assert result["recommended_action"] == "send_checkout_recovery"
    assert result["channel"] == "email"


def test_context_is_passed_through():
    engine = DecisionEngine()

    result = engine.decide(
        "payment_failure",
        2000,
        {"failure_reason": "insufficient_funds"},
    )

    assert result["root_cause"] == "temporary_payment_failure"


def test_negative_amount_rejected():
    engine = DecisionEngine()

    with pytest.raises(ValueError):
        engine.decide(
            "payment_failure",
            -100,
        )


def test_context_can_be_omitted():
    engine = DecisionEngine()

    result = engine.decide(
        "payment_failure",
        1000,
    )

    assert result["risk_score"] == 50