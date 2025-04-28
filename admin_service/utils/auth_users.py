# Простейшая "база"
USERS_DB = {
    1: {"id": 1, "email": "user1@example.com", "role": "user", "is_blocked": False},
    2: {"id": 2, "email": "admin@example.com", "role": "admin", "is_blocked": False},
}

async def get_user(user_id: int):
    return USERS_DB.get(user_id)

async def get_all_users():
    return list(USERS_DB.values())

async def set_block_status(user_id: int, blocked: bool):
    user = USERS_DB.get(user_id)
    if user:
        user["is_blocked"] = blocked

async def change_role(user_id: int, role: str):
    user = USERS_DB.get(user_id)
    if user:
        user["role"] = role

async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    return user and user["role"] == "admin"
