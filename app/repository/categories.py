from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.categories import Category

async def create_category(name: str, category_type: str, session: AsyncSession) -> Category:

    category = Category(
        name = name,
        type = category_type
    )

    session.add(category)

    await session.commit()
    await session.refresh(category)

    return category


async def is_category_exists(name: str, category_type: str, session: AsyncSession) -> bool:

    query = select(Category).where(Category.name == name, Category.type == category_type)
    result = await session.execute(query)

    return result.scalar_one_or_none() is not None


async def get_all_categories(session: AsyncSession) -> Sequence[Category]:

    query = select(Category)
    result = await session.execute(query)

    return  result.scalars().all()


async def get_category_by_category_id(category_id : int, session) -> Category | None:

    return await session.get(Category, category_id)


async def delete_category(category_id: int, session: AsyncSession) -> dict[str, Category] | None:

    category = await session.get(Category, category_id)

    if category is None:
        return None
    
    await session.delete(category)
    await session.flush()
    return {"deleted category": category}


async def is_category_id_exists(category_id: int, session: AsyncSession) -> bool:

    if await session.get(Category, category_id) is None:
        return False
    return True


async def type_check_income(category_id: int, session: AsyncSession) -> bool:

    query = select(Category).where(Category.category_id == category_id)
    result = await session.execute(query)
    category = result.scalar_one()

    if category.type != 'income':
        return False
    return True


async def type_check_expense(category_id: int, session: AsyncSession) -> bool:

    query = select(Category).where(Category.category_id == category_id)
    result = await session.execute(query)
    category = result.scalar_one()

    if category.type != 'expense':
        return False
    return True


async def categories_is_empty(session: AsyncSession) -> bool:

    query = select(Category)
    result = await session.execute(query)
    categories = result.scalars().all()

    return categories == []


async def get_category_name_by_id(category_id: int, session: AsyncSession) -> str:

    query = select(Category).where(Category.category_id == category_id)
    result = await session.execute(query)
    category = result.scalar_one()

    return category.name
