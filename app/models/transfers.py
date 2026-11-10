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

class Transfer(Base):
    __tablename__ = 'transfers'


    transfer_id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True
    )


    from_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False
    )


    to_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.account_id"),
        nullable=False
    )


    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("amount > 0", name='amount_check'),
        nullable=False
    )


    credited_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("credited_amount > 0", name='credited_amount_check'),
        nullable=False
    )


    from_currency: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("from_currency IN ('RUB', 'USD', 'EUR')", name='from_currency_check'),
        nullable=False
    )


    to_currency: Mapped[str] = mapped_column(
        String(3),
        CheckConstraint("to_currency IN ('RUB', 'USD', 'EUR')", name='to_currency_check'),
        nullable=False
    )


    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        CheckConstraint("exchange_rate > 0", name="exchange_rate_check"),
        nullable=False
    )


    date: Mapped[date] = mapped_column(
        Date(),
        nullable=False
    )


    rate_date: Mapped[date | None] = mapped_column(
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


    __table_args__ = (
        CheckConstraint(
            "from_account_id != to_account_id",
            name="different_accounts_check"
        ),
    )