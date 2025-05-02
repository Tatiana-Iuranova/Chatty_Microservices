#!/usr/bin/env bash
set -e

# Выход при ошибке
set -e

# Ожидаем запуск базы данных

# Устанавливаем значения по умолчанию, если переменные не заданы
DB_HOST="${DB_HOST:-post_db}"
DB_PORT="${DB_PORT:-5432}"

echo "Using DB_HOST=$DB_HOST"
echo "Using DB_PORT=$DB_PORT"

wait_for_db(){
  echo "Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
  done
  echo "База данных доступна!"
}
wait_for_db
# Применяем миграции
echo "Применяем миграции Alembic..."
alembic upgrade head

# Запускаем приложение
echo "Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload