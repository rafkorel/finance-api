from pydantic import BaseModel, Field, field_validator

from typing import TypedDict

class Account(TypedDict):
    account_id: int
    name: str
    balance: float
    currency: str

class CreateAccountRequest(BaseModel):
    name: str = Field(..., max_length=127)
    balance: float
    currency: str = Field(..., max_length=3)

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:

        v = v.strip()

        if not v:
            raise ValueError("Account name cannot be empty")

        return v

    @field_validator('balance')
    def balance_not_negative(cls, v: float) -> float:

        if v < 0:
            raise ValueError("Initial balance cannot be negative")
                
        return v

    @field_validator('currency')
    def validate_currency(cls, v: str) -> str:

        if v not in ["RUB", "EUR", "USD"]:
            raise ValueError("Currency must be one of RUB, USD, EUR")

        return v