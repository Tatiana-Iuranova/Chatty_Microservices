import asyncio
import os
import random
from dotenv import load_dotenv
from send_email import send_email
from faststream.rabbit import RabbitBroker

load_dotenv(".env.local", override=True)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
MAX_RETRIES = 10
RETRY_DELAY = 5

broker = RabbitBroker(RABBITMQ_URL)

async def start_broker_with_retries():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔌 Подключение к RabbitMQ: попытка {attempt}")
            await broker.start()
            return
        except Exception as e:
            print(f"⚠️ Ошибка подключения: {e}")
            if attempt == MAX_RETRIES:
                print("❌ Не удалось подключиться к RabbitMQ.")
                raise
            await asyncio.sleep(RETRY_DELAY)

@broker.subscriber("user.registered")
async def handle_user_registered(msg: dict):
    email = msg.get("email")
    if email:
        code = random.randint(100000, 999999)
        print(f"📩 Отправка кода {code} на {email}")
        await send_email(email, code, "confirmation")

if __name__ == "__main__":
    import uvloop
    uvloop.install()
    asyncio.run(start_broker_with_retries())
