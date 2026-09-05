from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import (
    Base,
    Customer,
    Payment,
    CheckoutEvent,
    Subscription,
    Invoice,
    RecoveryCase,
    Intervention,
    RootCauseCategory,
    RecoveryCaseStatus,
    CommunicationChannel,
)


def test_all_tables_exist():
    expected_tables = {
        "customers",
        "payments",
        "checkout_events",
        "subscriptions",
        "invoices",
        "recovery_cases",
        "interventions",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_customer_model():
    customer = Customer(
        name="Test Customer",
        email="test@example.com",
        phone="9999999999",
    )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(customer)
        session.flush()

        assert customer.name == "Test Customer"
        assert customer.email == "test@example.com"
        assert customer.segment == "standard"
        assert customer.lifetime_value == 0.0
        assert customer.id is not None


def test_payment_model():
    payment = Payment(
        customer_id="customer-1",
        amount=4999.0,
        currency="INR",
        status="failed",
        failure_reason="TIMEOUT",
    )

    assert payment.amount == 4999.0
    assert payment.status == "failed"
    assert payment.failure_reason == "TIMEOUT"


def test_recovery_case_model():
    case = RecoveryCase(
        customer_id="customer-1",
        source="payment",
        amount_at_risk=4999.0,
        risk_score=35.0,
        root_cause=RootCauseCategory.PAYMENT_GATEWAY,
        status=RecoveryCaseStatus.OPEN,
    )

    assert case.amount_at_risk == 4999.0
    assert case.risk_score == 35.0
    assert case.root_cause == RootCauseCategory.PAYMENT_GATEWAY
    assert case.status == RecoveryCaseStatus.OPEN


def test_intervention_relationship():
    case = RecoveryCase(
        customer_id="customer-1",
        source="payment",
        amount_at_risk=4999.0,
        risk_score=35.0,
        root_cause=RootCauseCategory.PAYMENT_GATEWAY,
    )

    intervention = Intervention(
        type="UPI_FALLBACK",
        channel=CommunicationChannel.WHATSAPP,
        message="Please complete your payment.",
    )

    case.interventions.append(intervention)

    assert len(case.interventions) == 1
    assert case.interventions[0].type == "UPI_FALLBACK"
    assert case.interventions[0].channel == CommunicationChannel.WHATSAPP


def test_enum_values():
    assert RootCauseCategory.PAYMENT_GATEWAY.value == "PAYMENT_GATEWAY"
    assert RecoveryCaseStatus.OPEN.value == "OPEN"
    assert CommunicationChannel.WHATSAPP.value == "WHATSAPP"