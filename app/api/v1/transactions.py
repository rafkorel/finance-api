from fastapi import APIRouter

from app.schemas.transactions import AddTransactionRequest

from app.service import transactions as transactions_service

router = APIRouter()

@router.post("/transactions/income", status_code=201)
async def create_income(request: AddTransactionRequest):
    return await transactions_service.create_income(request)


@router.post("/transactions/expense", status_code=201)
async def create_expense(request: AddTransactionRequest):
    return await transactions_service.create_expense(request)


@router.get("/transactions")
async def get_transactions():
    return await transactions_service.get_transactions()


@router.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: int):
    return await transactions_service.get_transaction(transaction_id)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    return await transactions_service.delete_transaction(transaction_id)