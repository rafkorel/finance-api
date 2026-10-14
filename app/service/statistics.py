from datetime import date
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import Account
from app.models.transactions import Transaction

from app.repository import accounts as accounts_repository
from app.repository import transactions as transactions_repository

async def get_balance_statistics(session: AsyncSession) -> dict[str, Decimal | Sequence[Account]]:

    return await accounts_repository.get_all_balance(session)


async def get_categories_statistics(category_type: str, session: AsyncSession) -> dict[str, Decimal]:

    if category_type not in ['income', 'expense']:
        raise HTTPException(
            status_code = 400,
            detail = "category type must be income or expense",
        )

    totals: dict[str, Decimal] = {}

    transactions = await transactions_repository.get_transactions_statistics(session)

    for transaction in transactions:
        if transaction.category.type == category_type:

            name = transaction.category.name

            if name not in totals:
                totals[name] = Decimal("0")

            totals[name] += transaction.amount

    return totals


async def get_transactions_statistics_by_period(date_from: date, date_to: date, session: AsyncSession) -> Sequence[Transaction]:

    if date_from > date_to:
        raise HTTPException(
            status_code= 400,
            detail = f"date_from cannot be later than date_to",
        )

    return await transactions_repository.get_transactions_statistics_by_period(date_from, date_to, session)