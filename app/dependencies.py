from app.database import SessionFactory

async def get_session():
    async with SessionFactory() as session:
        yield session