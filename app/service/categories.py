from fastapi import HTTPException

from app.schemas.categories import AddCategoryRequest

from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

async def create_category(request: AddCategoryRequest) -> dict:

    if not categories_repository.is_category_exists(request.name):
        raise HTTPException(
            status_code = 409,
            detail = f"Category with name '{request.name}' already exists"
        )

    return categories_repository.create_category(
        request.name,
        request.category_type,
    )


async def get_categories() -> dict:
    return categories_repository.get_all_categories()


async def get_category(category_id: int) -> dict:
    
    if not categories_repository.is_category_id_exists(category_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Category '{category_id}' not found"
        )

    return categories_repository.get_category_by_category_id(category_id)


async def delete_category(category_id: int) -> dict:
        
    if not categories_repository.is_category_id_exists(category_id):
        raise HTTPException(
            status_code = 404,
            detail = f"Category '{category_id}' not found"
        )

    if not transactions_repository.is_category_id_exists_in_transactions(category_id):
        raise HTTPException(
            status_code=409,
            detail = f"Category '{category_id}' cannot be deleted because it is used in a transaction",
        )

    return categories_repository.delete_category(category_id)