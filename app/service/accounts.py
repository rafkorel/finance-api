from fastapi import HTTPException

from app.schemas.accounts import Account, CreateAccountRequest

from app.repository import accounts as accounts_repository
from app.repository import transactions as transactions_repository
from app.repository import transfers as transfers_repository

async def create_account(request: CreateAccountRequest) -> Account:

    if not accounts_repository.is_account_exists(request.name):
        raise HTTPException(
            status_code = 409,
            detail = f"Account with name '{request.name}' already exists"
        )

    return accounts_repository.create_account(
        request.name,
        request.balance,
        request.currency
    )


async def get_accounts() -> dict[int, Account]:    
    return accounts_repository.get_all_accounts()


async def get_account(account_id : int) -> Account:

    account = accounts_repository.get_account_by_account_id(account_id)

    if account is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Account '{account_id}' not found"
        )
    
    return account


async def delete_account(account_id: int) -> dict[str, Account]:
    
    if not accounts_repository.is_account_id_exists(account_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Account '{account_id}' not found"
        )

    if not transactions_repository.is_account_id_exists_in_transactions(account_id):
        raise HTTPException(
            status_code=409,
            detail = f"Account '{account_id}' cannot be deleted because it is used in a transaction",
        )

    if not transfers_repository.is_account_id_exists_in_transfers(account_id):
        raise HTTPException(
            status_code=409,
            detail = f"Account '{account_id}' cannot be deleted because it is used in a transfer",
        )
    
    return accounts_repository.delete_account(account_id)