from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta


from database import get_db
import models
from utils.security import authenticate_user, create_access_token, get_current_user
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # можно также вынести в настройки


@router.post("/token", description="Получение access token для аутентификации пользователя")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"❌ Неверные данные для входа: {form_data.username}")
            raise HTTPException(status_code=401, detail="Неверные логин или пароль")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        logger.info(f"✅ Успешный вход для пользователя: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"❌ Ошибка в /token: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении токена")


@router.get("/verify", description="Проверка валидности токена пользователя")
async def verify_token(
        user: models.User = Depends(get_current_user)
):
    """
    Этот эндпоинт позволяет проверить токен пользователя.
    Если токен валиден, возвращается имя пользователя.
    """
    return {"username": user.username}