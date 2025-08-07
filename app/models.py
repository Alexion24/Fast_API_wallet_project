from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
