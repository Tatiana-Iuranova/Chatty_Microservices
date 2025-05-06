import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8003/auth"  # Основной путь теперь начинается с /auth для всех эндпоинтов аутентификации

@pytest.mark.asyncio
async def test_auth():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Регистрация первого пользователя
        user1 = {"email": "user1@example.com", "password": "password1", "username": "user1"}
        response = await client.post("/users/register", json=user1)  # Путь теперь начинается с /users
        assert response.status_code == 200
        user1_id = response.json()["id"]

        # 2. Логин первого пользователя и получение токена
        response = await client.post("/auth/token", json={"username": user1["username"], "password": user1["password"]})
        assert response.status_code == 200
        user1_token = response.json()["access_token"]

        # 3. Регистрация второго пользователя
        user2 = {"email": "user2@example.com", "password": "password2", "username": "user2"}
        response = await client.post("/users/register", json=user2)  # Путь теперь начинается с /users
        assert response.status_code == 200
        user2_id = response.json()["id"]

        # 4. Логин второго пользователя и получение токена
        response = await client.post("/auth/token", json={"username": user2["username"], "password": user2["password"]})
        assert response.status_code == 200
        user2_token = response.json()["access_token"]

