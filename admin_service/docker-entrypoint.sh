#!/bin/bash

# Выход при ошибке
set -e

# Загрузим переменные из .env.test, если есть
if [ -f /app/.env.test ]; then
  echo "Загружаем переменные из .env.test"
  export $(grep -v '^#' /app/.env.test | xargs)
fi

# Ожидаем запуск базы данных
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
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload