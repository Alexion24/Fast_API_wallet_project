from pydantic import BaseModel, Field
from enum import Enum

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: float = Field(..., gt=0)

class BalanceResponse(BaseModel):
    balance: float
