from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/test_wallet"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionMaker = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_session():
    async with TestSessionMaker() as session:
        try:
            yield session
        finally:
            await session.close()
