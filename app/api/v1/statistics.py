from datetime import date

from fastapi import APIRouter, Query, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session

from app.service import statistics as statistics_service

router = APIRouter()

@router.get("/statistics/balance")
async def get_balance_statistics(session: AsyncSession = Depends(get_session)):
    return await statistics_service.get_balance_statistics(session)


@router.get("/statistics/categories")
async def get_categories_statistics(
    category_type: str = Query(..., max_length=7),
    session: AsyncSession = Depends(get_session)
):
    return await statistics_service.get_categories_statistics(category_type, session)


@router.get("/statistics/period")
async def get_transactions_statistics_by_period(
    date_from: date,
    date_to: date,
    session: AsyncSession = Depends(get_session)
):
    return await statistics_service.get_transactions_statistics_by_period(date_from, date_to, session)