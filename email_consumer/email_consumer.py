print("🔥 email_consumer запущен")

import asyncio
import os
from dotenv import load_dotenv
from send_email import send_email
from faststream.rabbit import RabbitBroker

load_dotenv(".env.local", override=True)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
broker = RabbitBroker(RABBITMQ_URL)

@broker.subscriber("user.registered")
async def handle_user_registered(msg: dict):
    print("📨 Получено сообщение:", msg)

    email = msg.get("email")
    code = msg.get("code")
    email_type = msg.get("type", "confirmation")  # ✅ выбор типа письма

    if email and code:
        print(f"📩 Отправка кода {code} на {email} для типа: {email_type}")
        await send_email(email, code, email_type)
    else:
        print("⚠️ Получено сообщение без email или кода:", msg)

if __name__ == "__main__":
    import uvloop
    uvloop.install()

    async def main():
        await broker.start()
        while True:
            await asyncio.sleep(1)

    asyncio.run(main())
