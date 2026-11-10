"""add currency fields to transactions

Revision ID: 1961f5b6f119
Revises: 16c9d2913242
Create Date: 2026-11-10 21:26:51.342703

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "1961f5b6f119"
down_revision: Union[str, Sequence[str], None] = "16c9d2913242"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Добавляем новые столбцы
    op.add_column(
        "transactions",
        sa.Column(
            "account_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "account_currency",
            sa.String(length=3),
            nullable=False
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "exchange_rate",
            sa.Numeric(precision=24, scale=12),
            nullable=False
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "rate_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "rate_source",
            sa.String(length=20),
            nullable=True
        )
    )

    # Добавляем CHECK-ограничения
    op.create_check_constraint(
        "check_account_amount",
        "transactions",
        "account_amount > 0"
    )

    op.create_check_constraint(
        "currency_check",
        "transactions",
        "currency IN ('RUB', 'USD', 'EUR')"
    )

    op.create_check_constraint(
        "account_currency_check",
        "transactions",
        "account_currency IN ('RUB', 'USD', 'EUR')"
    )

    op.create_check_constraint(
        "exchange_rate_check",
        "transactions",
        "exchange_rate > 0"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Удаляем CHECK-ограничения
    op.drop_constraint(
        "exchange_rate_check",
        "transactions",
        type_="check"
    )

    op.drop_constraint(
        "account_currency_check",
        "transactions",
        type_="check"
    )

    op.drop_constraint(
        "currency_check",
        "transactions",
        type_="check"
    )

    op.drop_constraint(
        "check_account_amount",
        "transactions",
        type_="check"
    )

    # Удаляем добавленные столбцы
    op.drop_column("transactions", "rate_source")
    op.drop_column("transactions", "rate_date")
    op.drop_column("transactions", "exchange_rate")
    op.drop_column("transactions", "account_currency")
    op.drop_column("transactions", "currency")
    op.drop_column("transactions", "account_amount")