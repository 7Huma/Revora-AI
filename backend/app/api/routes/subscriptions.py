from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.subscription_service import record_subscription_event
from app.services.recovery_service import create_case

router = APIRouter()

@router.post("/event")
def subscription_event(payload: dict, db: Session = Depends(get_db)):
    sub = record_subscription_event(db, payload)
    case = None
    decision = None
    if payload.get("status") == "failed":
        case, decision = create_case(
            db, payload["customer_id"], "subscription_failure",
            payload.get("amount", 0),
            {"failure_count": payload.get("failure_count", 1)}
        )
    return {"subscription_id": sub.id, "recovery_case_id": getattr(case, "id", None), "decision": decision}
