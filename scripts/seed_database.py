import csv
from pathlib import Path
from datetime import datetime
from app.db.database import Base, engine, SessionLocal
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.checkout import CheckoutEvent
from app.models.invoice import Invoice
from app.services.recovery_service import create_case

ROOT = Path(__file__).resolve().parents[1]
Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    if db.query(Customer).count() == 0:
        with open(ROOT / "data/customers.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Customer(
                    id=int(row["id"]), name=row["name"], email=row["email"],
                    phone=row["phone"], segment=row["segment"],
                    lifetime_value=float(row["lifetime_value"])
                ))
        db.commit()

    if db.query(Payment).count() == 0:
        with open(ROOT / "data/payments.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Payment(
                    id=int(row["id"]), customer_id=int(row["customer_id"]),
                    amount=float(row["amount"]), currency=row["currency"],
                    status=row["status"], failure_reason=row["failure_reason"],
                    payment_method=row["payment_method"], timestamp=datetime.utcnow()
                ))
        db.commit()

    if db.query(CheckoutEvent).count() == 0:
        with open(ROOT / "data/checkouts.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(CheckoutEvent(
                    id=int(row["id"]), customer_id=int(row["customer_id"]),
                    session_id=row["session_id"], cart_value=float(row["cart_value"]),
                    event_type=row["event_type"], timestamp=datetime.utcnow()
                ))
        db.commit()

    if db.query(Invoice).count() == 0:
        with open(ROOT / "data/invoices.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                db.add(Invoice(
                    id=int(row["id"]), customer_id=int(row["customer_id"]),
                    amount=float(row["amount"]), due_date=datetime.utcnow(),
                    status=row["status"], days_overdue=int(row["days_overdue"])
                ))
        db.commit()

    if db.query(__import__("app.models.recovery_case", fromlist=["RecoveryCase"]).RecoveryCase).count() == 0:
        create_case(db, 1, "payment_failure", 4999, {"failure_reason": "insufficient_funds"})
        create_case(db, 2, "checkout_abandonment", 7999, {})
        create_case(db, 3, "overdue_invoice", 120000, {"days_overdue": 22})

    print("Database seeded successfully.")
finally:
    db.close()
