from datetime import datetime

from app.db.models import Payment


def record_payment(db, event):
    payment = Payment(
        customer_id=str(event.customer_id),
        amount=event.amount,
        currency=event.currency,
        status=event.status,
        failure_reason=event.failure_reason or None,
        payment_method=event.payment_method,
        timestamp=event.timestamp or datetime.utcnow(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
