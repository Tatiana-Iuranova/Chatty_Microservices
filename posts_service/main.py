from fastapi import FastAPI


from faststream import RabbitRouter, Logger

from routers.posts import post_router
from routers.comment import comment_router
from routers.like import like_router

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
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(like_router, prefix="/likes", tags=["Likes"])

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}