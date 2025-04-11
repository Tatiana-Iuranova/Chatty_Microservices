from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import LikeBase,  LikeCreate, LikeInDB
from models import Like
from database import get_db

like_router = APIRouter()


# Создание лайка
async def create_like(db: AsyncSession, like: LikeCreate) -> Like:
    # Проверка, был ли уже лайк от этого пользователя на этот пост
    result = await db.execute(
        select(Like).filter(Like.post_id == like.post_id, Like.user_id == like.user_id))
    existing_like = result.scalars().first()
    if existing_like:
        raise HTTPException(status_code=400, detail="User has already liked this post")

    db_like = Like(**like.dict())
    db.add(db_like)
    await db.commit()
    await db.refresh(db_like)
    return db_like


# Удаление лайка
async def delete_like(db: AsyncSession, post_id: int, user_id: int) -> Like | None:
    result = await db.execute(
        select(Like).filter(Like.post_id == post_id, Like.user_id == user_id))
    db_like = result.scalars().first()
    if db_like is None:
        return None
    await db.delete(db_like)
    await db.commit()
    return db_like


# Эндпоинты FastAPI для лайков

# Создание лайка
@like_router.post(
    "/",
    response_model=LikeInDB,
    summary="Создание лайка",
    description="Позволяет пользователю создать лайк"
)
async def create_like_endpoint(
        like: LikeCreate,
        db: AsyncSession = Depends(get_db)
):
    return await create_like(db, like)


# Удаление лайка
@like_router.delete(
    "/",
    response_model=LikeInDB,
    summary="Удаление лайка",
    description="Позволяет пользователю удалить лайк"
)
async def delete_like_endpoint(
        post_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    db_like = await delete_like(db, post_id, user_id)
    if db_like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    return db_like