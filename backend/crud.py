from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Wallet
from decimal import Decimal


async def get_wallet(session: AsyncSession, wallet_uuid):
    result = await session.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
    return result.scalar_one_or_none()


async def operate_wallet_balance(
    session: AsyncSession, wallet_uuid, amount: Decimal, operation_type: str
):
    async with session.begin_nested():  # Используем вложенную транзакцию
        wallet = (
            await session.execute(
                select(Wallet)
                .where(Wallet.uuid == wallet_uuid)
                .with_for_update(
                    nowait=True
                )  # Добавляем nowait для избежания взаимоблокировок
            )
        ).scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet not found")

        if operation_type == "DEPOSIT":
            wallet.balance += amount
        elif operation_type == "WITHDRAW":
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")
            wallet.balance -= amount
        else:
            raise ValueError("Invalid operation type")

        session.add(wallet)
        await session.flush()  # Принудительно сбрасываем изменения

    return wallet
