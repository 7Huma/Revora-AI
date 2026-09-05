from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import recovery


app = FastAPI()
app.include_router(recovery.router)

client = TestClient(app)


def make_case():
    return SimpleNamespace(
        id="case-123",
        customer_id="customer-123",
        source="payment_failure",
        amount_at_risk=5000,
        risk_score=75,
        root_cause="payment_degradation",
        status="open",
        agent_reason="Retry recoverable payment",
        reason_detail="INSUFFICIENT_FUNDS",
        suggested_action="retry_payment",
        created_at="2026-01-01",
    )


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def order_by(self, *args):
        return self

    def all(self):
        return self.rows


class FakeDB:
    def __init__(self, case=None):
        self.case = case

    def query(self, model):
        return FakeQuery([self.case] if self.case else [])

    def get(self, model, case_id):
        if self.case and case_id == self.case.id:
            return self.case
        return None


def test_list_cases():
    app.dependency_overrides[recovery.get_db] = lambda: FakeDB(make_case())

    response = client.get("/cases")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == "case-123"
    assert data[0]["customer_id"] == "customer-123"
    assert data[0]["source"] == "payment_failure"
    assert data[0]["amount_at_risk"] == 5000
    assert data[0]["risk_score"] == 75

    app.dependency_overrides.clear()


def test_get_case():
    app.dependency_overrides[recovery.get_db] = lambda: FakeDB(make_case())

    response = client.get("/cases/case-123")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "case-123"
    assert data["source"] == "payment_failure"
    assert data["status"] == "open"

    app.dependency_overrides.clear()


def test_get_missing_case():
    app.dependency_overrides[recovery.get_db] = lambda: FakeDB()

    response = client.get("/cases/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recovery case not found"

    app.dependency_overrides.clear()


def test_execute_case(monkeypatch):
    case = make_case()

    def fake_execute_case(db, case_obj, channel=None):
        assert case_obj.id == "case-123"
        assert channel == "email"

        return {
            "status": "recovery_attempted",
            "action": "retry_payment",
            "channel": "email",
        }

    monkeypatch.setattr(
        recovery,
        "execute_case",
        fake_execute_case,
    )

    app.dependency_overrides[recovery.get_db] = lambda: FakeDB(case)

    response = client.post(
        "/execute/case-123",
        json={"channel": "email"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "recovery_attempted",
        "action": "retry_payment",
        "channel": "email",
    }

    app.dependency_overrides.clear()


def test_execute_missing_case():
    app.dependency_overrides[recovery.get_db] = lambda: FakeDB()

    response = client.post("/execute/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recovery case not found"

    app.dependency_overrides.clear()