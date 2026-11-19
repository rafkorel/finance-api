from decimal import Decimal

from sqlalchemy import select

from app.models.accounts import Account
from main import app

import uuid

from httpx import ASGITransport, AsyncClient
import pytest

@pytest.mark.anyio
async def test_account_is_saved(verified_test_db):

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
