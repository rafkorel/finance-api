from pydantic import BaseModel, field_validator, model_validator

from typing import TypedDict

class Transfer(TypedDict):
    transfer_id: int
    from_account_id: int
    to_account_id: int
    amount: float
    description: str | None

class AddTransferRequest(BaseModel):
    from_account_id : int
    to_account_id: int
    amount: float
    description: str | None = None

    @model_validator(mode="after")
    def accounts_must_be_different(self):
        if self.from_account_id == self.to_account_id:
            raise ValueError('Source and destination accounts must be different')
        return self

    @field_validator('amount')
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v