#!/bin/bash
set -e

# Загрузка переменных окружения
if [ -f "$ENV_FILE" ]; then
  echo "Загружаем переменные из $ENV_FILE"
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Проверка доступности БД
wait_for_db() {
  echo "Ждём базу данных на $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "База данных доступна!"
}

wait_for_db

echo "Патчим alembic.ini URL на тестовую БД..."
sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME|" alembic.ini

# Применяем миграции
echo "Применяем миграции Alembic..."
alembic upgrade head

# Запускаем приложение
echo "Запуск FastAPI приложения..."
exec uvicorn main:app --host 0.0.0.0 --port 8006 --reload
