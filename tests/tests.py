import pytest
import asyncio
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"  # Заменить на реальный URL


@pytest.mark.asyncio
async def test_auth_post_subscription():
    async with AsyncClient(base_url=BASE_URL) as client:
        # 1. Регистрация первого пользователя
        user1 = {"email": "user1@example.com", "password": "password1", "username": "user1"}
        response = await client.post("/register", json=user1)
        assert response.status_code == 200
        user1_id = response.json()["id"]

        # 2. Логин первого пользователя и получение токена
        response = await client.post("/login", json={"email": user1["email"], "password": user1["password"]})
        assert response.status_code == 200
        user1_token = response.json()["access_token"]

        # 3. Создание поста первым пользователем
        headers = {"Authorization": f"Bearer {user1_token}"}
        post_data = {"title": "Первый пост", "content": "Тестовый контент"}
        response = await client.post("/posts", json=post_data, headers=headers)
        assert response.status_code == 201
        post_id = response.json()["id"]

        # 4. Регистрация второго пользователя
        user2 = {"email": "user2@example.com", "password": "password2", "username": "user2"}
        response = await client.post("/register", json=user2)
        assert response.status_code == 200
        user2_id = response.json()["id"]

        # 5. Логин второго пользователя и получение токена
        response = await client.post("/login", json={"email": user2["email"], "password": user2["password"]})
        assert response.status_code == 200
        user2_token = response.json()["access_token"]

        # 6. Подписка второго пользователя на первого
        headers = {"Authorization": f"Bearer {user2_token}"}
        response = await client.post(f"/subscribe/{user1_id}", headers=headers)
        assert response.status_code == 200

        # 7. Проверка, что второй пользователь видит пост первого
        response = await client.get("/feed", headers=headers)
        assert response.status_code == 200
        posts = response.json()
        assert any(post["id"] == post_id for post in posts)

        # 8. Негативные тесты
        # Попытка создания поста без токена
        response = await client.post("/posts", json=post_data)
        assert response.status_code == 401

        # Попытка подписки без токена
        response = await client.post(f"/subscribe/{user1_id}")
        assert response.status_code == 401