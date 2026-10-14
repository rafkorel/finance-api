"""add missing constraints

Revision ID: d23c4a689b14
Revises: 7781d61c645b
Create Date: 2026-10-13 22:47:37.090444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd23c4a689b14'
down_revision: Union[str, Sequence[str], None] = '7781d61c645b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_check_constraint(
        constraint_name="balance_check",
        table_name="accounts",
        condition="balance >= 0"
    )

    op.create_check_constraint(
        constraint_name="currency_check",
        table_name="accounts",
        condition="currency IN ('RUB', 'EUR', 'USD')"
    )

    op.create_check_constraint(
        constraint_name="type_check",
        table_name="categories",
        condition="type in ('income', 'expense')"
    )

    op.create_unique_constraint(
        constraint_name="unique_name_and_type",
        table_name="categories",
        columns=["name","type"]
    )

    op.create_check_constraint(
        constraint_name="amount_check",
        table_name="transactions",
        condition="amount > 0"
    )

    op.create_check_constraint(
        constraint_name="amount_check",
        table_name="transfers",
        condition="amount > 0"
    )


def downgrade() -> None:

    op.drop_constraint(
        constraint_name="balance_check",
        table_name="accounts",
        type_="check"
    )

    op.drop_constraint(
        constraint_name="currency_check",
        table_name="accounts",
        type_="check"
    )

    op.drop_constraint(
        constraint_name="type_check",
        table_name="categories",
        type_="check"
    )

    op.drop_constraint(
        constraint_name="unique_name_and_type",
        table_name="categories",
        type_="unique"
    )

    op.drop_constraint(
        constraint_name="amount_check",
        table_name="transactions",
        type_="check"
    )

    op.drop_constraint(
        constraint_name="amount_check",
        table_name="transfers",
        type_="check"
    )
