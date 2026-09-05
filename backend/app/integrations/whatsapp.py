class WhatsAppClient:
    def send(self, phone: str, message: str):
        return {"success": True, "provider": "mock_whatsapp", "phone": phone}
