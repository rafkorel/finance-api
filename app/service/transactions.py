from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transactions import AddTransactionRequest

from app.models.transactions import Transaction

from app.service.currency import convert_with_cbr 

from app.repository import accounts as accounts_repository
from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

async def create_income(request: AddTransactionRequest, session: AsyncSession) -> Transaction:

    account = await accounts_repository.get_account_by_account_id(request.account_id, session)

    if account is None:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )
    account_currency = account.currency

    if request.currency is None:
        currency = account_currency
    else:
        currency=request.currency

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

    await session.rollback()

    try:

        account_amount, exchange_rate, rate_date = await convert_with_cbr(
            amount=request.amount,
            from_currency=currency,
            to_currency=account_currency
        )
        if rate_date is None:
            rate_source = None
        else:
            rate_source = "CBR"

        account = await accounts_repository.get_account_for_update(request.account_id, session)

        if account.currency != account_currency:

            await session.rollback()

            raise HTTPException(
                status_code=409,
                detail="The account currency type has been changed"
            )

        account.balance += account_amount

        transaction = await transactions_repository.create_transaction(
            account_id=request.account_id,
            category_id=request.category_id,
            amount=request.amount,
            account_amount=account_amount,
            currency=currency,
            account_currency=account_currency,
            exchange_rate=exchange_rate,
            rate_date=rate_date,
            rate_source=rate_source,
            description=request.description,
            date=request.date,
            session=session
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

    account = await accounts_repository.get_account_by_account_id(request.account_id, session)

    if account is None:
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )
    account_currency = account.currency

    if request.currency is None:
        currency = account_currency
    else:
        currency=request.currency

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

    await session.rollback()

    try:

        account_amount, exchange_rate, rate_date = await convert_with_cbr(
            amount=request.amount,
            from_currency=currency,
            to_currency=account_currency
        )
        if rate_date is None:
            rate_source = None
        else:
            rate_source = "CBR"

        account = await accounts_repository.get_account_for_update(request.account_id, session)

        if account.currency != account_currency:

            await session.rollback()

            raise HTTPException(
                status_code=409,
                detail="The account currency type has been changed"
            )

        if account.balance < Decimal(account_amount):

            await session.rollback()

            raise HTTPException(
                status_code= 400,
                detail="Expense amount cannot exceed the account balance"
            )            

        account.balance -= account_amount

        transaction = await transactions_repository.create_transaction(
            account_id=request.account_id,
            category_id=request.category_id,
            amount=request.amount,
            account_amount=account_amount,
            currency=currency,
            account_currency=account_currency,
            exchange_rate=exchange_rate,
            rate_date=rate_date,
            rate_source=rate_source,
            description=request.description,
            date=request.date,
            session=session
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
        account_amount = transaction.account_amount
        category_type = transaction.category.type

        if category_type == 'income' and account.balance < account_amount:

            await session.rollback()

            raise HTTPException(
                status_code= 409,
                detail= f"Transaction '{transaction_id}' cannot be deleted because it would make the account balance negative"
            )

        if category_type == 'income':
            account.balance -= account_amount
        else:
            account.balance += account_amount

        deleted_transaction = await transactions_repository.delete_transaction(transaction, session)

        await session.commit()
        return deleted_transaction
    
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )