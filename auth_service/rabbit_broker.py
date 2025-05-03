from fastapi import FastAPI, HTTPException
from faststream.rabbit import RabbitBroker
from send_email import send_email
import random
import os

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv('.env.local', override=True)

# Инициализация RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
broker = RabbitBroker(RABBITMQ_URL)

# Инициализация FastAPI
app = FastAPI()

# Подключаем брокер RabbitMQ
@app.on_event("startup")
async def startup():
    await broker.start()  # Подключение к RabbitMQ при старте приложения

@app.on_event("shutdown")
async def shutdown():
    await broker.close()  # Закрытие соединения при завершении работы приложения

# Пример подписки
@broker.subscriber("user.registered")
async def handle_user_registered(msg: dict):
    email = msg.get("email")
    username = msg.get("username")

    if email:
        confirmation_code = random.randint(100000, 999999)
        send_email(email, confirmation_code, "confirmation")

@app.post("/register")
async def register_user(user_in: dict):
    # Пример логики регистрации пользователя
    username = user_in.get("username")
    email = user_in.get("email")

    # Публикуем сообщение в RabbitMQ
    try:
        await broker.publisher.publish(
            "user.registered",
            {"username": username, "email": email}
        )
        return {"message": "User registered and message sent to RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while sending message to RabbitMQ: {e}")
