import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def new_wallet_uuid():
    # При инициализации тестовой среды можно добавить создание кошелька (через фикстуру или init)
    return str(uuid.uuid4())

def test_deposit_and_withdraw(new_wallet_uuid):
    wallet_uuid = new_wallet_uuid

    # Для тестов нужно заранее создать кошелек в БД (например, через фикстуру)

    deposit_resp = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": 500}
    )
    assert deposit_resp.status_code == 200
    assert deposit_resp.json()["balance"] == 500

    withdraw_resp = client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200}
    )
    assert withdraw_resp.status_code == 200
    assert withdraw_resp.json()["balance"] == 300

    balance_resp = client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert balance_resp.status_code == 200
    assert balance_resp.json()["balance"] == 300
