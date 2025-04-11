from fastapi import FastAPI
from routers.posts import router as posts
from routers.comment import router as comments
from routers.like import router as likes
from faststream.rabbit.fastapi import RabbitRouter, Logger
# Инициализация FastAPI

router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")
app = FastAPI(
    title="PostService API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/api",  # внешний префикс
    root_path_in_servers=True  # включаем генерацию серверов с префиксом
)


# Подключение маршрутов
app.include_router(posts, prefix="/posts", tags=["Posts"])
app.include_router(comments, prefix="/comments", tags=["Comments"])
app.include_router(likes, prefix="/likes", tags=["Likes"])

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}