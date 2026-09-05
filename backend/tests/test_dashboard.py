from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import dashboard


app = FastAPI()
app.include_router(dashboard.router)

client = TestClient(app)


class FakeQuery:
    def __init__(self, rows=None, scalar_value=None, count_value=0):
        self.rows = rows or []
        self.scalar_value = scalar_value
        self.count_value = count_value

    def scalar(self):
        return self.scalar_value

    def filter(self, *args):
        return self

    def count(self):
        return self.count_value

    def all(self):
        return self.rows


class FakeDB:
    def query(self, model_or_expression):
        if model_or_expression is dashboard.RecoveryCase:
            return FakeQuery(
                rows=[
                    SimpleNamespace(
                        id="case-1",
                        source="payment_failure",
                        amount_at_risk=1000,
                        risk_score=50,
                    ),
                    SimpleNamespace(
                        id="case-2",
                        source="overdue_invoice",
                        amount_at_risk=2000,
                        risk_score=80,
                    ),
                ],
                count_value=2,
            )

        if model_or_expression is dashboard.Intervention:
            return FakeQuery(
                rows=[
                    SimpleNamespace(
                        id="int-1",
                        recovery_case_id="case-1",
                        recovered_amount=500,
                        result="SUCCESS",
                    ),
                    SimpleNamespace(
                        id="int-2",
                        recovery_case_id="case-2",
                        recovered_amount=1000,
                        result="SUCCESS",
                    ),
                ]
            )

        return FakeQuery(scalar_value=3000)


def test_revenue_at_risk():
    app.dependency_overrides[dashboard.get_db] = lambda: FakeDB()

    response = client.get("/revenue-at-risk")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "case-1",
            "source": "payment_failure",
            "amount": 1000,
            "risk_score": 50,
        },
        {
            "id": "case-2",
            "source": "overdue_invoice",
            "amount": 2000,
            "risk_score": 80,
        },
    ]

    app.dependency_overrides.clear()


def test_recovered_revenue():
    app.dependency_overrides[dashboard.get_db] = lambda: FakeDB()

    response = client.get("/recovered-revenue")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "int-1",
            "case_id": "case-1",
            "recovered_amount": 500,
            "result": "SUCCESS",
        },
        {
            "id": "int-2",
            "case_id": "case-2",
            "recovered_amount": 1000,
            "result": "SUCCESS",
        },
    ]

    app.dependency_overrides.clear()


def test_summary():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db.models import Base, RecoveryCase, Intervention

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    db = Session()

    db.add_all([
        RecoveryCase(
            id="case-1",
            customer_id="customer-1",
            source="payment_failure",
            amount_at_risk=1000,
            risk_score=50,
            root_cause="PAYMENT_GATEWAY",
        ),
        RecoveryCase(
            id="case-2",
            customer_id="customer-2",
            source="overdue_invoice",
            amount_at_risk=2000,
            risk_score=80,
            root_cause="INVOICE_OVERDUE",
        ),
    ])

    db.add_all([
        Intervention(
            id="int-1",
            recovery_case_id="case-1",
            type="retry",
            channel="PAYMENT_GATEWAY",
            recovered_amount=500,
            result="SUCCESS",
        ),
        Intervention(
            id="int-2",
            recovery_case_id="case-2",
            type="followup",
            channel="EMAIL",
            recovered_amount=1000,
            result="SUCCESS",
        ),
    ])

    db.commit()

    app.dependency_overrides[dashboard.get_db] = lambda: db

    response = client.get("/summary")

    assert response.status_code == 200
    assert response.json() == {
        "revenue_at_risk": 3000,
        "recovered_revenue": 1500,
        "recovery_rate": 50,
        "active_cases": 2,
    }

    app.dependency_overrides.clear()
    db.close()