from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transactions import AddTransactionRequest

from app.models.transactions import Transaction

from app.repository import accounts as accounts_repository
from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

async def create_income(request: AddTransactionRequest, session: AsyncSession) -> Transaction:

    if not await accounts_repository.is_account_id_exists(request.account_id, session):
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if not await categories_repository.is_category_id_exists(request.category_id, session):
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if not await categories_repository.type_check_income(request.category_id, session):
        raise HTTPException(
            status_code= 400,
            detail="Category must be income"
        )

    try:

        account = await accounts_repository.get_account_for_update(request.account_id, session)

        account.balance += request.amount

        transaction = await transactions_repository.create_transaction(
            request.account_id,
            request.category_id,
            request.amount,
            request.description,
            request.date,
            session
        )

        await session.commit()
        return transaction
    
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail = "Database operation failed"
        )


async def create_expense(request: AddTransactionRequest, session: AsyncSession) -> Transaction:

    if not await accounts_repository.is_account_id_exists(request.account_id, session):
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if not await categories_repository.is_category_id_exists(request.category_id, session):
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if not await categories_repository.type_check_expense(request.category_id, session):
        raise HTTPException(
            status_code= 400,
            detail="Category must be expense"
        )

    try:
        account = await accounts_repository.get_account_for_update(request.account_id, session)

        if account.balance < Decimal(request.amount):

            await session.rollback()

            raise HTTPException(
                status_code= 400,
                detail="Expense amount cannot exceed the account balance"
            )            

        account.balance -= request.amount

        transaction =  await transactions_repository.create_transaction(
            request.account_id,
            request.category_id,
            request.amount,
            request.description,
            request.date,
            session
        )

        await session.commit()
        return transaction
    
    except SQLAlchemyError:
        await session.rollback()
        
        raise HTTPException(
            status_code=500,
            detail = "Database operation failed"
        )


async def get_transactions(session: AsyncSession) -> Sequence[Transaction]:
    return await transactions_repository.get_all_transactions(session)


async def get_transaction(transaction_id: int, session: AsyncSession) -> Transaction:

    transaction = await transactions_repository.get_transaction_by_transaction_id(transaction_id, session)

    if transaction is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Transaction '{transaction_id}' not found"
        )
    return transaction


async def delete_transaction(transaction_id: int, session: AsyncSession) -> dict[str, Transaction]:

    try:

        transaction = await transactions_repository.get_transaction_for_update(transaction_id, session)

        if transaction is None:

            await session.rollback()

            raise HTTPException(
                status_code = 404,
                detail = f"Transaction '{transaction_id}' not found"
            )

        account_id = transaction.account_id

        account = await accounts_repository.get_account_for_update(account_id, session)
        amount = transaction.amount
        category_type = transaction.category.type

        if category_type == 'income'and account.balance < amount:

            await session.rollback()

            raise HTTPException(
                status_code= 409,
                detail= f"Transaction '{transaction_id}' cannot be deleted because it would make the account balance negative"
            )

        if category_type == 'income':
            account.balance -= amount
        else:
            account.balance += amount

        deleted_transaction = await transactions_repository.delete_transaction(transaction, session)

        await session.commit()
        return deleted_transaction
    
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )