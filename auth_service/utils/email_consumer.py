import asyncio
from dotenv import load_dotenv
import random
import os
from send_email import send_email
from faststream.rabbit import RabbitBroker

load_dotenv(".env.local", override=True)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
MAX_RETRIES = 10
RETRY_DELAY = 5  # секунд

broker = RabbitBroker(RABBITMQ_URL)

# Повторное подключение с задержкой при ошибке
async def start_broker_with_retries():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Попытка подключения к RabbitMQ: {attempt}")
            await broker.start()
            return  # успешно подключились
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            if attempt == MAX_RETRIES:
                print("Не удалось подключиться к RabbitMQ после нескольких попыток.")
                raise
            await asyncio.sleep(RETRY_DELAY)

@broker.subscriber("user.registered")
async def handle_user_registered(msg: dict):
    email = msg.get("email")
    username = msg.get("username")

    if email:
        confirmation_code = random.randint(100000, 999999)
        print(f"Отправка письма на {email} с кодом: {confirmation_code}")
        await send_email(email, confirmation_code, "confirmation")

if __name__ == "__main__":
    import uvloop
    uvloop.install()
    asyncio.run(start_broker_with_retries())

