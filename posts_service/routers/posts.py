from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from posts_service import models, schemas, database

router = APIRouter()

# Создание поста
@router.post("/", response_model=schemas.PostInDB)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(database.get_async_session)
):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    await db.commit()  # Коммит асинхронно
    await db.refresh(db_post)  # Асинхронное обновление
    return db_post

# Обновление поста
@router.patch("/{post_id}", response_model=schemas.PostInDB)
@router.put("/{post_id}", response_model=schemas.PostInDB)
async def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: AsyncSession = Depends(database.get_async_session)
):
    result = await db.execute(select(models.Post).filter(models.Post.id == post_id))
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
@router.delete("/{post_id}", response_model=schemas.PostInDB)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(database.get_async_session)
):
    result = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    db_post = result.scalars().first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(db_post)
    await db.commit()
    return db_post