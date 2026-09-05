import pytest

from app.agents.outcome_analyzer import analyze_outcome


def test_full_recovery():
    result = analyze_outcome(
        at_risk=10000,
        recovered=10000,
    )

    assert result["recovered_amount"] == 10000
    assert result["recovery_rate"] == 100.0
    assert result["success"] is True


def test_partial_recovery():
    result = analyze_outcome(
        at_risk=10000,
        recovered=2500,
    )

    assert result["recovered_amount"] == 2500
    assert result["recovery_rate"] == 25.0
    assert result["success"] is True


def test_no_recovery():
    result = analyze_outcome(
        at_risk=10000,
        recovered=0,
    )

    assert result["recovered_amount"] == 0
    assert result["recovery_rate"] == 0.0
    assert result["success"] is False


def test_zero_amount_at_risk():
    result = analyze_outcome(
        at_risk=0,
        recovered=0,
    )

    assert result["recovery_rate"] == 0.0
    assert result["success"] is False


def test_decimal_recovery_rate():
    result = analyze_outcome(
        at_risk=3000,
        recovered=1000,
    )

    assert result["recovery_rate"] == 33.33
    assert result["success"] is True


def test_negative_at_risk_rejected():
    with pytest.raises(ValueError):
        analyze_outcome(
            at_risk=-1000,
            recovered=500,
        )


def test_negative_recovered_rejected():
    with pytest.raises(ValueError):
        analyze_outcome(
            at_risk=1000,
            recovered=-500,
        )


def test_recovered_cannot_exceed_at_risk():
    with pytest.raises(ValueError):
        analyze_outcome(
            at_risk=1000,
            recovered=1500,
        )