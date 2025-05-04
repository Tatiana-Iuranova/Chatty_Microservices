FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN chmod +x wait-for-rabbitmq.sh

# Загружаем переменные окружения перед запуском
ENTRYPOINT ["/bin/sh", "-c", ". /app/.env.local && ./wait-for-rabbitmq.sh && python email_consumer.py"]

