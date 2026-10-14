from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session

from app.schemas.categories import AddCategoryRequest

from app.service import categories as categories_service

router = APIRouter()

@router.post("/categories", status_code=201)
async def create_category(
    request: AddCategoryRequest,
    session: AsyncSession = Depends(get_session)
):
    return await categories_service.create_category(request, session)


@router.get("/categories")
async def get_categories(session: AsyncSession = Depends(get_session)):
    return await categories_service.get_categories(session)


@router.get("/categories/{category_id}")
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await categories_service.get_category(category_id, session)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await categories_service.delete_category(category_id, session)