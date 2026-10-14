from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

class CreateAccountRequest(BaseModel):
    name: str = Field(
        ...,
        max_length=100
    )
    balance: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2
    )
    currency: str = Field(
        ...,
        max_length=3
    )

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:

        v = v.strip()

        if not v:
            raise ValueError("Account name cannot be empty")

        return v

    @field_validator('currency')
    def validate_currency(cls, v: str) -> str:

        if v not in ["RUB", "EUR", "USD"]:
            raise ValueError("Currency must be one of RUB, USD, EUR")

        return v