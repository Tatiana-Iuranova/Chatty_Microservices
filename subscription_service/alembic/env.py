import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from config import settings
from models import Base

# Создание движка
engine = create_async_engine(settings.async_database_url, echo=True)

# Получение конфигурации Alembic
config = context.config
config.set_main_option("sqlalchemy.url", settings.async_database_url)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Подключаем метаданные моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )