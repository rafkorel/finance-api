from decimal import Decimal

from pydantic import BaseModel, Field, field_validator
from datetime import date

class AddTransactionRequest(BaseModel):
    account_id: int
    category_id: int
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    description: str | None = Field(
        None,
        max_length=250
    )
    date: date
    currency: str | None = Field(
        default=None,
        max_length=3
    )

    @field_validator('currency')
    def validate_currency(cls, v: str | None) -> str | None:

        if v is not None:
            if v not in ["RUB", "EUR", "USD"]:
                raise ValueError("Currency must be one of RUB, USD, EUR")

        return v