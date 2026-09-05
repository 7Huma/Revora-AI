from datetime import datetime
from app.models.checkout import CheckoutEvent

def record_checkout(db, payload):
    event = CheckoutEvent(
        customer_id=payload.get("customer_id"),
        session_id=payload["session_id"],
        cart_value=payload.get("cart_value", 0),
        event_type=payload.get("event_type", "started"),
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
