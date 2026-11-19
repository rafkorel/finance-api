from main import app

from httpx import ASGITransport, AsyncClient
import pytest

@pytest.mark.anyio
async def test_expense_route_exists():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:

        response = await client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()["paths"]
        assert "post" in data["/api/v1/transactions/expense"]
