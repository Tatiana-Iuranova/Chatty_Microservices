

import pytest
from httpx import AsyncClient

AUTH_SERVICE_URL = "http://auth_service:8003"

@pytest.fixture(scope="session")
async def auth_client():
    async with AsyncClient(base_url=AUTH_SERVICE_URL) as client:
        yield client

@pytest.fixture(scope="session")
async def user1(auth_client):
    user_data = {
        "email": "user1@example.com",
        "password": "password1",
        "username": "user1"
    }

    # Пытаемся зарегистрировать пользователя (можно игнорировать ошибку, если уже зарегистрирован)
    await auth_client.post("/register", json=user_data)

    # Логинимся
    response = await auth_client.post("/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })

    assert response.status_code == 200
    response_json = response.json()
    return {
        "token": response_json["access_token"],
        "id": response_json.get("user_id") or response_json.get("id")  # зависит от API
    }

@pytest.fixture(scope="session")
async def user1_token(user1):
    return user1["token"]

@pytest.fixture(scope="session")
async def user1_id(user1):
    return user1["id"]
