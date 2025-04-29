#!/usr/bin/env bash
set -e
# Устанавливаем значения по умолчанию, если переменные не заданы
DB_HOST="${DB_HOST:-admin_db}"
DB_PORT="${DB_PORT:-5432}"

echo "Using DB_HOST=$DB_HOST"
echo "Using DB_PORT=$DB_PORT"


## Устанавливаем PYTHONPATH
#PYTHONPATH=/app exec uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Ожидаем запуск базы данных
wait_for_db(){
  echo "Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
  done
  echo "База данных доступна!"
}

# Применяем миграции
echo "Применяем миграции Alembic..."
alembic upgrade head

# Запускаем приложение
echo "Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload