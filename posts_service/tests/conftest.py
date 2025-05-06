
import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.test'))

# Подключение к БД
@pytest.fixture(scope="session")
def test_db_url():
    return f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

@pytest_asyncio.fixture(scope="session")
async def test_db(test_db_url):
    engine = create_async_engine(test_db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db


    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# 💡 Добавляем недостающие фикстуры
BASE_AUTH_URL = "http://localhost:8003/auth"

@pytest_asyncio.fixture(scope="session")
async def user1_token():
    user_data = {
        "email": "user1@example.com",
        "password": "password1",
        "username": "user1"
    }

    async with AsyncClient(base_url=BASE_AUTH_URL) as ac:
        # Регистрация (можно игнорировать 400, если пользователь уже есть)
        await ac.post("/users/register", json=user_data)

        # Логин (OAuth2PasswordRequestForm требует именно form-data)
        response = await ac.post(
            "/auth/token",
            data={
                "username": user_data["username"],  # важно: username — это email
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json()["access_token"]
        return token


@pytest_asyncio.fixture(scope="session")
def user1_id():
    return 1