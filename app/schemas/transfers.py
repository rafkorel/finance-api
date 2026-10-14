from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

class AddTransferRequest(BaseModel):
    from_account_id : int
    to_account_id: int
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    description: str | None = Field(
        None,
        max_length=250
    )

    @model_validator(mode="after")
    def accounts_must_be_different(self):
        if self.from_account_id == self.to_account_id:
            raise ValueError('Source and destination accounts must be different')
        return self