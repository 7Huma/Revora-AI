from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.payment import PaymentEvent
from app.services.payment_service import record_payment
from app.services.recovery_service import create_case

router = APIRouter()


@router.post("/event")
def payment_event(event: PaymentEvent, db: Session = Depends(get_db)):
    payment = record_payment(db, event)
    case = None
    decision = None

    if event.status.lower() == "failed":
        case, decision = create_case(
            db,
            event.customer_id,
            "payment_failure",
            event.amount,
            {
                "event_type": "payment.failed",
                "failure_code": event.failure_reason,
                "failure_description": event.failure_reason,
            },
        )

    return {
        "payment_id": payment.id,
        "recovery_case_id": getattr(case, "id", None),
        "decision": decision,
    }
