from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import receivables


app = FastAPI()
app.include_router(receivables.router)

client = TestClient(app)


def test_normal_invoice(monkeypatch):
    def fake_record_invoice(db, payload):
        return SimpleNamespace(id="invoice-123")

    def fake_create_case(*args, **kwargs):
        raise AssertionError(
            "create_case should not be called for a normal invoice"
        )

    monkeypatch.setattr(
        receivables,
        "record_invoice",
        fake_record_invoice,
    )
    monkeypatch.setattr(
        receivables,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/invoice",
        json={
            "customer_id": "customer-123",
            "amount": 5000,
            "status": "open",
            "days_overdue": 0,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "invoice_id": "invoice-123",
        "recovery_case_id": None,
        "decision": None,
    }


def test_overdue_invoice_creates_recovery_case(monkeypatch):
    def fake_record_invoice(db, payload):
        return SimpleNamespace(id="invoice-456")

    def fake_create_case(
        db,
        customer_id,
        source,
        amount,
        context,
    ):
        assert customer_id == "customer-123"
        assert source == "overdue_invoice"
        assert amount == 10000
        assert context == {"days_overdue": 45}

        return (
            SimpleNamespace(id="case-456"),
            {
                "risk_score": 80,
                "recommended_action": "receivables_chase",
            },
        )

    monkeypatch.setattr(
        receivables,
        "record_invoice",
        fake_record_invoice,
    )
    monkeypatch.setattr(
        receivables,
        "create_case",
        fake_create_case,
    )

    response = client.post(
        "/invoice",
        json={
            "customer_id": "customer-123",
            "amount": 10000,
            "status": "overdue",
            "days_overdue": 45,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["invoice_id"] == "invoice-456"
    assert data["recovery_case_id"] == "case-456"
    assert data["decision"]["risk_score"] == 80
    assert data["decision"]["recommended_action"] == "receivables_chase"


def test_overdue_invoices(monkeypatch):
    class FakeQuery:
        def filter(self, *args):
            return self

        def all(self):
            return [
                SimpleNamespace(
                    id="invoice-1",
                    customer_id="customer-1",
                    amount=5000,
                    days_overdue=10,
                ),
                SimpleNamespace(
                    id="invoice-2",
                    customer_id="customer-2",
                    amount=12000,
                    days_overdue=45,
                ),
            ]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    app.dependency_overrides[receivables.get_db] = lambda: FakeDB()

    response = client.get("/overdue")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "invoice-1",
            "customer_id": "customer-1",
            "amount": 5000,
            "days_overdue": 10,
        },
        {
            "id": "invoice-2",
            "customer_id": "customer-2",
            "amount": 12000,
            "days_overdue": 45,
        },
    ]

    app.dependency_overrides.clear()