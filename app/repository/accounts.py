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


async def is_account_id_exists(account_id: int, session: AsyncSession) -> bool:
    
    if await session.get(Account, account_id) is None:
        return False
    return True


async def add_to_balance(account_id: int, amount: Decimal, session: AsyncSession) -> None:

    query = select(Account).where(Account.account_id == account_id)
    result = await session.execute(query)
    account = result.scalar_one()

    account.balance += Decimal(amount)
    await session.flush()


async def subtract_amount(account_id: int, amount: Decimal, session: AsyncSession) -> bool:

    query = select(Account).where(Account.account_id == account_id)
    result = await session.execute(query)
    account = result.scalar_one()

    if account.balance < Decimal(amount):
        return False
    return True


async def deduct_from_balance(account_id: int, amount: Decimal, session: AsyncSession) -> None:

    query = select(Account).where(Account.account_id == account_id)
    result = await session.execute(query)
    account = result.scalar_one()

    account.balance -= Decimal(amount)
    await session.flush()


async def get_balance_by_account_id(account_id: int, session: AsyncSession) -> Decimal:

    query = select(Account).where(Account.account_id == account_id)
    result = await session.execute(query)
    account = result.scalar_one()

    return account.balance


async def accounts_is_empty(session: AsyncSession) -> bool:

    query = select(Account)
    result = await session.execute(query)
    accounts = result.scalars().all()

    return accounts == []


async def get_all_balance(session: AsyncSession) -> dict[str, Decimal | Sequence[Account]]:

    total_balance = Decimal("0")

    query = select(Account)
    result = await session.execute(query)
    accounts = result.scalars().all() 

    for account in accounts:
        total_balance += account.balance
    return {
        "total_balance": total_balance,
        "accounts": accounts
    }


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