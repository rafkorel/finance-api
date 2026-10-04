from fastapi import APIRouter

from app.schemas.categories import AddCategoryRequest

from app.service import categories as categories_service

router = APIRouter()

@router.post("/categories", status_code=201)
async def create_category(request: AddCategoryRequest):
    return await categories_service.create_category(request)


@router.get("/categories")
async def get_categories():
    return await categories_service.get_categories()


@router.get("/categories/{category_id}")
async def get_category(category_id: int):
    return await categories_service.get_category(category_id)


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int):
    return await categories_service.delete_category(category_id)