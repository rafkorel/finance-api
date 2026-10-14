from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session

from app.schemas.accounts import CreateAccountRequest

from app.service import accounts as accounts_service

router = APIRouter()

@router.post("/accounts", status_code=201)
async def create_account(
    request: CreateAccountRequest,
    session: AsyncSession = Depends(get_session)
):
    return await accounts_service.create_account(request, session)


@router.get("/accounts")
async def get_accounts(
    session: AsyncSession = Depends(get_session),
):
    return await accounts_service.get_accounts(session)


@router.get("/accounts/{account_id}")
async def get_account(
    account_id : int,
    session: AsyncSession = Depends(get_session)
):
    return await accounts_service.get_account(account_id, session)


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await accounts_service.delete_account(account_id, session)