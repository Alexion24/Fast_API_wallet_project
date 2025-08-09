import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_balance_not_found(client):
    wallet_uuid = uuid4()
    response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Wallet not found"}


@pytest.mark.asyncio
async def test_wallet_operation_invalid(client):
    wallet_uuid = uuid4()
    operation_data = {"amount": -10, "operation_type": "invalid_type"}

    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation", json=operation_data
    )
    # Ожидаем 422, так как данные не проходят Pydantic валидацию
    assert response.status_code == 422
    assert "detail" in response.json()
