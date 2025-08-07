import pytest
import uuid
import asyncio


@pytest.mark.asyncio
async def test_concurrent_operations(async_client, test_wallet):
    """Тест конкурентных операций с кошельком"""
    # Создаем список конкурентных операций
    operations = [
        async_client.post(
            f"/api/v1/wallets/{test_wallet.uuid}/operation",
            json={"operation_type": "DEPOSIT", "amount": 10.00},
        )
        for _ in range(5)
    ]

    # Выполняем операции конкурентно
    responses = await asyncio.gather(*operations)

    # Проверяем, что все операции выполнились успешно
    for response in responses:
        assert response.status_code == 200

    # Проверяем финальный баланс (100 + 5 * 10 = 150)
    final_response = await async_client.get(f"/api/v1/wallets/{test_wallet.uuid}")
    assert final_response.status_code == 200
    assert final_response.json() == {"balance": 150.00}


@pytest.mark.asyncio
async def test_get_wallet_balance(async_client, test_wallet):
    response = await async_client.get(f"/api/v1/wallets/{test_wallet.uuid}")
    assert response.status_code == 200
    assert response.json() == {"balance": 100.00}


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(async_client):
    response = await async_client.get(f"/api/v1/wallets/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deposit_operation(async_client, test_wallet):
    response = await async_client.post(
        f"/api/v1/wallets/{test_wallet.uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": 50.00},
    )
    assert response.status_code == 200
    assert response.json() == {"balance": 150.00}


@pytest.mark.asyncio
async def test_withdraw_operation(async_client, test_wallet):
    response = await async_client.post(
        f"/api/v1/wallets/{test_wallet.uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": 50.00},
    )
    assert response.status_code == 200
    assert response.json() == {"balance": 50.00}
