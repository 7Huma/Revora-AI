from datetime import datetime
from app.models.subscription import Subscription

def record_subscription_event(db, payload):
    subscription = Subscription(
        customer_id=payload["customer_id"],
        plan=payload.get("plan", "unknown"),
        amount=payload.get("amount", 0),
        status=payload.get("status", "failed"),
        next_billing_date=datetime.utcnow(),
        failure_count=payload.get("failure_count", 1),
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
