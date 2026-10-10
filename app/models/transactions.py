from decimal import Decimal
from datetime import date

from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    Identity,
    CheckConstraint,
    Date
)

class Transaction(Base):
    __tablename__ = "transactions"


    transaction_id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True
    )


    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False
    )


    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.category_id"),
        nullable=False
    )


    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("amount > 0", name='amount_check'),
        nullable=False
    )


    date: Mapped[date] = mapped_column(
        Date(),
        nullable=False
    )


    description: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )