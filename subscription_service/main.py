from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
from routers.subscription_router import router as subscription_router
from utils.messaging import rabbit_broker


app = FastAPI(
    title="Subscription Service API",  # Название вашего API
    version="1.0.0",  # Версия вашего API
    description="API для управления подписками на события",  # Описание API
    openapi_url="/openapi.json",  # URL для OpenAPI JSON документа
    docs_url="/docs",  # URL для стандартной документации (Swagger UI)
    redoc_url="/redoc",  # URL для альтернативной документации (ReDoc)
    root_path="/subscribe",
    root_path_in_servers=True
)

# Подключаем маршруты из отдельных файлов
app.include_router(subscription_router, prefix="/subscribe", tags=["subscribe"])

# Создаем экземпляр RabbitRouter
rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")


# Подключение к RabbitMQ
async def connect_broker():
    await rabbit_router.broker.connect()

# Подключаем брокер при старте приложения
@app.on_event("startup")
async def startup_event():
    await rabbit_broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_broker.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Subscription_Services API"}
