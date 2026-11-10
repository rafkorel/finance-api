from decimal import Decimal
from datetime import date as DateType

from app.models.base import Base
from app.models.categories import Category
from app.models.accounts import Account

from sqlalchemy.orm import Mapped, mapped_column, relationship

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


    account_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("account_amount > 0", name="check_account_amount"),
        nullable=False
    )


    currency: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("currency IN ('RUB', 'USD', 'EUR')", name='currency_check'),
        nullable=False
    )

    account_currency: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("account_currency IN ('RUB', 'USD', 'EUR')", name='account_currency_check'),
        nullable=False
    )


    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        CheckConstraint("exchange_rate > 0", name="exchange_rate_check"),
        nullable=False
    )


    date: Mapped[DateType] = mapped_column(
        Date(),
        nullable=False
    )


    rate_date: Mapped[DateType | None] = mapped_column(
        Date(),
        nullable=True
    )


    rate_source: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )


    description: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )


    account: Mapped[Account] = relationship(
        "Account",
        back_populates="transactions"
    )


    category: Mapped[Category] = relationship(
        "Category",
        back_populates="transactions"
    )