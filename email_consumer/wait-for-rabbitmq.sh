#!/usr/bin/env bash
set -e

# НИЧЕГО не загружай вручную из .env.local — docker-compose это делает сам!

RABBITMQ_HOST="${RABBITMQ_HOST:-rabbitmq}"
RABBITMQ_PORT="${RABBITMQ_PORT:-5672}"

echo "🔍 Переменные окружения:"
echo "RABBITMQ_HOST=$RABBITMQ_HOST"
echo "RABBITMQ_PORT=$RABBITMQ_PORT"

echo "⏳ Ожидание RabbitMQ на $RABBITMQ_HOST:$RABBITMQ_PORT..."
while ! nc -z "$RABBITMQ_HOST" "$RABBITMQ_PORT"; do
  echo "❌ Всё ещё не доступен..."
  sleep 2
done

echo "✅ RabbitMQ доступен!"

exec python email_consumer.py
