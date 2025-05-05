from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter, Logger
from routers.posts import post_router
from routers.comment import comment_router
from routers.like import like_router
from fastapi.staticfiles import StaticFiles
from routers import image
from utils.messaging import rabbit_broker

app = FastAPI(
    title="Posts Service API",
    version="1.0.0",
    description="API для управления постами, комментариями и лайками",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/posts",  # внешний префикс
    root_path_in_servers=True  # включаем генерацию серверов с префиксом
)
# Подключение маршрутов
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(like_router, prefix="/likes", tags=["Likes"])
app.include_router(image.router, prefix="/images", tags=["Images"])
# Подключение папки со статическими файлами
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await rabbit_broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_broker.close()

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}