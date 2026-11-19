from decimal import Decimal
import uuid
from httpx import ASGITransport, AsyncClient, MockTransport, Response
import pytest
from sqlalchemy import or_, delete, select

from main import app

from app.models.accounts import Account
from app.models.transfers import Transfer

from app.integrations import cbr

xml_data = """
    <ValCurs Date="13.11.2026">
        <Valute ID="R01235">
            <CharCode>USD</CharCode>
            <Nominal>1</Nominal>
            <Value>100</Value>
        </Valute>

        <Valute ID="R01239">
            <CharCode>EUR</CharCode>
            <Nominal>1</Nominal>
            <Value>100,50</Value>
        </Valute>
    </ValCurs>
"""

@pytest.fixture
async def transfer_accounts(verified_test_db):

    first_account_name = uuid.uuid4().hex
    second_account_name = uuid.uuid4().hex

    try:
        async with verified_test_db() as session:

            first_account = Account(
                name = first_account_name,
                balance = Decimal("1000"),
                currency = "RUB"
            )

            second_account = Account(
                name = second_account_name,
                balance = Decimal("5"),
                currency = "USD"
            )

            session.add_all([first_account, second_account])

            await session.commit()

        yield first_account.account_id, second_account.account_id

    finally:

        async with verified_test_db() as session:

            query = select(Account).where(Account.name == first_account_name)
            result = await session.execute(query)
            first_account = result.scalar_one_or_none()

            query = select(Account).where(Account.name == second_account_name)
            result = await session.execute(query)
            second_account = result.scalar_one_or_none()

            account_ids = []
            if first_account is not None:
                account_ids.append(first_account.account_id)
            if second_account is not None:
                account_ids.append(second_account.account_id)

            if account_ids:
                query = delete(
                    Transfer
                ).where(
                    or_(
                        Transfer.from_account_id.in_(account_ids),
                        Transfer.to_account_id.in_(account_ids)
                    )
                )
                await session.execute(query)

            if first_account is not None:
                await session.delete(first_account)

            if second_account is not None:
                await session.delete(second_account)

            await session.commit()


def fake_cbr_response(_request):
    return Response(status_code=200, text=xml_data)


def fake_cbr_client(**kwargs):
    return AsyncClient(transport=MockTransport(fake_cbr_response), **kwargs)


@pytest.mark.anyio
async def test_cross_currency_transfer(transfer_accounts, verified_test_db, monkeypatch):

    monkeypatch.setattr(cbr, "AsyncClient", fake_cbr_client)

    first_account_id, second_account_id = transfer_accounts
    transfer_data ={
        "from_account_id": first_account_id,
        "to_account_id": second_account_id,
        "amount": "200"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transfers", json=transfer_data)

    assert response.status_code == 201, response.text

    data = response.json()
    transfer_id = data["transfer_id"]

    async with verified_test_db() as session:

        first_account = await session.get(Account, first_account_id)
        second_account = await session.get(Account, second_account_id)
        transfer = await session.get(Transfer, transfer_id)

    assert first_account is not None
    assert first_account.balance == Decimal("800")

    assert second_account is not None
    assert second_account.balance == Decimal("7")

    assert transfer is not None
    assert transfer.from_account_id == first_account_id
    assert transfer.to_account_id == second_account_id
    assert transfer.amount == Decimal("200")
    assert transfer.credited_amount == Decimal("2")


@pytest.mark.anyio
async def test_transfer_not_enough_money(transfer_accounts, verified_test_db, monkeypatch):

    monkeypatch.setattr(cbr, "AsyncClient", fake_cbr_client)

    first_account_id, second_account_id = transfer_accounts
    transfer_data ={
        "from_account_id": first_account_id,
        "to_account_id": second_account_id,
        "amount": "1100"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transfers", json=transfer_data)

    assert response.status_code == 400

    response_data = response.json()
    assert response_data["detail"] == "Transfer amount cannot exceed the source account balance"

    async with verified_test_db() as session:

        first_account = await session.get(Account, first_account_id)
        second_account = await session.get(Account, second_account_id)

        query = select(Transfer).where(Transfer.from_account_id == first_account_id)
        result = await session.execute(query)
        transfer = result.scalar_one_or_none()

    assert first_account is not None
    assert first_account.balance == Decimal("1000")

    assert second_account is not None
    assert second_account.balance == Decimal("5")

    assert transfer is None


@pytest.mark.anyio
async def test_delete_restores_both_balances(transfer_accounts, verified_test_db, monkeypatch):

    monkeypatch.setattr(cbr, "AsyncClient", fake_cbr_client)

    first_account_id, second_account_id = transfer_accounts
    transfer_data ={
        "from_account_id": first_account_id,
        "to_account_id": second_account_id,
        "amount": "200"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post("/api/v1/transfers", json=transfer_data)

        assert response.status_code == 201, response.text

        data = response.json()
        transfer_id = data["transfer_id"]

        response = await client.delete(f"/api/v1/transfers/{transfer_id}")

        assert response.status_code == 200, response.text

    async with verified_test_db() as session:

        first_account = await session.get(Account, first_account_id)
        second_account = await session.get(Account, second_account_id)
        transfer = await session.get(Transfer, transfer_id)

    assert first_account is not None
    assert first_account.balance == Decimal("1000")

    assert second_account is not None
    assert second_account.balance == Decimal("5")

    assert transfer is None