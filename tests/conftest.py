import pytest
from httpx import AsyncClient

from app.main import app
from app.utils.service_config import BASE_URL


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        yield ac
