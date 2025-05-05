import httpx

AUTH_SERVICE_URL = "http://auth_service:8003"  # Используется в Docker-сети

async def get_user_from_auth_service(user_id: int) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
    except httpx.RequestError as e:
        print(f"Ошибка запроса к auth_service: {e}")
        return None

async def get_user(user_id: int):
    return await get_user_from_auth_service(user_id)

async def get_all_users():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/")
            if response.status_code == 200:
                return response.json()
            return []
    except httpx.RequestError as e:
        print(f"Ошибка при получении всех пользователей: {e}")
        return []

async def set_block_status(user_id: int, blocked: bool):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{AUTH_SERVICE_URL}/users/{user_id}/block",
                json={"is_blocked": blocked}
            )
            return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Ошибка при обновлении статуса блокировки: {e}")
        return False

async def change_role(user_id: int, role: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{AUTH_SERVICE_URL}/users/{user_id}/role",
                json={"role": role}
            )
            return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Ошибка при смене роли: {e}")
        return False

async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user and user.get("is_admin") is True)
