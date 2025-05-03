from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import schemas
from database import get_db
from utils.security import get_password_hash
from utils.messaging import rabbit_broker  # Импортируем rabbit_broker, не rabbit_router

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

    # Публикуем сообщение в RabbitMQ
    try:
        await rabbit_broker.publish(
            {"username": user_in.username, "email": user_in.email},
            routing_key="user.registered"  # FastStream требует routing_key
        )
        print(f"Message sent to RabbitMQ for user {user_in.username}")
    except Exception as e:
        print(f"Error while sending message to RabbitMQ: {e}")

    return schemas.UserResponse(id=user.id, username=user.username, email=user.email)
