from fastapi import APIRouter, Depends, HTTPException
from utils.auth_users import (
    get_user, get_all_users, set_block_status, change_role, is_admin
)

router = APIRouter()

# Заглушка для current_user
async def get_current_user_id():
    return 2  # представим, что это админ

@router.get("/admin/users")
async def list_users(current_user: int = Depends(get_current_user_id)):
    if not await is_admin(current_user):
        raise HTTPException(403, detail="Forbidden")
    return await get_all_users()

@router.post("/admin/users/{user_id}/block")
async def block_user(user_id: int, current_user: int = Depends(get_current_user_id)):
    if not await is_admin(current_user):
        raise HTTPException(403, detail="Forbidden")
    await set_block_status(user_id, True)
    return {"message": "User blocked"}

@router.post("/admin/users/{user_id}/unblock")
async def unblock_user(user_id: int, current_user: int = Depends(get_current_user_id)):
    if not await is_admin(current_user):
        raise HTTPException(403, detail="Forbidden")
    await set_block_status(user_id, False)
    return {"message": "User unblocked"}

@router.patch("/admin/users/{user_id}/role")
async def update_role(user_id: int, role: str, current_user: int = Depends(get_current_user_id)):
    if not await is_admin(current_user):
        raise HTTPException(403, detail="Forbidden")
    if role not in ["user", "admin"]:
        raise HTTPException(400, detail="Invalid role")
    await change_role(user_id, role)
    return {"message": "Role updated"}