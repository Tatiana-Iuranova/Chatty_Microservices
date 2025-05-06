from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import List
from models import Post
from database import get_db
from schemas import PostCreate, PostUpdate, PostInDB
from fastapi import Query
import logging
import httpx
import aio_pika  # Используем aio-pika для асинхронной работы с RabbitMQ

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация RabbitMQ (с использованием aio-pika)
# async def get_rabbitmq_channel():
#     connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
#     channel = await connection.channel()
#     return channel

# Создаём функцию для публикации события
async def publish_post_created(post_data):
    channel = await get_rabbitmq_channel()
    exchange = await channel.declare_exchange('post_exchange', aio_pika.ExchangeType.FANOUT)
    await exchange.publish(
        aio_pika.Message(body=str(post_data).encode()),
        routing_key='post.created'
    )
    await channel.close()

# Инициализируем маршруты для постов
post_router = APIRouter()

# Создание поста
@post_router.post(
    "/",
    response_model=PostInDB,
    summary="Создать пост",
    description="Позволяет пользователю создать пост"
)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Запрос на создание поста получен с данными: {post.dict()}")

        db_post = Post(**post.dict())
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)

        logger.info(f"Пост с ID {db_post.id} успешно создан.")

        # Публикуем событие в RabbitMQ
        await publish_post_created({"post_id": db_post.id, "title": db_post.title, "content": db_post.content})

        logger.info(f"Событие для поста {db_post.id} опубликовано в RabbitMQ.")
        return db_post

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка при сохранении поста в БД: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при создании поста")

    except Exception as e:
        logger.error(f"Ошибка при публикации события RabbitMQ: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при публикации события")

# Получение всех постов
@post_router.get(
    "/",
    response_model=List[PostInDB],
    summary="Получить список постов")
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return posts

# Получение одного поста по ID
@post_router.get(
    "/{post_id}",
    response_model=PostInDB,
    summary="Получить конкретный пост")

async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Обновление поста
@post_router.put(
    "/{post_id}",
    response_model=PostInDB,
    summary="Редактировать пост")
async def update_post(post_id: int, post: PostUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return db_post

# Удаление поста
@post_router.delete(
    "/{post_id}",
    response_model=PostInDB,
    summary="Удалить пост")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(db_post)
    await db.commit()
    return db_post


@post_router.get(
    "/posts/by_user",
    response_model=List[PostInDB],
    summary="Получить посты по пользователям")

async def get_posts_by_users(
        user_ids: List[int] = Query(..., description="Список идентификаторов пользователей для фильтрации постов"),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.user_id.in_(user_ids)))
    posts = result.scalars().all()
    return posts
