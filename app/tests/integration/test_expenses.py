from main import app

from decimal import Decimal
import uuid

from httpx import ASGITransport, AsyncClient, MockTransport, Response
import pytest
from sqlalchemy import delete, select

from app.models.accounts import Account
from app.models.categories import Category
from app.models.transactions import Transaction

from app.integrations import cbr

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
async def test_expense_lowers_balance(expense_setup, verified_test_db):

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


@pytest.mark.anyio
async def test_not_enough_money(expense_setup, verified_test_db):

    account_id, category_id = expense_setup
    transactions_data = {
        "account_id": account_id,
        "category_id": category_id,
        "amount": "130",
        "date": "2026-11-15"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transactions/expense", json=transactions_data)

    assert response.status_code == 400, response.text

    data = response.json()
    assert data['detail'] == 'Expense amount cannot exceed the account balance'

    async with verified_test_db() as session:

        account = await session.get(Account, account_id)

        query = select(Transaction).where(Transaction.account_id == account_id)
        result = await session.execute(query)
        transaction = result.scalar_one_or_none()

    assert account is not None
    assert account.balance == Decimal("100")

    assert transaction is None


@pytest.mark.anyio
async def test_delete_restores_balance(expense_setup, verified_test_db):

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

        response = await client.delete(f"/api/v1/transactions/{transaction_id}")

        assert response.status_code == 200

    async with verified_test_db() as session:

        account = await session.get(Account, account_id)

        transaction = await session.get(Transaction, transaction_id)

    assert account is not None
    assert account.balance == Decimal("100")

    assert transaction is None


def fake_cbr_response(_request):
    return Response(status_code=503)


def fake_cbr_client(**kwargs):
    return AsyncClient(transport=MockTransport(fake_cbr_response), **kwargs)


@pytest.mark.anyio
async def test_cbr_error_keeps_balance(expense_setup, verified_test_db, monkeypatch):

    monkeypatch.setattr(cbr, "AsyncClient", fake_cbr_client)

    account_id, category_id = expense_setup
    transactions_data = {
        "account_id": account_id,
        "category_id": category_id,
        "amount": "1",
        "currency": "USD",
        "date": "2026-11-15"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transactions/expense", json=transactions_data)

    assert response.status_code == 502, response.text

    data = response.json()
    assert data['detail'] == "CBR Server Status Error"

    async with verified_test_db() as session:

        account = await session.get(Account, account_id)

        query = select(Transaction).where(Transaction.account_id == account_id)
        result = await session.execute(query)
        transaction = result.scalar_one_or_none()

    assert account is not None
    assert account.balance == Decimal("100")

    assert transaction is None
