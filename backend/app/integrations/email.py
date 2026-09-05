class EmailClient:
    def send(self, subject: str, body: str):
        return {"success": True, "provider": "mock_email", "subject": subject}
