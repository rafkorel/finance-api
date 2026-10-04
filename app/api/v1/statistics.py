from datetime import date

from fastapi import APIRouter, Query

from app.service import statistics as statistics_service

router = APIRouter()

@router.get("/statistics/balance")
async def get_balance_statistics():
    return await statistics_service.get_balance_statistics()

@router.get("/statistics/categories")
async def get_categories_statistics(category_type: str = Query(..., max_length=7)):
    return await statistics_service.get_categories_statistics(category_type)

@router.get("/statistics/period")
async def get_transactions_statistics_by_period(date_from: date, date_to: date):
    return await statistics_service.get_transactions_statistics_by_period(date_from, date_to)