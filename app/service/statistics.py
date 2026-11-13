from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import Account
from app.models.transactions import Transaction

from app.repository import accounts as accounts_repository
from app.repository import transactions as transactions_repository

from app.integrations.cbr import (
    fetch_cbr_rates_xml,
    parse_cbr_rates_xml
)

async def get_balance_statistics(currency: str | None, session: AsyncSession) -> dict[str, dict[str, Decimal] | list[dict[str, int | str | Decimal]] | Decimal | str | date | None]:

    if currency is not None and currency not in ("USD", "EUR", "RUB"):

        raise HTTPException(
            status_code=422,
            detail="Currency must be one of RUB, USD, EUR"
        )

    balances_by_currencies: dict[str, Decimal] = {}
    accounts_data: list[dict[str, int | str | Decimal]] = []

    accounts = await accounts_repository.get_all_accounts(session)
    for account in accounts:

        if account.currency not in balances_by_currencies:
            balances_by_currencies[account.currency] = account.balance
        else:
            balances_by_currencies[account.currency] += account.balance

        accounts_data.append({
                "account_id": account.account_id,
                "name": account.name,
                "balance": account.balance,
                "currency": account.currency,
        })

    await session.rollback()

    if currency is None:
        return {"balances_by_currencies": balances_by_currencies, "accounts": accounts_data}

    total_balance = Decimal("0")

    if not any(
        account_currency != currency and balance > 0
        for account_currency, balance in balances_by_currencies.items()
    ):

        total_balance += balances_by_currencies.get(currency, Decimal("0"))
        return {"balances_by_currencies": balances_by_currencies, "total_balance": total_balance, "currency": currency, "rate_date": None, "accounts": accounts_data}

    xml_data = await fetch_cbr_rates_xml()
    rate_date, rates = parse_cbr_rates_xml(xml_data)
    rates["RUB"] = Decimal("1")

    for account_currency, balance in balances_by_currencies.items():

        if balance == 0:
            continue

        if account_currency == currency:

            total_balance += balance

        else:

            new_balance = balance * rates[account_currency] / rates[currency]
            total_balance += new_balance

    total_balance = total_balance.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return {"balances_by_currencies": balances_by_currencies, "total_balance": total_balance, "currency": currency, "rate_date": rate_date, "accounts": accounts_data}


async def get_categories_statistics(category_type: str, currency: str | None, session: AsyncSession) -> dict[str, dict[str, Decimal]]:

    if category_type not in ['income', 'expense']:
        raise HTTPException(
            status_code = 400,
            detail = "category type must be income or expense",
        )

    if currency is not None and currency not in ("USD", "EUR", "RUB"):

        raise HTTPException(
            status_code=422,
            detail="Currency must be one of RUB, USD, EUR"
        )

    amounts_by_categories: dict[str, dict[str, Decimal]] = {}

    transactions = await transactions_repository.get_transactions_statistics(session)

    for transaction in transactions:

        if transaction.category.type == category_type:

            name = transaction.category.name
            transaction_currency = transaction.currency
            amount = transaction.amount

            if name not in amounts_by_categories:

                amounts_by_categories[name] = {}

            if transaction_currency not in amounts_by_categories[name]:
                amounts_by_categories[name][transaction_currency] = Decimal("0")

            amounts_by_categories[name][transaction_currency] += amount

    await session.rollback()

    if currency is None:
        return amounts_by_categories

    need_conversion = any(
        transaction_currency != currency and amount != 0
        for amounts in amounts_by_categories.values()
        for transaction_currency, amount in amounts.items()
    )

    rates: dict[str, Decimal] = {}
    
    if need_conversion:
        xml_data = await fetch_cbr_rates_xml()
        rates = parse_cbr_rates_xml(xml_data)[1]
        rates["RUB"] = Decimal("1")

    converted_totals: dict[str, dict[str, Decimal]] = {}

    for category_name, amounts in amounts_by_categories.items():

        converted_totals[category_name] = {}
        total_amount = Decimal("0")

        for transaction_currency, amount in amounts.items():

            if amount == 0:
                continue

            if transaction_currency == currency: 

                total_amount += amount

            else:

                new_amount = amount * rates[transaction_currency] / rates[currency]
                total_amount += new_amount

        total_amount = total_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        converted_totals[category_name][currency] = total_amount

    return converted_totals       

async def get_transactions_statistics_by_period(date_from: date, date_to: date, session: AsyncSession) -> Sequence[Transaction]:

    if date_from > date_to:
        raise HTTPException(
            status_code= 400,
            detail = f"date_from cannot be later than date_to",
        )

    return await transactions_repository.get_transactions_statistics_by_period(date_from, date_to, session)