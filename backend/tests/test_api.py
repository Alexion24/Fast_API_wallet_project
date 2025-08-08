import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from httpx import AsyncClient
from backend.models import Base, Wallet
from backend.main import app, get_session
from .test_database import test_engine, get_test_session

# Переопределяем зависимость
app.dependency_overrides[get_session] = get_test_session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_wallet():
    async with TestSessionMaker() as session:
        wallet = Wallet(balance=Decimal("100.00"))
        session.add(wallet)
        await session.commit()
        await session.refresh(wallet)
        return str(wallet.uuid)


@pytest.mark.asyncio
async def test_get_wallet_balance(client, test_wallet):
    response = await client.get(f"/api/v1/wallets/{test_wallet}")
    assert response.status_code == 200
    assert response.json()["balance"] == 100.00


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(client):
    response = await client.get(f"/api/v1/wallets/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deposit_operation(client, test_wallet):
    response = await client.post(
        f"/api/v1/wallets/{test_wallet}/operation",
        json={"operation_type": "DEPOSIT", "amount": 50.00},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 150.00


@pytest.mark.asyncio
async def test_withdraw_operation(client, test_wallet):
    response = await client.post(
        f"/api/v1/wallets/{test_wallet}/operation",
        json={"operation_type": "WITHDRAW", "amount": 50.00},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 50.00
