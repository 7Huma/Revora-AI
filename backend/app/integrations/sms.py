class SMSClient:
    def send(self, phone: str, message: str):
        return {"success": True, "provider": "mock_sms", "phone": phone}
