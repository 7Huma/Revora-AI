import pytest
from pydantic import ValidationError

from app.schemas.dashboard import DashboardSummary


def test_dashboard_summary():
    summary = DashboardSummary(
        revenue_at_risk=100000.0,
        recovered_revenue=25000.0,
        recovery_rate=25.0,
        active_cases=10,
    )

    assert summary.revenue_at_risk == 100000.0
    assert summary.recovered_revenue == 25000.0
    assert summary.recovery_rate == 25.0
    assert summary.active_cases == 10


def test_dashboard_defaults():
    summary = DashboardSummary()

    assert summary.revenue_at_risk == 0.0
    assert summary.recovered_revenue == 0.0
    assert summary.recovery_rate == 0.0
    assert summary.active_cases == 0


def test_negative_revenue_at_risk_rejected():
    with pytest.raises(ValidationError):
        DashboardSummary(revenue_at_risk=-100)


def test_recovery_rate_above_100_rejected():
    with pytest.raises(ValidationError):
        DashboardSummary(recovery_rate=101)


def test_negative_active_cases_rejected():
    with pytest.raises(ValidationError):
        DashboardSummary(active_cases=-1)