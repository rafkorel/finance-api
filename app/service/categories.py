from typing import Sequence

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.categories import AddCategoryRequest
from app.models.categories import Category

from app.repository import categories as categories_repository
from app.repository import transactions as transactions_repository

async def create_category(request: AddCategoryRequest, session: AsyncSession) -> Category:

    if await categories_repository.is_category_exists(request.name, request.category_type, session):
        raise HTTPException(
            status_code = 409,
            detail = f"Category with name '{request.name}' and type '{request.category_type}' already exists"
        )
    try:
        return await categories_repository.create_category(
            request.name,
            request.category_type,
            session
        )
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database operation failed"
        )


async def get_categories(session: AsyncSession) -> Sequence[Category]:
    return await categories_repository.get_all_categories(session)


async def get_category(category_id: int, session: AsyncSession) -> Category:

    category = await categories_repository.get_category_by_category_id(category_id, session)

    if category is None:
        raise HTTPException(
            status_code = 404,
            detail = f"Category '{category_id}' not found"
        )

    return category


async def delete_category(category_id: int, session: AsyncSession) -> dict[str, Category]:

    if await transactions_repository.is_category_id_exists_in_transactions(category_id, session):
        raise HTTPException(
            status_code=409,
            detail = f"Category '{category_id}' cannot be deleted because it is used in a transaction",
        )    

    try:
        deleted_category = await categories_repository.delete_category(category_id, session)

        if deleted_category is None:
            raise HTTPException(
                status_code = 404,
                detail = f"Category '{category_id}' not found"
            )

        await session.commit()
        
        return deleted_category
    
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Database operation failed"
        )