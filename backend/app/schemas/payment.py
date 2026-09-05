from datetime import datetime

from pydantic import BaseModel, Field


class PaymentEvent(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=50)

    amount: float = Field(..., gt=0)

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=10,
    )

    status: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )

    failure_reason: str = Field(
        default="",
        max_length=500,
    )

    payment_method: str = Field(
        default="card",
        min_length=1,
        max_length=30,
    )

    timestamp: datetime | None = None