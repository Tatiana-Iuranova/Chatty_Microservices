from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routers.posts import post_router
from routers.comment import comment_router
from routers.like import like_router
from fastapi.staticfiles import StaticFiles
from routers import image
from database import get_db
from models import Post
from utils.messaging import rabbit_broker


app = FastAPI(
    title="Posts Service API",
    version="1.0.0",
    description="API для управления постами, комментариями и лайками",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="/posts",
    root_path_in_servers=True
)

# Подключение маршрутов
app.include_router(post_router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(like_router, prefix="/likes", tags=["Likes"])
app.include_router(image.router, prefix="/images", tags=["Images"])

app.mount("/static", StaticFiles(directory="static"), name="static")



@app.on_event("startup")
async def startup_event():
    await rabbit_broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_broker.close()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Post Service API"}
