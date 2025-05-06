import pytest
from httpx import AsyncClient

BASE_URL = "http://subscription_service:8004"

@pytest.mark.asyncio
async def test_subscription(user1_id, user2_token, user2_id, post_id):
    async with AsyncClient(base_url=BASE_URL) as client:
        headers = {"Authorization": f"Bearer {user2_token}"}

        # 1. Подписка второго пользователя на первого
        response = await client.post(
            f"/subscriptions/subscribe/{user1_id}?follower_id={user2_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Subscription failed: {response.text}"

        # 2. Проверка, что второй пользователь видит пост первого
        response = await client.get(
            f"/subscriptions/feed/{user2_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Feed retrieval failed: {response.text}"

        # Проверка, что в ленте есть пост с id первого пользователя
        posts = response.json().get("posts", [])
        assert any(post["id"] == post_id for post in posts), f"Post with id {post_id} not found in feed"

        # 3. Проверка подписки на самого себя
        response = await client.post(
            f"/subscriptions/subscribe/{user1_id}?follower_id={user1_id}",
            headers=headers
        )
        assert response.status_code == 400, f"Should not allow user to subscribe to themselves: {response.text}"

        # 4. Проверка повторной подписки
        response = await client.post(
            f"/subscriptions/subscribe/{user1_id}?follower_id={user2_id}",
            headers=headers
        )
        assert response.status_code == 400, f"Should not allow user to subscribe twice: {response.text}"

