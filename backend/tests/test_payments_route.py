from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import payments


app = FastAPI()
app.include_router(payments.router)

client = TestClient(app)


def test_successful_payment_event(monkeypatch):
    def fake_record_payment(db, event):
        return SimpleNamespace(id="payment-123")

    def fake_create_case(*args, **kwargs):
        raise AssertionError("create_case should not be called for successful payment")

    monkeypatch.setattr(
        payments,
        "record_payment",
        fake_record_payment,
    )
    monkeypatch.setattr(
        payments,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "amount": 1000,
            "currency": "INR",
            "status": "success",
            "failure_reason": "",
            "payment_method": "card",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "payment_id": "payment-123",
        "recovery_case_id": None,
        "decision": None,
    }


def test_failed_payment_creates_recovery_case(monkeypatch):
    def fake_record_payment(db, event):
        return SimpleNamespace(id="payment-456")

    def fake_create_case(
        db,
        customer_id,
        source,
        amount,
        context,
    ):
        assert customer_id == "customer-123"
        assert source == "payment_failure"
        assert amount == 5000
        assert context["event_type"] == "payment.failed"
        assert context["failure_code"] == "insufficient_funds"
        assert context["failure_description"] == "insufficient_funds"

        return (
            SimpleNamespace(id="case-456"),
            {
                "risk_score": 75,
                "recommended_action": "retry_payment",
            },
        )

    monkeypatch.setattr(
        payments,
        "record_payment",
        fake_record_payment,
    )
    monkeypatch.setattr(
        payments,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "amount": 5000,
            "currency": "INR",
            "status": "failed",
            "failure_reason": "insufficient_funds",
            "payment_method": "card",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_id"] == "payment-456"
    assert data["recovery_case_id"] == "case-456"
    assert data["decision"]["risk_score"] == 75
    assert data["decision"]["recommended_action"] == "retry_payment"


def test_invalid_payment_event_rejected(monkeypatch):
    response = client.post(
        "/event",
        json={
            "amount": 1000,
            "status": "failed",
        },
    )

    assert response.status_code == 422