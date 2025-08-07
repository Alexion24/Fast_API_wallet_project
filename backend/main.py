from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
import uuid

from . import crud, schemas
from .database import AsyncSessionLocal

app = FastAPI()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post(
    "/api/v1/wallets/{wallet_uuid}/operation", response_model=schemas.BalanceResponse
)
async def wallet_operation(
    wallet_uuid: uuid.UUID = Path(...),
    operation: schemas.OperationRequest = ...,
    session: AsyncSession = Depends(get_session),
):
    try:
        wallet = await crud.operate_wallet_balance(
            session,
            wallet_uuid,
            Decimal(str(operation.amount)),
            operation.operation_type,
        )
        return schemas.BalanceResponse(balance=float(wallet.balance))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/wallets/{wallet_uuid}", response_model=schemas.BalanceResponse)
async def get_balance(
    wallet_uuid: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    wallet = await crud.get_wallet(session, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return schemas.BalanceResponse(balance=float(wallet.balance))
