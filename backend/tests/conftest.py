import os
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend import models
from backend.database import get_session
from backend.main import app
import httpx

TEST_DATABASE_URL = os.getenv("DATABASE_URL")
assert (
    TEST_DATABASE_URL is not None
), "DATABASE_URL должен быть установлен на тестовую БД"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncSessionTest = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    # Создаем таблицы перед тестами и удаляем их после
    async with engine_test.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session(prepare_database):
    async with AsyncSessionTest() as session:
        async with session.begin():
            yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    base_url = os.getenv("APP_BASE_URL", "http://app:8000")

    async with httpx.AsyncClient(base_url=base_url) as ac:
        yield ac

    app.dependency_overrides.clear()
