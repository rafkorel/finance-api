from decimal import Decimal

from pydantic import BaseModel, Field
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