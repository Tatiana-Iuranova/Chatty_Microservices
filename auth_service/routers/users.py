from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from database import get_db
from utils.security import get_password_hash
from utils.messaging import rabbit_broker  # Импортируем rabbit_broker, не rabbit_router
from schemas import EmailVerification
from fastapi import HTTPException
from sqlalchemy import select
import random

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

    verification_code = str(random.randint(100000, 999999))

    user = models.User(
        username=user_in.username,
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password),
        verification_code = verification_code
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Публикуем сообщение в RabbitMQ
    try:
        await rabbit_broker.publish(
            {
                "username": user_in.username,
                "email": user_in.email,
                "code": verification_code  # передаём тот же код!
            },
            routing_key="user.registered"
        )
        print(f"Message sent to RabbitMQ for user {user_in.username}")
    except Exception as e:
        print(f"Error while sending message to RabbitMQ: {e}")

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email)




@router.post("/verify", description="Подтверждение email по коду из письма")
async def verify_email(data: EmailVerification, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == data.email))
    user = result.scalar_one_or_none()


    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_verified:
        return {"message": "Email уже подтверждён"}

    print(f"🔍 код в базе: {user.verification_code}, от клиента: {data.code}")



    if user.verification_code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user.is_verified = True
    user.verification_code = None
    await db.commit()

    return {"message": "Email успешно подтверждён"}


