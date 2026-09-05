from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.receivable_service import record_invoice
from app.services.recovery_service import create_case

router = APIRouter()

@router.post("/invoice")
def invoice(payload: dict, db: Session = Depends(get_db)):
    inv = record_invoice(db, payload)
    case = None
    decision = None
    if payload.get("status", "open") == "overdue":
        case, decision = create_case(
            db, payload["customer_id"], "overdue_invoice",
            payload["amount"],
            {"days_overdue": payload.get("days_overdue", 0)}
        )
    return {"invoice_id": inv.id, "recovery_case_id": getattr(case, "id", None), "decision": decision}

@router.get("/overdue")
def overdue(db: Session = Depends(get_db)):
    from app.models.invoice import Invoice
    rows = db.query(Invoice).filter(Invoice.status == "overdue").all()
    return [{"id": x.id, "customer_id": x.customer_id, "amount": x.amount, "days_overdue": x.days_overdue} for x in rows]
