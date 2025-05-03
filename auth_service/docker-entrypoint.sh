#!/usr/bin/bash
set -e

# Устанавливаем значения по умолчанию
RABBIT_HOST="${RABBIT_HOST:-rabbitmq}"
RABBIT_PORT="${RABBIT_PORT:-5672}"

echo "Using RABBIT_HOST=$RABBIT_HOST"
echo "Using RABBIT_PORT=$RABBIT_PORT"

wait_for_rabbit() {
  echo "⏳ Ожидание RabbitMQ на $RABBIT_HOST:$RABBIT_PORT..."
  while ! nc -z "$RABBIT_HOST" "$RABBIT_PORT"; do
    echo "🐇 RabbitMQ пока не доступен..."
    sleep 1
  done
  echo "✅ RabbitMQ доступен!"
}

wait_for_rabbit

echo "🚀 Запуск email_consumer.py..."
exec python email_consumer.py
