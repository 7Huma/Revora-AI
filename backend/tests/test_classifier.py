from app.core.classifier import analyze_root_cause
from app.db.models import RootCauseCategory


def test_payment_timeout():
    result = analyze_root_cause(
        "payment.failed",
        failure_code="TIMEOUT",
    )

    assert result["root_cause"] == RootCauseCategory.PAYMENT_GATEWAY
    assert result["reason_detail"] == "BANK_SERVER_TIMEOUT"
    assert result["risk_score"] == 35.0
    assert result["suggested_action"] == "INSTANT_UPI_FALLBACK"


def test_payment_insufficient_balance():
    result = analyze_root_cause(
        "payment.failed",
        failure_description="Insufficient balance",
    )

    assert result["root_cause"] == RootCauseCategory.PAYMENT_GATEWAY
    assert result["reason_detail"] == "INSUFFICIENT_FUNDS"
    assert result["risk_score"] == 75.0


def test_generic_payment_failure():
    result = analyze_root_cause(
        "payment.failed",
        failure_code="DECLINED",
    )

    assert result["reason_detail"] == "GENERIC_DECLINE"
    assert result["risk_score"] == 50.0


def test_subscription_failure():
    result = analyze_root_cause(
        "subscription.halted",
    )

    assert result["root_cause"] == RootCauseCategory.SUBSCRIPTION_FAILED
    assert result["reason_detail"] == "RECURRING_MANDATE_DECLINED"
    assert result["risk_score"] == 60.0


def test_checkout_abandonment():
    result = analyze_root_cause(
        "checkout.abandoned",
    )

    assert result["root_cause"] == RootCauseCategory.CHECKOUT_DROP_OFF
    assert result["reason_detail"] == "CART_ABANDONMENT"
    assert result["risk_score"] == 50.0


def test_invoice_overdue():
    result = analyze_root_cause(
        "invoice.overdue",
    )

    assert result["root_cause"] == RootCauseCategory.INVOICE_OVERDUE
    assert result["reason_detail"] == "OVERDUE_RECEIVABLE"
    assert result["risk_score"] == 80.0


def test_receivable_overdue():
    result = analyze_root_cause(
        "receivable.overdue",
    )

    assert result["root_cause"] == RootCauseCategory.INVOICE_OVERDUE


def test_event_type_is_normalized():
    result = analyze_root_cause(
        "  PAYMENT.FAILED  ",
        failure_code=" timeout ",
    )

    assert result["reason_detail"] == "BANK_SERVER_TIMEOUT"


def test_unknown_event_uses_fallback():
    result = analyze_root_cause(
        "unknown.event",
    )

    assert result["root_cause"] == RootCauseCategory.PAYMENT_GATEWAY
    assert result["reason_detail"] == "GENERIC_DECLINE"
    assert result["risk_score"] == 50.0