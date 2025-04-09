import pytest
import httpx
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_flow(auth_client, posts_client, subscription_client):
    # 1. Зарегистрировать первого пользователя
    user1 = {"username": "alice", "password": "secret123"}
    r = await auth_client.post("/register", json=user1)
    assert r.status_code == 201
    token1 = r.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Зарегистрировать второго пользователя
    user2 = {"username": "bob", "password": "secret123"}
    r = await auth_client.post("/register", json=user2)
    assert r.status_code == 201
    token2 = r.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 3. Создать пост от первого пользователя
    post_data = {"title": "Hello", "content": "This is a test post"}
    r = await posts_client.post("/posts", json=post_data, headers=headers1)
    assert r.status_code == 201
    post = r.json()

    # 4. Подписаться вторым пользователем на первого
    sub_data = {"target_username": "alice"}
    r = await subscription_client.post("/subscribe", json=sub_data, headers=headers2)
    assert r.status_code == 200

    # 5. Проверить, что второй пользователь видит пост первого
    r = await subscription_client.get("/feed", headers=headers2)
    assert r.status_code == 200
    feed = r.json()
    assert any(p["title"] == post["title"] for p in feed)