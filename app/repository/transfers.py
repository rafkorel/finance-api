from decimal import Decimal
from typing import Sequence
from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transfers import Transfer

async def create_transfer(
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        description: str | None,
        session: AsyncSession
    ) -> Transfer:

    transfer = Transfer(
        from_account_id = from_account_id,
        to_account_id = to_account_id,
        amount = amount,
        description = description,
        date = date.today()
    )

    session.add(transfer)

    await session.flush()

    return transfer


async def get_all_transfers(session: AsyncSession) -> Sequence[Transfer]:

    query = select(Transfer)
    result = await session.execute(query)
    return result.scalars().all()


async def get_transfer_by_transfer_id(transfer_id : int, session: AsyncSession) -> Transfer | None:
    
    return await session.get(Transfer, transfer_id)


async def delete_transfer(transfer: Transfer, session: AsyncSession) -> dict[str, Transfer]:

    await session.delete(transfer)
    await session.flush()
    
    return {"deleted transfer": transfer}


async def is_account_id_exists_in_transfers(account_id : int, session: AsyncSession) -> bool:

    query = select(Transfer).where(
        or_(
            Transfer.from_account_id == account_id,
            Transfer.to_account_id == account_id
        )
    )   
    result = await session.execute(query)
    transfers = result.scalars().all() 

    if transfers == []:
        return False
    return True


async def get_amount_by_transfer_id(transfer_id: int, session: AsyncSession) -> Decimal:

    query = select(Transfer).where(Transfer.transfer_id == transfer_id)
    result = await session.execute(query)
    transfer = result.scalar_one()

    return transfer.amount


async def get_transfer_for_update(
        transfer_id: int,
        session: AsyncSession
) -> Transfer | None:

    query = (
        select(
            Transfer
        ).where(
            Transfer.transfer_id == transfer_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    
    result = await session.execute(query)

    return result.scalar_one_or_none()