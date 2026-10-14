from datetime import date
from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.transactions import Transaction

async def create_transaction(
        account_id : int,
        category_id: int,
        amount: Decimal,
        description: str | None,
        date: date,
        session: AsyncSession
    ) -> Transaction:

    transaction = Transaction(
        account_id = account_id,
        category_id = category_id,
        amount = amount,
        description = description,
        date = date,
    )

    session.add(transaction)

    await session.flush()

    return transaction


async def get_all_transactions(session: AsyncSession) -> Sequence[Transaction]:

    query = select(Transaction)
    result = await session.execute(query)
    return result.scalars().all()


async def get_transaction_by_transaction_id(transaction_id : int, session) -> Transaction | None:

    return await session.get(Transaction, transaction_id)


async def delete_transaction(transaction: Transaction, session: AsyncSession) -> dict[str, Transaction]:

    await session.delete(transaction)
    await session.flush()
    
    return {"deleted transaction": transaction}


async def get_type_by_transaction_id(transaction_id: int, session: AsyncSession) -> str:

    query = select(
        Transaction
    ).options(
        selectinload(
            Transaction.category
        )
    ).where(
        Transaction.transaction_id == transaction_id
    )
    result = await session.execute(query)
    transaction = result.scalar_one()

    return transaction.category.type


async def get_amount_by_transaction_id(transaction_id: int, session: AsyncSession) -> Decimal:

    query = select(Transaction).where(Transaction.transaction_id == transaction_id)
    result = await session.execute(query)
    transaction = result.scalar_one()

    return transaction.amount


async def is_account_id_exists_in_transactions(account_id : int, session: AsyncSession) -> bool:

    query = select(Transaction).where(Transaction.account_id == account_id)
    result = await session.execute(query)
    transaction = result.scalars().all()

    if transaction == []:
        return False
    return True


async def is_category_id_exists_in_transactions(category_id: int, session: AsyncSession) -> bool:

    query = select(Transaction).where(Transaction.category_id == category_id)
    result = await session.execute(query)
    transaction = result.scalars().all()

    if transaction == []:
        return False
    return True


async def transactions_is_empty(session: AsyncSession) -> bool:

    query = select(Transaction)
    result = await session.execute(query)
    transactions = result.scalars().all()

    return transactions == []


async def is_category_type_exists_in_transactions(category_type: str, session: AsyncSession) -> bool:

    query = select(Transaction).options(selectinload(Transaction.category))
    result = await session.execute(query)
    transactions = result.scalars().all()

    return any(
        transaction.category.type == category_type
        for transaction in transactions
    )


async def get_transactions_statistics_by_period(date_from: date, date_to: date, session: AsyncSession) -> Sequence[Transaction]:

    query = select(Transaction).where(Transaction.date >= date_from, Transaction.date <= date_to)
    result = await session.execute(query)

    return result.scalars().all()


async def get_transactions_statistics(session: AsyncSession) -> Sequence[Transaction]:

    query = select(Transaction).options(selectinload(Transaction.category))
    result = await session.execute(query)
    return result.scalars().all()


async def get_transaction_for_update(
        transaction_id: int,
        session: AsyncSession
) -> Transaction | None:

    query = (
        select(
            Transaction
        ).options(
            selectinload(
                Transaction.category
            )
        ).where(
            Transaction.transaction_id == transaction_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    
    result = await session.execute(query)

    return result.scalar_one_or_none()