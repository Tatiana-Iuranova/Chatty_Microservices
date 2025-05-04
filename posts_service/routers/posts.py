import logging
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy.exc import SQLAlchemyError
from schemas import PostBase, PostCreate, PostUpdate, PostInDB
from models import Post
from database import get_db

# Подключаем RabbitMQ
rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")

# создаём функцию publisher
publish_post_created = rabbit_router.publisher("post.created")

post_router = APIRouter()

logger = logging.getLogger(__name__)
# Создание поста
@post_router.post(
    "/",
    response_model=PostInDB,
    summary="Создать пост",
    description="Позволяет пользователю создать пост"
)
async def create_post(
        post: PostCreate,
        db: AsyncSession = Depends(get_db)
):
    try:
        logger.info("Запрос на создание поста получен.")

        # Создаем новый пост
        db_post = Post(**post.dict())
        db.add(db_post)
        # Коммит асинхронно
        await db.commit()
        # Асинхронное обновление объекта
        await db.refresh(db_post)

        logger.info(f"Пост с ID {db_post.id} успешно создан.")

        # Публикуем событие в RabbitMQ
        publish_post_created({"post_id": db_post.id, "title": db_post.title, "content": db_post.content})

        logger.info(f"Событие для поста {db_post.id} опубликовано в RabbitMQ.")

        return db_post

    except SQLAlchemyError as e:
        # Откатываем изменения в БД в случае ошибки
        await db.rollback()
        logger.error(f"Ошибка при сохранении поста в БД: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании поста"
        )

    except Exception as e:
        # Логируем ошибку и возвращаем исключение для RabbitMQ
        logger.error(f"Ошибка при публикации события RabbitMQ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при публикации события"
        )

@post_router.get(
    "/",
    response_model=list[PostInDB],
    summary="Получение списка постов",
    description="Позволяет пользователю получить список постов"
)
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return posts

# Получение одного поста по ID
@post_router.get(
    "/{post_id}",
    response_model=PostInDB,
    summary="Получение конкретного поста",
    description="Позволяет пользователю получить конкретного поста"
)
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
    summary="Редактирование поста",
    description="Позволяет пользователю отредактировать пост"
)
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Обновление поста
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return db_post

# Удаление поста
@post_router.delete(
    "/{post_id}",
    response_model=PostInDB,
    summary="Удаление поста",
    description="Позволяет пользователю удалить пост"
)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(db_post)
    await db.commit()
    return db_post