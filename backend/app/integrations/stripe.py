class StripeClient:
    def retry_payment(self, payment_id: str):
        return {"success": True, "payment_id": payment_id, "provider": "stripe_adapter"}
