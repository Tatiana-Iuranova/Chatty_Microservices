# admin_service/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from utils.auth_client import authenticate_user, verify_token

router = APIRouter()
security = HTTPBearer()

@router.post("/auth/token")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = await authenticate_user(form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Неверные логин или пароль")
    return user_data  # вернёт token и token_type

@router.get("/auth/verify")
async def verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = await verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Неверный токен или пользователь не найден")
    return user_data
