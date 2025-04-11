from asyncio import Event

from fastapi import FastAPI
from sqlalchemy.sql.operators import from_

from routers.subscription_router import router as subscription_router
from schemas import SubscriptionResponse
from faststream.rabbit.fastapi import RabbitRouter


# Создание экземпляра RabbitRouter для подключения к RabbitMQ
rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")
app = FastAPI(
    title="Subscription Service API",   # Название вашего API
    version="1.0.0",                   # Версия вашего API
    description="API для управления подписками на события",  # Описание API
    openapi_url="/openapi.json",        # URL для OpenAPI JSON документа
    docs_url="/docs",                  # URL для стандартной документации (Swagger UI)
    redoc_url="/redoc")               # URL для альтернативной документации (ReDoc)
# Подключаем маршруты из отдельных файлов
app.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])

# Пример публикации события подписки в RabbitMQ
@rabbit_router.subscribe("user_subscribed")
async def handle_user_subscribed(event: Event):
    data = event.payload
    user_id = data.get("user_id")
    follower_id = data.get("follower_id")
    print(f"User {follower_id} subscribed to user {user_id}")
    return {"message": f"User {follower_id} subscribed to user {user_id}"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Subscription_Services API"}