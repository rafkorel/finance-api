from fastapi import FastAPI

from app.api.v1.accounts import router as accounts_router
from app.api.v1.categories import router as categories_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.transfers import router as transfers_router
from app.api.v1.statistics import router as statistics_router

app = FastAPI()

app.include_router(
    accounts_router,
    prefix="/api/v1",
    tags=["accounts"]
)

app.include_router(
    categories_router,
    prefix="/api/v1",
    tags=["categories"]
)

app.include_router(
    transactions_router,
    prefix="/api/v1",
    tags=["transactions"]
)

app.include_router(
    transfers_router,
    prefix="/api/v1",
    tags=["transfers"]
)

app.include_router(
    statistics_router,
    prefix="/api/v1",
    tags=["statistics"]
)