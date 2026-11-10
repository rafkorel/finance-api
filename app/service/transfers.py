from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.transfers import AddTransferRequest

from app.models.transfers import Transfer

from app.service.currency import convert_with_cbr 

from app.repository import accounts as accounts_repository
from app.repository import transfers as transfers_repository

async def create_transfer(request: AddTransferRequest, session: AsyncSession) -> Transfer:

    from_account = await accounts_repository.get_account_by_account_id(request.from_account_id, session)
    if from_account is None:
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.from_account_id}' not found among accounts"
        )
    from_currency = from_account.currency

    to_account = await accounts_repository.get_account_by_account_id(request.to_account_id, session)
    if to_account is None:
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.to_account_id}' not found among accounts"
        )
    to_currency = to_account.currency

    await session.rollback()

    try:

        credited_amount, exchange_rate, rate_date = await convert_with_cbr(
            amount=request.amount,
            from_currency=from_currency,
            to_currency=to_currency
        )
        if rate_date is None:
            rate_source = None
        else:
            rate_source = "CBR"

        from_account, to_account = await accounts_repository.get_accounts_for_update(
            request.from_account_id,
            request.to_account_id,
            session
        )

        if from_account.currency != from_currency or to_account.currency != to_currency:

            await session.rollback()

            raise HTTPException(
                status_code=409,
                detail="The account's currency type has been changed"
            )

        if from_account.balance < request.amount:

            await session.rollback()

            raise HTTPException(
                status_code = 400,
                detail = 'Transfer amount cannot exceed the source account balance'
            )

        from_account.balance -= request.amount
        to_account.balance += credited_amount

        transfer = await transfers_repository.create_transfer(
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            amount=request.amount,
            credited_amount=credited_amount,
            from_currency=from_currency,
            to_currency=to_currency,
            exchange_rate=exchange_rate,
            rate_date=rate_date,
            rate_source=rate_source,
            description=request.description,
            session=session
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
        credited_amount = transfer.credited_amount

        from_account, to_account = await accounts_repository.get_accounts_for_update(
            from_account_id,
            to_account_id,
            session
        )

        if to_account.balance < credited_amount:

            await session.rollback()

            raise HTTPException(
            status_code=409,
            detail = f"Transfer '{transfer_id}' cannot be deleted because the recipient account has insufficient balance",
        )

        from_account.balance += amount
        to_account.balance -= credited_amount

        deleted_transfer = await transfers_repository.delete_transfer(transfer, session)

        await session.commit()
        return deleted_transfer
    
    except SQLAlchemyError:
        
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )