from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.classifier import analyze_root_cause
from app.db.models import Base, Customer, RecoveryCaseStatus, RootCauseCategory
from app.services.recovery_service import create_case


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_classifier_is_independent():
    result = analyze_root_cause(
        "payment.failed",
        "TIMEOUT",
        "Bank server timed out",
    )
    assert result["root_cause"] == RootCauseCategory.PAYMENT_GATEWAY
    assert result["suggested_action"] == "INSTANT_UPI_FALLBACK"


def test_event_to_recovery_case_pipeline():
    db = make_db()
    customer = Customer(name="Demo Customer", email="demo@example.com")
    db.add(customer)
    db.commit()
    db.refresh(customer)

    case, diagnosis = create_case(
        db,
        customer.id,
        "payment_failure",
        4999,
        {
            "event_type": "payment.failed",
            "failure_code": "TIMEOUT",
            "failure_description": "Bank server timed out",
        },
    )

    assert case.id
    assert case.customer_id == customer.id
    assert case.amount_at_risk == 4999
    assert case.risk_score == 35.0
    assert case.root_cause == RootCauseCategory.PAYMENT_GATEWAY
    assert case.status == RecoveryCaseStatus.OPEN
    assert diagnosis["reason_detail"] == "BANK_SERVER_TIMEOUT"
