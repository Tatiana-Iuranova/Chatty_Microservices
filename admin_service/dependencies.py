from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings

# Используем HTTP Bearer схему
oauth2_scheme = HTTPBearer()

async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        is_admin = payload.get("is_admin", False)

        if not is_admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        if not user_id:
            raise HTTPException(status_code=401, detail="ID не найден")

        return {"user_id": int(user_id), "is_admin": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")
