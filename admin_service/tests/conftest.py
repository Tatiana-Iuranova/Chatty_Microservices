import pytest
import pytest_asyncio
from httpx import AsyncClient
import sys
import os

# Добавляем путь к проекту в sys.path для корректного импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Импортируем FastAPI приложение
from admin_service.main import app
from sqlalchemy.ext.asyncio import AsyncSession
from admin_service.database import get_db

@pytest_asyncio.fixture(scope="module")
async def client():
    # Убираем параметр 'app' из конструктора AsyncClient
    async with AsyncClient(base_url="http://testserver") as ac:
        yield ac