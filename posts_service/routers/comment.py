from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from posts_service import models, schemas, database

router = APIRouter()

# Создание комментария
async def create_comment(db: AsyncSession, comment: schemas.CommentCreate) -> models.Comment:
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

# Получение комментариев по ID поста
async def get_comments_by_post(db: AsyncSession, post_id: int) -> list[models.Comment]:
    result = await db.execute(select(models.Comment).filter(models.Comment.post_id == post_id))
    return result.scalars().all()

# Обновление комментария
async def update_comment(db: AsyncSession, comment_id: int, comment_update: schemas.CommentUpdate) -> models.Comment | None:
    result = await db.execute(select(models.Comment).filter(models.Comment.id == comment_id))
    db_comment = result.scalars().first()
    if db_comment is None:
        return None
    for key, value in comment_update.dict(exclude_unset=True).items():
        setattr(db_comment, key, value)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

# Удаление комментария
async def delete_comment(db: AsyncSession, comment_id: int) -> models.Comment | None:
    result = await db.execute(select(models.Comment).filter(models.Comment.id == comment_id))
    db_comment = result.scalars().first()
    if db_comment is None:
        return None
    await db.delete(db_comment)
    await db.commit()
    return db_comment


# Эндпоинты FastAPI для комментариев

# Создание комментария
@router.post("/", response_model=schemas.CommentInDB)
async def create_comment_endpoint(
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(database.get_async_session)
):
    return await create_comment(db, comment)

# Получение комментариев для поста
@router.get("/{post_id}", response_model=list[schemas.CommentInDB])
async def get_comments(
    post_id: int,
    db: AsyncSession = Depends(database.get_async_session)
):
    comments = await get_comments_by_post(db, post_id)
    return comments

# Обновление комментария
@router.patch("/{comment_id}", response_model=schemas.CommentInDB)
@router.put("/{comment_id}", response_model=schemas.CommentInDB)
async def update_comment_endpoint(
    comment_id: int,
    comment: schemas.CommentUpdate,
    db: AsyncSession = Depends(database.get_async_session)
):
    db_comment = await update_comment(db, comment_id, comment)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

# Удаление комментария
@router.delete("/{comment_id}", response_model=schemas.CommentInDB)
async def delete_comment_endpoint(
    comment_id: int,
    db: AsyncSession = Depends(database.get_async_session)
):
    db_comment = await delete_comment(db, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment