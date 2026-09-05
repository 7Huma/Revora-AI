import requests

BASE = "http://localhost:8000"

events = [
    {
        "customer_id": 1, "amount": 4999, "currency": "INR",
        "status": "failed", "failure_reason": "insufficient_funds",
        "payment_method": "card"
    },
    {
        "customer_id": 2, "amount": 7999, "currency": "INR",
        "status": "failed", "failure_reason": "bank_declined",
        "payment_method": "upi"
    },
]

for event in events:
    response = requests.post(f"{BASE}/payments/event", json=event, timeout=10)
    print(response.status_code, response.json())
