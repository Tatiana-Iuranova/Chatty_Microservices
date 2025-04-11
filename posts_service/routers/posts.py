from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import PostBase, PostCreate, PostUpdate, PostInDB
from models import Post
from database import get_db

post_router = APIRouter()

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
    db_post = Post(**post.dict())
    db.add(db_post)
    await db.commit()  # Коммит асинхронно
    await db.refresh(db_post)  # Асинхронное обновление
    return db_post

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