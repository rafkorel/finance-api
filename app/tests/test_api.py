from main import app

from httpx import ASGITransport, AsyncClient
import pytest
import uuid

from sqlalchemy import text, select, delete
from decimal import Decimal

from app.models.accounts import Account
from app.models.categories import Category
from app.models.transactions import Transaction
from app.database import engine, SessionFactory

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def verified_test_db():

    assert engine.url.database == 'finance_api_test'

    try:

        async with SessionFactory() as session:

            query = text('SELECT current_database()')
            actual_database = await session.scalar(query)

        assert actual_database == 'finance_api_test'

        yield SessionFactory

    finally:

        await engine.dispose()


@pytest.fixture
async def expense_setup(verified_test_db):

    account_name = uuid.uuid4().hex
    category_name = uuid.uuid4().hex

    try:
    
        async with verified_test_db() as session:

            account = Account(
                name = account_name,
                balance = Decimal("100"),
                currency = 'RUB'
            )

            category = Category(
                name = category_name,
                type = 'expense'
            )

            session.add_all([account, category])

            await session.commit()

        yield account.account_id, category.category_id

    finally:

        async with verified_test_db() as session:

            query = select(Account).where(Account.name == account_name)
            result = await session.execute(query)
            account = result.scalar_one_or_none()

            query = select(Category).where(Category.name == category_name)
            result = await session.execute(query)
            category = result.scalar_one_or_none()

            if account is not None:

                query = delete(Transaction).where(Transaction.account_id == account.account_id)
                await session.execute(query)

                await session.delete(account)

            if category is not None:
                await session.delete(category)

            await session.commit()


@pytest.mark.anyio
async def test_openapi_includes_expense_endpoint():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:

        response = await client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()["paths"]
        assert "post" in data["/api/v1/transactions/expense"]


@pytest.mark.anyio
async def test_create_account_persists_balance(verified_test_db):

    account_name = uuid.uuid4().hex
    account_data = {
        "name": account_name,
        "balance": "100",
        "currency": "RUB"
    }

    try:

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:

            response = await client.post("/api/v1/accounts", json=account_data)

        assert response.status_code == 201

        data = response.json()
        account_id = data["account_id"]

        async with verified_test_db() as session:

            account = await session.get(Account, account_id)

            assert account is not None
            assert account.balance == Decimal("100")

    finally:

        async with verified_test_db() as session:

            query = select(Account).where(Account.name == account_name)
            result = await session.execute(query)
            account = result.scalar_one_or_none()

            if account is not None:
                await session.delete(account)
                await session.commit()


@pytest.mark.anyio
async def test_create_expense_decreases_balance(expense_setup, verified_test_db):

    account_id, category_id = expense_setup
    transactions_data = {
        "account_id": account_id,
        "category_id": category_id,
        "amount": "30",
        "date": "2026-11-15"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )   as client:

        response = await client.post("/api/v1/transactions/expense", json=transactions_data)

    assert response.status_code == 201, response.text

    data = response.json()
    transaction_id = data["transaction_id"]

    async with verified_test_db() as session:

        transaction = await session.get(Transaction, transaction_id)
        account = await session.get(Account, account_id)

    assert transaction is not None
    assert transaction.account_id == account_id
    assert transaction.category_id == category_id
    assert transaction.amount == Decimal("30")

    assert account is not None
    assert account.balance == Decimal("70")