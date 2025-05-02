#!/usr/bin/env bash
set -e
# Устанавливаем значения по умолчанию, если переменные не заданы
DB_HOST="${DB_HOST:-auth_db}"
DB_PORT="${DB_PORT:-5432}"

echo "Using DB_HOST=$DB_HOST"
echo "Using DB_PORT=$DB_PORT"

wait_for_db() {
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    echo "Database is not ready yet..."
    sleep 1
  done
  echo "Database is ready!"
}
wait_for_db

echo "Applying Alembic migrations..."
alembic upgrade head

echo "Starting AuthService..."
exec uvicorn main:app --host 0.0.0.0 --port 8003  --reload