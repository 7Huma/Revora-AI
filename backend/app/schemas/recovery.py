from pydantic import BaseModel, Field


class RecoveryDecision(BaseModel):
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
    )

    root_cause: str = Field(
        ...,
        min_length=1,
    )

    recommended_action: str = Field(
        ...,
        min_length=1,
    )

    channel: str = Field(
        ...,
        min_length=1,
    )

    priority: str = Field(
        ...,
        min_length=1,
    )

    reason: str = Field(
        ...,
        min_length=1,
    )


class ExecuteRecovery(BaseModel):
    channel: str | None = Field(
        default=None,
        min_length=1,
    )