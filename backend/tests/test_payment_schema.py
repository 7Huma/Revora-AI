import pytest
from pydantic import ValidationError

from app.schemas.payment import PaymentEvent


def test_payment_event():
    payment = PaymentEvent(
        customer_id="customer-123",
        amount=4999.0,
        status="failed",
        failure_reason="TIMEOUT",
    )

    assert payment.customer_id == "customer-123"
    assert payment.amount == 4999.0
    assert payment.currency == "INR"
    assert payment.status == "failed"
    assert payment.failure_reason == "TIMEOUT"
    assert payment.payment_method == "card"


def test_payment_event_custom_values():
    payment = PaymentEvent(
        customer_id="customer-456",
        amount=1000.0,
        currency="USD",
        status="success",
        payment_method="upi",
    )

    assert payment.currency == "USD"
    assert payment.status == "success"
    assert payment.payment_method == "upi"


def test_payment_amount_must_be_positive():
    with pytest.raises(ValidationError):
        PaymentEvent(
            customer_id="customer-123",
            amount=0,
            status="failed",
        )


def test_customer_id_required():
    with pytest.raises(ValidationError):
        PaymentEvent(
            amount=1000,
            status="failed",
        )


def test_status_required():
    with pytest.raises(ValidationError):
        PaymentEvent(
            customer_id="customer-123",
            amount=1000,
        )