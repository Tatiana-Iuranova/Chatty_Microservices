import pytest
from httpx import AsyncClient

BASE_URL = "http://admin_service:8006"  # 👈 имя сервиса в docker-compose-test.yml

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(base_url=BASE_URL) as ac:
        yield ac

@pytest.fixture(scope="session")
def admin_token():
    # Тут ты можешь подставить реальный токен или добавить авторизацию через login-эндпоинт
    return "Bearer valid_admin_token"
