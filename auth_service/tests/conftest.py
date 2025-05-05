import pytest
from httpx import AsyncClient


BASE_URL = "http://auth_service:8003"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(base_url=BASE_URL) as ac:
        yield ac


@pytest.fixture(scope="session")
def user_token():
    return "Bearer valid_user_token"
