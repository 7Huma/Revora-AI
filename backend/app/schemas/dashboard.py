from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    revenue_at_risk: float = Field(
        default=0.0,
        ge=0.0,
    )

    recovered_revenue: float = Field(
        default=0.0,
        ge=0.0,
    )

    expected_recovery: float = Field(
        default=0.0,
        ge=0.0,
    )

    recovery_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    active_cases: int = Field(
        default=0,
        ge=0,
    )