from pydantic import BaseModel, field_validator

from datetime import date

from typing import TypedDict

class Transaction(TypedDict):
    transaction_id: int
    account_id: int
    category_id: int
    type: str
    amount: float
    description: str | None
    date: date

class AddTransactionRequest(BaseModel):
    account_id: int
    category_id: int
    amount: float
    description: str | None = None
    date: date

    @field_validator('amount')
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v