import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def new_id() -> str:
    """Generate a unique string ID for database records."""
    return str(uuid.uuid4())


# ============================================================
# ENUMS
# ============================================================

class RiskScoreCategory(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RootCauseCategory(str, enum.Enum):
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"
    CHECKOUT_DROP_OFF = "CHECKOUT_DROP_OFF"
    SUBSCRIPTION_FAILED = "SUBSCRIPTION_FAILED"
    INVOICE_OVERDUE = "INVOICE_OVERDUE"


class RecoveryCaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class CommunicationChannel(str, enum.Enum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    EMAIL = "EMAIL"
    VOICE_CALL = "VOICE_CALL"
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"
    SYSTEM = "SYSTEM"


# ============================================================
# CUSTOMER
# ============================================================

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        default="",
    )

    segment: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False,
    )

    lifetime_value: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )
# ============================================================
# PAYMENT
# ============================================================

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        default=None,
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        default="card",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )


# ============================================================
# CHECKOUT EVENT
# ============================================================

class CheckoutEvent(Base):
    __tablename__ = "checkout_events"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    cart_value: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        default="started",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )


# ============================================================
# SUBSCRIPTION
# ============================================================

class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    plan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
    )

    next_billing_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )


# ============================================================
# INVOICE
# ============================================================

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="open",
    )

    days_overdue: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )


# ============================================================
# RECOVERY CASE
# ============================================================

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    amount_at_risk: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    root_cause: Mapped[RootCauseCategory] = mapped_column(
        Enum(RootCauseCategory),
        nullable=False,
    )

    reason_detail: Mapped[Optional[str]] = mapped_column(
        String(100),
        default=None,
    )

    suggested_action: Mapped[Optional[str]] = mapped_column(
        String(100),
        default=None,
    )

    agent_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        default=None,
    )

    status: Mapped[RecoveryCaseStatus] = mapped_column(
        Enum(RecoveryCaseStatus),
        default=RecoveryCaseStatus.OPEN,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )


# ============================================================
# INTERVENTION
# ============================================================

class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=new_id,
    )

    recovery_case_id: Mapped[str] = mapped_column(
        ForeignKey("recovery_cases.id"),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    channel: Mapped[CommunicationChannel] = mapped_column(
        Enum(CommunicationChannel),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    result: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
    )

    recovered_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    case: Mapped["RecoveryCase"] = relationship(
        back_populates="interventions",
    )