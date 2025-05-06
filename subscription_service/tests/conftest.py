import pytest
from httpx import AsyncClient
import uuid
import os

# Получение базовых URL для сервисов через переменные окружения (если они определены)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8003")
POSTS_SERVICE_URL = os.getenv("POSTS_SERVICE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
async def auth_client():
    async with AsyncClient(base_url=AUTH_SERVICE_URL) as client:
        yield client

@pytest.fixture(scope="session")
async def posts_client():
    async with AsyncClient(base_url=POSTS_SERVICE_URL) as client:
        yield client

# Создание уникальных пользователей для тестов
@pytest.fixture(scope="session")
async def user1(auth_client):
    user_data = {
        "email": f"user1_{uuid.uuid4()}@example.com",  # Уникальный email
        "password": "password1",
        "username": "user1"
    }
    await auth_client.post("/register", json=user_data)
    response = await auth_client.post("/login", json=user_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    response_json = response.json()
    return {
        "token": response_json["access_token"],
        "id": response_json.get("user_id") or response_json.get("id")
    }

@pytest.fixture(scope="session")
async def user2(auth_client):
    user_data = {
        "email": f"user2_{uuid.uuid4()}@example.com",  # Уникальный email
        "password": "password2",
        "username": "user2"
    }
    await auth_client.post("/register", json=user_data)
    response = await auth_client.post("/login", json=user_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    response_json = response.json()
    return {
        "token": response_json["access_token"],
        "id": response_json.get("user_id") or response_json.get("id")
    }

# Токены пользователей для тестов
@pytest.fixture(scope="session")
async def user1_token(user1):
    return user1["token"]

@pytest.fixture(scope="session")
async def user2_token(user2):
    return user2["token"]

# ID пользователей для тестов
@pytest.fixture(scope="session")
async def user1_id(user1):
    return user1["id"]

@pytest.fixture(scope="session")
async def user2_id(user2):
    return user2["id"]

# Создание поста для проверки в сервисе постов
@pytest.fixture(scope="session")
async def post_id(user1_token, posts_client):
    headers = {"Authorization": f"Bearer {user1_token}"}
    post_data = {"title": "Пост от user1", "content": "Контент поста"}
    response = await posts_client.post("/posts", json=post_data, headers=headers)
    assert response.status_code == 201, f"Post creation failed: {response.text}"
    return response.json()["id"]
