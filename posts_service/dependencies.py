from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings

# Используем HTTP Bearer схему
oauth2_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")



        if not user_id:
            raise HTTPException(status_code=401, detail="ID не найден")

        return {"user_id": int(user_id)}
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")