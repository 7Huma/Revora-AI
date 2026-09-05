from datetime import datetime
from app.models.invoice import Invoice

def record_invoice(db, payload):
    invoice = Invoice(
        customer_id=payload["customer_id"],
        amount=payload["amount"],
        due_date=datetime.utcnow(),
        status=payload.get("status", "open"),
        days_overdue=payload.get("days_overdue", 0),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
