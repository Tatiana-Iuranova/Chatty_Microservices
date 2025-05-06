#!/bin/bash
set -e

# Ожидаем запуск базы данных
DB_HOST="${DB_HOST:-auth_db}"
DB_PORT="${DB_PORT:-5432}"

RABBIT_HOST="${RABBIT_HOST:-rabbitmq}"
RABBIT_PORT="${RABBIT_PORT:-5672}"

echo "Using DB_HOST=$DB_HOST"
echo "Using DB_PORT=$DB_PORT"
echo "Using RABBIT_HOST=$RABBIT_HOST"
echo "Using RABBIT_PORT=$RABBIT_PORT"

wait_for_db(){
  echo "⌛ Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "✅ База данных доступна!"
}

wait_for_rabbitmq(){
  echo "⌛ Ждём RabbitMQ на $RABBIT_HOST:$RABBIT_PORT..."
  while ! nc -z "$RABBIT_HOST" "$RABBIT_PORT"; do
    sleep 1
  done
  echo "✅ RabbitMQ доступен!"
}

wait_for_db
wait_for_rabbitmq

echo "🚀 Применяем миграции Alembic..."
alembic upgrade head

echo "🚀 Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8003 --reload
