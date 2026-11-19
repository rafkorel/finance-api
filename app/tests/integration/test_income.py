from decimal import Decimal
import uuid

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from main import app

from app.models.accounts import Account
from app.models.categories import Category
from app.models.transactions import Transaction

@pytest.fixture
async def income_setup(verified_test_db):

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
                type = 'income'
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
async def test_income_increases_balance(income_setup, verified_test_db):

    account_id, category_id = income_setup
    transaction_data = {
        "account_id": account_id,
        "category_id": category_id,
        "amount": "50",
        "date": "2026-11-20"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transactions/income", json=transaction_data)

    assert response.status_code == 201, response.text

    data = response.json()
    transaction_id = data["transaction_id"]

    async with verified_test_db() as session:

        transaction = await session.get(Transaction, transaction_id)
        account = await session.get(Account, account_id)

    assert transaction is not None
    assert transaction.account_id == account_id
    assert transaction.category_id == category_id
    assert transaction.amount == Decimal("50")
    assert transaction.account_amount == Decimal("50")

    assert account is not None
    assert account.balance == Decimal("150")