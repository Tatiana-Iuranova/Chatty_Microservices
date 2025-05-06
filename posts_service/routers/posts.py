from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Union
from typing import List
from models import Post
from database import get_db
from schemas import PostCreate, PostUpdate, PostInDB
from dependencies import get_current_user

import aio_pika
import logging
import json

logger = logging.getLogger(__name__)

post_router = APIRouter()


# --- RabbitMQ ---
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"
EXCHANGE_NAME = "post_exchange"
ROUTING_KEY = "post.created"

async def publish_to_rabbitmq(message: dict):
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT)
        body = json.dumps(message).encode()

        await exchange.publish(
            aio_pika.Message(body=body),
            routing_key=ROUTING_KEY
        )

        await channel.close()
        await connection.close()
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
        # Можно не выбрасывать исключение, чтобы не прерывать основной флоу
        raise


#  --- Создание поста ---
@post_router.post("/", response_model=PostInDB, summary="Создать пост")
async def create_post(
        post: PostCreate, db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    try:
        new_post = Post(**post.dict(), user_id=current_user["user_id"])
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)

        # Отправка события в RabbitMQ
        await publish_to_rabbitmq({
            "post_id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "user_id": new_post.user_id
        })

        return new_post

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка БД при создании поста: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании поста")


# ---  Получение всех постов ---
@post_router.get("/", response_model=List[PostInDB], summary="Получить все посты")
async def get_all_posts(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Post))
    return result.scalars().all()


# --- Получение одного поста ---
@post_router.get("/{post_id}", response_model=PostInDB, summary="Получить пост по ID")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return post


#  --- Обновление поста ---
@post_router.put("/{post_id}", response_model=PostInDB, summary="Обновить пост")
async def update_post(post_id: int, post: PostUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalars().first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return db_post


# ---  Удаление поста ---
@post_router.delete("/{post_id}", response_model=PostInDB, summary="Удалить пост")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db),    current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    db_post = result.scalars().first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    await db.delete(db_post)
    await db.commit()
    return db_post


# # --- Получение постов по пользователям ---
# @post_router.get(""
#                  "/by_user",
#                  response_model=List[PostInDB],
#                  summary="Посты по пользователям")
#
# async def get_posts_by_users(
#         user_ids: List[int] = Query(..., description="Список ID пользователей"),
#         db: AsyncSession = Depends(get_db)
# ):
#     if not user_ids:
#         raise HTTPException(status_code=400, detail="Не переданы user_ids")
#
#     # Запрос к базе данных, чтобы получить посты для этих пользователей
#     result = await db.execute(select(Post).where(Post.user_id.in_(user_ids)))
#     posts = result.scalars().all()
#
#     if not posts:
#         raise HTTPException(status_code=404, detail="Посты не найдены для указанных пользователей")
#
#     return posts

@post_router.get("/posts/by_user/{user_id}", response_model=List[PostInDB], summary="Получить посты пользователя")
async def get_posts_by_user(
        user_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Запрос к базе данных, чтобы получить все посты для пользователя с user_id
    result = await db.execute(select(Post).where(Post.user_id == user_id))
    posts = result.scalars().all()

    if not posts:
        raise HTTPException(status_code=404, detail="Посты не найдены для данного пользователя")

    return posts