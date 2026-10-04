from fastapi import HTTPException

from app.schemas.transactions import AddTransactionRequest

from app.repository import accounts as accounts_repository
from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

async def create_income(request: AddTransactionRequest) -> dict:

    if not accounts_repository.is_account_id_exists(request.account_id):
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if not categories_repository.is_category_id_exists(request.category_id):
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if not categories_repository.type_check_income(request.category_id):
        raise HTTPException(
            status_code= 400,
            detail="Category must be income"
        )
    
    accounts_repository.add_to_balance(request.account_id, request.amount)

    category_type = categories_repository.get_type_by_category_id(request.category_id)

    return transactions_repository.create_transactions(
        request.account_id,
        request.category_id,
        request.amount,
        request.description,
        request.date,
        category_type,
    )


async def create_expense(request: AddTransactionRequest) -> dict:

    if not accounts_repository.is_account_id_exists(request.account_id):
        raise HTTPException(
            status_code= 404,
            detail=f"Account id: '{request.account_id}' not found among accounts"
        )

    if not categories_repository.is_category_id_exists(request.category_id):
        raise HTTPException(
            status_code= 404,
            detail=f"Category id: '{request.category_id}' not found among categories"
        )

    if not categories_repository.type_check_expense(request.category_id):
        raise HTTPException(
            status_code= 400,
            detail="Category must be expense"
        )

    if not accounts_repository.subtract_amount(request.account_id, request.amount):
        raise HTTPException(
            status_code= 400,
            detail="Expense amount cannot exceed the account balance"
        )
    
    accounts_repository.deduct_from_balance(request.account_id, request.amount)

    category_type = categories_repository.get_type_by_category_id(request.category_id)

    return transactions_repository.create_transactions(
        request.account_id,
        request.category_id,
        request.amount,
        request.description,
        request.date,
        category_type
    )


async def get_transactions() -> dict:
    return transactions_repository.get_all_transactions()


async def get_transaction(transaction_id: int) -> dict:
    
    if not transactions_repository.is_transaction_id_exists(transaction_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Transaction '{transaction_id}' not found"
        )
    
    return transactions_repository.get_transaction_by_transaction_id(transaction_id)


async def delete_transaction(transaction_id: int) -> dict:
        
    if not transactions_repository.is_transaction_id_exists(transaction_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Transaction '{transaction_id}' not found"
        )

    account_id = transactions_repository.get_transaction_by_transaction_id(transaction_id)["account_id"]

    if (
        transactions_repository.get_type_by_transaction_id(transaction_id) == 'income' 
        and accounts_repository.get_balance_by_account_id(account_id) < transactions_repository.get_amount_by_transaction_id(transaction_id)
    ):
        raise HTTPException(
            status_code= 409,
            detail= f"Transaction '{transaction_id}' cannot be deleted because it would make the account balance negative"
        )
    
    deleted_transaction = transactions_repository.delete_transaction(transaction_id)

    account_id_from_transaction = deleted_transaction['account_id']
    amount_from_transaction = deleted_transaction['amount']

    if deleted_transaction['type'] == 'income':
        accounts_repository.deduct_from_balance(account_id_from_transaction, amount_from_transaction)
    else:
        accounts_repository.add_to_balance(account_id_from_transaction, amount_from_transaction)

    return {"deleted transaction": deleted_transaction}