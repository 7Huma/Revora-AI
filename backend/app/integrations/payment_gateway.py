class PaymentGateway:
    def retry(self, amount: float):
        # Safe demo adapter. Replace with Stripe/Razorpay/etc. in production.
        return {"success": True, "amount": amount, "provider": "mock_gateway"}
