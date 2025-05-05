FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN chmod +x docker-entrypoint.sh

EXPOSE 8004

ENV ENV_FILE="/app/.env.test"

ENTRYPOINT ["/app/docker-entrypoint.sh"]