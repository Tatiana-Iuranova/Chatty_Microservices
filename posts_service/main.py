from fastapi import FastAPI
from routers.posts import post_router
from routers.comment import comment_router
from routers.like import like_router
# Инициализация FastAPI
app = FastAPI()

# Подключение маршрутов
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(like_router, prefix="/likes", tags=["Likes"])

# Главная страница
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}