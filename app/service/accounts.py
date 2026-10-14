from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.accounts import CreateAccountRequest

from app.models.accounts import Account

from app.repository import accounts as accounts_repository
from app.repository import transactions as transactions_repository
from app.repository import transfers as transfers_repository

async def create_account(
    request: CreateAccountRequest,
    session: AsyncSession
) -> Account:

    if await accounts_repository.is_account_exists(request.name, session):
        raise HTTPException(
            status_code = 409,
            detail = f"Account with name '{request.name}' already exists"
        )
    try:
        return await accounts_repository.create_account(
            request.name,
            request.balance,
            request.currency,
            session
        )
    except IntegrityError:

        await session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database operation failed"
        )


async def get_accounts(session: AsyncSession) -> Sequence[Account]:    
    return await accounts_repository.get_all_accounts(session)


async def get_account(account_id : int, session: AsyncSession) -> Account:

    account = await accounts_repository.get_account_by_account_id(account_id, session)

    if account is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Account '{account_id}' not found"
        )

    return account


async def delete_account(account_id: int, session: AsyncSession) -> dict[str, Account]:

    if await transactions_repository.is_account_id_exists_in_transactions(account_id, session):
        raise HTTPException(
            status_code=409,
            detail = f"Account '{account_id}' cannot be deleted because it is used in a transaction",
        )

    if await transfers_repository.is_account_id_exists_in_transfers(account_id, session):
        raise HTTPException(
            status_code=409,
            detail = f"Account '{account_id}' cannot be deleted because it is used in a transfer",
        )
    
    try:
        deleted_account = await accounts_repository.delete_account(account_id, session)

        if deleted_account is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Account '{account_id}' not found"
            )   
        
        await session.commit()
        
        return deleted_account
    
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database operation failed"
        )
