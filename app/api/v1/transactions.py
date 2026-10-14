from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session

from app.schemas.transactions import AddTransactionRequest

from app.service import transactions as transactions_service

router = APIRouter()

@router.post("/transactions/income", status_code=201)
async def create_income(
    request: AddTransactionRequest,
    session: AsyncSession = Depends(get_session)
):
    return await transactions_service.create_income(request, session)


@router.post("/transactions/expense", status_code=201)
async def create_expense(
    request: AddTransactionRequest,
    session: AsyncSession = Depends(get_session)
):
    return await transactions_service.create_expense(request, session)


@router.get("/transactions")
async def get_transactions(session: AsyncSession = Depends(get_session)):
    return await transactions_service.get_transactions(session)


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await transactions_service.get_transaction(transaction_id, session)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await transactions_service.delete_transaction(transaction_id, session)