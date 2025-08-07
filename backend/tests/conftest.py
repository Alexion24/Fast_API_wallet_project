import asyncio
import pytest
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.models import Base, Wallet
from backend.main import app
from backend.database import AsyncSessionLocal
import uuid
from decimal import Decimal

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/test_wallet"


@pytest.fixture(scope="session")
def event_loop():
    """Создаем единый цикл событий для всех тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine(event_loop):
    """Создаем движок базы данных с правильными настройками пула"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
        pool_size=20,  # Увеличиваем размер пула
        max_overflow=20,
        future=True,
        pool_timeout=30,  # Добавляем таймаут для пула
        isolation_level="REPEATABLE READ",  # Устанавливаем уровень изоляции
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def async_session_maker(test_engine):
    """Создаем фабрику сессий"""
    return async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )


@pytest.fixture
async def test_session(async_session_maker, event_loop):
    """Создаем тестовую сессию"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def async_client(async_session_maker, event_loop):
    """Создаем тестовый клиент"""

    async def override_get_session():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[AsyncSessionLocal] = override_get_session

    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=True,
    )

    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=30.0
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_wallet(test_session):
    """Создаем тестовый кошелек"""
    wallet = Wallet(uuid=uuid.uuid4(), balance=Decimal("100.00"))
    test_session.add(wallet)
    await test_session.commit()
    await test_session.refresh(wallet)
    return wallet
