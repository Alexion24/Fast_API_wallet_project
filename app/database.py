from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/wallet")

engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для отладки запросов
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
