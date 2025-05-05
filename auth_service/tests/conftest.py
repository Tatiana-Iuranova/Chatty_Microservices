import os, pytest, pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from auth_service.models import Base
from auth_service.database import get_db
from auth_service.main import app
from httpx import AsyncClient, ASGITransport

# переменные из .env.test
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.test'))

@pytest.fixture(scope="session")
def test_db_url():
    user = os.getenv("TEST_DB_USER")
    pwd  = os.getenv("TEST_DB_PASSWORD")
    host = os.getenv("TEST_DB_HOST")
    port = os.getenv("TEST_DB_PORT")
    name = os.getenv("TEST_DB_NAME")
    return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{name}"

@pytest_asyncio.fixture(scope="session")
async def test_db(test_db_url):
    engine = create_async_engine(test_db_url, echo=True)
    async with engine.begin() as conn:
        # создаём таблицы
        await conn.run_sync(Base.metadata.create_all)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
    async with engine.begin() as conn:
        # чистим после тестов
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(test_db):
    # переопределяем get_db → тестовая сессия
    def _override():
        yield test_db
    app.dependency_overrides[get_db] = _override

    # httpx-клиент для ASGI
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield