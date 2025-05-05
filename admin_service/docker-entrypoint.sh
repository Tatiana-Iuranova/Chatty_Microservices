#!/bin/bash
set -e

# Отладочный вывод
echo "Используемые переменные окружения:"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_NAME=$DB_NAME"

# Ожидаем доступность БД
wait_for_db() {
  echo "Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "База данных доступна!"
}

wait_for_db

# Патчим alembic.ini на актуальные переменные
echo "Патчим alembic.ini..."
sed -i "s|^sqlalchemy.url = .*|sqlalchemy.url = postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|" alembic.ini

# Применяем миграции
echo "Применяем миграции Alembic..."
alembic upgrade head

# Запускаем FastAPI
echo "Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload
