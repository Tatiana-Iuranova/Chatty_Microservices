import pytest
from httpx import AsyncClient
import sys
import os

# Добавляем путь к проекту в sys.path для корректного импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app  # где запускается FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac
