import pytest

from sqlalchemy import text

from app.database import SessionFactory, engine

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