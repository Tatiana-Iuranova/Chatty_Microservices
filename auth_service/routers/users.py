from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from utils.security import get_password_hash
from utils.messaging import rabbit_broker
import models
import schemas
import random

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, description="Регистрация нового пользователя")
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка уникальности имени
    existing_user = await db.execute(select(models.User).where(models.User.username == user_in.username))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")

    # Проверка уникальности email
    existing_email = await db.execute(select(models.User).where(models.User.email == user_in.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    # Генерация кода подтверждения
    verification_code = str(random.randint(100000, 999999))

    user = models.User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password),
        verification_code=verification_code
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Отправка сообщения в RabbitMQ
    try:
        await rabbit_broker.publish(
            {
                "username": user.username,
                "email": user.email,
                "code": verification_code
            },
            routing_key="user.registered"
        )
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения в RabbitMQ: {e}")

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email, is_admin=user.is_admin)


@router.post("/verify", description="Подтверждение email по коду")
async def verify_email(data: schemas.EmailVerification, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_verified:
        return {"message": "Email уже подтверждён"}

    if user.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user.is_verified = True
    user.verification_code = None
    await db.commit()

    return {"message": "Email успешно подтверждён"}


@router.post("/request-password-reset", description="Запрос на сброс пароля")
async def request_password_reset(data: schemas.PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email не подтверждён")

    code = str(random.randint(100000, 999999))
    user.verification_code = code
    await db.commit()

    try:
        await rabbit_broker.publish(
            {
                "username": user.username,
                "email": user.email,
                "code": code,
                "type": "password_reset"
            },
            routing_key="user.registered"
        )
    except Exception as e:
        print(f"❌ Ошибка при отправке email: {e}")

    return {"message": "Код для сброса пароля отправлен на email"}


@router.post("/reset-password", description="Сброс пароля")
async def reset_password(data: schemas.PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user.hashed_password = get_password_hash(data.new_password)
    user.verification_code = None
    await db.commit()

    return {"message": "Пароль успешно сброшен"}


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
