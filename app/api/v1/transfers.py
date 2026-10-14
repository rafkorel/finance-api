from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session

from app.schemas.transfers import AddTransferRequest

from app.service import transfers as transfer_service

router = APIRouter()

@router.post("/transfers", status_code=201)
async def create_transfer(
    request: AddTransferRequest,
    session: AsyncSession = Depends(get_session)
):
    return await transfer_service.create_transfer(request, session)


@router.get("/transfers")
async def get_transfers(session: AsyncSession = Depends(get_session)):
    return await transfer_service.get_transfers(session)


@router.get("/transfers/{transfer_id}")
async def get_transfer(
    transfer_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await transfer_service.get_transfer(transfer_id, session)


@router.delete("/transfers/{transfer_id}")
async def delete_transfer(
    transfer_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await transfer_service.delete_transfer(transfer_id, session)