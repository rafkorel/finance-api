from fastapi import HTTPException

from app.schemas.transfers import AddTransferRequest

from app.repository import accounts as accounts_repository
from app.repository import transfers as transfers_repository

async def create_transfer(request: AddTransferRequest) -> dict:

    if not accounts_repository.is_account_id_exists(request.from_account_id):
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.from_account_id}' not found among accounts"
        )

    if not accounts_repository.is_account_id_exists(request.to_account_id):
        raise HTTPException(
            status_code=404,
            detail = f"Id: '{request.to_account_id}' not found among accounts"
        )

    if not accounts_repository.subtract_amount(request.from_account_id, request.amount):
        raise HTTPException(
            status_code = 400,
            detail = 'Transfer amount cannot exceed the source account balance'
        )

    accounts_repository.deduct_from_balance(request.from_account_id, request.amount)
    accounts_repository.add_to_balance(request.to_account_id, request.amount)

    return transfers_repository.create_transfer(
        request.from_account_id,
        request.to_account_id,
        request.amount,
        request.description
    )


async def get_transfers() -> dict:
    return transfers_repository.get_all_transfers()


async def get_transfer(transfer_id: int) -> dict:
        
    if not transfers_repository.is_transfer_id_exists(transfer_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Transfer '{transfer_id}' not found"
        )

    return transfers_repository.get_transfer_by_transfer_id(transfer_id)


async def delete_transfer(transfer_id: int) -> dict:
            
    if not transfers_repository.is_transfer_id_exists(transfer_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Transfer '{transfer_id}' not found"
        )

    account_id = transfers_repository.get_transfer_by_transfer_id(transfer_id)["to_account_id"]

    if accounts_repository.get_balance_by_account_id(account_id) < transfers_repository.get_amount_by_transfer_id(transfer_id):
        raise HTTPException(
            status_code=409,
            detail = f"Transfer '{transfer_id}' cannot be deleted because the recipient account has insufficient balance",
        )

    deleted_transfer = transfers_repository.delete_transfer(transfer_id)

    account_id_1_from_transfer = deleted_transfer['from_account_id']
    account_id_2_from_transfer = deleted_transfer['to_account_id']
    amount_from_transfer = deleted_transfer['amount']

    accounts_repository.add_to_balance(account_id_1_from_transfer, amount_from_transfer)
    accounts_repository.deduct_from_balance(account_id_2_from_transfer, amount_from_transfer)

    return {"deleted transfer": deleted_transfer}