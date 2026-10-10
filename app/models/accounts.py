from typing import TYPE_CHECKING

from decimal import Decimal

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.transactions import Transaction

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy import String, Numeric, Identity, CheckConstraint

class Account(Base):
    __tablename__ = "accounts"


    account_id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True
    )


    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint('balance >= 0', name='check_balance_positive'),
        nullable=False
    )


    currency: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("currency IN ('RUB', 'USD', 'EUR')", name='currency_check'),
        nullable=False
    )


    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="account"
    )