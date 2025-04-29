

import pytest
from httpx import AsyncClient

BASE_URL = "http://subscription_service:8004"

@pytest.mark.asyncio
async def test_subscription(user1_id, user2_token, post_id):
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = {"Authorization": f"Bearer {user2_token}"}

        # 1. Подписка второго пользователя на первого
        response = await client.post(f"/subscribe/{user1_id}", headers=headers)
        assert response.status_code == 200

        # 2. Проверка, что второй пользователь видит пост первого
        response = await client.get("/feed", headers=headers)
        assert response.status_code == 200
        posts = response.json()
        assert any(post["id"] == post_id for post in posts)
