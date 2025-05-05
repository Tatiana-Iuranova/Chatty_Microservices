import pytest
from httpx import AsyncClient

BASE_URL = "http://auth_service:8003"


@pytest.mark.asyncio
async def test_auth():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Регистрация первого пользователя
        user1 = {
            "email": "user1@example.com",
            "password": "password1",
            "username": "user1"
        }
        response = await client.post("/register", json=user1)
        assert response.status_code == 200
        user1_id = response.json()["id"]

        # 2. Логин первого пользователя и получение токена
        response = await client.post("/login", json={
            "email": user1["email"],
            "password": user1["password"]
        })
        assert response.status_code == 200
        user1_token = response.json()["access_token"]

        # 3. Регистрация второго пользователя
        user2 = {
            "email": "user2@example.com",
            "password": "password2",
            "username": "user2"
        }
        response = await client.post("/register", json=user2)
        assert response.status_code == 200
        user2_id = response.json()["id"]

        # 4. Логин второго пользователя и получение токена
        response = await client.post("/login", json={
            "email": user2["email"],
            "password": user2["password"]
        })
        assert response.status_code == 200
        user2_token = response.json()["access_token"]
