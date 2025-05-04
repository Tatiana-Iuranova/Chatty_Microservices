print("🔥 email_consumer запущен")


import asyncio
import os
import random
from dotenv import load_dotenv
from send_email import send_email
from faststream.rabbit import RabbitBroker

load_dotenv(".env.local", override=True)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
broker = RabbitBroker(RABBITMQ_URL)

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


    async def main():
        await broker.start()
        while True:
            await asyncio.sleep(1)  # не даём приложению завершиться


    if __name__ == "__main__":
        import uvloop

        uvloop.install()
        asyncio.run(main())