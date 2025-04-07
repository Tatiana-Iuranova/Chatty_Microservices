from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth_service import models,schemas
from auth_service.database import get_db
from auth_service.utils.security import get_password_hash


router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, нет ли такого пользователя
    existing_user = await db.execute(select(models.User).where(models.User.username == user_in.username))
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")

    # Создаем пользователя
    user = models.User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email)

@router.patch("/users/{user_id}/activate", response_model=schemas.UserResponse)
async def activate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Получаем пользователя по ID
    user = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Активируем пользователя
    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email, is_active=user.is_active)