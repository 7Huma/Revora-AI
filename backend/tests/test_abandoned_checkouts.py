from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import checkouts


app = FastAPI()
app.include_router(checkouts.router)

client = TestClient(app)


class FakeQuery:
    def filter(self, *args):
        return self

    def all(self):
        return [
            SimpleNamespace(
                id="checkout-1",
                session_id="session-1",
                cart_value=2500,
            ),
            SimpleNamespace(
                id="checkout-2",
                session_id="session-2",
                cart_value=5000,
            ),
        ]


class FakeDB:
    def query(self, model):
        return FakeQuery()





def test_abandoned_checkouts_with_fake_db():
    app.dependency_overrides[checkouts.get_db] = lambda: FakeDB()

    response = client.get("/abandoned")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "checkout-1",
            "session_id": "session-1",
            "cart_value": 2500,
        },
        {
            "id": "checkout-2",
            "session_id": "session-2",
            "cart_value": 5000,
        },
    ]

    app.dependency_overrides.clear()