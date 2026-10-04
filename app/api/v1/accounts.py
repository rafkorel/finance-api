from fastapi import APIRouter

from app.schemas.accounts import CreateAccountRequest

from app.service import accounts as accounts_service

router = APIRouter()

@router.post("/accounts", status_code=201)
async def create_account(request: CreateAccountRequest):
    return await accounts_service.create_account(request)


@router.get("/accounts")
async def get_accounts():    
    return await accounts_service.get_accounts()


@router.get("/accounts/{account_id}")
async def get_account(account_id : int):
    return await accounts_service.get_account(account_id)


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: int):
    return await accounts_service.delete_account(account_id)