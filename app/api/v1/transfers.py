from fastapi import APIRouter

from app.schemas.transfers import AddTransferRequest

from app.service import transfers as transfer_service

router = APIRouter()

@router.post("/transfers", status_code=201)
async def create_transfer(request: AddTransferRequest):
    return await transfer_service.create_transfer(request)


@router.get("/transfers")
async def get_transfers():
    return await transfer_service.get_transfers()


@router.get("/transfers/{transfer_id}")
async def get_transfer(transfer_id: int):
    return await transfer_service.get_transfer(transfer_id)


@router.delete("/transfers/{transfer_id}")
async def delete_transfer(transfer_id: int):
    return await transfer_service.delete_transfer(transfer_id)