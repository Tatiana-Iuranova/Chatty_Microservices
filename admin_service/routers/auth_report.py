from fastapi import Depends, HTTPException

from jose import jwt, JWTError

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi import Depends, HTTPException
from jose import jwt, JWTError


oauth2_scheme = HTTPBearer()

SECRET_KEY = "your_very_secure_secret_key" # обязательно должен совпадать с тем, что в auth_service
ALGORITHM = "HS256"

async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        is_admin = payload.get("is_admin", False)

        if not is_admin:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        return {"user_id": user_id, "is_admin": True}

    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")
