from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.checkout_service import record_checkout
from app.services.recovery_service import create_case
from app.models.checkout import CheckoutEvent

router = APIRouter()

@router.post("/event")
def checkout_event(payload: dict, db: Session = Depends(get_db)):
    event = record_checkout(db, payload)
    case = None
    if payload.get("event_type") == "abandoned":
        case, decision = create_case(
            db, payload.get("customer_id"), "checkout_abandonment",
            payload.get("cart_value", 0), {}
        )
    else:
        decision = None
    return {"checkout_event_id": event.id, "recovery_case_id": getattr(case, "id", None), "decision": decision}

@router.get("/abandoned")
def abandoned_checkouts(db: Session = Depends(get_db)):
    from app.models.checkout import CheckoutEvent
    rows = db.query(CheckoutEvent).filter(CheckoutEvent.event_type == "abandoned").all()
    return [{"id": x.id, "session_id": x.session_id, "cart_value": x.cart_value} for x in rows]
