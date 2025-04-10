from fastapi import FastAPI
from routers.posts import router as posts
from routers.comment import router as comments
from routers.like import router as likes
# Инициализация FastAPI
app = FastAPI()

# Подключение маршрутов
app.include_router(posts, prefix="/posts", tags=["Posts"])
app.include_router(comments, prefix="/comments", tags=["Comments"])
app.include_router(likes, prefix="/likes", tags=["Likes"])

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}