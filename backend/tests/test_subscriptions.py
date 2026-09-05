from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import subscriptions


app = FastAPI()
app.include_router(subscriptions.router)

client = TestClient(app)


def test_successful_subscription_event(monkeypatch):
    def fake_record_subscription_event(db, payload):
        return SimpleNamespace(id="sub-123")

    def fake_create_case(*args, **kwargs):
        raise AssertionError(
            "create_case should not be called for a successful subscription"
        )

    monkeypatch.setattr(
        subscriptions,
        "record_subscription_event",
        fake_record_subscription_event,
    )
    monkeypatch.setattr(
        subscriptions,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "status": "active",
            "amount": 2000,
            "failure_count": 0,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "subscription_id": "sub-123",
        "recovery_case_id": None,
        "decision": None,
    }


def test_failed_subscription_creates_recovery_case(monkeypatch):
    def fake_record_subscription_event(db, payload):
        return SimpleNamespace(id="sub-456")

    def fake_create_case(
        db,
        customer_id,
        source,
        amount,
        context,
    ):
        assert customer_id == "customer-123"
        assert source == "subscription_failure"
        assert amount == 3000
        assert context == {"failure_count": 3}

        return (
            SimpleNamespace(id="case-456"),
            {
                "risk_score": 70,
                "recommended_action": "subscription_recovery",
            },
        )

    monkeypatch.setattr(
        subscriptions,
        "record_subscription_event",
        fake_record_subscription_event,
    )
    monkeypatch.setattr(
        subscriptions,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-123",
            "status": "failed",
            "amount": 3000,
            "failure_count": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["subscription_id"] == "sub-456"
    assert data["recovery_case_id"] == "case-456"
    assert data["decision"]["risk_score"] == 70
    assert data["decision"]["recommended_action"] == "subscription_recovery"


def test_failed_subscription_default_amount_and_failure_count(monkeypatch):
    def fake_record_subscription_event(db, payload):
        return SimpleNamespace(id="sub-789")

    def fake_create_case(
        db,
        customer_id,
        source,
        amount,
        context,
    ):
        assert customer_id == "customer-789"
        assert source == "subscription_failure"
        assert amount == 0
        assert context == {"failure_count": 1}

        return (
            SimpleNamespace(id="case-789"),
            {"risk_score": 60},
        )

    monkeypatch.setattr(
        subscriptions,
        "record_subscription_event",
        fake_record_subscription_event,
    )
    monkeypatch.setattr(
        subscriptions,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/event",
        json={
            "customer_id": "customer-789",
            "status": "failed",
        },
    )

    assert response.status_code == 200
    assert response.json()["subscription_id"] == "sub-789"
    assert response.json()["recovery_case_id"] == "case-789"