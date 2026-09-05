import pytest
from pydantic import ValidationError

from app.schemas.recovery import (
    RecoveryDecision,
    ExecuteRecovery,
)


def test_recovery_decision():
    decision = RecoveryDecision(
        risk_score=35.0,
        root_cause="PAYMENT_GATEWAY",
        recommended_action="INSTANT_UPI_FALLBACK",
        channel="WHATSAPP",
        priority="HIGH",
        reason="Bank server timeout detected.",
    )

    assert decision.risk_score == 35.0
    assert decision.root_cause == "PAYMENT_GATEWAY"
    assert decision.recommended_action == "INSTANT_UPI_FALLBACK"
    assert decision.channel == "WHATSAPP"
    assert decision.priority == "HIGH"
    assert decision.reason == "Bank server timeout detected."


def test_execute_recovery():
    recovery = ExecuteRecovery(
        channel="WHATSAPP",
    )

    assert recovery.channel == "WHATSAPP"


def test_execute_recovery_without_channel():
    recovery = ExecuteRecovery()

    assert recovery.channel is None


def test_risk_score_cannot_exceed_100():
    with pytest.raises(ValidationError):
        RecoveryDecision(
            risk_score=101,
            root_cause="PAYMENT_GATEWAY",
            recommended_action="RETRY",
            channel="WHATSAPP",
            priority="HIGH",
            reason="Test",
        )


def test_risk_score_cannot_be_negative():
    with pytest.raises(ValidationError):
        RecoveryDecision(
            risk_score=-1,
            root_cause="PAYMENT_GATEWAY",
            recommended_action="RETRY",
            channel="WHATSAPP",
            priority="HIGH",
            reason="Test",
        )