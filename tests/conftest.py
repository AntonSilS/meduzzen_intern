import pytest
from httpx import AsyncClient

from app.main import app
from app.utils.service_config import settings


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=app, base_url=settings.BASE_URL) as ac:
        yield ac
