#!/bin/bash
set -e

# Ожидаем БД
wait_for_db() {
  echo "Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "База данных доступна!"
}

wait_for_db

# Патчим alembic.ini под тестовую/продовую БД
echo "Обновляем sqlalchemy.url в alembic.ini..."
sed -i "s|^sqlalchemy.url.*|sqlalchemy.url = postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}|" alembic.ini

# Миграции
echo "Применяем миграции Alembic..."
alembic upgrade head

# Стартуем
echo "Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload