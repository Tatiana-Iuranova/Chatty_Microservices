# admin_service/utils/auth_client.py
import httpx

AUTH_SERVICE_URL = "http://auth_service:8003"

async def authenticate_user(username: str, password: str) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f" Ошибка при запросе в auth_service: {e}")
        return None

async def verify_token(token: str) -> dict | None:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/auth/verify", headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        print(f"❌ Ошибка при верификации токена: {e}")
        return None



async def get_all_users():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_SERVICE_URL}/users/")
        if response.status_code == 200:
            return response.json()
        return []

async def set_block_status(user_id: int, blocked: bool):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{AUTH_SERVICE_URL}/users/{user_id}/block",
            json={"is_blocked": blocked}
        )
        return response.status_code == 200

async def change_role(user_id: int, role: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{AUTH_SERVICE_URL}/users/{user_id}/role",
            json={"role": role}
        )
        return response.status_code == 200
