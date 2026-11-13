from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import Account

async def create_account(name: str, balance: Decimal, currency: str, session: AsyncSession) -> Account:

    account = Account(
        name=name,
        balance=Decimal(balance),
        currency=currency
    )

    session.add(account)

    await session.commit()
    await session.refresh(account)

    return account


async def is_account_exists(name: str, session: AsyncSession) -> bool:

    query = select(Account).where(Account.name == name)
    result = await session.execute(query)
    accounts = result.scalar_one_or_none()

    if accounts is None:
        return False
    return True


async def get_all_accounts(session: AsyncSession) -> Sequence[Account]:

    query = select(Account)
    result = await session.execute(query)
    return result.scalars().all()


async def get_account_by_account_id(account_id : int, session: AsyncSession) -> Account | None:

    return await session.get(Account, account_id)


async def delete_account(account_id: int, session: AsyncSession) -> dict[str, Account] | None:

    account = await session.get(Account, account_id)

    if account is None:
        return None

    await session.delete(account)
    await session.flush()
    return {"deleted account": account}


async def get_account_for_update(
    account_id: int,
    session: AsyncSession
) -> Account:

    query = (
        select(
            Account
        ).where(
            Account.account_id == account_id
        ).with_for_update().execution_options(populate_existing=True)
    )
    
    result = await session.execute(query)

    return result.scalar_one()


async def get_accounts_for_update(
    from_account_id: int,
    to_account_id: int,
    session: AsyncSession
) -> tuple[Account, Account]:

    sort_ids = sorted((from_account_id, to_account_id))

    account_1 = await get_account_for_update(sort_ids[0], session)
    account_2 = await get_account_for_update(sort_ids[1], session)

    if account_1.account_id == from_account_id:
        return account_1, account_2
    else:
        return account_2, account_1