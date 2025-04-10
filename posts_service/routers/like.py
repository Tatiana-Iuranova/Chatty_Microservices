from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from posts_service import models, schemas, database

router = APIRouter()


# Создание лайка
async def create_like(db: AsyncSession, like: schemas.LikeCreate) -> models.Like:
    # Проверка, был ли уже лайк от этого пользователя на этот пост
    result = await db.execute(
        select(models.Like).filter(models.Like.post_id == like.post_id, models.Like.user_id == like.user_id))
    existing_like = result.scalars().first()
    if existing_like:
        raise HTTPException(status_code=400, detail="User has already liked this post")

    db_like = models.Like(**like.dict())
    db.add(db_like)
    await db.commit()
    await db.refresh(db_like)
    return db_like


# Удаление лайка
async def delete_like(db: AsyncSession, post_id: int, user_id: int) -> models.Like | None:
    result = await db.execute(
        select(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == user_id))
    db_like = result.scalars().first()
    if db_like is None:
        return None
    await db.delete(db_like)
    await db.commit()
    return db_like


# Эндпоинты FastAPI для лайков

# Создание лайка
@router.post("/", response_model=schemas.LikeInDB)
async def create_like_endpoint(
        like: schemas.LikeCreate,
        db: AsyncSession = Depends(database.get_async_session)
):
    return await create_like(db, like)


# Удаление лайка
@router.delete("/", response_model=schemas.LikeInDB)
async def delete_like_endpoint(
        post_id: int,
        user_id: int,
        db: AsyncSession = Depends(database.get_async_session)
):
    db_like = await delete_like(db, post_id, user_id)
    if db_like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    return db_like