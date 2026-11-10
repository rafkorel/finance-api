"""add currency fields to transfers

Revision ID: 16c9d2913242
Revises: d23c4a689b14
Create Date: 2026-11-10 20:03:06.746783

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "16c9d2913242"
down_revision: Union[str, Sequence[str], None] = "d23c4a689b14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Добавление новых столбцов
    op.add_column(
        "transfers",
        sa.Column(
            "credited_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False
        )
    )

    op.add_column(
        "transfers",
        sa.Column(
            "from_currency",
            sa.String(length=3),
            nullable=False
        )
    )

    op.add_column(
        "transfers",
        sa.Column(
            "to_currency",
            sa.String(length=3),
            nullable=False
        )
    )

    op.add_column(
        "transfers",
        sa.Column(
            "exchange_rate",
            sa.Numeric(precision=24, scale=12),
            nullable=False
        )
    )

    op.add_column(
        "transfers",
        sa.Column(
            "rate_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "transfers",
        sa.Column(
            "rate_source",
            sa.String(length=20),
            nullable=True
        )
    )

    # Добавление CHECK-ограничений
    op.create_check_constraint(
        "credited_amount_check",
        "transfers",
        "credited_amount > 0"
    )

    op.create_check_constraint(
        "from_currency_check",
        "transfers",
        "from_currency IN ('RUB', 'USD', 'EUR')"
    )

    op.create_check_constraint(
        "to_currency_check",
        "transfers",
        "to_currency IN ('RUB', 'USD', 'EUR')"
    )

    op.create_check_constraint(
        "exchange_rate_check",
        "transfers",
        "exchange_rate > 0"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Удаление CHECK-ограничений
    op.drop_constraint(
        "exchange_rate_check",
        "transfers",
        type_="check"
    )

    op.drop_constraint(
        "to_currency_check",
        "transfers",
        type_="check"
    )

    op.drop_constraint(
        "from_currency_check",
        "transfers",
        type_="check"
    )

    op.drop_constraint(
        "credited_amount_check",
        "transfers",
        type_="check"
    )

    # Удаление добавленных столбцов
    op.drop_column("transfers", "rate_source")
    op.drop_column("transfers", "rate_date")
    op.drop_column("transfers", "exchange_rate")
    op.drop_column("transfers", "to_currency")
    op.drop_column("transfers", "from_currency")
    op.drop_column("transfers", "credited_amount")