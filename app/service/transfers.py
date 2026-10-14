from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transfers import AddTransferRequest

from app.models.transfers import Transfer

from app.repository import accounts as accounts_repository
from app.repository import transfers as transfers_repository

async def create_transfer(request: AddTransferRequest, session: AsyncSession) -> Transfer:

    if not await accounts_repository.is_account_id_exists(request.from_account_id, session):
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.from_account_id}' not found among accounts"
        )

    if not await accounts_repository.is_account_id_exists(request.to_account_id, session):
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.to_account_id}' not found among accounts"
        )

    try:

        from_account, to_account = await accounts_repository.get_accounts_for_update(
            request.from_account_id,
            request.to_account_id,
            session
        )

        if from_account.balance < request.amount:

            await session.rollback()

            raise HTTPException(
                status_code = 400,
                detail = 'Transfer amount cannot exceed the source account balance'
            )

        from_account.balance -= request.amount
        to_account.balance += request.amount

        transfer = await transfers_repository.create_transfer(
            request.from_account_id,
            request.to_account_id,
            request.amount,
            request.description,
            session
        )

        await session.commit()
        return transfer
    
    except SQLAlchemyError:

        await session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )


async def get_transfers(session: AsyncSession) -> Sequence[Transfer]:
    return await transfers_repository.get_all_transfers(session)


async def get_transfer(transfer_id: int, session: AsyncSession) -> Transfer:

    transfer = await transfers_repository.get_transfer_by_transfer_id(transfer_id, session)
        
    if transfer is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Transfer '{transfer_id}' not found"
        )

    return transfer


async def delete_transfer(transfer_id: int, session: AsyncSession) -> dict[str, Transfer]:

    try:

        transfer = await transfers_repository.get_transfer_for_update(transfer_id, session)
            
        if transfer is None:

            await session.rollback()

            raise HTTPException(
                status_code = 404,
                detail = f"Transfer '{transfer_id}' not found"
            )

        from_account_id = transfer.from_account_id
        to_account_id = transfer.to_account_id
        amount = transfer.amount

        from_account, to_account = await accounts_repository.get_accounts_for_update(
            from_account_id,
            to_account_id,
            session
        )

        if to_account.balance < amount:

            await session.rollback()

            raise HTTPException(
            status_code=409,
            detail = f"Transfer '{transfer_id}' cannot be deleted because the recipient account has insufficient balance",
        )

        from_account.balance += amount
        to_account.balance -= amount

        deleted_transfer = await transfers_repository.delete_transfer(transfer, session)

        await session.commit()
        return deleted_transfer
    
    except SQLAlchemyError:
        
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )