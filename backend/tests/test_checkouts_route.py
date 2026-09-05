from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import checkouts


app = FastAPI()
app.include_router(checkouts.router)

client = TestClient(app)


def test_checkout_started(monkeypatch):
    def fake_record_checkout(db, payload):
        return SimpleNamespace(id="checkout-123")

    def fake_create_case(*args, **kwargs):
        raise AssertionError(
            "create_case should not be called for a non-abandoned checkout"
        )

    monkeypatch.setattr(
        checkouts,
        "record_checkout",
        fake_record_checkout,
    )
    monkeypatch.setattr(
        checkouts,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "session_id": "session-123",
            "cart_value": 2000,
            "event_type": "started",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "checkout_event_id": "checkout-123",
        "recovery_case_id": None,
        "decision": None,
    }


def test_abandoned_checkout_creates_case(monkeypatch):
    def fake_record_checkout(db, payload):
        return SimpleNamespace(id="checkout-456")

    def fake_create_case(
        db,
        customer_id,
        source,
        amount,
        context,
    ):
        assert customer_id == "customer-123"
        assert source == "checkout_abandonment"
        assert amount == 5000
        assert context == {}

        return (
            SimpleNamespace(id="case-456"),
            {
                "risk_score": 50,
                "recommended_action": "send_checkout_recovery",
            },
        )

    monkeypatch.setattr(
        checkouts,
        "record_checkout",
        fake_record_checkout,
    )
    monkeypatch.setattr(
        checkouts,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "session_id": "session-456",
            "cart_value": 5000,
            "event_type": "abandoned",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["checkout_event_id"] == "checkout-456"
    assert data["recovery_case_id"] == "case-456"
    assert data["decision"]["risk_score"] == 50
    assert data["decision"]["recommended_action"] == "send_checkout_recovery"