from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from database import get_db
from utils.security import get_password_hash
from faststream import RabbitRouter

rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")


router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, description="Регистрация нового пользователя")
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, нет ли такого пользователя
    existing_user = await db.execute(select(models.User).where(models.User.username == user_in.username))
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    existing_email = await db.execute(
        select(models.User).where(models.User.email == user_in.email)
    )
    existing_email = existing_email.scalar_one_or_none()

    if existing_email:
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    # Создаем пользователя
    user = models.User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    await rabbit_router.publish(
        "user.registered",  # название очереди или топика
        {"username": user_in.username, "email": user_in.email}  # данные, которые отправляем
    )

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email)





@router.patch("/users/{user_id}/activate", response_model=schemas.UserResponse, description="Активация пользователя")
async def activate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Получаем пользователя по ID
    user = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        raise HTTPException(status_code=400, detail="Пользователь уже активирован")

    # Активируем пользователя
    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email, is_active=user.is_active)