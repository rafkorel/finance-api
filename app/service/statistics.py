from datetime import date

from fastapi import HTTPException

from app.repository import accounts as accounts_repository
from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

from app.schemas.accounts import Account
from app.schemas.transactions import Transaction
from app.schemas.statistics import CategoryStatistics

async def get_balance_statistics() -> dict[str, float | list[Account]]:

    if accounts_repository.accounts_is_empty():
        raise HTTPException(
            status_code=400,
            detail = "Accounts is empty"
        )

    return accounts_repository.get_all_balance()


async def get_categories_statistics(category_type: str) -> list[CategoryStatistics]:

    if category_type not in ['income', 'expense']:
        raise HTTPException(
            status_code = 400,
            detail = "category type must be income or expense",
        )

    if categories_repository.categories_is_empty():
        raise HTTPException(
            status_code=400,
            detail = "Categories is empty"
        )

    if transactions_repository.transactions_is_empty():
        raise HTTPException(
            status_code=400,
            detail = "Transactions is empty"
        )

    if not transactions_repository.is_category_type_exists_in_transactions(category_type):
        raise HTTPException(
            status_code=404,
            detail = f"type '{category_type}' not found among categories"
        )

    result = []

    transactions = transactions_repository.get_all_transactions()

    for transaction in transactions.values():
        if transaction['type'] == category_type:

            found = False
            name = categories_repository.get_category_name_by_id(transaction['category_id'])

            for dicts in result:
                if name == dicts['category']:

                    dicts['total'] += transaction['amount']
                    found = True

            if not found:

                result.append({
                    'category': name,
                    'total': transaction['amount']
                })

    return result


async def get_transactions_statistics_by_period(date_from: date, date_to: date) -> list[Transaction]:

    if date_from > date_to:
        raise HTTPException(
            status_code= 400,
            detail = f"date_from cannot be later than date_to",
        )

    return transactions_repository.get_transactions_statistics_by_period(date_from, date_to)