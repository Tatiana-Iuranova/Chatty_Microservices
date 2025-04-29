

import pytest
from httpx import AsyncClient

BASE_URL = "http://posts_service:8000"

@pytest.mark.asyncio
async def test_post(user1_token, user1_id):
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = {"Authorization": f"Bearer {user1_token}"}
        post_data = {"title": "Первый пост", "content": "Тестовый контент"}

        # 1. Создание поста первым пользователем
        response = await client.post("/posts", json=post_data, headers=headers)
        assert response.status_code == 201
        post_id = response.json()["id"]

        # 2. Попытка создания поста без токена
        response = await client.post("/posts", json=post_data)
        assert response.status_code == 401

        # 3. Попытка подписки без токена
        response = await client.post(f"/subscribe/{user1_id}")
        assert response.status_code == 401
