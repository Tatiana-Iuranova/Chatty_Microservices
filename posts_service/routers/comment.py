from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import CommentBase, CommentCreate, CommentUpdate, CommentInDB
from models import Comment
from database import get_db
from dependencies import get_current_user


comment_router = APIRouter()

# Создание комментария
async def create_comment(db: AsyncSession, comment: CommentCreate) -> Comment:
    db_comment = Comment(**comment.model_dump())
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

# Получение комментариев по ID поста
async def get_comments_by_post(db: AsyncSession, post_id: int) -> list[Comment]:
    result = await db.execute(select(Comment).filter(Comment.post_id == post_id))
    return result.scalars().all()

# Обновление комментария
async def update_comment(db: AsyncSession, comment_id: int, comment_update: CommentUpdate) -> Comment | None:
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    db_comment = result.scalars().first()
    if db_comment is None:
        return None
    for key, value in comment_update.dict(exclude_unset=True).items():
        setattr(db_comment, key, value)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

# Удаление комментария
async def delete_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    db_comment = result.scalars().first()
    if db_comment is None:
        return None
    await db.delete(db_comment)
    await db.commit()
    return db_comment


# Эндпоинты FastAPI для комментариев

# Создание комментария
@comment_router.post(
    "/",
    response_model=CommentInDB,
    summary="Написать комментарий",
    description="Позволяет пользователю написать комментарий"
)
async def create_comment_endpoint(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await create_comment(db, comment)

# Получение комментариев для поста
@comment_router.get(
    "/{post_id}",
    response_model=list[CommentInDB],
    summary="Получение комментариев для поста",
    description="Позволяет пользователю получить комментарий для конкретного поста"
)
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comments = await get_comments_by_post(db, post_id)
    return comments

# Обновление комментария
@comment_router.put(
    "/{comment_id}",
    response_model=CommentInDB,
    summary="Обновление комментария",
    description="Позволяет пользователю обновить комментарий"
)
async def update_comment_endpoint(
    comment_id: int,
    comment: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_comment = await update_comment(db, comment_id, comment)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

# Удаление комментария
@comment_router.delete(
    "/{comment_id}",
    response_model=CommentInDB,
    summary="Удаление комментария",
    description="Позволяет пользователю удалить комментарий"
)
async def delete_comment_endpoint(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_comment = await delete_comment(db, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment