from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter, Logger
from routers.posts import post_router
from routers.comment import comment_router
from routers.like import like_router
from fastapi.staticfiles import StaticFiles
from routers import image

# Инициализация FastAPI

router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")
app = FastAPI(
    title="PostService API",
    version="1.0.0",
    description="API для управления постами, комментариями и лайками",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/posts",  # внешний префикс
    root_path_in_servers=True  # включаем генерацию серверов с префиксом
)
# Подключение папки со статическими файлами
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение маршрутов
app.include_router(post_router,  tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(like_router, prefix="/likes", tags=["Likes"])
app.include_router(image.router, prefix="/images", tags=["Images"])

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}